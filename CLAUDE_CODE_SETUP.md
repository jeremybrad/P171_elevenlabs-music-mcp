# Claude Code Web - Development Setup Guide

**Project**: P171 - ElevenLabs Music MCP Server  
**Phase**: Phase 1 MVP  
**Time Budget**: ~$700 Claude Code Web credit (use efficiently!)

---

## 🎯 Quick Context

You're building an MCP server that lets AI agents (Claude Desktop, Betty, etc.) generate music using the ElevenLabs Music API. This guide assumes you're working in Claude Code Web and need to maximize your promo credit.

**Key Goal**: Get Phase 1 MVP working so Jeremy can generate music through Claude Desktop.

---

## 📋 Pre-Session Checklist

Before you start in Claude Code Web:

- [ ] Read PRD.md (understand the vision)
- [ ] Read ARCHITECTURE.md (understand the structure)
- [ ] Read PHASE1_TASKS.md (your implementation roadmap)
- [ ] Have ElevenLabs API key ready
- [ ] Review the MCP Protocol basics
- [ ] Check out Betty MCP server as reference pattern

---

## 🚀 Development Workflow

### Step 1: Environment Setup (5 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ELEVENLABS_API_KEY
```

### Step 2: Understand the Codebase (10 min)

**Entry Point**: `src/music_mcp_server.py`
- This is the MCP server that exposes tools to clients
- Follows the Betty MCP server pattern from P033_resonance-prime
- Uses the `mcp` Python SDK

**Core Modules**:
- `music_generator.py`: Handles ElevenLabs API calls
- `file_manager.py`: Saves and organizes generated music files
- `config_manager.py`: Handles configuration and env vars
- `composition_planner.py`: Creates structured composition plans
- `context_analyzer.py`: Analyzes mood/context for music suggestions
- `preference_learner.py`: (Phase 2) Learns user preferences

### Step 3: Implementation Order (Follow PHASE1_TASKS.md)

Work through tasks in this exact order:

1. **Core Infrastructure**
   - Config management
   - Environment variable handling
   - Logging setup

2. **ElevenLabs Integration**
   - API client
   - Authentication
   - Simple music generation endpoint

3. **File Management**
   - Directory structure creation
   - File naming convention
   - Metadata storage

4. **MCP Server**
   - Server scaffold
   - `generate_music_simple` tool
   - Tool registration
   - Error handling

5. **Testing & Validation**
   - Unit tests
   - Integration tests
   - Manual testing with Claude Desktop

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_music_generator.py -v

# Run with coverage
pytest --cov=src tests/
```

### Integration Testing

1. **Mock API Testing**:
```python
# Use mock responses to avoid burning API credits during development
from tests.mocks import mock_elevenlabs_response

# Test with mock
result = music_generator.generate(prompt="test", use_mock=True)
```

2. **Real API Testing**:
```python
# Only test with real API when mocks pass
result = music_generator.generate(prompt="gentle piano, 10 seconds")
assert result.success
assert os.path.exists(result.audio_path)
```

### Manual Testing with Claude Desktop

Once MCP server works:

```bash
# Start the MCP server (for manual testing)
python src/music_mcp_server.py
```

Then configure Claude Desktop (see config/claude_desktop_config.template.json) and test:
- "Generate music for coding, 30 seconds"
- "Create calming ambient music"
- "Make energizing morning music"

---

## 🔧 Key Implementation Details

### MCP Server Pattern (from Betty MCP)

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

