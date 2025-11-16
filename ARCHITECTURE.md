# Technical Architecture: ElevenLabs Music MCP Server

**Version**: 1.0  
**Author**: Jeremy Bradford & Claude  
**Date**: 2025-11-16

---

## System Overview

The ElevenLabs Music MCP Server is a bridge between AI agents and music generation capabilities. It exposes music creation tools through the Model Context Protocol (MCP), enabling any compatible client to generate, manage, and learn from personalized music.

## Core Architecture Principles

1. **Separation of Concerns**: Music generation logic isolated from client implementation
2. **Stateless Operations**: Each request is independent (preferences stored separately)
3. **Fail-Safe Design**: Graceful degradation when API or features unavailable
4. **Local-First**: All generated content stored locally for reliability
5. **Extensible**: Easy to add new tools or integrate with other systems

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Claude       │  │ Claude Code  │  │ Betty                │  │
│  │ Desktop      │  │              │  │ (OpenWebUI)          │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────────┘  │
│         │                 │                  │                   │
│         └─────────────────┴──────────────────┘                   │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
            ╔═══════════════╧════════════════╗
            ║    MCP Protocol (stdio)        ║
            ║    - JSON-RPC 2.0              ║
            ║    - Tool invocation           ║
            ║    - Result streaming          ║
            ╚═══════════════╤════════════════╝
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                           │                                      │
│              Music MCP Server (Python)│                                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Core MCP Server (music_mcp_server.py)       │  │
│  │                                                            │  │
│  │  • Tool Registration & Routing                           │  │
│  │  • Request Validation                                    │  │
│  │  • Error Handling & Logging                             │  │
│  │  • Response Formatting                                   │  │
│  └────────────┬──────────────┬──────────────┬──────────────┘  │
│               │              │              │                  │
│      ┌────────┴────────┐     │     ┌────────┴────────┐         │
│      │                 │     │     │                 │         │
│  ┌───┴───────────┐ ┌───┴────────┐ ┌┴───────────┐ ┌──┴────────┐│
│  │ Music         │ │ Composition│ │ Context    │ │ Preference││
│  │ Generator     │ │ Planner    │ │ Analyzer   │ │ Learner   ││
│  └───────┬───────┘ └───────┬────┘ └────┬───────┘ └──┬────────┘│
│          │                 │            │            │         │
│          │                 │            │            │         │
│  ┌───────┴─────────────────┴────────────┴────────────┴───────┐ │
│  │                 Shared Services                            │ │
│  │  • File Manager  • Metadata Handler  • Config Manager    │ │
│  └────────────────────────────┬──────────────────────────────┘ │
│                                │                                │
└────────────────────────────────┼────────────────────────────────┘
                                 │
            ╔════════════════════╧═════════════════════╗
            ║     External Dependencies                ║
            ║                                          ║
            ║  ┌─────────────────┐  ┌───────────────┐ ║
            ║  │ ElevenLabs API  │  │ Local         │ ║
            ║  │ • /music/compose│  │ Filesystem    │ ║
            ║  │ • /music/stream │  │ • Music files │ ║
            ║  │ • Rate limiting │  │ • Metadata    │ ║
            ║  └─────────────────┘  │ • Preferences │ ║
            ║                       └───────────────┘ ║
            ╚═════════════════════════════════════════╝
```

---

## Component Breakdown

### 1. MCP Server Core (`music_mcp_server.py`)

**Responsibilities**:
- Initialize MCP server with stdio transport
- Register all available tools
- Route requests to appropriate handlers
- Validate input parameters
- Handle errors and format responses
- Manage server lifecycle

**Key Classes**:
```python
class MusicMCPServer:
    """Main server instance"""
    def __init__(self):
        self.server = Server("elevenlabs-music")
        self.generator = MusicGenerator()
        self.planner = CompositionPlanner()
        self.context_analyzer = ContextAnalyzer()
        self.file_manager = FileManager()
        self.preference_learner = PreferenceLearner()
        
    async def run(self):
        """Start MCP server with stdio transport"""
        
    def register_tools(self):
        """Register all MCP tools"""
