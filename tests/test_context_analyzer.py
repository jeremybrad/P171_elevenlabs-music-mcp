"""
Tests for context analysis and mood detection
"""

import pytest
from src.context_analyzer import ContextAnalyzer, Mood, Activity


def test_detect_frustrated_mood():
    """Test detection of frustrated mood"""
    analyzer = ContextAnalyzer()

    context = "This code isn't working! I'm so frustrated. Nothing makes sense."
    result = analyzer.detect_mood(context)

    assert result["mood"] == Mood.FRUSTRATED.value
    assert result["confidence"] > 0.5


def test_detect_focused_mood():
    """Test detection of focused mood"""
    analyzer = ContextAnalyzer()

    context = "I'm really concentrating on this algorithm. Deep work mode."
    result = analyzer.detect_mood(context)

    assert result["mood"] == Mood.FOCUSED.value
    assert result["confidence"] > 0.5


def test_detect_coding_activity():
    """Test detection of coding activity"""
    analyzer = ContextAnalyzer()

    context = "Working on the authentication function. Debugging some API calls."
    result = analyzer.detect_activity(context)

    assert result["activity"] == Activity.CODING.value
    assert result["confidence"] > 0.5


def test_detect_writing_activity():
    """Test detection of writing activity"""
    analyzer = ContextAnalyzer()

    context = "I'm drafting the documentation for this project. Writing the README."
    result = analyzer.detect_activity(context)

    assert result["activity"] == Activity.WRITING.value
    assert result["confidence"] > 0.5


def test_suggest_music_for_frustrated_coding():
    """Test music suggestion for frustrated coder"""
    analyzer = ContextAnalyzer()

    suggestion = analyzer.suggest_music_for_context(
        activity="coding",
        mood="frustrated",
        duration_ms=60000
    )

    assert isinstance(suggestion, str)
    assert len(suggestion) > 0
    # Should suggest calming music for frustrated state
    assert any(word in suggestion.lower() for word in ["calm", "gentle", "ambient"])


def test_suggest_music_for_focused_coding():
    """Test music suggestion for focused coder"""
    analyzer = ContextAnalyzer()

    suggestion = analyzer.suggest_music_for_context(
        activity="coding",
        mood="focused",
        duration_ms=60000
    )

    assert isinstance(suggestion, str)
    # Should suggest lo-fi or steady beats for focus
    assert any(word in suggestion.lower() for word in ["lo-fi", "steady", "beat"])


def test_suggest_music_for_creative_work():
    """Test music suggestion for creative work"""
    analyzer = ContextAnalyzer()

    suggestion = analyzer.suggest_music_for_context(
        activity="creating",
        mood="creative",
        duration_ms=60000
    )

    assert isinstance(suggestion, str)
    # Should suggest inspiring/ambient music
    assert any(word in suggestion.lower() for word in ["ambient", "flowing", "inspiring"])


def test_detect_happy_mood():
    """Test detection of happy mood"""
    analyzer = ContextAnalyzer()

    context = "This is amazing! I love it! Everything is going great today!"
    result = analyzer.detect_mood(context)

    assert result["mood"] == Mood.HAPPY.value
    assert result["confidence"] > 0.5


def test_detect_stressed_mood():
    """Test detection of stressed mood"""
    analyzer = ContextAnalyzer()

    context = "I'm so stressed out. The deadline is tomorrow and I'm overwhelmed."
    result = analyzer.detect_mood(context)

    assert result["mood"] == Mood.STRESSED.value
    assert result["confidence"] > 0.5


def test_detect_exercising_activity():
    """Test detection of exercising activity"""
    analyzer = ContextAnalyzer()

    context = "Going for a run. Doing my workout routine."
    result = analyzer.detect_activity(context)

    assert result["activity"] == Activity.EXERCISING.value
    assert result["confidence"] > 0.5


def test_suggest_music_for_exercising():
    """Test music suggestion for exercising"""
    analyzer = ContextAnalyzer()

    suggestion = analyzer.suggest_music_for_context(
        activity="exercising",
        mood="motivated",
        duration_ms=180000
    )

    assert isinstance(suggestion, str)
    # Should suggest energetic music
    assert any(word in suggestion.lower() for word in ["energetic", "upbeat", "driving", "fast"])


def test_all_moods_have_keywords():
    """Test that all mood types have keyword definitions"""
    analyzer = ContextAnalyzer()

    for mood in Mood:
        # Each mood should have keywords defined
        assert mood.value in analyzer.mood_keywords
        assert len(analyzer.mood_keywords[mood.value]) > 0


def test_all_activities_have_keywords():
    """Test that all activity types have keyword definitions"""
    analyzer = ContextAnalyzer()

    for activity in Activity:
        # Each activity should have keywords defined
        assert activity.value in analyzer.activity_keywords
        assert len(analyzer.activity_keywords[activity.value]) > 0


def test_neutral_mood_default():
    """Test that neutral mood is returned for unclear context"""
    analyzer = ContextAnalyzer()

    context = "The weather is nice."
    result = analyzer.detect_mood(context)

    # Should default to neutral with low confidence
    assert result["mood"] == Mood.NEUTRAL.value or result["confidence"] < 0.3


def test_unknown_activity_default():
    """Test that unknown activity is returned for unclear context"""
    analyzer = ContextAnalyzer()

    context = "Just sitting here."
    result = analyzer.detect_activity(context)

    # Should default to unknown with low confidence
    assert result["activity"] == Activity.UNKNOWN.value or result["confidence"] < 0.3


def test_confidence_scores_valid():
    """Test that confidence scores are in valid range"""
    analyzer = ContextAnalyzer()

    contexts = [
        "I'm coding and really frustrated",
        "Writing documentation",
        "Happy and exercising"
    ]

    for context in contexts:
        mood_result = analyzer.detect_mood(context)
        activity_result = analyzer.detect_activity(context)

        assert 0.0 <= mood_result["confidence"] <= 1.0
        assert 0.0 <= activity_result["confidence"] <= 1.0


def test_suggest_music_handles_time_of_day():
    """Test that time of day affects suggestions"""
    analyzer = ContextAnalyzer()

    # Should handle time_of_day parameter gracefully
    suggestion = analyzer.suggest_music_for_context(
        activity="relaxing",
        mood="calm",
        duration_ms=60000,
        time_of_day="evening"
    )

    assert isinstance(suggestion, str)
    assert len(suggestion) > 0
