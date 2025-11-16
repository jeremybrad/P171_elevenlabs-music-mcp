# Phase 1: MVP Implementation Tasks

**Goal**: Working MCP server that generates music from text prompts  
**Time Estimate**: 4-6 hours  
**Priority**: Must complete for basic functionality

---

## 🎯 Definition of Done

- [ ] MCP server starts and runs without errors
- [ ] `generate_music_simple` tool successfully generates music
- [ ] Music files saved with proper organization
- [ ] Claude Desktop can request and receive music
- [ ] Basic error handling works
- [ ] Core tests passing
- [ ] README updated with setup instructions

---

## 📋 Task Breakdown

### Task 1: Project Infrastructure (30 minutes)

**1.1 Environment Setup**
- [ ] Create `.env` file from `.env.example`
- [ ] Add ElevenLabs API key to `.env`
- [ ] Test API key validity with simple curl command
- [ ] Create output directories (~/Music/ElevenLabs/generated, etc.)

**1.2 Logging Configuration**
- [ ] Set up Python logging in `config_manager.py`
- [ ] Configure log levels (DEBUG for development, INFO for production)
- [ ] Create log file in appropriate location
- [ ] Add timestamp and log level to messages

**1.3 Configuration Management**
```python
# src/config_manager.py

class Config:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.output_dir = Path(os.getenv("MUSIC_OUTPUT_DIR", "~/Music/ElevenLabs/generated")).expanduser()
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
    def validate(self):
        """Ensure required config is present"""
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")
        if not self.api_key.startswith("sk_"):
            raise ValueError("Invalid API key format")
```

**Validation**:
```bash
# Should work without errors
python -c "from src.config_manager import Config; Config().validate()"
```

---

### Task 2: ElevenLabs API Integration (1-2 hours)

**2.1 Basic API Client**
- [ ] Create `MusicGenerator` class in `music_generator.py`
- [ ] Implement authentication headers
- [ ] Create `generate()` method for simple generation
- [ ] Handle API response (audio data + metadata)

**2.2 Error Handling**
- [ ] Parse error responses from API
- [ ] Handle `bad_prompt` (copyright) errors
- [ ] Handle `bad_composition_plan` errors
- [ ] Handle rate limiting (429 errors)
- [ ] Handle network errors
- [ ] Handle invalid API key (401 errors)

**2.3 Response Processing**
- [ ] Extract audio data from response
- [ ] Parse composition plan from detailed endpoint
- [ ] Capture generation metadata
- [ ] Return structured result object

**Implementation Template**:
```python
# src/music_generator.py

class GenerationResult:
    success: bool
    audio_data: bytes | None
    composition_plan: dict | None
    error: str | None
    metadata: dict

class MusicGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate(
        self, 
        prompt: str, 
        duration_ms: int | None = None,
        output_format: str = "mp3_44100_128"
    ) -> GenerationResult:
        """Generate music from text prompt"""
        try:
            result = self._call_api(prompt, duration_ms, output_format)
            return GenerationResult(
                success=True,
                audio_data=result['audio'],
                composition_plan=result.get('plan'),
                metadata=result.get('metadata', {})
            )
        except CopyrightError as e:
            # Use suggested prompt from API
            return GenerationResult(
                success=False,
                error=f"Copyright issue: {e.suggested_prompt}"
            )
        except RateLimitError:
            return GenerationResult(
                success=False,
                error="Rate limit exceeded. Try again in a moment."
            )
```

**Validation**:
```bash
# Test with real API (uses credits!)
python -c "
from src.music_generator import MusicGenerator
gen = MusicGenerator(api_key='your-key')
result = gen.generate('gentle piano, 10 seconds', duration_ms=10000)
assert result.success
print(f'Generated {len(result.audio_data)} bytes of audio')
"
```

---

### Task 3: File Management (1 hour)

**3.1 Directory Structure**
- [ ] Implement `FileManager` class
- [ ] Create date-based subdirectories (YYYY-MM)
- [ ] Ensure directory creation is idempotent
- [ ] Handle permission errors gracefully

**3.2 File Naming**
- [ ] Generate unique filenames with timestamp
- [ ] Include descriptive slug from prompt
- [ ] Add counter for multiple generations same minute
- [ ] Sanitize filename for filesystem safety

**3.3 File Operations**
- [ ] Save audio data to MP3 file
- [ ] Save metadata to accompanying JSON file
- [ ] Atomic writes (temp file + rename)
- [ ] Verify files written successfully