```

**Tool Registration Pattern**:
```python
@self.server.tool()
async def generate_music_simple(
    prompt: str,
    duration_ms: int = None,
    output_format: str = "mp3_44100_128",
    metadata: dict = None
) -> dict:
    """Tool implementation"""
    try:
        result = await self.generator.generate_simple(...)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Music Generator (`music_generator.py`)

**Responsibilities**:
- Interface with ElevenLabs API
- Handle API authentication
- Manage generation requests
- Process API responses
- Handle retries and rate limiting

**Key Methods**:
```python
class MusicGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.session = aiohttp.ClientSession()
        
    async def generate_simple(
        self, 
        prompt: str, 
        duration_ms: int = None,
        output_format: str = "mp3_44100_128"
    ) -> MusicResult:
        """Generate music from simple prompt"""
        
    async def generate_structured(
        self,
        composition_plan: dict,
        strict_duration: bool = False
    ) -> MusicResult:
        """Generate from composition plan"""
        
    async def stream_music(self, prompt: str) -> AsyncIterator[bytes]:
        """Stream music generation (future)"""
```

**API Integration**:
```python
# POST /v1/music/compose
payload = {
    "prompt": prompt,
    "duration_ms": duration_ms,
    "output_format": output_format
}

headers = {
    "xi-api-key": self.api_key,
    "Content-Type": "application/json"
}

response = await self.session.post(
    f"{self.base_url}/music/compose",
    json=payload,
    headers=headers
)
```

**Error Handling**:
```python
class MusicGenerationError(Exception):
    """Base exception for generation errors"""
    
class CopyrightError(MusicGenerationError):
    """Copyrighted content detected"""
    def __init__(self, suggestion: str):
        self.suggestion = suggestion
        
class RateLimitError(MusicGenerationError):
    """API rate limit exceeded"""
    
class QuotaExceededError(MusicGenerationError):
    """API quota exceeded"""
```

### 3. Composition Planner (`composition_planner.py`)

**Responsibilities**:
- Generate composition plans from prompts
- Validate plan structure
- Build template-based plans
- Handle plan modifications

**Composition Plan Schema**:
```python
@dataclass
class Section:
    style: str
    duration_ms: int
    mood: str
    instruments: List[str]
    tempo: int
    key: str
    transition_from_previous: str = "smooth"
    
@dataclass
class CompositionPlan:
    sections: List[Section]
    total_duration_ms: int
    overall_mood: str
    genre: str
    metadata: dict
    
    def to_api_format(self) -> dict:
        """Convert to ElevenLabs API format"""
```

**Plan Generation**:
```python
class CompositionPlanner:
    async def create_from_prompt(
        self,
        prompt: str,
        duration_ms: int
    ) -> CompositionPlan:
        """Use API to generate plan"""
        
    def create_from_template(
        self,
        template_name: str,
        customizations: dict
    ) -> CompositionPlan:
        """Generate from pre-defined template"""
        
    def validate_plan(self, plan: CompositionPlan) -> bool:
        """Ensure plan is valid"""
```

**Templates**:
```python
TEMPLATES = {
    "focus_work": {
        "sections": [
            {"style": "ambient intro", "duration_ms": 10000},
            {"style": "steady rhythm", "duration_ms": 40000},
            {"style": "gentle outro", "duration_ms": 10000}
        ],
        "mood": "focused",
        "tempo": 70
    },
    "energizing": {...},
    "calming": {...}
}
```

### 4. Context Analyzer (`context_analyzer.py`)

**Responsibilities**:
- Analyze text for emotional content
- Detect mood indicators
- Suggest appropriate music parameters
- Learn from patterns

**Mood Detection**:
```python
class ContextAnalyzer:
    def __init__(self):
        self.mood_indicators = self.load_indicators()
        
    async def analyze_mood(
        self,
        context: str,
        activity: str = None,
        time_of_day: str = None
    ) -> MoodAnalysis:
        """Extract mood from context"""
        
    def detect_frustration(self, text: str) -> float:
        """Frustration level 0-1"""
        indicators = ["fuck", "damn", "ugh", "frustrated",
                     "not working", "broken"]
        score = sum(1 for word in indicators if word in text.lower())
        return min(score / 5, 1.0)
        
    def suggest_music_params(
        self,
        mood: MoodAnalysis
    ) -> MusicSuggestion:
        """Suggest prompt and parameters"""
```

