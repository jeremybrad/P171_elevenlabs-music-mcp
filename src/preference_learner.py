"""
Preference Learner - Learn and adapt to user music preferences

Tracks user's music generation history and learns patterns to make
better suggestions over time.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MusicPreference:
    """Record of user's music preference."""
    prompt: str
    liked: bool
    context: Optional[str] = None
    activity: Optional[str] = None
    mood: Optional[str] = None
    timestamp: str = None
    duration_ms: Optional[int] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class PreferenceLearner:
    """
    Learn from user interactions to improve suggestions.

    Features:
    - Track all music generations
    - Record user feedback (implicit and explicit)
    - Identify patterns in preferences
    - Make personalized recommendations
    """

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.storage_path / "preferences.json"
        self.history_file = self.storage_path / "history.json"
        self.preferences: List[MusicPreference] = []
        self.load()
        logger.info(f"PreferenceLearner initialized with {len(self.preferences)} preferences")

    def load(self):
        """Load preferences from JSON."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file) as f:
                    data = json.load(f)
                    self.preferences = [MusicPreference(**p) for p in data]
                    logger.info(f"Loaded {len(self.preferences)} preferences")
            except Exception as e:
                logger.error(f"Error loading preferences: {e}")
                self.preferences = []

    def save(self):
        """Save preferences to JSON."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump([asdict(p) for p in self.preferences], f, indent=2)
            logger.debug(f"Saved {len(self.preferences)} preferences")
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def record_preference(
        self,
        prompt: str,
        liked: bool = True,
        context: Optional[str] = None,
        activity: Optional[str] = None,
        mood: Optional[str] = None,
        duration_ms: Optional[int] = None
    ):
        """
        Record a preference.

        Args:
            prompt: Music prompt that was generated
            liked: Whether user liked it (default True for generation=interest)
            context: Optional context information
            activity: What user was doing
            mood: User's mood at time
            duration_ms: Duration of track
        """
        pref = MusicPreference(
            prompt=prompt,
            liked=liked,
            context=context,
            activity=activity,
            mood=mood,
            duration_ms=duration_ms
        )

        self.preferences.append(pref)
        self.save()

        logger.info(f"Recorded preference: {prompt[:50]}... (liked={liked}, activity={activity})")

    def record_generation(
        self,
        prompt: str,
        metadata: Dict,
        result_path: Path
    ):
        """
        Record a music generation for learning.

        Assumes generation = user wanted it = positive signal.

        Args:
            prompt: Generated music prompt
            metadata: Generation metadata (mood, activity, etc.)
            result_path: Where file was saved
        """
        self.record_preference(
            prompt=prompt,
            liked=True,  # Assumption: if they generated it, they liked it
            context=metadata.get('context'),
            activity=metadata.get('activity'),
            mood=metadata.get('mood'),
            duration_ms=metadata.get('duration_ms')
        )

    def record_feedback(
        self,
        prompt: str,
        feedback_type: str,
        context: Optional[Dict] = None
    ):
        """
        Record explicit user feedback.

        Args:
            prompt: The music prompt
            feedback_type: "like", "dislike", "skip", "replay"
            context: Optional context
        """
        liked = feedback_type in ["like", "replay"]

        self.record_preference(
            prompt=prompt,
            liked=liked,
            context=context.get('context') if context else None,
            activity=context.get('activity') if context else None,
            mood=context.get('mood') if context else None
        )

    def get_recommendations(
        self,
        activity: Optional[str] = None,
        mood: Optional[str] = None,
        limit: int = 5
    ) -> List[str]:
        """
        Get music prompts user has liked in similar contexts.

        Args:
            activity: Filter by activity
            mood: Filter by mood
            limit: Max number of recommendations

        Returns:
            List of recommended prompts
        """
        # Filter to liked preferences
        liked_prefs = [p for p in self.preferences if p.liked]

        if not liked_prefs:
            return []

        # Apply filters
        filtered = liked_prefs
        if activity:
            filtered = [p for p in filtered if p.activity == activity]

        if mood:
            filtered = [p for p in filtered if p.mood == mood]

        # If too few results, fall back to just liked
        if len(filtered) < 3:
            filtered = liked_prefs

        # Get unique prompts (most recent first)
        seen_prompts = set()
        recommendations = []

        for pref in reversed(filtered):  # Reverse to get most recent first
            if pref.prompt not in seen_prompts:
                recommendations.append(pref.prompt)
                seen_prompts.add(pref.prompt)

            if len(recommendations) >= limit:
                break

        logger.info(f"Generated {len(recommendations)} recommendations for activity={activity}, mood={mood}")
        return recommendations

    def get_favorite_moods(self, limit: int = 5) -> List[str]:
        """
        Get user's favorite moods based on preference history.

        Returns:
            List of moods, ordered by frequency
        """
        liked_prefs = [p for p in self.preferences if p.liked and p.mood]

        if not liked_prefs:
            return []

        # Count moods
        mood_counts = defaultdict(int)
        for pref in liked_prefs:
            mood_counts[pref.mood] += 1

        # Sort by frequency
        sorted_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)

        return [mood for mood, count in sorted_moods[:limit]]

    def get_favorite_activities(self, limit: int = 5) -> List[str]:
        """
        Get user's favorite activities based on preference history.

        Returns:
            List of activities, ordered by frequency
        """
        liked_prefs = [p for p in self.preferences if p.liked and p.activity]

        if not liked_prefs:
            return []

        # Count activities
        activity_counts = defaultdict(int)
        for pref in liked_prefs:
            activity_counts[pref.activity] += 1

        # Sort by frequency
        sorted_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)

        return [activity for activity, count in sorted_activities[:limit]]

    def get_statistics(self) -> Dict:
        """
        Get preference statistics.

        Returns:
            Dict with various statistics
        """
        total = len(self.preferences)
        liked = len([p for p in self.preferences if p.liked])

        return {
            "total_generations": total,
            "liked_count": liked,
            "disliked_count": total - liked,
            "like_rate": liked / total if total > 0 else 0,
            "favorite_moods": self.get_favorite_moods(3),
            "favorite_activities": self.get_favorite_activities(3),
            "most_recent": self.preferences[-5:] if self.preferences else []
        }

    def clear_old_preferences(self, days: int = 90):
        """
        Remove preferences older than specified days.

        Args:
            days: Keep only preferences from last N days
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        original_count = len(self.preferences)

        self.preferences = [
            p for p in self.preferences
            if datetime.fromisoformat(p.timestamp).timestamp() > cutoff
        ]

        removed = original_count - len(self.preferences)
        if removed > 0:
            self.save()
            logger.info(f"Removed {removed} old preferences (older than {days} days)")

    def export_preferences(self, export_path: Path):
        """
        Export preferences to a file.

        Args:
            export_path: Where to export
        """
        with open(export_path, 'w') as f:
            json.dump([asdict(p) for p in self.preferences], f, indent=2)

        logger.info(f"Exported {len(self.preferences)} preferences to {export_path}")

    def import_preferences(self, import_path: Path, merge: bool = True):
        """
        Import preferences from a file.

        Args:
            import_path: File to import from
            merge: If True, merge with existing. If False, replace.
        """
        with open(import_path) as f:
            data = json.load(f)
            imported_prefs = [MusicPreference(**p) for p in data]

        if merge:
            self.preferences.extend(imported_prefs)
        else:
            self.preferences = imported_prefs

        self.save()
        logger.info(f"Imported {len(imported_prefs)} preferences (merge={merge})")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PreferenceLearner(Path(tmpdir))
        learner.record_generation("test prompt", {}, Path("test.mp3"))
        print(f"✅ Recorded generation. Total: {learner.preferences['history_summary']['total_generations']}")
