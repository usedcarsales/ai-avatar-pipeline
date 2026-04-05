"""Unit tests for HeyGen API client with mocked HTTP calls."""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.config import Config
from src.heygen_client import (
    HeyGenClient,
    HeyGenError,
    HeyGenRateLimitError,
    HeyGenVideoTimeout,
)


@pytest.fixture
def config() -> Config:
    return Config(
        heygen_api_key="test-key-123",
        default_avatar_id="avatar_001",
        default_voice_id="voice_001",
        poll_interval=0.1,
        max_poll_time=1.0,
        max_retries=2,
        backoff_base=0.1,
    )


@pytest.fixture
def client(config: Config) -> HeyGenClient:
    return HeyGenClient(config)


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> httpx.Response:
    resp = httpx.Response(status_code, json=json_data or {})
    return resp


class TestHeyGenClientInit:
    def test_requires_api_key(self) -> None:
        with pytest.raises(HeyGenError, match="HEYGEN_API_KEY"):
            HeyGenClient(Config(heygen_api_key=""))

    def test_creates_with_valid_key(self, config: Config) -> None:
        client = HeyGenClient(config)
        assert client.config.heygen_api_key == "test-key-123"


class TestListAvatars:
    @pytest.mark.asyncio
    async def test_returns_avatar_list(self, client: HeyGenClient) -> None:
        avatars = [{"avatar_id": "a1", "name": "Test Avatar"}]
        mock_resp = _mock_response(200, {"data": {"avatars": avatars}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.list_avatars()

        assert result == avatars


class TestListVoices:
    @pytest.mark.asyncio
    async def test_returns_voice_list(self, client: HeyGenClient) -> None:
        voices = [{"voice_id": "v1", "name": "English Female"}]
        mock_resp = _mock_response(200, {"data": {"voices": voices}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.list_voices()

        assert result == voices


class TestGenerateVideo:
    @pytest.mark.asyncio
    async def test_returns_video_id(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(200, {"data": {"video_id": "vid_123"}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            video_id = await client.generate_video("Hello world", avatar_id="a1")

        assert video_id == "vid_123"

    @pytest.mark.asyncio
    async def test_raises_without_avatar_id(self, client: HeyGenClient) -> None:
        client.config.default_avatar_id = ""
        with pytest.raises(HeyGenError, match="avatar_id"):
            await client.generate_video("Hello", avatar_id="")

    @pytest.mark.asyncio
    async def test_uses_default_avatar(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(200, {"data": {"video_id": "vid_456"}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            video_id = await client.generate_video("Hello")

        assert video_id == "vid_456"


class TestGetVideoStatus:
    @pytest.mark.asyncio
    async def test_returns_status(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(200, {"data": {"status": "processing"}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            result = await client.get_video_status("vid_123")

        assert result["status"] == "processing"


class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self, client: HeyGenClient) -> None:
        rate_limit_resp = _mock_response(429, {})
        ok_resp = _mock_response(200, {"data": {"avatars": []}})

        with patch(
            "httpx.AsyncClient.request",
            new_callable=AsyncMock,
            side_effect=[rate_limit_resp, ok_resp],
        ):
            result = await client.list_avatars()

        assert result == []

    @pytest.mark.asyncio
    async def test_raises_on_4xx(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(403, {})
        mock_resp = httpx.Response(403, text="Forbidden")

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(HeyGenError, match="403"):
                await client.list_avatars()


class TestWaitForVideo:
    @pytest.mark.asyncio
    async def test_returns_url_on_completed(self, client: HeyGenClient) -> None:
        statuses = [
            _mock_response(200, {"data": {"status": "processing"}}),
            _mock_response(200, {"data": {"status": "completed", "video_url": "https://example.com/v.mp4"}}),
        ]

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, side_effect=statuses):
            url = await client.wait_for_video("vid_123")

        assert url == "https://example.com/v.mp4"

    @pytest.mark.asyncio
    async def test_raises_on_failure(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(200, {"data": {"status": "failed", "error": "bad input"}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(HeyGenError, match="failed"):
                await client.wait_for_video("vid_123")

    @pytest.mark.asyncio
    async def test_raises_on_timeout(self, client: HeyGenClient) -> None:
        mock_resp = _mock_response(200, {"data": {"status": "processing"}})

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(HeyGenVideoTimeout):
                await client.wait_for_video("vid_123")
