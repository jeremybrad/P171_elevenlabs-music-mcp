# Phase 2 - Enhanced Generation & Device Features

**Status**: Ready to Start  
**Prerequisite**: Phase 1 MVP Complete ✅  
**Estimated Time**: 3-4 hours

---

## Phase 1 Completion Summary

✅ **What Works Now**:
- Music generation from text prompts via ElevenLabs API
- Atomic file saving with date-based organization
- Comprehensive error handling (copyright, rate limits, network)
- Metadata storage alongside audio files
- 13/13 core tests passing
- **TESTED WITH REAL API**: Successfully generated and saved music!

**Known Issues Fixed**:
- ✅ Default timeout increased to 120s (music generation takes 60-90s)
- ✅ pytest.ini created for async tests
- ⚠️ Async tests need `pytest-asyncio` properly configured (minor)

---

## Phase 2 Goals

Add intelligent features that make music generation context-aware and compositionally sophisticated:

1. **Composition Planning** - Multi-section structured music
2. **Mood Analysis** - Detect user context and suggest appropriate music
3. **Preference Learning** - Remember what user likes
4. **Enhanced MCP Tools** - Expose new capabilities to AI agents

---

## Implementation Tasks

### Task 1: Composition Planner (60-90 min)

**File**: `src/composition_planner.py`

Implement structured composition plans that break music into sections:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CompositionSection:
    """One section of a multi-part composition."""
    style: str  # "gentle piano intro", "building tension", etc.
    duration_ms: int
    mood: str  # "calm", "energetic", "melancholic", etc.
    tempo_hint: Optional[str] = None  # "slow", "moderate", "fast"
    
@dataclass
class CompositionPlan:
    """Complete plan for structured music generation."""
    sections: List[CompositionSection]
    total_duration_ms: int
    overall_mood: str
    
class CompositionPlanner:
    """Generate structured composition plans."""
    
    def create_plan_from_prompt(
        self, 
        prompt: str,
        total_duration_ms: int = 60000
    ) -> CompositionPlan:
        """
        Analyze prompt and create structured plan.
        
        Examples:
        - "3 minute dramatic build" → intro (30s) → tension (90s) → climax (60s)
        - "ambient study music" → consistent gentle atmosphere throughout
        """
        pass
    
    def create_progressive_plan(
        self,
        start_mood: str,
        end_mood: str,
        duration_ms: int,
        num_sections: int = 3
    ) -> CompositionPlan:
        """Create gradual progression from one mood to another."""
        pass
```

**MCP Integration** (`src/music_mcp_server.py`):

Add new tool:
```python
@self.server.tool()
async def create_composition_plan(
    prompt: str,
    total_duration_ms: int = 60000,
    sections: int = None,
    mood_progression: str = None
) -> dict:
    """
    Generate a structured composition plan before creating music.
    
    Allows for multi-section pieces with different moods/styles.
    
    Args:
        prompt: Description of desired music
        total_duration_ms: Total length
        sections: Number of distinct sections (auto if None)
        mood_progression: "calm_to_energetic", "build_and_release", etc.
    
    Returns:
        dict with composition plan structure
    """
    pass
```

**Tests** (`tests/test_composition_planner.py`):
- Test plan generation from various prompts
- Test section duration adds up to total
- Test mood progression logic

---

### Task 2: Context Analyzer (45-60 min)

**File**: `src/context_analyzer.py`

Analyze conversation context and suggest appropriate music:

```python
from typing import Dict, Optional, List
from enum import Enum

class Activity(Enum):
    CODING = "coding"
    WRITING = "writing"
    BRAINSTORMING = "brainstorming"
    RELAXING = "relaxing"
    EXERCISING = "exercising"
    STUDYING = "studying"

class Mood(Enum):
    CALM = "calm"
    ENERGETIC = "energetic"
    FOCUSED = "focused"
    CREATIVE = "creative"
    STRESSED = "stressed"
    HAPPY = "happy"

