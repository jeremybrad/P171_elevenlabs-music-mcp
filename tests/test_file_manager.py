"""
Tests for file management
"""

import pytest
from pathlib import Path
import json
from src.file_manager import FileManager


def test_create_slug():
    """Test slug creation from prompts"""
    fm = FileManager(Path("/tmp/test"))

    assert fm._create_slug("Lo-fi Hip Hop Beats") == "lo_fi_hip_hop_beats"
    assert fm._create_slug("Calm Piano (2 min)") == "calm_piano_2_min"
    assert fm._create_slug("!!!Special###") == "special"
    assert fm._create_slug("") == "music"
    assert fm._create_slug("a" * 50, max_length=10) == "aaaaaaaaaa"


def test_save_music(tmp_path):
    """Test saving music files with metadata"""
    fm = FileManager(tmp_path)

    audio_data = b"fake audio data"
    metadata = {
        "prompt": "test music",
        "duration_ms": 30000
    }

    audio_path, metadata_path = fm.save_music(audio_data, metadata)

    # Check files exist
    assert audio_path.exists()
    assert metadata_path.exists()

    # Check audio content
    assert audio_path.read_bytes() == audio_data

    # Check metadata content
    saved_metadata = json.loads(metadata_path.read_text())
    assert saved_metadata["prompt"] == "test music"
    assert saved_metadata["duration_ms"] == 30000
    assert "saved_at" in saved_metadata
    assert "file_size_bytes" in saved_metadata


def test_file_organization(tmp_path):
    """Test date-based directory organization"""
    fm = FileManager(tmp_path)

    audio_data = b"test data"
    metadata = {"prompt": "test"}

    audio_path, _ = fm.save_music(audio_data, metadata)

    # Check path structure includes YYYY-MM directory
    from datetime import datetime
    now = datetime.now()
    expected_dir = tmp_path / now.strftime("%Y-%m")

    assert audio_path.parent == expected_dir
    assert audio_path.parent.exists()


def test_counter_increment(tmp_path):
    """Test that counter increments for duplicate slugs"""
    fm = FileManager(tmp_path)

    # Create first file
    audio_path1, _ = fm.save_music(b"data1", {"prompt": "test"})
    assert "_001.mp3" in audio_path1.name

    # Create second file with same prompt
    audio_path2, _ = fm.save_music(b"data2", {"prompt": "test"})
    assert "_002.mp3" in audio_path2.name

    # Ensure they're different files
    assert audio_path1 != audio_path2


def test_atomic_write(tmp_path):
    """Test atomic file writing"""
    fm = FileManager(tmp_path)

    test_file = tmp_path / "2025-11" / "test.mp3"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    data = b"test data"
    fm._atomic_write(test_file, data)

    assert test_file.exists()
    assert test_file.read_bytes() == data

    # Ensure no temp files left behind
    temp_files = list(test_file.parent.glob("*.tmp"))
    assert len(temp_files) == 0


def test_get_next_counter(tmp_path):
    """Test counter calculation"""
    fm = FileManager(tmp_path)

    date_dir = tmp_path / "2025-11"
    date_dir.mkdir(parents=True, exist_ok=True)

    # No existing files
    assert fm._get_next_counter(date_dir, "2025-11-16", "test") == 1

    # Create some files
    (date_dir / "2025-11-16_test_001.mp3").touch()
    (date_dir / "2025-11-16_test_002.mp3").touch()

    assert fm._get_next_counter(date_dir, "2025-11-16", "test") == 3

    # Non-sequential files
    (date_dir / "2025-11-16_test_005.mp3").touch()
    assert fm._get_next_counter(date_dir, "2025-11-16", "test") == 6