**Implementation Template**:
```python
# src/file_manager.py

class FileManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def save_music(
        self, 
        audio_data: bytes, 
        metadata: dict
    ) -> tuple[Path, Path]:
        """Save music and metadata, return paths"""
        # Create date directory
        date_dir = self.base_dir / datetime.now().strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d")
        slug = self._create_slug(metadata.get('prompt', 'music'))
        counter = self._get_next_counter(date_dir, timestamp, slug)
        filename = f"{timestamp}_{slug}_{counter:03d}"
        
        # Save audio
        audio_path = date_dir / f"{filename}.mp3"
        self._atomic_write(audio_path, audio_data)
        
        # Save metadata
        metadata_path = date_dir / f"{filename}.json"
        self._atomic_write(
            metadata_path, 
            json.dumps(metadata, indent=2).encode()
        )
        
        return audio_path, metadata_path
        
    def _create_slug(self, prompt: str, max_length: int = 20) -> str:
        """Create filesystem-safe slug from prompt"""
        # Remove special chars, lowercase, truncate
        slug = re.sub(r'[^a-z0-9]+', '_', prompt.lower())
        return slug[:max_length].strip('_')
        
    def _atomic_write(self, path: Path, data: bytes):
        """Write file atomically using temp file"""
        temp_path = path.with_suffix('.tmp')
        try:
            with open(temp_path, 'wb') as f:
                f.write(data)
            temp_path.rename(path)  # Atomic on POSIX
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            raise
```

**Validation**:
```bash
# Test file operations
python -c "
from src.file_manager import FileManager
from pathlib import Path

fm = FileManager(Path('/tmp/test_music'))
audio_path, meta_path = fm.save_music(
    audio_data=b'fake audio data',
    metadata={'prompt': 'test music', 'duration_ms': 10000}
)
assert audio_path.exists()
assert meta_path.exists()
print(f'Saved to {audio_path}')
"
```

---

### Task 4: MCP Server Implementation (2 hours)

**4.1 Server Scaffold**
- [ ] Create `MusicMCPServer` class
- [ ] Initialize MCP server with proper name
- [ ] Set up server instance
- [ ] Implement graceful shutdown

**4.2 Tool Registration**
- [ ] Register `generate_music_simple` tool
- [ ] Define tool schema (parameters, types, requirements)
- [ ] Add detailed descriptions for LLM understanding
- [ ] Add examples in tool description

**4.3 Tool Implementation**
- [ ] Implement `generate_music_simple` handler
- [ ] Parameter validation
- [ ] Call music generator
- [ ] Save files via file manager
- [ ] Format response for MCP client
- [ ] Error handling and reporting

**4.4 Server Lifecycle**
- [ ] Implement `main()` function
- [ ] Set up stdio transport (for Claude Desktop)
- [ ] Add signal handlers (SIGINT, SIGTERM)
- [ ] Cleanup on shutdown

**Implementation Template**:
```python
# src/music_mcp_server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

class MusicMCPServer:
    def __init__(self):
        self.server = Server("elevenlabs-music")
        self.config = Config()
        self.generator = MusicGenerator(self.config.api_key)
        self.file_manager = FileManager(self.config.output_dir)
        self._register_handlers()
        
    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="generate_music_simple",
                    description="""Generate music from a natural language prompt using ElevenLabs.
                    
                    Example prompts:
                    - "lo-fi hip hop beats for coding, 90 BPM"
                    - "calming ambient piano, gentle, 2 minutes"
                    - "energizing workout music with bass"
                    
                    The AI will interpret your description and generate appropriate music.
                    Files are automatically saved with metadata.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Natural language description of desired music"
                            },
                            "duration_ms": {
                                "type": "integer",
                                "description": "Duration in milliseconds (3000-300000, i.e. 3s-5min)",
                                "minimum": 3000,
                                "maximum": 300000
                            }
                        },
                        "required": ["prompt"]
                    }
                )
            ]
            
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "generate_music_simple":
                return await self._generate_music_simple(arguments)
            raise ValueError(f"Unknown tool: {name}")
            
    async def _generate_music_simple(self, args: dict):
        """Handle music generation request"""
        try:
            # Generate music
            result = self.generator.generate(
                prompt=args["prompt"],
                duration_ms=args.get("duration_ms")
            )
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=f"Error: {result.error}"
                )]
            
            # Save files
            audio_path, meta_path = self.file_manager.save_music(
                audio_data=result.audio_data,
                metadata={
                    "prompt": args["prompt"],
                    "duration_ms": args.get("duration_ms"),
                    "composition_plan": result.composition_plan,
                    "generated_at": datetime.now().isoformat()
                }
            )
            
            # Format response
            response = f"""Music generated successfully!

File: {audio_path}
Prompt: {args['prompt']}
Duration: {args.get('duration_ms', 'auto')}ms

Composition: {result.composition_plan.get('style', 'N/A')}

Ready to play! 🎵"""

            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Failed to generate music: {str(e)}"
            )]

async def main():
    """Run the MCP server"""
    server = MusicMCPServer()
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Validation**:
```bash
# Test server starts without errors
python src/music_mcp_server.py

