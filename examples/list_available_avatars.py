#!/usr/bin/env python3
"""Utility: List all available HeyGen avatars and voices.

Usage:
    python -m examples.list_available_avatars

Requires HEYGEN_API_KEY environment variable or .env file.
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.heygen_client import HeyGenClient

logging.basicConfig(level=logging.WARNING)


async def main() -> None:
    config = Config.from_env()
    if not config.heygen_api_key:
        print("HEYGEN_API_KEY is required. Set it in .env or environment.")
        sys.exit(1)

    client = HeyGenClient(config)

    print("=" * 60)
    print("HEYGEN AVATARS")
    print("=" * 60)
    avatars = await client.list_avatars()
    for av in avatars:
        print(f"  ID: {av.get('avatar_id', 'N/A')}")
        print(f"  Name: {av.get('avatar_name', 'N/A')}")
        print(f"  Gender: {av.get('gender', 'N/A')}")
        print()

    print("=" * 60)
    print("HEYGEN VOICES")
    print("=" * 60)
    voices = await client.list_voices()
    for v in voices:
        print(f"  ID: {v.get('voice_id', 'N/A')}")
        print(f"  Name: {v.get('display_name', v.get('name', 'N/A'))}")
        print(f"  Language: {v.get('language', 'N/A')}")
        print()

    print(f"Total: {len(avatars)} avatars, {len(voices)} voices")


if __name__ == "__main__":
    asyncio.run(main())
