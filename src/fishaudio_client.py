"""Fish Audio API wrapper for text-to-speech and voice cloning."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx

from src.config import Config

logger = logging.getLogger(__name__)

BASE_URL = "https://api.fish.audio"


class FishAudioError(Exception):
    """Base exception for Fish Audio API errors."""


class FishAudioClient:
    """Async client for the Fish Audio TTS and voice cloning API.

    Args:
        config: Pipeline configuration. If None, loads from environment.
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config.from_env()
        if not self.config.fish_api_key:
            raise FishAudioError("FISH_API_KEY is required")
        self._headers = {
            "Authorization": f"Bearer {self.config.fish_api_key}",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        data: Any = None,
        files: Any = None,
        accept: str = "application/json",
    ) -> httpx.Response:
        """Make an API request with retry and exponential backoff.

        Args:
            method: HTTP method.
            path: API endpoint path.
            json: JSON body.
            data: Form data.
            files: Multipart file uploads.
            accept: Accept header value.

        Returns:
            The httpx Response object.

        Raises:
            FishAudioError: On API errors after retries.
        """
        url = f"{BASE_URL}{path}"
        last_exc: Exception | None = None
        headers = {**self._headers, "Accept": accept}

        for attempt in range(self.config.max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.request(
                        method,
                        url,
                        headers=headers,
                        json=json,
                        data=data,
                        files=files,
                    )

                if resp.status_code == 429:
                    wait = self.config.backoff_base ** attempt
                    logger.warning("Fish Audio rate limit, retrying in %.1fs", wait)
                    await asyncio.sleep(wait)
                    continue

                if resp.status_code >= 400:
                    raise FishAudioError(
                        f"Fish Audio API error {resp.status_code}: {resp.text}"
                    )

                return resp

            except httpx.HTTPError as exc:
                wait = self.config.backoff_base ** attempt
                logger.warning(
                    "Fish Audio request failed (attempt %d/%d): %s",
                    attempt + 1,
                    self.config.max_retries,
                    exc,
                )
                last_exc = exc
                await asyncio.sleep(wait)

        raise last_exc or FishAudioError("Request failed after retries")

    async def text_to_speech(
        self,
        text: str,
        reference_id: str | None = None,
        model: str | None = None,
        output_path: str | Path | None = None,
    ) -> bytes:
        """Convert text to speech audio.

        Args:
            text: The text to synthesize.
            reference_id: Voice reference ID for cloned/community voices.
            model: TTS model to use. Defaults to config fish_model.
            output_path: If provided, saves audio bytes to this file path.

        Returns:
            Raw audio bytes (MP3 format).
        """
        ref_id = reference_id or self.config.fish_reference_id
        payload: dict[str, Any] = {
            "text": text,
            "format": "mp3",
        }
        if ref_id:
            payload["reference_id"] = ref_id

        if not text.strip():
            raise FishAudioError("Text cannot be empty")
        if len(text) > 10000:
            raise FishAudioError("Text exceeds 10,000 character limit")

        logger.info("Generating TTS (%d chars, ref=%s)", len(text), ref_id or "default")
        resp = await self._request(
            "POST",
            "/v1/tts",
            json=payload,
            accept="audio/mpeg",
        )
        audio_bytes = resp.content

        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(audio_bytes)
            logger.info("Audio saved to %s (%d bytes)", path, len(audio_bytes))

        return audio_bytes

    async def list_voices(self) -> list[dict[str, Any]]:
        """List available voices in your Fish Audio account.

        Returns:
            List of voice model objects.
        """
        logger.info("Listing Fish Audio voices")
        resp = await self._request("GET", "/model")
        return resp.json().get("items", [])

    async def clone_voice(
        self,
        audio_path: str | Path,
        voice_name: str,
        description: str = "",
    ) -> dict[str, Any]:
        """Clone a voice from an audio sample.

        Args:
            audio_path: Path to the reference audio file (WAV/MP3, 10s+ recommended).
            voice_name: Display name for the cloned voice.
            description: Optional description.

        Returns:
            The created voice model object including its reference ID.

        Raises:
            FishAudioError: If the audio file doesn't exist or API fails.
        """
        path = Path(audio_path)
        if not path.exists():
            raise FishAudioError(f"Audio file not found: {path}")

        logger.info("Cloning voice from %s as '%s'", path, voice_name)

        files = [
            ("voices", (path.name, path.read_bytes(), "audio/mpeg")),
        ]
        data = {
            "visibility": "private",
            "type": "tts",
            "title": voice_name,
            "description": description or f"Cloned voice: {voice_name}",
        }

        resp = await self._request("POST", "/model", data=data, files=files)
        result = resp.json()
        logger.info("Voice cloned: %s", result.get("_id", "unknown"))
        return result
