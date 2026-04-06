"""Configuration and environment variable loading for AI Avatar Pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Pipeline configuration loaded from environment variables."""

    heygen_api_key: str = ""
    fish_api_key: str = ""

    # HeyGen defaults
    default_avatar_id: str = ""
    default_voice_id: str = ""
    video_width: int = 1280
    video_height: int = 720

    # Fish Audio defaults
    fish_model: str = "s2"
    fish_reference_id: str = ""

    # Pipeline defaults
    output_dir: str = "output"
    poll_interval: float = 5.0
    max_poll_time: float = 600.0  # 10 minutes

    # Retry settings
    max_retries: int = 3
    backoff_base: float = 2.0

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables.

        Reads from os.environ and .env file if python-dotenv is available.
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        return cls(
            heygen_api_key=os.environ.get("HEYGEN_API_KEY", ""),
            fish_api_key=os.environ.get("FISH_API_KEY", ""),
            default_avatar_id=os.environ.get("HEYGEN_DEFAULT_AVATAR_ID", ""),
            default_voice_id=os.environ.get("HEYGEN_DEFAULT_VOICE_ID", ""),
            video_width=int(os.environ.get("VIDEO_WIDTH", "1280")),
            video_height=int(os.environ.get("VIDEO_HEIGHT", "720")),
            fish_model=os.environ.get("FISH_MODEL", "s2"),
            fish_reference_id=os.environ.get("FISH_REFERENCE_ID", ""),
            output_dir=os.environ.get("OUTPUT_DIR", "output"),
            poll_interval=float(os.environ.get("POLL_INTERVAL", "5.0")),
            max_poll_time=float(os.environ.get("MAX_POLL_TIME", "600.0")),
            max_retries=int(os.environ.get("MAX_RETRIES", "3")),
            backoff_base=float(os.environ.get("BACKOFF_BASE", "2.0")),
        )

    def validate(self) -> list[str]:
        """Return a list of missing required configuration fields."""
        missing = []
        if not self.heygen_api_key:
            missing.append("HEYGEN_API_KEY")
        return missing

    def redacted(self) -> dict[str, str]:
        """Return config as dict with API keys masked for safe logging."""
        def _mask(val: str) -> str:
            if not val or len(val) < 8:
                return "***" if val else ""
            return val[:4] + "..." + val[-4:]

        return {
            "heygen_api_key": _mask(self.heygen_api_key),
            "fish_api_key": _mask(self.fish_api_key),
            "default_avatar_id": self.default_avatar_id,
            "default_voice_id": self.default_voice_id,
            "video_width": str(self.video_width),
            "video_height": str(self.video_height),
            "output_dir": self.output_dir,
        }
