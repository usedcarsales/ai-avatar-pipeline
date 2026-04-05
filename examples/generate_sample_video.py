#!/usr/bin/env python3
"""Example: Generate an AI avatar video using the pipeline.

Usage:
    # Option A: HeyGen handles voice (default)
    python -m examples.generate_sample_video

    # Option B: Fish Audio custom voice
    VOICE_SOURCE=fish python -m examples.generate_sample_video

Requires .env file or environment variables set (see .env.example).
"""

import asyncio
import logging
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.pipeline import AvatarPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

SAMPLE_SCRIPT = """
Hi there! I'm your AI avatar, powered by the Particulate LLC video pipeline.

This system can generate professional talking-head videos automatically,
using either HeyGen's built-in voices or custom voices from Fish Audio.

Pretty cool, right? Let's build something amazing together.
""".strip()


async def main() -> None:
    config = Config.from_env()

    missing = config.validate()
    if missing:
        print(f"Missing required config: {', '.join(missing)}")
        print("Set environment variables or create a .env file. See .env.example.")
        sys.exit(1)

    pipeline = AvatarPipeline(config)
    voice_source = os.environ.get("VOICE_SOURCE", "heygen")

    print(f"Generating video with voice_source={voice_source}...")
    output = await pipeline.run(
        script=SAMPLE_SCRIPT,
        output_path="output/sample_video.mp4",
        voice_source=voice_source,
    )
    print(f"Video saved to: {output}")


if __name__ == "__main__":
    asyncio.run(main())
