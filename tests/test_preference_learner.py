"""
Tests for preference learning functionality
"""

import pytest
import tempfile
from pathlib import Path
from src.preference_learner import PreferenceLearner, MusicPreference


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_initialization(temp_storage):
    """Test PreferenceLearner initialization"""
    learner = PreferenceLearner(temp_storage)

    assert learner.storage_path == temp_storage
    assert len(learner.preferences) == 0
    assert (temp_storage / "preferences.json").exists()


def test_record_preference(temp_storage):
    """Test recording a single preference"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference(
        prompt="lo-fi beats for coding",
        liked=True,
        activity="coding",
        mood="focused"
    )

    assert len(learner.preferences) == 1
    assert learner.preferences[0].prompt == "lo-fi beats for coding"
    assert learner.preferences[0].liked is True
    assert learner.preferences[0].activity == "coding"


def test_record_generation(temp_storage):
    """Test recording music generation"""
    learner = PreferenceLearner(temp_storage)

    metadata = {
        "activity": "coding",
        "mood": "focused",
        "duration_ms": 60000
    }

    learner.record_generation(
        prompt="ambient coding music",
        metadata=metadata,
        result_path=Path("/tmp/test.mp3")
    )

    assert len(learner.preferences) == 1
    assert learner.preferences[0].liked is True  # Implicit like


def test_save_and_load(temp_storage):
    """Test saving and loading preferences"""
    learner1 = PreferenceLearner(temp_storage)

    learner1.record_preference("test prompt 1", True, activity="coding")
    learner1.record_preference("test prompt 2", False, activity="writing")

    # Create new instance to test loading
    learner2 = PreferenceLearner(temp_storage)

    assert len(learner2.preferences) == 2
    assert learner2.preferences[0].prompt == "test prompt 1"
    assert learner2.preferences[1].prompt == "test prompt 2"


def test_get_recommendations_by_activity(temp_storage):
    """Test getting recommendations filtered by activity"""
    learner = PreferenceLearner(temp_storage)

    # Record some preferences
    learner.record_preference("coding music 1", True, activity="coding")
    learner.record_preference("coding music 2", True, activity="coding")
    learner.record_preference("workout music", True, activity="exercising")

    # Get coding recommendations
    recs = learner.get_recommendations(activity="coding", limit=5)

    assert len(recs) == 2
    assert "coding music" in recs[0] or "coding music" in recs[1]


def test_get_recommendations_by_mood(temp_storage):
    """Test getting recommendations filtered by mood"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("calm music 1", True, mood="calm")
    learner.record_preference("calm music 2", True, mood="calm")
    learner.record_preference("energetic music", True, mood="energetic")

    recs = learner.get_recommendations(mood="calm", limit=5)

    assert len(recs) == 2
    assert "calm music" in recs[0] or "calm music" in recs[1]


def test_get_recommendations_with_activity_and_mood(temp_storage):
    """Test recommendations with both activity and mood filters"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("focus coding 1", True, activity="coding", mood="focused")
    learner.record_preference("focus coding 2", True, activity="coding", mood="focused")
    learner.record_preference("calm coding", True, activity="coding", mood="calm")
    learner.record_preference("focus writing", True, activity="writing", mood="focused")

    recs = learner.get_recommendations(activity="coding", mood="focused", limit=5)

    assert len(recs) == 2
    assert all("focus coding" in r for r in recs)


def test_recommendations_exclude_disliked(temp_storage):
    """Test that disliked items are not recommended"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("good music", True, activity="coding")
    learner.record_preference("bad music", False, activity="coding")

    recs = learner.get_recommendations(activity="coding", limit=5)

    assert len(recs) == 1
    assert recs[0] == "good music"