class ContextAnalyzer:
    """Analyze context and suggest music."""
    
    def analyze_conversation(
        self,
        recent_messages: List[str],
        time_of_day: Optional[str] = None
    ) -> Dict:
        """
        Detect mood and activity from conversation.
        
        Examples:
        - "Ugh this code isn't working" → stressed, coding
        - "Let's brainstorm ideas" → creative, brainstorming
        - "Time to focus" → focused, studying/working
        """
        pass
    
    def suggest_music_for_context(
        self,
        activity: Activity,
        mood: Mood,
        duration_ms: int = 60000
    ) -> str:
        """Generate appropriate music prompt for context."""
        # Stressed + Coding → "calming ambient with gentle rhythm, 80 BPM"
        # Energetic + Exercise → "upbeat electronic, driving bass, 128 BPM"
        pass
```

**MCP Integration**:

Add tool:
```python
@self.server.tool()
async def analyze_mood_for_music(
    context: str,
    activity: str = None,
    time_of_day: str = None
) -> dict:
    """
    Analyze context and suggest appropriate music.
    
    Helps AI agents choose music that matches user's current state.
    
    Args:
        context: Recent conversation or situation
        activity: What user is doing (coding, writing, etc.)
        time_of_day: morning, afternoon, evening, night
    
    Returns:
        dict with:
        - detected_mood: str
        - detected_activity: str
        - suggested_prompt: str (ready to pass to generate_music_simple)
        - reasoning: str (why this music was suggested)
    """
    pass
```

---

### Task 3: Preference Learner (45-60 min)

**File**: `src/preference_learner.py`

Track what user likes and learns patterns:

```python
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class MusicPreference:
    """Record of user's music preference."""
    prompt: str
    liked: bool  # True if user requested similar again
    context: Optional[str] = None
    activity: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class PreferenceLearner:
    """Learn and apply user music preferences."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path / "preferences.json"
        self.preferences: List[MusicPreference] = []
        self.load()
    
    def record_preference(
        self,
        prompt: str,
        liked: bool,
        context: str = None,
        activity: str = None
    ):
        """Record a preference."""
        pref = MusicPreference(prompt, liked, context, activity)
        self.preferences.append(pref)
        self.save()
    
    def get_recommendations(
        self,
        activity: str = None,
        mood: str = None,
        limit: int = 5
    ) -> List[str]:
        """Get music prompts user has liked in similar contexts."""
        pass
    
    def save(self):
        """Save preferences to JSON."""
        with open(self.storage_path, 'w') as f:
            json.dump([asdict(p) for p in self.preferences], f, indent=2)
    
    def load(self):
        """Load preferences from JSON."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = json.load(f)
                self.preferences = [MusicPreference(**p) for p in data]
```

**MCP Integration**:

Modify `generate_music_simple` to record usage:
```python
# After successful generation
if self.config.enable_preference_learning:
    self.preference_learner.record_preference(
        prompt=prompt,
        liked=True,  # Assumption: if they generated it, they wanted it
        context=metadata.get('context') if metadata else None
    )
```

---

### Task 4: Enhanced MCP Tools (30 min)

**File**: `src/music_mcp_server.py`

Add the structured generation tool:

```python
@self.server.tool()
async def generate_music_structured(
    composition_plan: dict,
    strict_duration: bool = True,
    metadata: dict = None
) -> dict:
    """
    Generate music from a detailed composition plan.
    
    Allows precise control over multi-section pieces.
    
    Args:
        composition_plan: dict from create_composition_plan
        strict_duration: Enforce exact section durations
        metadata: Additional tags
    
    Returns:
        Same as generate_music_simple
    """
    # Convert composition_plan dict to API format
    # Call generator.generate_structured()
    # Save with file_manager
    pass
