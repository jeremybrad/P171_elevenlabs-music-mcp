# 🎵 ElevenLabs Music MCP - Quick Start

**5-Minute Setup Guide**

---

## For Jeremy (Local Development)

### 1. Get Your API Key
```bash
# Visit: https://elevenlabs.io/app/settings/api-keys
# Copy your API key (starts with sk_...)
```

### 2. Setup Environment
```bash
cd /Users/jeremybradford/SyncedProjects/P171_elevenlabs-music-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API key
```

### 3. Test It Works
```bash
# Quick API test
python -c "
from src.config_manager import Config
from src.music_generator import MusicGenerator

config = Config()
gen = MusicGenerator(config.api_key)
result = gen.generate('gentle piano, 10 seconds', duration_ms=10000)
print('Success!' if result.success else f'Error: {result.error}')
"
```

### 4. Start MCP Server
```bash
python src/music_mcp_server.py
# Should start without errors
# Press Ctrl+C to stop
```

### 5. Configure Claude Desktop
```bash
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
# Add the elevenlabs-music server config from:
cat config/claude_desktop_config.template.json

# Restart Claude Desktop completely
```

### 6. Test with Claude Desktop
Open Claude Desktop and try:
> "Generate 30 seconds of lo-fi music for coding"

Music should appear in `~/Music/ElevenLabs/generated/`

---

## For Claude Code Web

### 1. Clone & Setup
```bash
# Repository already initialized locally
# When in Claude Code Web, install deps:
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add API key
```

### 2. Read Documentation
1. **PRD.md** - Understand the vision
2. **CLAUDE_CODE_SETUP.md** - Development guide
3. **PHASE1_TASKS.md** - Implementation roadmap

### 3. Start Building
Follow PHASE1_TASKS.md sequentially:
- Task 1: Infrastructure
- Task 2: API Integration
- Task 3: File Management  
- Task 4: MCP Server
- Task 5: Testing
- Task 6: Documentation

### 4. Test Frequently
```bash
# Unit tests
pytest tests/ -v

# Integration test
python -c "
from src.music_mcp_server import MusicMCPServer
server = MusicMCPServer()
# If no errors, server initialized successfully
"
```

### 5. Commit Progress
```bash
git add -A
git commit -m "feat: implement [what you did]"
git push origin main
```

---

## Common Issues

### "API key invalid"
- Check `.env` has correct key
- Key should start with `sk_`
- No quotes needed in `.env`

### "Permission denied" writing files
```bash
mkdir -p ~/Music/ElevenLabs/generated
chmod 755 ~/Music/ElevenLabs/generated
```

### "Module not found"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "MCP server not connecting"
- Restart Claude Desktop completely (Quit + relaunch)
- Check config path: `~/Library/Application Support/Claude/`
- Verify JSON syntax in config file

---

## Success Criteria

✅ **You're ready when**:
- API test generates music successfully
- MCP server starts without errors  
- Claude Desktop can request music
- Files appear in output directory

🎉 **You've succeeded when**:
- Say "Generate music" to Claude → Music appears
- Files are well-organized and named
- Metadata is captured accurately
- System handles errors gracefully

---

## Next Steps

After Phase 1 works:
1. Update README with your findings
2. Document any API quirks
3. Plan Phase 2 (composition plans, mood analysis)
4. Celebrate! 🎵

---

**Need help?** Check:
- CLAUDE_CODE_SETUP.md for detailed guidance
- PHASE1_TASKS.md for implementation details
- PRD.md for design decisions
- Jeremy's Claude for architecture questions