def test_get_favorite_moods(temp_storage):
    """Test getting favorite moods"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("music 1", True, mood="calm")
    learner.record_preference("music 2", True, mood="calm")
    learner.record_preference("music 3", True, mood="focused")

    favorites = learner.get_favorite_moods(limit=5)

    assert len(favorites) == 2
    assert favorites[0] == "calm"  # Most frequent
    assert favorites[1] == "focused"


def test_get_favorite_activities(temp_storage):
    """Test getting favorite activities"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("music 1", True, activity="coding")
    learner.record_preference("music 2", True, activity="coding")
    learner.record_preference("music 3", True, activity="coding")
    learner.record_preference("music 4", True, activity="writing")

    favorites = learner.get_favorite_activities(limit=5)

    assert len(favorites) == 2
    assert favorites[0] == "coding"  # Most frequent
    assert favorites[1] == "writing"


def test_get_statistics(temp_storage):
    """Test statistics generation"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("music 1", True, activity="coding", mood="focused")
    learner.record_preference("music 2", True, activity="coding", mood="focused")
    learner.record_preference("music 3", False, activity="coding", mood="calm")

    stats = learner.get_statistics()

    assert stats["total_generations"] == 3
    assert stats["liked_count"] == 2
    assert stats["disliked_count"] == 1
    assert stats["like_rate"] == pytest.approx(2/3)
    assert "favorite_moods" in stats
    assert "favorite_activities" in stats


def test_record_feedback(temp_storage):
    """Test recording explicit feedback"""
    learner = PreferenceLearner(temp_storage)

    # Record likes
    learner.record_feedback("music 1", "like")
    learner.record_feedback("music 2", "replay")

    # Record dislikes
    learner.record_feedback("music 3", "dislike")
    learner.record_feedback("music 4", "skip")

    assert len(learner.preferences) == 4
    assert learner.preferences[0].liked is True  # like
    assert learner.preferences[1].liked is True  # replay
    assert learner.preferences[2].liked is False  # dislike
    assert learner.preferences[3].liked is False  # skip


def test_recommendations_no_duplicates(temp_storage):
    """Test that recommendations don't include duplicates"""
    learner = PreferenceLearner(temp_storage)

    # Record same prompt multiple times
    learner.record_preference("same music", True, activity="coding")
    learner.record_preference("same music", True, activity="coding")
    learner.record_preference("same music", True, activity="coding")

    recs = learner.get_recommendations(activity="coding", limit=5)

    assert len(recs) == 1  # No duplicates
    assert recs[0] == "same music"


def test_recommendations_most_recent_first(temp_storage):
    """Test that recommendations prioritize most recent"""
    learner = PreferenceLearner(temp_storage)

    learner.record_preference("old music", True, activity="coding")
    learner.record_preference("new music", True, activity="coding")

    recs = learner.get_recommendations(activity="coding", limit=5)

    assert recs[0] == "new music"  # Most recent first
    assert recs[1] == "old music"


def test_export_and_import(temp_storage):
    """Test exporting and importing preferences"""
    learner1 = PreferenceLearner(temp_storage)

    learner1.record_preference("music 1", True, activity="coding")
    learner1.record_preference("music 2", False, activity="writing")

    # Export
    export_path = temp_storage / "export.json"
    learner1.export_preferences(export_path)

    # Import to new learner
    new_storage = temp_storage / "new"
    new_storage.mkdir()
    learner2 = PreferenceLearner(new_storage)
    learner2.import_preferences(export_path, merge=False)

    assert len(learner2.preferences) == 2
    assert learner2.preferences[0].prompt == "music 1"


def test_recommendations_fallback_when_filtered_too_few(temp_storage):
    """Test that recommendations fall back to all liked when filters return too few"""
    learner = PreferenceLearner(temp_storage)

    # Add many liked items with different activities
    learner.record_preference("coding music", True, activity="coding")
    learner.record_preference("general music 1", True, activity="general")
    learner.record_preference("general music 2", True, activity="general")
    learner.record_preference("general music 3", True, activity="general")

    # Request writing music (which has none)
    recs = learner.get_recommendations(activity="writing", limit=5)

    # Should fall back to all liked items
    assert len(recs) >= 3
