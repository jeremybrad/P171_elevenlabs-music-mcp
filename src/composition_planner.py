"""
Composition Planner - Create structured music compositions

Creates multi-section composition plans for intelligent music generation.
Supports templates, mood progressions, and custom structures.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """A section of a musical composition."""
    style: str
    duration_ms: int
    mood: str
    tempo: Optional[int] = None
    key: Optional[str] = None
    instruments: Optional[List[str]] = None


@dataclass
class CompositionPlan:
    """Complete composition plan."""
    sections: List[Section]
    total_duration_ms: int
    overall_mood: str
    genre: Optional[str] = None
    
    def to_api_format(self) -> dict:
        """Convert to ElevenLabs API format."""
        # TODO: Implement conversion
        return {
            "sections": [
                {
                    "style": s.style,
                    "duration_ms": s.duration_ms
                }
                for s in self.sections
            ]
        }


class CompositionPlanner:
    """
    Create and manage composition plans.

    Features:
    - Template-based generation for common scenarios
    - Intelligent prompt analysis for custom plans
    - Mood progression support
    - Duration-aware section planning
    """

    def __init__(self):
        self.templates = self._load_templates()
        logger.info(f"CompositionPlanner initialized with {len(self.templates)} templates")

    def _load_templates(self) -> Dict:
        """Load pre-built composition templates."""
        return {
            "focus_work": {
                "sections": [
                    {"style": "ambient intro", "duration_pct": 0.15, "mood": "calm"},
                    {"style": "steady lo-fi beat", "duration_pct": 0.70, "mood": "focused"},
                    {"style": "gentle outro", "duration_pct": 0.15, "mood": "calm"}
                ],
                "overall_mood": "focused",
                "genre": "lo-fi",
                "description": "Steady focus music for deep work"
            },
            "energetic_workout": {
                "sections": [
                    {"style": "warm-up beat", "duration_pct": 0.20, "mood": "building"},
                    {"style": "high energy driving rhythm", "duration_pct": 0.60, "mood": "energetic"},
                    {"style": "cool-down", "duration_pct": 0.20, "mood": "recovery"}
                ],
                "overall_mood": "energetic",
                "genre": "electronic",
                "description": "High-energy workout music"
            },
            "calming_meditation": {
                "sections": [
                    {"style": "very slow ambient", "duration_pct": 1.0, "mood": "peaceful"}
                ],
                "overall_mood": "peaceful",
                "genre": "ambient",
                "description": "Consistent calming atmosphere"
            },
            "creative_flow": {
                "sections": [
                    {"style": "gentle uplifting intro", "duration_pct": 0.25, "mood": "inspired"},
                    {"style": "flowing melodic middle", "duration_pct": 0.50, "mood": "creative"},
                    {"style": "resolving outro", "duration_pct": 0.25, "mood": "satisfied"}
                ],
                "overall_mood": "creative",
                "genre": "ambient-electronic",
                "description": "Music to support creative thinking"
            },
            "dramatic_build": {
                "sections": [
                    {"style": "quiet beginning", "duration_pct": 0.20, "mood": "anticipation"},
                    {"style": "building tension", "duration_pct": 0.40, "mood": "rising"},
                    {"style": "powerful climax", "duration_pct": 0.30, "mood": "peak"},
                    {"style": "resolution", "duration_pct": 0.10, "mood": "resolved"}
                ],
                "overall_mood": "dramatic",
                "genre": "orchestral",
                "description": "Dramatic arc with tension and release"
            }
        }

    def create_plan_from_prompt(
        self,
        prompt: str,
        total_duration_ms: int = 60000,
        num_sections: Optional[int] = None
    ) -> CompositionPlan:
        """
        Analyze prompt and create intelligent composition plan.

        Args:
            prompt: Natural language description
            total_duration_ms: Total length
            num_sections: Force specific number of sections (auto if None)

        Returns:
            CompositionPlan ready for generation

        Examples:
            "3 minute dramatic build" → 4 sections with tension arc
            "ambient study music" → single consistent section
            "workout warmup to cooldown" → 3 sections with energy arc
        """
        logger.info(f"Creating plan from prompt: '{prompt[:50]}...'")

        # Detect if prompt matches a template
        template = self._detect_template_from_prompt(prompt)
        if template:
            logger.info(f"Using template: {template}")
            return self.create_from_template(template, total_duration_ms)

        # Detect mood progression keywords
        progression = self._detect_mood_progression(prompt)
        if progression:
            logger.info(f"Detected progression: {progression}")
            return self.create_progressive_plan(
                start_mood=progression['start'],
                end_mood=progression['end'],
                duration_ms=total_duration_ms,
                num_sections=num_sections or 3
            )

        # Default: create simple plan based on prompt analysis
        mood = self._extract_mood(prompt)
        num_sections = num_sections or self._suggest_section_count(total_duration_ms)

        sections = self._create_sections_for_mood(
            mood=mood,
            total_duration=total_duration_ms,
            count=num_sections
        )

        return CompositionPlan(
            sections=sections,
            total_duration_ms=total_duration_ms,
            overall_mood=mood,
            genre=self._extract_genre(prompt)
        )

    def create_progressive_plan(
        self,
        start_mood: str,
        end_mood: str,
        duration_ms: int,
        num_sections: int = 3
    ) -> CompositionPlan:
        """
        Create gradual progression from one mood to another.

        Args:
            start_mood: Starting emotional state
            end_mood: Ending emotional state
            duration_ms: Total duration
            num_sections: How many steps in the progression

        Returns:
            CompositionPlan with smooth mood transition
        """
        logger.info(f"Creating progressive plan: {start_mood} → {end_mood}")

        sections = []
        section_duration = duration_ms // num_sections

        # Define mood spectrum for interpolation
        mood_progression = self._interpolate_moods(start_mood, end_mood, num_sections)

        for i, mood in enumerate(mood_progression):
            style = self._mood_to_style(mood, position=i, total=num_sections)
            sections.append(Section(
                style=style,
                duration_ms=section_duration,
                mood=mood
            ))

        return CompositionPlan(
            sections=sections,
            total_duration_ms=duration_ms,
            overall_mood=f"{start_mood}_to_{end_mood}",
            genre=None
        )

    def create_from_template(
        self,
        template_name: str,
        duration_ms: Optional[int] = None
    ) -> CompositionPlan:
        """
        Create plan from pre-defined template.

        Args:
            template_name: Name of template to use
            duration_ms: Total duration (uses template default if None)

        Returns:
            CompositionPlan based on template
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.templates.keys())}")

        template = self.templates[template_name]
        total_duration = duration_ms or 60000

        sections = []
        for section_template in template['sections']:
            section_duration = int(total_duration * section_template['duration_pct'])
            sections.append(Section(
                style=section_template['style'],
                duration_ms=section_duration,
                mood=section_template['mood']
            ))

        return CompositionPlan(
            sections=sections,
            total_duration_ms=total_duration,
            overall_mood=template['overall_mood'],
            genre=template.get('genre')
        )

    def _detect_template_from_prompt(self, prompt: str) -> Optional[str]:
        """Detect if prompt matches a known template."""
        prompt_lower = prompt.lower()

        keywords = {
            "focus_work": ["focus", "coding", "work", "study", "concentration", "lo-fi"],
            "energetic_workout": ["workout", "exercise", "gym", "running", "energetic"],
            "calming_meditation": ["meditation", "calm", "peaceful", "relaxing", "sleep"],
            "creative_flow": ["creative", "brainstorm", "inspire", "flow"],
            "dramatic_build": ["dramatic", "build", "climax", "epic", "cinematic"]
        }

        for template, keywords_list in keywords.items():
            if any(keyword in prompt_lower for keyword in keywords_list):
                return template

        return None

    def _detect_mood_progression(self, prompt: str) -> Optional[Dict]:
        """Detect mood progression keywords in prompt."""
        prompt_lower = prompt.lower()

        # Pattern: "X to Y" or "X → Y"
        patterns = [
            (r'(\w+)\s+to\s+(\w+)', lambda m: {'start': m.group(1), 'end': m.group(2)}),
            (r'(\w+)\s*→\s*(\w+)', lambda m: {'start': m.group(1), 'end': m.group(2)}),
            (r'from\s+(\w+)\s+to\s+(\w+)', lambda m: {'start': m.group(1), 'end': m.group(2)}),
        ]

        for pattern, extractor in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                return extractor(match)

        # Common phrase patterns
        if "build" in prompt_lower and ("tension" in prompt_lower or "energy" in prompt_lower):
            return {'start': 'calm', 'end': 'energetic'}

        if "wind down" in prompt_lower or "cool down" in prompt_lower:
            return {'start': 'energetic', 'end': 'calm'}

        return None

    def _extract_mood(self, prompt: str) -> str:
        """Extract primary mood from prompt."""
        prompt_lower = prompt.lower()

        mood_keywords = {
            "calm": ["calm", "peaceful", "gentle", "quiet", "serene"],
            "energetic": ["energetic", "upbeat", "lively", "exciting", "dynamic"],
            "focused": ["focus", "concentration", "steady", "determined"],
            "happy": ["happy", "joyful", "cheerful", "uplifting"],
            "melancholic": ["sad", "melancholic", "somber", "reflective"],
            "dramatic": ["dramatic", "epic", "powerful", "intense"],
            "creative": ["creative", "inspiring", "flowing", "imaginative"]
        }

        for mood, keywords in mood_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return mood

        return "neutral"

    def _extract_genre(self, prompt: str) -> Optional[str]:
        """Extract genre hint from prompt."""
        prompt_lower = prompt.lower()

        genres = ["ambient", "lo-fi", "electronic", "orchestral", "piano", "jazz", "classical"]

        for genre in genres:
            if genre in prompt_lower:
                return genre

        return None

    def _suggest_section_count(self, duration_ms: int) -> int:
        """Suggest appropriate number of sections based on duration."""
        if duration_ms < 30000:  # < 30 seconds
            return 1
        elif duration_ms < 90000:  # < 90 seconds
            return 2
        elif duration_ms < 180000:  # < 3 minutes
            return 3
        else:
            return 4

    def _create_sections_for_mood(
        self,
        mood: str,
        total_duration: int,
        count: int
    ) -> List[Section]:
        """Create sections that maintain a consistent mood."""
        sections = []
        section_duration = total_duration // count

        for i in range(count):
            if count == 1:
                style = f"{mood} atmosphere throughout"
            elif i == 0:
                style = f"{mood} intro"
            elif i == count - 1:
                style = f"{mood} outro"
            else:
                style = f"{mood} middle section"

            sections.append(Section(
                style=style,
                duration_ms=section_duration,
                mood=mood
            ))

        return sections

    def _interpolate_moods(
        self,
        start: str,
        end: str,
        steps: int
    ) -> List[str]:
        """Create smooth mood progression."""
        # Simplified: return progression of moods
        if steps == 1:
            return [end]
        elif steps == 2:
            return [start, end]
        elif steps == 3:
            middle = self._blend_moods(start, end)
            return [start, middle, end]
        else:
            # For 4+ steps, create gradual progression
            result = [start]
            for i in range(steps - 2):
                result.append(f"transitioning from {start} to {end}")
            result.append(end)
            return result

    def _blend_moods(self, mood1: str, mood2: str) -> str:
        """Create a blended mood description."""
        return f"{mood1} transitioning to {mood2}"

    def _mood_to_style(self, mood: str, position: int, total: int) -> str:
        """Convert mood to musical style description."""
        position_desc = ""
        if total > 1:
            if position == 0:
                position_desc = "intro - "
            elif position == total - 1:
                position_desc = "outro - "
            else:
                position_desc = "middle - "

        return f"{position_desc}{mood} section"

    def validate_plan(self, plan: CompositionPlan) -> bool:
        """
        Validate that a composition plan is valid.

        Checks:
        - Total duration matches sum of sections
        - Each section has required fields
        - Durations are reasonable
        """
        if not plan.sections:
            logger.error("Plan has no sections")
            return False

        # Check duration sum
        total_section_duration = sum(s.duration_ms for s in plan.sections)
        if abs(total_section_duration - plan.total_duration_ms) > 1000:  # Allow 1s tolerance
            logger.error(f"Duration mismatch: sections={total_section_duration}ms, plan={plan.total_duration_ms}ms")
            return False

        # Check individual sections
        for i, section in enumerate(plan.sections):
            if section.duration_ms < 1000:  # Min 1 second per section
                logger.error(f"Section {i} too short: {section.duration_ms}ms")
                return False

            if not section.style or not section.mood:
                logger.error(f"Section {i} missing style or mood")
                return False

        logger.debug(f"Plan validated: {len(plan.sections)} sections, {plan.total_duration_ms}ms")
        return True


if __name__ == "__main__":
    planner = CompositionPlanner()
    print(f"✅ Loaded {len(planner.templates)} templates")
