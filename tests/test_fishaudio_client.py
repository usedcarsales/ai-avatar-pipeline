"""Unit tests for Fish Audio API client with mocked HTTP calls."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.config import Config
from src.fishaudio_client import FishAudioClient, FishAudioError


@pytest.fixture
def config() -> Config:
    return Config(
        fish_api_key="fish-test-key-456",
        fish_model="s2",
        fish_reference_id="ref_default",
        max_retries=2,
        backoff_base=0.1,
    )


@pytest.fixture
def client(config: Config) -> FishAudioClient:
    return FishAudioClient(config)


def _mock_response(
    status_code: int = 200,
    json_data: dict | None = None,
    content: bytes = b"",
) -> httpx.Response:
    if json_data is not None:
        return httpx.Response(status_code, json=json_data)
    return httpx.Response(status_code, content=content)


class TestFishAudioClientInit:
    def test_requires_api_key(self) -> None:
        with pytest.raises(FishAudioError, match="FISH_API_KEY"):
            FishAudioClient(Config(fish_api_key=""))

    def test_creates_with_valid_key(self, config: Config) -> None:
        client = FishAudioClient(config)
        assert client.config.fish_api_key == "fish-test-key-456"


class TestTextToSpeech:
    @pytest.mark.asyncio
    async def test_returns_audio_bytes(self, client: FishAudioClient) -> None:
        audio = b"\xff\xfb\x90\x00" * 100  # fake MP3 bytes
        mock_resp = _mock_response(200, content=audio)

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.text_to_speech("Hello world")

        assert result == audio

    @pytest.mark.asyncio
    async def test_saves_to_file(self, client: FishAudioClient, tmp_path: Path) -> None:
        audio = b"\xff\xfb\x90\x00" * 50
        out = tmp_path / "speech.mp3"
        mock_resp = _mock_response(200, content=audio)

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.text_to_speech("Test", output_path=out)

        assert out.exists()
        assert out.read_bytes() == audio
        assert result == audio

    @pytest.mark.asyncio
    async def test_uses_custom_reference_id(self, client: FishAudioClient) -> None:
        mock_resp = _mock_response(200, content=b"audio")

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp) as mock_req:
            await client.text_to_speech("Hi", reference_id="custom_voice")

        call_kwargs = mock_req.call_args
        assert call_kwargs.kwargs["json"]["reference_id"] == "custom_voice"


class TestListVoices:
    @pytest.mark.asyncio
    async def test_returns_voice_list(self, client: FishAudioClient) -> None:
        voices = [{"_id": "v1", "title": "Test Voice"}]
        mock_resp = _mock_response(200, json_data={"items": voices})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.list_voices()

        assert result == voices


class TestCloneVoice:
    @pytest.mark.asyncio
    async def test_clone_returns_model(self, client: FishAudioClient, tmp_path: Path) -> None:
        audio_file = tmp_path / "sample.mp3"
        audio_file.write_bytes(b"\xff\xfb\x90\x00" * 100)

        mock_resp = _mock_response(200, json_data={"_id": "new_voice_123", "title": "My Voice"})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.clone_voice(audio_file, "My Voice")

        assert result["_id"] == "new_voice_123"

    @pytest.mark.asyncio
    async def test_raises_on_missing_file(self, client: FishAudioClient) -> None:
        with pytest.raises(FishAudioError, match="not found"):
            await client.clone_voice("/nonexistent/audio.mp3", "Test")


class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self, client: FishAudioClient) -> None:
        rate_resp = _mock_response(429)
        ok_resp = _mock_response(200, json_data={"items": []})

        with patch(
            "httpx.AsyncClient.request",
            new_callable=AsyncMock,
            side_effect=[rate_resp, ok_resp],
        ):
            result = await client.list_voices()

        assert result == []

    @pytest.mark.asyncio
    async def test_raises_on_server_error(self, client: FishAudioClient) -> None:
        mock_resp = httpx.Response(500, text="Internal Server Error")

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(FishAudioError, match="500"):
                await client.list_voices()
