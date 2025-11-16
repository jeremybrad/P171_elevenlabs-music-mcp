"""
Tests for music generator
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.music_generator import (
    MusicGenerator,
    MusicResult,
    CopyrightError,
    RateLimitError,
    APIError
)


@pytest.fixture
def generator():
    """Create a MusicGenerator instance for testing"""
    return MusicGenerator(api_key="sk_test_key")


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session"""
    session = MagicMock()
    return session


@pytest.mark.asyncio
async def test_generator_initialization():
    """Test generator initialization"""
    gen = MusicGenerator(
        api_key="sk_test",
        base_url="https://api.example.com",
        timeout=60,
        max_retries=5
    )

    assert gen.api_key == "sk_test"
    assert gen.base_url == "https://api.example.com"
    assert gen.max_retries == 5


@pytest.mark.asyncio
async def test_get_headers(generator):
    """Test API header generation"""
    headers = generator._get_headers()

    assert headers["xi-api-key"] == "sk_test_key"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_successful_generation_mock():
    """Test successful music generation with mock response"""
    gen = MusicGenerator(api_key="sk_test")

    # Mock response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"fake audio data")
    mock_response.headers = {}

    # Mock session
    async def mock_post(*args, **kwargs):
        return mock_response

    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    async with gen:
        gen.session.post = mock_post

        result = await gen.generate_simple(
            prompt="test music",
            duration_ms=30000
        )

        assert result.success is True
        assert result.audio_data == b"fake audio data"
        assert result.duration_ms == 30000


@pytest.mark.asyncio
async def test_copyright_error_handling():
    """Test handling of copyright errors"""
    gen = MusicGenerator(api_key="sk_test")

    # Mock copyright error response
    mock_response = MagicMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={
        "error": {
            "type": "bad_prompt",
            "message": "Copyrighted content detected",
            "suggested_prompt": "gentle piano music"
        }
    })

    async def mock_post(*args, **kwargs):
        return mock_response

    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    async with gen:
        gen.session.post = mock_post

        result = await gen.generate_simple(prompt="Beatles song")

        assert result.success is False
        assert "Copyright" in result.error
        assert result.suggested_prompt == "gentle piano music"


@pytest.mark.asyncio
async def test_rate_limit_handling():
    """Test handling of rate limit errors"""
    gen = MusicGenerator(api_key="sk_test")

    # Mock rate limit response
    mock_response = MagicMock()
    mock_response.status = 429
    mock_response.text = AsyncMock(return_value="Rate limit exceeded")

    async def mock_post(*args, **kwargs):
        return mock_response

    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    async with gen:
        gen.session.post = mock_post

        result = await gen.generate_simple(prompt="test")

        assert result.success is False
        assert "Rate limit" in result.error


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test handling of invalid API key"""
    gen = MusicGenerator(api_key="sk_test")

    # Mock unauthorized response
    mock_response = MagicMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value="Unauthorized")

    async def mock_post(*args, **kwargs):
        return mock_response

    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    async with gen:
        gen.session.post = mock_post

        result = await gen.generate_simple(prompt="test")

        assert result.success is False
        assert "Invalid API key" in result.error


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager usage"""
    gen = MusicGenerator(api_key="sk_test")

    assert gen.session is None

    async with gen:
        assert gen.session is not None

    # Session should be closed after context
    assert gen.session.closed


@pytest.mark.asyncio
async def test_generate_with_duration():
    """Test generation with specific duration"""
    gen = MusicGenerator(api_key="sk_test")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"audio")
    mock_response.headers = {}

    async def mock_post(*args, **kwargs):
        # Verify duration was passed
        payload = kwargs.get('json', {})
        assert payload.get('duration_ms') == 45000
        return mock_response

    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    async with gen:
        gen.session.post = mock_post

        result = await gen.generate_simple(
            prompt="test",
            duration_ms=45000
        )

        assert result.success is True
        assert result.duration_ms == 45000