# Should see MCP server initialization
# Press Ctrl+C to stop
```

---

### Task 5: Testing (1-2 hours)

**5.1 Unit Tests**
- [ ] Test `Config` validation
- [ ] Test `MusicGenerator` with mocks
- [ ] Test `FileManager` file operations
- [ ] Test error handling paths

**5.2 Integration Tests**
- [ ] Test full generation flow with mock API
- [ ] Test MCP tool schema validation
- [ ] Test end-to-end with real API (minimal)

**5.3 Manual Testing**
- [ ] Configure Claude Desktop with MCP server
- [ ] Test basic generation: "generate music for coding"
- [ ] Test with duration: "generate 30 seconds of calm music"
- [ ] Test error cases: copyrighted content, invalid params
- [ ] Verify files created correctly
- [ ] Verify metadata is accurate

**Test Files to Create**:
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── mocks.py                 # Mock API responses
├── test_config.py
├── test_music_generator.py
├── test_file_manager.py
└── test_integration.py
```

**Example Test**:
```python
# tests/test_music_generator.py

import pytest
from src.music_generator import MusicGenerator
from tests.mocks import mock_api_response

def test_successful_generation(mock_api_response):
    """Test successful music generation"""
    gen = MusicGenerator(api_key="test_key")
    
    # Inject mock
    gen._call_api = mock_api_response
    
    result = gen.generate(
        prompt="gentle piano",
        duration_ms=10000
    )
    
    assert result.success
    assert result.audio_data is not None
    assert result.composition_plan is not None
    
def test_copyright_error_handling(mock_copyright_error):
    """Test handling of copyrighted content"""
    gen = MusicGenerator(api_key="test_key")
    gen._call_api = mock_copyright_error
    
    result = gen.generate(prompt="Beatles song")
    
    assert not result.success
    assert "copyright" in result.error.lower()
    assert "suggested_prompt" in result.error
```

---

### Task 6: Documentation & Polish (30 minutes)

**6.1 Update README**
- [ ] Add installation instructions
- [ ] Add configuration instructions
- [ ] Add usage examples
- [ ] Add troubleshooting section

**6.2 Code Documentation**
- [ ] Add docstrings to all functions
- [ ] Add type hints throughout
- [ ] Add inline comments for complex logic
- [ ] Add module-level docstrings

**6.3 Configuration Examples**
- [ ] Complete .env.example with all variables
- [ ] Add Claude Desktop config example
- [ ] Add example prompts document

---

## 🔧 Development Commands Reference

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

# Development
python src/music_mcp_server.py  # Run server

# Testing
pytest tests/                    # All tests
pytest tests/ -v                 # Verbose
pytest tests/ -k "test_generator"  # Specific tests
pytest --cov=src tests/          # With coverage

# Validation
python -m src.config_manager     # Test config
python -c "from src.music_generator import MusicGenerator; ..."  # Test generation

# Git
git add -A
git commit -m "feat: complete Phase 1 MVP"
git push origin main
```

---

## 🎯 Phase 1 Completion Checklist

Mark these as you complete:

### Core Functionality
- [ ] Config manager loads and validates settings
- [ ] Music generator calls API successfully
- [ ] File manager saves files with proper naming
- [ ] MCP server starts and registers tools
- [ ] `generate_music_simple` tool works end-to-end

### Error Handling
- [ ] API errors parsed and displayed clearly
- [ ] Copyright errors show suggested alternatives
- [ ] Rate limiting handled gracefully
- [ ] File system errors reported helpfully
- [ ] Network errors don't crash server

### Quality
- [ ] All core functions have docstrings
- [ ] Type hints on function signatures
- [ ] Tests passing for critical paths
- [ ] No obvious bugs in happy path
- [ ] Code is readable and organized

### Documentation
- [ ] README has setup instructions
- [ ] .env.example shows all required vars
- [ ] Claude Desktop config documented
- [ ] Example prompts provided
- [ ] Troubleshooting guide started

### Integration
- [ ] Claude Desktop can connect to server
- [ ] Music generation request succeeds
- [ ] Files appear in correct location
- [ ] Metadata is accurate
- [ ] Response formatting is good

---

## 📊 Time Estimates

| Task | Estimated Time | Notes |
|------|---------------|-------|
| Infrastructure | 30 min | Config, logging, directories |
| API Integration | 1-2 hours | Client, errors, parsing |
| File Management | 1 hour | Naming, saving, metadata |
| MCP Server | 2 hours | Tools, handlers, lifecycle |
| Testing | 1-2 hours | Unit, integration, manual |
| Documentation | 30 min | README, examples, docstrings |
| **Total** | **6-8 hours** | Can be faster with focus |

---

## 🚀 Go Time!

You have everything you need:
- ✅ Clear requirements (PRD.md)
- ✅ Architecture design (ARCHITECTURE.md)
- ✅ Detailed tasks (this document)
- ✅ Setup guide (CLAUDE_CODE_SETUP.md)
- ✅ Project skeleton (src/ files)

**Start with Task 1 and work through sequentially.** Each task builds on the previous one.

**Good luck! Make Jeremy proud.** 🎵

When you finish, create a `PHASE1_COMPLETE.md` with:
- What worked well
- Any challenges
- Test results
- Next steps for Phase 2