**Mood Categories**:
```python
@dataclass
class MoodAnalysis:
    primary_mood: str  # "calm", "energetic", "frustrated", etc.
    intensity: float   # 0-1
    valence: float     # negative-positive (-1 to 1)
    arousal: float     # low-high (0-1)
    indicators: List[str]
    confidence: float
    
MOOD_TO_MUSIC_MAPPING = {
    ("frustrated", high_intensity): "calming ambient, gentle",
    ("energetic", high_arousal): "upbeat electronic, driving",
    ("focused", moderate_arousal): "lo-fi beats, steady rhythm"
}
```

### 5. File Manager (`file_manager.py`)

**Responsibilities**:
- Organize generated files
- Handle naming conventions
- Manage metadata
- Cleanup old files (optional)

**File Organization**:
```python
class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.music_dir = self.base_dir / "generated"
        self.journal_dir = self.base_dir / "journal"
        
    def get_output_path(
        self,
        category: str = "generated",
        prefix: str = None,
        metadata: dict = None
    ) -> Path:
        """Generate organized file path"""
        # /generated/2025-11/2025-11-16_prefix_001.mp3
        
    def save_audio(
        self,
        audio_data: bytes,
        metadata: dict
    ) -> Path:
        """Save with metadata"""
        
    def save_metadata(
        self,
        audio_path: Path,
        metadata: dict
    ):
        """Save accompanying JSON"""
```

**Metadata Structure**:
```python
{
    "file": "2025-11-16_focus_coding_001.mp3",
    "generated_at": "2025-11-16T14:30:00Z",
    "prompt": "lo-fi beats for coding",
    "duration_ms": 60000,
    "composition_plan": {...},
    "context": {
        "activity": "coding",
        "mood": "focused",
        "agent": "claude-desktop"
    },
    "feedback": {
        "completed": true,
        "rating": null
    }
}
```

### 6. Preference Learner (`preference_learner.py`)

**Responsibilities**:
- Track music generation history
- Learn from implicit feedback
- Build user preference model
- Make personalized suggestions

**Learning Signals**:```python
class PreferenceLearner:
    def __init__(self, storage_path: Path):
        self.storage = storage_path
        self.preferences = self.load_preferences()
        
    def record_generation(
        self,
        prompt: str,
        metadata: dict,
        result_path: Path
    ):
        """Record generation for learning"""
        
    def record_feedback(
        self,
        file_id: str,
        feedback_type: str,  # "completed", "skipped", "replayed"
        context: dict = None
    ):
        """Learn from user actions"""
        
    def get_preferences(
        self,
        context: dict = None
    ) -> PreferenceProfile:
        """Get learned preferences for context"""
```

**Preference Profile**:
```python
{
    "user": "jeremy",
    "preferences": {
        "coding": {
            "preferred_styles": ["lo-fi", "ambient", "minimal techno"],
            "avg_duration_ms": 120000,
            "tempo_range": [60, 90],
            "completion_rate": 0.85
        },
        "frustrated": {
            "intervention_style": "calming ambient",
            "effectiveness_score": 0.9
        }
    },
    "history_summary": {
        "total_generations": 150,
        "favorite_moods": ["focused", "calm", "energetic"],
        "peak_usage_times": ["morning", "afternoon"]
    }
}
```

---

## Data Flow

### Simple Music Generation Flow