class MusicMCPServer:
    def __init__(self):
        self.server = Server("elevenlabs-music")
        self.generator = MusicGenerator()
        
    def register_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="generate_music_simple",
                    description="Generate music from natural language prompt",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "duration_ms": {"type": "integer"},
                            # ...more params
                        },
                        "required": ["prompt"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "generate_music_simple":
                return await self.generate_music_simple(arguments)
```

### ElevenLabs API Integration

```python
import requests

class MusicGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate(self, prompt: str, duration_ms: int = None):
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {"prompt": prompt}
        if duration_ms:
            payload["duration_ms"] = duration_ms
            
        response = requests.post(
            f"{self.base_url}/music/compose",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            # Handle audio data
            return self._save_audio(response.content)
        else:
            # Handle errors (copyright, rate limit, etc.)
            return self._handle_error(response)
```

### File Organization

```python
class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        
    def save_generated_music(self, audio_data: bytes, metadata: dict):
        # Create directory structure: /2025-11/
        date_dir = self.base_dir / datetime.now().strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename: 2025-11-16_focus_coding_001.mp3
        filename = self._generate_filename(metadata)
        audio_path = date_dir / filename
        
        # Save audio
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
            
        # Save metadata
        metadata_path = audio_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return audio_path
```

---

## 🎨 Phase 1 MVP Scope

**What You MUST Build**:
1. MCP server that starts and registers tools
2. `generate_music_simple` tool that:
   - Takes a text prompt
   - Calls ElevenLabs API
   - Saves the audio file
   - Returns file path and metadata
3. Basic error handling
4. File organization system
5. Configuration management

**What You CAN Skip (for now)**:
- Composition plans (Phase 2)
- Mood analysis (Phase 2)
- Preference learning (Phase 2-4)
- Journal integration (Phase 3)
- Advanced features

**Quality Bar**:
- Clean, readable code
- Proper error messages
- Type hints on functions
- Basic tests passing
- Documentation strings
- Works with Claude Desktop

---

## 🐛 Common Pitfalls & Solutions

### Problem: "Module not found" errors
**Solution**: Make sure you're in the right directory and venv is activated
```bash
cd /path/to/P171_elevenlabs-music-mcp
source venv/bin/activate  # or python -m venv venv if not created
pip install -r requirements.txt
```

### Problem: "API key invalid"
**Solution**: Check your .env file has the correct key format
```bash
# .env
ELEVENLABS_API_KEY=sk_...  # Should start with sk_
```

### Problem: "Copyright error from API"
**Solution**: The prompt contains copyrighted material. Use the API's suggested prompt from the error response
```python
if error.type == "bad_prompt":
    suggested_prompt = error.composition_plan_suggestion
    # Retry with suggested prompt
```

### Problem: "Permission denied" writing files
**Solution**: Check output directory exists and is writable
```bash
mkdir -p ~/Music/ElevenLabs/generated
chmod 755 ~/Music/ElevenLabs/generated
```

### Problem: "MCP server not connecting"
**Solution**: Check Claude Desktop config path and restart Claude
```bash
# Check config at: ~/Library/Application Support/Claude/claude_desktop_config.json
# After editing, fully quit and restart Claude Desktop
```

---

## 📊 Progress Tracking

Use this checklist as you work:

### Infrastructure (1-2 hours)
- [ ] Config manager loading environment variables
- [ ] Logging setup with proper levels
- [ ] Directory structure auto-creation
- [ ] Error handling framework

### API Integration (1-2 hours)
- [ ] ElevenLabs client class
- [ ] Authentication working
- [ ] Simple generation endpoint
- [ ] Error response parsing
- [ ] Copyright detection handling

### File Management (1 hour)
- [ ] File naming convention implemented
- [ ] Directory organization working
- [ ] Metadata storage
- [ ] Audio file writing

### MCP Server (2 hours)
- [ ] Server scaffold
- [ ] Tool registration
- [ ] `generate_music_simple` implementation
- [ ] Response formatting
- [ ] Error propagation to client

### Testing (1-2 hours)
- [ ] Unit tests for core functions
- [ ] Integration test with mock API
- [ ] Manual test with real API
- [ ] Claude Desktop integration test

---

## 🎯 Success Criteria

**You're done with Phase 1 when**:

1. **Technical**:
   - MCP server starts without errors
   - Can call `generate_music_simple` via MCP
   - Music files saved to correct location
   - Metadata captured properly
   - Basic tests passing

2. **Functional**:
   - Claude Desktop can request music
   - Generated music matches prompt reasonably
   - Files organized in date-based folders
   - Error messages are helpful

3. **User Experience**:
   - "Generate music for coding" → works
   - "Make calming piano music" → works
   - "Create energizing workout music" → works
   - Errors are graceful, not crashes

**Demo Script**:
```
User → Claude Desktop: "Generate 30 seconds of lo-fi hip hop for coding"
Claude → MCP Server: generate_music_simple(prompt="...", duration_ms=30000)
MCP Server → ElevenLabs API: POST /music/compose
ElevenLabs API → MCP Server: {audio data, composition plan}
MCP Server → File System: Save to /Music/ElevenLabs/generated/2025-11/...
MCP Server → Claude: {audio_path, metadata}
Claude → User: "Created: [path]. Lo-fi hip hop at 70 BPM, perfect for focus."
```

---

## 💾 Saving Your Work

Since you're using Claude Code Web with expiring credits:

1. **Commit Frequently**:
```bash
git add -A
git commit -m "feat: implement music generator"
git push origin main
```

2. **Document Decisions**:
Create `DEVELOPMENT_LOG.md` and note:
- What worked well
- What was challenging
- API quirks discovered
- Design decisions made

3. **Leave Breadcrumbs**:
If you don't finish, create `RESUME_HERE.md`:
- What's complete
- What's next
- Any blockers encountered
- Test commands that work

---

## 📞 Getting Help

**Stuck on something?** 

1. Check the ElevenLabs API docs: https://elevenlabs.io/docs/api-reference/music/compose
2. Review Betty MCP server code: `/SyncedProjects/P033_resonance-prime/Betty-Memory/betty_mcp_server.py`
3. Check MCP SDK examples: https://github.com/modelcontextprotocol/python-sdk

**Returning to Jeremy's Claude**:
- Architectural questions
- Design decisions
- Integration concerns
- Future phase planning

---

## 🎉 Celebration Criteria

When you successfully:
1. Generate first track via Claude Desktop → Screenshot it!
2. Have clean, working test suite → Leave a note!
3. Complete Phase 1 checklist → Update README!

---

## Next Steps After Phase 1

Once MVP is working:
1. Update README with setup instructions
2. Create demo video/screenshots
3. Document any API quirks
4. Plan Phase 2 (if time/credits remain)

**Phase 2 would add**:
- Composition plan creation
- Mood analysis
- Template-based generation

But Phase 1 is the priority! Get the fundamentals rock solid first.

---

*Good luck! You're building something genuinely cool. Music generation as an AI capability feels like the future. Make it awesome.* 🎵