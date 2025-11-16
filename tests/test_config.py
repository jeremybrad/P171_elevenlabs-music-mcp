"""
Tests for configuration management
"""

import pytest
import os
from pathlib import Path
from src.config_manager import Config


def test_config_validates_api_key():
    """Test that config validates API key format"""
    with pytest.raises(ValueError, match="ELEVENLABS_API_KEY is required"):
        Config(api_key="")


def test_config_validates_api_key_format():
    """Test that config validates API key format"""
    with pytest.raises(ValueError, match="Invalid API key format"):
        Config(api_key="invalid_key")


def test_config_with_mock_api():
    """Test that config allows non-sk_ keys in mock mode"""
    config = Config(api_key="test_key", use_mock_api=True)
    assert config.api_key == "test_key"
    assert config.use_mock_api is True


def test_config_validates_duration():
    """Test that config validates duration ranges"""
    with pytest.raises(ValueError, match="min_duration_ms must be at least"):
        Config(api_key="sk_test", min_duration_ms=1000)


def test_config_creates_directories(tmp_path):
    """Test that config creates output directories"""
    music_dir = tmp_path / "music"
    journal_dir = tmp_path / "journal"

    config = Config(
        api_key="sk_test",
        music_output_dir=music_dir,
        journal_output_dir=journal_dir,
        preference_storage_path=tmp_path / "prefs"
    )

    assert music_dir.exists()
    assert journal_dir.exists()
    assert (tmp_path / "prefs").exists()


def test_config_from_env_requires_api_key(monkeypatch):
    """Test that from_env raises error without API key"""
    # Clear both the environment variable and prevent .env loading
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")  # Set to empty string

    with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
        Config.from_env()


def test_config_from_env_loads_correctly(monkeypatch, tmp_path):
    """Test that from_env loads environment variables"""
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test_123")
    monkeypatch.setenv("MUSIC_OUTPUT_DIR", str(tmp_path / "music"))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("USE_MOCK_API", "true")

    config = Config.from_env()

    assert config.api_key == "sk_test_123"
    assert config.music_output_dir == tmp_path / "music"
    assert config.log_level == "DEBUG"
    assert config.use_mock_api is True