```
1. Client Request
   │
   ├─→ Claude Desktop sends MCP request:
   │   {
   │     "tool": "generate_music_simple",
   │     "params": {
   │       "prompt": "lo-fi coding music",
   │       "duration_ms": 120000
   │     }
   │   }
   │
2. MCP Server Receives
   │
   ├─→ music_mcp_server.py routes to generate_music_simple()
   │
   ├─→ Validates parameters
   │
3. Music Generator
   │
   ├─→ music_generator.py sends API request to ElevenLabs
   │
   ├─→ Receives audio data + composition plan
   │
4. File Management
   │
   ├─→ file_manager.py saves audio file
   │
   ├─→ Generates metadata JSON
   │
   ├─→ Returns file path to server
   │
5. Preference Learning
   │
   ├─→ preference_learner.py records generation
   │
6. Response to Client
   │
   └─→ MCP server sends result:
       {
         "success": true,
         "audio_path": "/Music/.../2025-11-16_coding_001.mp3",
         "duration_ms": 120000,
         "composition_plan": {...}
       }
```

### Context-Aware Generation Flow (Betty)

```
1. Betty Analyzes Context
   │
   ├─→ User says: "Ugh this isn't working"
   │
   ├─→ Betty detects frustration
   │
2. Betty Calls MCP Tool
   │
   ├─→ analyze_mood_for_music(context="user frustrated")
   │
   ├─→ Returns: "calming ambient, 90 seconds"
   │
3. Betty Generates Music
   │
   ├─→ generate_music_simple(
   │     prompt="calming ambient piano",
   │     duration_ms=90000,
   │     metadata={"triggered_by": "frustration_detection"}
   │   )
   │
4. Betty Responds
   │
   └─→ "I made you something calming. Take a breath."
```

---

## API Integration Details

### ElevenLabs Music API

**Base URL**: `https://api.elevenlabs.io/v1`

**Authentication**:
```python
headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}
```

**Endpoints Used**:

#### 1. POST /music/compose
Simple music generation.

**Request**:
```json
{
  "prompt": "lo-fi beats with piano, 70 BPM",
  "duration_ms": 60000,
  "output_format": "mp3_44100_128"
}
```

**Response**:
```json
{
  "audio": "<base64-encoded-audio>",
  "composition_plan": {
    "sections": [...]
  }
}
```

#### 2. POST /music/compose-detailed
Returns composition plan + audio.

**Request**: Same as compose

**Response**: Includes detailed composition_plan JSON

#### 3. POST /music/stream
Streaming generation (Phase 2+).

**Error Responses**:
```json
{
  "error": "bad_prompt",
  "message": "Copyrighted content detected",
  "suggestion": "Try: 'chill electronic music'",
  "original_prompt": "Beatles-style music"
}
```

**Rate Limiting**:
- Headers include rate limit info
- Implement exponential backoff
- Queue requests if needed

---

## Configuration Management

### Environment Variables
```bash
# Required
ELEVENLABS_API_KEY=sk-...

# Optional
MUSIC_OUTPUT_DIR=/path/to/music
JOURNAL_OUTPUT_DIR=/path/to/journal
ENABLE_PREFERENCE_LEARNING=true
LOG_LEVEL=INFO
LOG_FILE=/path/to/logs/music_mcp.log
```

### Configuration File Schema
```python
@dataclass
class Config:
    # API
    api_key: str
    api_base_url: str = "https://api.elevenlabs.io/v1"
    api_timeout: int = 30
    
    # Output
    music_output_dir: Path
    journal_output_dir: Path
    default_output_format: str = "mp3_44100_128"
    
    # Generation defaults
    default_duration_ms: int = 60000
    max_duration_ms: int = 300000
    min_duration_ms: int = 10000
    
    # Learning
    enable_preference_learning: bool = True
    preference_storage_path: Path
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = None
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load from environment variables"""
        
    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        """Load from JSON/YAML file"""
```

---

## Error Handling Strategy

### Error Categories

1. **API Errors**
   - Network failures → Retry with backoff
   - Rate limiting → Queue and retry
   - Copyright detected → Use API suggestion
   - Quota exceeded → Clear error to user

2. **Validation Errors**
   - Invalid parameters → Return validation message
   - Duration out of range → Auto-adjust or error
   - Invalid format → Use default

3. **File System Errors**
   - Directory not writable → Clear error message
   - Disk full → Cleanup old files or error
   - Permission denied → Configuration fix needed

