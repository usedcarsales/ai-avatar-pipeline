"""HeyGen API wrapper for AI avatar video generation."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from src.config import Config

logger = logging.getLogger(__name__)

BASE_URL = "https://api.heygen.com"


class HeyGenError(Exception):
    """Base exception for HeyGen API errors."""


class HeyGenRateLimitError(HeyGenError):
    """Raised when the HeyGen API rate limit is hit."""


class HeyGenVideoTimeout(HeyGenError):
    """Raised when video generation exceeds the max poll time."""


class HeyGenClient:
    """Async client for the HeyGen video generation API.

    Args:
        config: Pipeline configuration. If None, loads from environment.
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config.from_env()
        if not self.config.heygen_api_key:
            raise HeyGenError("HEYGEN_API_KEY is required")
        self._headers = {
            "X-Api-Key": self.config.heygen_api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Make an API request with retry and exponential backoff.

        Args:
            method: HTTP method.
            path: API endpoint path (appended to BASE_URL).
            json: JSON body for POST/PUT requests.
            params: Query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            HeyGenRateLimitError: If rate limit persists after retries.
            HeyGenError: On non-retryable API errors.
        """
        url = f"{BASE_URL}{path}"
        last_exc: Exception | None = None

        for attempt in range(self.config.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.request(
                        method, url, headers=self._headers, json=json, params=params
                    )

                if resp.status_code == 429:
                    wait = self.config.backoff_base ** attempt
                    logger.warning("HeyGen rate limit hit, retrying in %.1fs", wait)
                    await asyncio.sleep(wait)
                    last_exc = HeyGenRateLimitError("Rate limit exceeded")
                    continue

                if resp.status_code >= 400:
                    raise HeyGenError(
                        f"HeyGen API error {resp.status_code}: {resp.text}"
                    )

                return resp.json()

            except httpx.HTTPError as exc:
                wait = self.config.backoff_base ** attempt
                logger.warning(
                    "HeyGen request failed (attempt %d/%d): %s — retrying in %.1fs",
                    attempt + 1,
                    self.config.max_retries,
                    exc,
                    wait,
                )
                last_exc = exc
                await asyncio.sleep(wait)

        raise last_exc or HeyGenError("Request failed after retries")

    async def list_avatars(self) -> list[dict[str, Any]]:
        """List all available avatars.

        Returns:
            List of avatar objects with id, name, and preview info.
        """
        logger.info("Listing HeyGen avatars")
        data = await self._request("GET", "/v2/avatars")
        return data.get("data", {}).get("avatars", [])

    async def list_voices(self) -> list[dict[str, Any]]:
        """List all available voices.

        Returns:
            List of voice objects with voice_id, name, and language.
        """
        logger.info("Listing HeyGen voices")
        data = await self._request("GET", "/v2/voices")
        return data.get("data", {}).get("voices", [])

    async def generate_video(
        self,
        script: str,
        avatar_id: str | None = None,
        voice_id: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> str:
        """Submit a video generation request.

        Args:
            script: The text script for the avatar to speak.
            avatar_id: HeyGen avatar ID. Falls back to config default.
            voice_id: HeyGen voice ID. Falls back to config default.
            width: Video width in pixels. Defaults to config value.
            height: Video height in pixels. Defaults to config value.

        Returns:
            The video_id for polling status.

        Raises:
            HeyGenError: If required IDs are missing or API call fails.
        """
        avatar_id = avatar_id or self.config.default_avatar_id
        voice_id = voice_id or self.config.default_voice_id
        if not avatar_id:
            raise HeyGenError("avatar_id is required")

        payload: dict[str, Any] = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script,
                    },
                    "background": {"type": "color", "value": "#FFFFFF"},
                }
            ],
            "dimension": {
                "width": width or self.config.video_width,
                "height": height or self.config.video_height,
            },
        }

        if voice_id:
            payload["video_inputs"][0]["voice"]["voice_id"] = voice_id

        logger.info("Submitting video generation (avatar=%s)", avatar_id)
        data = await self._request("POST", "/v2/video/generate", json=payload)
        video_id = data.get("data", {}).get("video_id", "")
        if not video_id:
            raise HeyGenError(f"No video_id in response: {data}")
        logger.info("Video submitted: %s", video_id)
        return video_id

    async def get_video_status(self, video_id: str) -> dict[str, Any]:
        """Check the status of a video generation job.

        Args:
            video_id: The video ID returned from generate_video.

        Returns:
            Dict with 'status' and optionally 'video_url'.
        """
        data = await self._request(
            "GET", f"/v1/video_status.get", params={"video_id": video_id}
        )
        return data.get("data", {})

    async def wait_for_video(self, video_id: str) -> str:
        """Poll until video is ready and return the download URL.

        Args:
            video_id: The video ID to poll.

        Returns:
            The video download URL.

        Raises:
            HeyGenVideoTimeout: If polling exceeds max_poll_time.
            HeyGenError: If video generation fails.
        """
        start = time.monotonic()
        while True:
            elapsed = time.monotonic() - start
            if elapsed > self.config.max_poll_time:
                raise HeyGenVideoTimeout(
                    f"Video {video_id} not ready after {elapsed:.0f}s"
                )

            status = await self.get_video_status(video_id)
            state = status.get("status", "")

            if state == "completed":
                url = status.get("video_url", "")
                logger.info("Video ready: %s", url)
                return url

            if state == "failed":
                raise HeyGenError(
                    f"Video generation failed: {status.get('error', 'unknown')}"
                )

            logger.debug(
                "Video %s status: %s (%.0fs elapsed)", video_id, state, elapsed
            )
            await asyncio.sleep(self.config.poll_interval)