```

---

### Task 5: Update music_generator.py (30 min)

Add structured generation support:

```python
async def generate_structured(
    self,
    composition_plan: dict,
    output_format: str = "mp3_44100_128"
) -> MusicResult:
    """
    Generate music from structured composition plan.
    
    Uses ElevenLabs /v1/music/compose-detailed endpoint.
    """
    url = f"{self.base_url}/music/compose-detailed"
    payload = {
        "composition_plan": composition_plan,
        "output_format": output_format
    }
    # Similar flow to generate_simple()
    pass
```

---

## Testing Phase 2

### Unit Tests

```bash
pytest tests/test_composition_planner.py -v
pytest tests/test_context_analyzer.py -v
pytest tests/test_preference_learner.py -v
```

### Integration Test

Create `tests/test_phase2_integration.py`:

```python
async def test_full_workflow():
    """Test: Context analysis → Plan creation → Music generation"""
    
    # 1. Analyze context
    analyzer = ContextAnalyzer()
    context_result = analyzer.analyze_conversation(
        ["I'm stressed about this deadline", "Need to focus"]
    )
    
    # 2. Get music suggestion
    prompt = analyzer.suggest_music_for_context(
        activity=Activity.CODING,
        mood=Mood.STRESSED
    )
    
    # 3. Create composition plan
    planner = CompositionPlanner()
    plan = planner.create_plan_from_prompt(prompt, duration_ms=120000)
    
    # 4. Generate music (with real API)
    # ... test end-to-end
```

---

## Configuration Updates

**`.env.example`**:
```bash
# Phase 2 Features
ENABLE_PREFERENCE_LEARNING=true
ENABLE_MOOD_ANALYSIS=true
```

**`config_manager.py`**:
Already has these flags - just enable them in actual Config class initialization.

---

## Success Criteria - Phase 2 Complete When:

- ✅ `create_composition_plan` tool works and generates valid plans
- ✅ `analyze_mood_for_music` tool detects context and suggests music
- ✅ `generate_music_structured` tool creates multi-section pieces
- ✅ Preference learning stores and retrieves user likes
- ✅ All Phase 2 tests pass
- ✅ End-to-end test: conversation → analysis → plan → generation → save

---

## Usage Examples (After Phase 2)

### Betty Detects User Stress:

```
User: "Ugh this code won't compile. So frustrated."

Betty (internal):
1. Calls analyze_mood_for_music(context="frustrated with code")
   → Returns: mood=stressed, activity=coding, suggested_prompt="calming ambient piano, 70 BPM"
   
2. Calls generate_music_simple(prompt="calming ambient piano, 70 BPM", duration_ms=90000)
   → Music generated and saved

Betty: "I made you something - gentle piano for 90 seconds. Take a breath. Want to walk through the error together?"
```

### User Requests Structured Piece:

```
User: "Create a 3-minute piece that starts calm and builds to energetic"

Claude:
1. Calls create_composition_plan(
     prompt="calm to energetic progression",
     total_duration_ms=180000,
     mood_progression="calm_to_energetic"
   )
   → Returns plan with 4 sections
   
2. Calls generate_music_structured(composition_plan=plan)
   → Music generated with distinct sections
   
Claude: "Created your 3-minute progression: calm intro (30s) → building (60s) → peak energy (60s) → resolve (30s)"
```

---

## Phase 2 Improvements Over Phase 1

1. **More Intelligent**: Context-aware suggestions instead of manual prompts
2. **Better Structure**: Multi-section compositions vs single-section only
3. **Learns Over Time**: Preference tracking improves recommendations
4. **Agent-Friendly**: Tools designed for AI agents to use automatically

---

## Next Phase Preview (Phase 3 - Journal Integration)

After Phase 2, we'll add:
- Daily journal entry generation from conversation history
- Music generation matching journal mood
- Combined journal + soundtrack HTML output
- Integration with Betty Memory MCP for conversation analysis

---

**Ready to build Phase 2?** Estimated 3-4 hours total. Focus on Composition Planner first (it's the most impactful), then Context Analyzer, then Preference Learning.