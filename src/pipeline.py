"""End-to-end AI avatar video pipeline orchestrator."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import httpx

from src.config import Config
from src.fishaudio_client import FishAudioClient
from src.heygen_client import HeyGenClient

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when the pipeline encounters an unrecoverable error."""


class AvatarPipeline:
    """Orchestrates video generation through HeyGen and optionally Fish Audio.

    Supports two modes:
      - voice_source="heygen": HeyGen handles both avatar and voice (simpler).
      - voice_source="fish": Fish Audio generates the voice, HeyGen uses the
        audio file for avatar lip-sync (custom voice support).

    Args:
        config: Pipeline configuration. If None, loads from environment.
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config.from_env()
        self.heygen = HeyGenClient(self.config)
        self._fish: FishAudioClient | None = None

    @property
    def fish(self) -> FishAudioClient:
        """Lazy-initialize Fish Audio client (only needed for voice_source='fish')."""
        if self._fish is None:
            self._fish = FishAudioClient(self.config)
        return self._fish

    async def run(
        self,
        script: str,
        avatar_id: str | None = None,
        output_path: str | Path | None = None,
        voice_source: Literal["heygen", "fish"] = "heygen",
        voice_id: str | None = None,
    ) -> Path:
        """Run the full video generation pipeline.

        Args:
            script: Text script for the avatar to speak.
            avatar_id: HeyGen avatar ID. Falls back to config default.
            output_path: Where to save the final .mp4. Defaults to output_dir/video.mp4.
            voice_source: "heygen" for HeyGen's built-in TTS, "fish" for Fish Audio.
            voice_id: Voice ID (HeyGen voice_id or Fish Audio reference_id).

        Returns:
            Path to the saved .mp4 file.

        Raises:
            PipelineError: On pipeline failures.
        """
        output = Path(output_path) if output_path else Path(self.config.output_dir) / "video.mp4"
        output.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Pipeline start — voice_source=%s, avatar=%s", voice_source, avatar_id)

        if voice_source == "fish":
            return await self._run_with_fish(script, avatar_id, output, voice_id)
        return await self._run_heygen_only(script, avatar_id, output, voice_id)

    async def _run_heygen_only(
        self,
        script: str,
        avatar_id: str | None,
        output: Path,
        voice_id: str | None,
    ) -> Path:
        """Option A: HeyGen handles both avatar rendering and voice."""
        logger.info("Mode A: HeyGen handles voice + avatar")

        video_id = await self.heygen.generate_video(
            script=script,
            avatar_id=avatar_id,
            voice_id=voice_id,
        )

        logger.info("Waiting for video %s to complete...", video_id)
        video_url = await self.heygen.wait_for_video(video_id)

        await self._download(video_url, output)
        logger.info("Pipeline complete — saved to %s", output)
        return output

    async def _run_with_fish(
        self,
        script: str,
        avatar_id: str | None,
        output: Path,
        voice_id: str | None,
    ) -> Path:
        """Option B: Fish Audio generates voice, HeyGen renders avatar with audio.

        Generates TTS audio via Fish Audio, then uploads it to HeyGen
        as the voice input for the avatar video.
        """
        logger.info("Mode B: Fish Audio voice → HeyGen avatar")

        # Step 1: Generate TTS audio
        audio_path = output.parent / f"{output.stem}_voice.mp3"
        await self.fish.text_to_speech(
            text=script,
            reference_id=voice_id,
            output_path=audio_path,
        )
        logger.info("TTS audio saved to %s", audio_path)

        # Step 2: Upload audio to HeyGen and generate video
        # HeyGen v2 supports audio URL input — upload the audio first
        audio_url = await self._upload_audio_to_heygen(audio_path)

        avatar_id = avatar_id or self.config.default_avatar_id
        if not avatar_id:
            raise PipelineError("avatar_id is required")

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "audio",
                        "audio_url": audio_url,
                    },
                    "background": {"type": "color", "value": "#FFFFFF"},
                }
            ],
            "dimension": {
                "width": self.config.video_width,
                "height": self.config.video_height,
            },
        }

        data = await self.heygen._request("POST", "/v2/video/generate", json=payload)
        video_id = data.get("data", {}).get("video_id", "")
        if not video_id:
            raise PipelineError(f"No video_id in HeyGen response: {data}")

        logger.info("Waiting for video %s to complete...", video_id)
        video_url = await self.heygen.wait_for_video(video_id)

        await self._download(video_url, output)
        logger.info("Pipeline complete — saved to %s", output)
        return output

    async def _upload_audio_to_heygen(self, audio_path: Path) -> str:
        """Upload a local audio file to HeyGen and return the hosted URL.

        Args:
            audio_path: Local path to the audio file.

        Returns:
            URL of the uploaded audio on HeyGen's servers.
        """
        logger.info("Uploading audio to HeyGen: %s", audio_path)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"https://api.heygen.com/v1/asset",
                headers={"X-Api-Key": self.config.heygen_api_key},
                files={"file": (audio_path.name, audio_path.read_bytes(), "audio/mpeg")},
            )
        if resp.status_code >= 400:
            raise PipelineError(f"Audio upload failed: {resp.status_code} {resp.text}")
        url = resp.json().get("data", {}).get("url", "")
        if not url:
            raise PipelineError(f"No URL in upload response: {resp.json()}")
        return url

    async def _download(self, url: str, output: Path) -> None:
        """Download a file from a URL and save it locally.

        Args:
            url: The download URL.
            output: Local path to save the file.
        """
        logger.info("Downloading video to %s", output)
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        output.write_bytes(resp.content)
        logger.info("Downloaded %d bytes", len(resp.content))
