"""Integration tests for the AvatarPipeline orchestrator.

Live API tests are skipped by default. Set RUN_LIVE_TESTS=1 to enable.
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.config import Config
from src.pipeline import AvatarPipeline, PipelineError

LIVE = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_TESTS", "") != "1",
    reason="Set RUN_LIVE_TESTS=1 to run live API tests",
)


@pytest.fixture
def config() -> Config:
    return Config(
        heygen_api_key="test-key",
        fish_api_key="fish-key",
        default_avatar_id="avatar_test",
        default_voice_id="voice_test",
        poll_interval=0.1,
        max_poll_time=1.0,
        max_retries=1,
        backoff_base=0.1,
    )


@pytest.fixture
def pipeline(config: Config) -> AvatarPipeline:
    return AvatarPipeline(config)


class TestPipelineInit:
    def test_creates_heygen_client(self, pipeline: AvatarPipeline) -> None:
        assert pipeline.heygen is not None

    def test_fish_client_lazy(self, pipeline: AvatarPipeline) -> None:
        assert pipeline._fish is None
        _ = pipeline.fish
        assert pipeline._fish is not None


class TestHeyGenOnlyPipeline:
    @pytest.mark.asyncio
    async def test_full_heygen_flow(self, pipeline: AvatarPipeline, tmp_path: Path) -> None:
        output = tmp_path / "test_video.mp4"
        video_bytes = b"fake-mp4-content"

        with (
            patch.object(
                pipeline.heygen,
                "generate_video",
                new_callable=AsyncMock,
                return_value="vid_001",
            ),
            patch.object(
                pipeline.heygen,
                "wait_for_video",
                new_callable=AsyncMock,
                return_value="https://example.com/video.mp4",
            ),
            patch.object(
                pipeline,
                "_download",
                new_callable=AsyncMock,
            ) as mock_download,
        ):
            # Simulate _download writing the file
            async def write_file(url: str, path: Path) -> None:
                path.write_bytes(video_bytes)

            mock_download.side_effect = write_file

            result = await pipeline.run(
                script="Hello world",
                avatar_id="a1",
                output_path=output,
                voice_source="heygen",
            )

        assert result == output
        assert output.read_bytes() == video_bytes


class TestFishAudioPipeline:
    @pytest.mark.asyncio
    async def test_fish_voice_flow(self, pipeline: AvatarPipeline, tmp_path: Path) -> None:
        output = tmp_path / "test_fish.mp4"

        with (
            patch.object(
                pipeline.fish,
                "text_to_speech",
                new_callable=AsyncMock,
                return_value=b"audio-bytes",
            ),
            patch.object(
                pipeline,
                "_upload_audio_to_heygen",
                new_callable=AsyncMock,
                return_value="https://heygen.com/audio/uploaded.mp3",
            ),
            patch.object(
                pipeline.heygen,
                "_request",
                new_callable=AsyncMock,
                return_value={"data": {"video_id": "vid_fish_001"}},
            ),
            patch.object(
                pipeline.heygen,
                "wait_for_video",
                new_callable=AsyncMock,
                return_value="https://example.com/fish_video.mp4",
            ),
            patch.object(
                pipeline,
                "_download",
                new_callable=AsyncMock,
            ) as mock_download,
        ):
            async def write_file(url: str, path: Path) -> None:
                path.write_bytes(b"fish-video")

            mock_download.side_effect = write_file

            result = await pipeline.run(
                script="Fish voice test",
                output_path=output,
                voice_source="fish",
                voice_id="fish_ref_123",
            )

        assert result == output


@LIVE
class TestLivePipeline:
    """Live API tests — require real API keys and RUN_LIVE_TESTS=1."""

    @pytest.mark.asyncio
    async def test_heygen_list_avatars(self) -> None:
        config = Config.from_env()
        pipeline = AvatarPipeline(config)
        avatars = await pipeline.heygen.list_avatars()
        assert isinstance(avatars, list)

    @pytest.mark.asyncio
    async def test_generate_video_e2e(self) -> None:
        config = Config.from_env()
        pipeline = AvatarPipeline(config)
        result = await pipeline.run(
            script="This is a live test of the AI avatar pipeline.",
            output_path="output/live_test.mp4",
        )
        assert Path(result).exists()
