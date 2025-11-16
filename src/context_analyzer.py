"""
Context Analyzer - Detect mood and suggest music

Analyzes conversation context, detects emotional state and activity,
then suggests appropriate music parameters.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class Activity(Enum):
    """Common user activities."""
    CODING = "coding"
    WRITING = "writing"
    BRAINSTORMING = "brainstorming"
    RELAXING = "relaxing"
    EXERCISING = "exercising"
    STUDYING = "studying"
    MEETING = "meeting"
    CREATING = "creating"
    UNKNOWN = "unknown"


class Mood(Enum):
    """Emotional states."""
    CALM = "calm"
    ENERGETIC = "energetic"
    FOCUSED = "focused"
    CREATIVE = "creative"
    STRESSED = "stressed"
    FRUSTRATED = "frustrated"
    HAPPY = "happy"
    SAD = "sad"
    TIRED = "tired"
    MOTIVATED = "motivated"
    NEUTRAL = "neutral"


@dataclass
class MoodAnalysis:
    """Analysis of emotional context."""
    primary_mood: str  # "calm", "energetic", "frustrated", etc.
    intensity: float   # 0-1
    confidence: float  # 0-1
    indicators: List[str]
    reasoning: str


@dataclass
class MusicSuggestion:
    """Suggested music parameters."""
    prompt: str
    duration_ms: int
    mood: str
    reasoning: str


class ContextAnalyzer:
    """
    Analyze text for mood and suggest appropriate music.

    Features:
    - Keyword-based mood detection
    - Activity inference from context
    - Time-of-day aware suggestions
    - Comprehensive mood-to-music mapping
    """

    def __init__(self):
        self.mood_keywords = self._load_mood_keywords()
        self.activity_keywords = self._load_activity_keywords()
        logger.info("ContextAnalyzer initialized")

    def _load_mood_keywords(self) -> Dict[str, List[str]]:
        """Load mood detection keywords."""
        return {
            "frustrated": [
                "fuck", "damn", "ugh", "shit", "broken", "not working",
                "frustrated", "annoyed", "angry", "hate this", "stupid",
                "doesn't work", "error", "failed", "wrong"
            ],
            "stressed": [
                "stressed", "overwhelmed", "too much", "deadline", "pressure",
                "anxious", "worried", "panic", "rush", "urgent"
            ],
            "focused": [
                "working on", "coding", "analyzing", "building", "implementing",
                "focus", "concentrating", "deep work", "debugging"
            ],
            "creative": [
                "brainstorm", "idea", "creative", "design", "imagine",
                "thinking about", "exploring", "inspiration", "innovate"
            ],
            "happy": [
                "happy", "excited", "great", "awesome", "love", "amazing",
                "celebrate", "success", "yay", "finally", "yes!"
            ],
            "tired": [
                "tired", "exhausted", "sleepy", "fatigued", "drained",
                "can't focus", "need break", "worn out"
            ],
            "calm": [
                "calm", "peaceful", "relaxed", "chilling", "quiet",
                "meditative", "serene", "tranquil"
            ],
            "sad": [
                "sad", "down", "depressed", "lonely", "hurt", "disappointed",
                "upset", "crying", "miss"
            ],
            "motivated": [
                "motivated", "determined", "ready", "let's go", "pumped",
                "energized", "committed", "focused on goal"
            ]
        }

    def _load_activity_keywords(self) -> Dict[str, List[str]]:
        """Load activity detection keywords."""
        return {
            "coding": [
                "code", "coding", "programming", "debug", "implement",
                "function", "bug", "compile", "python", "javascript"
            ],
            "writing": [
                "writing", "blog", "article", "document", "draft",
                "essay", "email", "report"
            ],
            "brainstorming": [
                "brainstorm", "ideas", "thinking", "planning", "strategy",
                "design", "concept"
            ],
            "studying": [
                "study", "learning", "reading", "research", "exam",
                "homework", "assignment", "course"
            ],
            "exercising": [
                "workout", "exercise", "gym", "running", "training",
                "cardio", "strength", "yoga"
            ],
            "meeting": [
                "meeting", "call", "presentation", "discussion", "conference"
            ],
            "relaxing": [
                "relax", "chill", "unwind", "rest", "break", "meditate"
            ],
            "creating": [
                "create", "build", "make", "design", "craft", "produce"
            ]
        }

    def analyze_conversation(
        self,
        recent_messages: List[str],
        time_of_day: Optional[str] = None,
        activity_hint: Optional[str] = None
    ) -> Dict:
        """
        Analyze conversation history for mood and activity.

        Args:
            recent_messages: Last few messages from user
            time_of_day: Optional time context
            activity_hint: Optional activity override

        Returns:
            dict with detected_mood, detected_activity, confidence, reasoning
        """
        # Combine messages into context
        context = " ".join(recent_messages[-5:])  # Last 5 messages
        logger.info(f"Analyzing context: '{context[:100]}...'")

        # Detect mood
        mood_analysis = self.analyze_mood(context, time_of_day)

        # Detect activity
        detected_activity = activity_hint or self._detect_activity(context)

        return {
            "detected_mood": mood_analysis.primary_mood,
            "mood_intensity": mood_analysis.intensity,
            "detected_activity": detected_activity,
            "confidence": mood_analysis.confidence,
            "indicators": mood_analysis.indicators,
            "reasoning": mood_analysis.reasoning
        }

    def analyze_mood(
        self,
        context: str,
        time_of_day: Optional[str] = None
    ) -> MoodAnalysis:
        """
        Analyze context for emotional mood.

        Args:
            context: Text to analyze
            time_of_day: Optional time context (morning, afternoon, evening, night)

        Returns:
            MoodAnalysis with detected mood and confidence
        """
        context_lower = context.lower()
        mood_scores = {}

        # Score each mood based on keyword matches
        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in context_lower)
            if score > 0:
                mood_scores[mood] = score

        # No strong indicators
        if not mood_scores:
            return MoodAnalysis(
                primary_mood="neutral",
                intensity=0.5,
                confidence=0.3,
                indicators=[],
                reasoning="No strong mood indicators detected"
            )

        # Get top mood
        primary_mood = max(mood_scores, key=mood_scores.get)
        score = mood_scores[primary_mood]

        # Find which keywords matched
        matched_keywords = [
            kw for kw in self.mood_keywords[primary_mood]
            if kw in context_lower
        ]

        # Calculate intensity and confidence
        intensity = min(score / 3.0, 1.0)
        confidence = min(0.5 + (score * 0.15), 0.95)

        reasoning = f"Detected '{primary_mood}' mood based on keywords: {', '.join(matched_keywords[:3])}"

        return MoodAnalysis(
            primary_mood=primary_mood,
            intensity=intensity,
            confidence=confidence,
            indicators=matched_keywords[:5],
            reasoning=reasoning
        )

    def _detect_activity(self, context: str) -> str:
        """Detect activity from context."""
        context_lower = context.lower()
        activity_scores = {}

        for activity, keywords in self.activity_keywords.items():
            score = sum(1 for keyword in keywords if keyword in context_lower)
            if score > 0:
                activity_scores[activity] = score

        if not activity_scores:
            return Activity.UNKNOWN.value

        return max(activity_scores, key=activity_scores.get)

    def suggest_music_for_context(
        self,
        activity: str,
        mood: str,
        duration_ms: int = 60000,
        time_of_day: Optional[str] = None
    ) -> str:
        """
        Generate appropriate music prompt for context.

        Args:
            activity: What user is doing
            mood: User's emotional state
            duration_ms: Desired duration
            time_of_day: Optional time context

        Returns:
            Music prompt string ready for generation
        """
        logger.info(f"Suggesting music for: activity={activity}, mood={mood}")

        # Map mood + activity to music style
        prompts = {
            # Frustrated moods - need calming
            ("frustrated", "coding"): "calming ambient with gentle rhythm, non-distracting, 70 BPM",
            ("frustrated", "writing"): "peaceful piano, flowing, meditative, stress relief",
            ("stressed", "coding"): "gentle lo-fi beats, calming, steady, 65 BPM",
            ("stressed", "studying"): "ambient soundscape, peaceful, concentration aid",

            # Focused moods - support concentration
            ("focused", "coding"): "lo-fi hip hop, steady beat, non-vocal, 85 BPM",
            ("focused", "writing"): "minimal piano, ambient textures, calm",
            ("focused", "studying"): "classical study music, baroque, gentle",

            # Creative moods - inspire and flow
            ("creative", "brainstorming"): "uplifting ambient, inspiring, flowing melodies",
            ("creative", "creating"): "atmospheric electronic, dreamy, evolving",
            ("creative", "writing"): "gentle jazz, inspiring, fluid",

            # Energetic moods - match energy
            ("motivated", "coding"): "upbeat electronic, driving beat, energizing, 110 BPM",
            ("motivated", "exercising"): "high energy electronic, powerful bass, 128 BPM",
            ("happy", "creating"): "uplifting indie, cheerful, positive energy",

            # Tired moods - gentle energy
            ("tired", "coding"): "gentle beats, coffee shop ambiance, warm",
            ("tired", "studying"): "soft piano, soothing, focus support",

            # Calm/Relaxing
            ("calm", "relaxing"): "ambient soundscape, nature sounds, peaceful",
            ("calm", "studying"): "minimal piano, serene, non-distracting"
        }

        # Try exact match
        key = (mood, activity)
        if key in prompts:
            return prompts[key]

        # Fall back to mood-only suggestions
        mood_defaults = {
            "frustrated": "calming piano and strings, peaceful, stress relief",
            "stressed": "ambient relaxation, gentle, soothing",
            "focused": "lo-fi study beats, concentration, steady rhythm",
            "creative": "inspiring ambient, flowing, uplifting",
            "happy": "upbeat indie, positive, cheerful melodies",
            "sad": "gentle piano, comforting, reflective",
            "tired": "soft ambient, relaxing, gentle energy",
            "motivated": "energizing electronic, driving beat, powerful",
            "calm": "peaceful ambient, serene, meditative"
        }

        if mood in mood_defaults:
            return mood_defaults[mood]

        # Ultimate fallback
        return "lo-fi beats, steady rhythm, focus music"

    def suggest_music_params(
        self,
        mood: MoodAnalysis,
        activity: Optional[str] = None
    ) -> MusicSuggestion:
        """
        Suggest music parameters based on mood analysis.

        Args:
            mood: MoodAnalysis result
            activity: Optional activity context

        Returns:
            MusicSuggestion with prompt and reasoning
        """
        activity = activity or Activity.UNKNOWN.value

        # Generate prompt
        prompt = self.suggest_music_for_context(
            activity=activity,
            mood=mood.primary_mood
        )

        # Duration based on mood intensity
        if mood.intensity > 0.7:
            # Strong mood - longer duration for effect
            duration_ms = 120000  # 2 minutes
        else:
            duration_ms = 60000  # 1 minute

        reasoning = (
            f"Detected {mood.primary_mood} mood "
            f"(intensity: {mood.intensity:.1f}, confidence: {mood.confidence:.1f}) "
            f"during {activity}. "
            f"Suggesting music to {'counterbalance' if mood.primary_mood in ['frustrated', 'stressed'] else 'support'} "
            f"current state."
        )

        return MusicSuggestion(
            prompt=prompt,
            duration_ms=duration_ms,
            mood=mood.primary_mood,
            reasoning=reasoning
        )

    def detect_mood(self, context: str) -> Dict:
        """
        Simple mood detection returning dict format for MCP tools.

        Args:
            context: Text to analyze

        Returns:
            dict with mood and confidence
        """
        analysis = self.analyze_mood(context)
        return {
            "mood": analysis.primary_mood,
            "confidence": analysis.confidence,
            "intensity": analysis.intensity,
            "indicators": analysis.indicators
        }

    def detect_activity(self, context: str) -> Dict:
        """
        Simple activity detection returning dict format for MCP tools.

        Args:
            context: Text to analyze

        Returns:
            dict with activity and confidence
        """
        conversation_analysis = self.analyze_conversation(context, recent_prompts=[])
        return {
            "activity": conversation_analysis.inferred_activity or "unknown",
            "confidence": 0.7 if conversation_analysis.inferred_activity else 0.3
        }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        analyzer = ContextAnalyzer()
        
        # Test frustration detection
        mood = await analyzer.analyze_mood("Ugh this code isn't working!")
        print(f"✅ Detected mood: {mood.primary_mood} (confidence: {mood.confidence})")
        
        suggestion = analyzer.suggest_music_params(mood)
        print(f"✅ Suggested: {suggestion.prompt}")
    
    asyncio.run(test())