4. **Integration Errors**
   - MCP protocol errors → Log and fail gracefully
   - Tool not found → Return available tools
   - Timeout → Configurable timeout handling

### Error Response Format
```python
{
    "success": false,
    "error": {
        "type": "CopyrightError",
        "message": "Prompt contains copyrighted content",
        "details": "Mentioned 'Beatles' which is copyrighted",
        "suggestion": "Try 'classic rock style music'",
        "recoverable": true
    }
}
```

---

## Performance Considerations

### API Optimization
- Cache composition plans for similar prompts
- Batch multiple requests when possible
- Use streaming for large generations (Phase 2+)
- Monitor API usage and costs

### File System
- Compress old audio files (optional)
- Cleanup after 90 days (configurable)
- Use indexed metadata for fast search
- Lazy load large files

### Memory Management
- Stream large audio files
- Don't hold API responses in memory
- Clean up temporary files
- Limit concurrent generations

---

## Security Considerations

### API Key Management
- Never log API keys
- Store in environment variables
- Support key rotation
- Validate key on startup

### Input Validation
- Sanitize all prompts
- Validate duration ranges
- Check file paths (no directory traversal)
- Rate limit per client (if multi-user)

### Data Privacy
- All data stored locally
- No telemetry without consent
- User can delete history
- Metadata doesn't leak sensitive info

---

## Testing Strategy

### Unit Tests
```python
# test_music_generator.py
async def test_generate_simple():
    generator = MusicGenerator(api_key="test")
    result = await generator.generate_simple(
        prompt="test music",
        duration_ms=30000
    )
    assert result.success
    assert result.audio_path.exists()

# test_composition_planner.py
def test_create_from_template():
    planner = CompositionPlanner()
    plan = planner.create_from_template("focus_work")
    assert plan.total_duration_ms == 60000
    assert len(plan.sections) == 3
```

### Integration Tests
```python
# test_mcp_integration.py
async def test_mcp_tool_call():
    server = MusicMCPServer()
    result = await server.handle_tool_call(
        tool="generate_music_simple",
        params={"prompt": "test", "duration_ms": 10000}
    )
    assert result["success"]
```

### Manual Testing
```bash
# Test server startup
python src/music_mcp_server.py --test

# Test with Claude Desktop
# (Restart Claude Desktop after config update)

# Test with mock API
MOCK_API=true python src/music_mcp_server.py
```

---

## Monitoring & Logging

### Log Structure
```python
{
    "timestamp": "2025-11-16T14:30:00Z",
    "level": "INFO",
    "component": "music_generator",
    "event": "generation_complete",
    "details": {
        "prompt": "lo-fi beats",
        "duration_ms": 60000,
        "output_path": "/path/to/file.mp3",
        "api_latency_ms": 3500
    }
}
```

### Metrics to Track
- Generation success rate
- API latency
- File sizes
- User satisfaction (implicit feedback)
- Common error types
- Daily usage patterns

---

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
export ELEVENLABS_API_KEY="your-key"

# Run tests
pytest tests/

# Start server
python src/music_mcp_server.py
```

### Claude Desktop Integration
```bash
# Copy config template
cp config/claude_desktop_config.template.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Edit with your API key
# Restart Claude Desktop
```

### Production Considerations
- Monitor API usage and costs
- Set up log rotation
- Implement cleanup of old files
- Consider database for metadata (if scale increases)
- Add monitoring/alerting for errors

---

## Future Architecture Enhancements

### Phase 3: Journal Integration
```
Journal System
    ↓
Conversation History → Mood Extraction → Music Generation
    ↓                       ↓                  ↓
Text Summary          Music Prompt       Audio File
    ↓                       ↓                  ↓
Combined HTML with embedded audio player
```

### Phase 4: Learning System
```
User Actions → Feature Extraction → Model Training
                    ↓
              Preference Profile
                    ↓
         Personalized Suggestions
```

### Phase 5+: Advanced Features
- Real-time collaboration between agents
- Voice control integration
- Ableton Live DAW integration
- Mobile app with push notifications
- Community sharing (opt-in)