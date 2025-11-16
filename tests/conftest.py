# Test Infrastructure

import pytest
from pathlib import Path

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    return tmp_path / "music_output"

@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "sk_test_key_12345"

@pytest.fixture
def sample_prompt():
    """Sample music generation prompt"""
    return "gentle piano, ambient, calming"

@pytest.fixture
def sample_metadata():
    """Sample metadata for testing"""
    return {
        "prompt": "gentle piano",
        "duration_ms": 30000,
        "generated_at": "2025-11-16T12:00:00"
    }
