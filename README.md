# P171: ElevenLabs Music MCP Server

🎵 **Transform AI agents into musical co-creators**

An MCP (Model Context Protocol) server that enables any AI agent to generate personalized music using the ElevenLabs Music API. Part of Jeremy Bradford's AI ecosystem, designed for seamless integration with Claude Desktop, Claude Code, Betty, and other agents.

## 🌟 What This Does

- **Simple Prompts → Professional Music**: "Generate lo-fi coding music" → Instant MP3
- **Context-Aware Generation**: Betty detects you're stressed → Suggests calming soundscape
- **Journal Soundtracks**: Daily journal entries with custom-generated music (Phase 3)
- **Universal Access**: Any MCP-compatible agent can generate music

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# ElevenLabs API Key
export ELEVENLABS_API_KEY="your-key-here"
```

### Installation

```bash
# Clone repository
cd /Users/jeremybradford/SyncedProjects/P171_elevenlabs-music-mcp

# Install dependencies
pip install -r requirements.txt

# Test the server
python src/music_mcp_server.py --test
```

### Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "elevenlabs-music": {
      "command": "python",
      "args": [
        "/Users/jeremybradford/SyncedProjects/P171_elevenlabs-music-mcp/src/music_mcp_server.py"
      ],
      "env": {
        "ELEVENLABS_API_KEY": "your-key-here"
      }
    }
  }
}
```

Restart Claude Desktop. You're ready!

## 💬 Usage Examples

### With Claude Desktop

```
You: "Generate upbeat electronic music for 60 seconds"

Claude: [Calls MCP tool: generate_music_simple]
        Created: /Music/ElevenLabs/generated/2025-11/upbeat_electronic_001.mp3
        Energetic EDM track at 128 BPM with synth leads and driving bass.
```

### With Betty (Context-Aware)

```
You: "Ugh, this code isn't working. I'm so frustrated."

Betty: [Analyzes mood: frustrated]
       [Calls: analyze_mood_for_music]
       [Generates: calming ambient music]
       
       "I made you something - gentle piano with ambient textures, 
       90 seconds. Take a breath. Want to walk through the problem together?"
```

### Advanced: Composition Plans

```python
# Create structured multi-section piece
plan = {
    "sections": [
        {"style": "gentle piano intro", "duration_ms": 15000},
        {"style": "building ambient layers", "duration_ms": 30000},
        {"style": "uplifting resolution", "duration_ms": 15000}
    ]
}

# Generate from plan
result = generate_music_structured(composition_plan=plan)
```

## 🏗️ Architecture

```
MCP Client (Claude Desktop, Betty, etc.)
           ↓
    [MCP Protocol Layer]
           ↓
   Music MCP Server
    ├── Music Generator
    ├── Composition Planner
    ├── Context Analyzer (mood detection)
    ├── File Manager
    └── Preference Learner
           ↓
    ElevenLabs API
```

## 🛠️ MCP Tools Available

### 1. `generate_music_simple`
Quick music generation from natural language.

**Parameters**: `prompt`, `duration_ms`, `output_format`, `metadata`  
**Returns**: Audio file path, composition plan, metadata

### 2. `create_composition_plan`
Generate structured composition before creating music.

**Parameters**: `prompt`, `total_duration_ms`, `sections`, `mood_progression`  
**Returns**: Detailed composition plan JSON

### 3. `generate_music_structured`
Create music from detailed composition plan.

**Parameters**: `composition_plan`, `strict_duration`, `metadata`  
**Returns**: Audio file with precise structure

### 4. `analyze_mood_for_music`
Analyze context and suggest appropriate music.

**Parameters**: `context`, `activity`, `time_of_day`  
**Returns**: Suggested prompt and reasoning

### 5. `generate_journal_entry_with_music` (Phase 3)
Create daily journal with matching soundtrack.

**Parameters**: `conversation_history`, `date`, `music_duration_ms`  
**Returns**: Journal entry + custom music + combined HTML

## 📁 File Organization

```
/Users/jeremybradford/Music/ElevenLabs/
├── generated/           # All generated music
│   └── 2025-11/
│       ├── focus_coding_001.mp3
│       ├── calm_ambient_002.mp3
│       └── metadata.json
├── journal/             # Journal entries + soundtracks (Phase 3)
│   └── 2025-11/
│       ├── 2025-11-16_entry.json
│       ├── 2025-11-16_soundtrack.mp3
│       └── 2025-11-16_combined.html
└── preferences/         # Learning system
    └── learned_preferences.json
```

## 🗺️ Development Roadmap

### ✅ Phase 1: MVP (Current Focus)
- [x] Repository structure
- [x] Documentation (PRD, README, Architecture)
- [ ] MCP server scaffold
- [ ] Basic music generation (simple prompts)
- [ ] File management
- [ ] Error handling
- [ ] Claude Desktop integration tested

### 🔄 Phase 2: Enhanced Generation
- [ ] Composition plan generation
- [ ] Structured music generation
- [ ] Mood analysis tool
- [ ] Preference storage
- [ ] Betty context integration

### 📅 Phase 3: Journal Integration
- [ ] Daily journal entry generation
- [ ] Music matching journal mood
- [ ] Combined HTML output
- [ ] Search and retrieval
- [ ] Timeline view

### 🚀 Phase 4+: Intelligence & Polish
- [ ] Preference learning
- [ ] Proactive suggestions
- [ ] Voice control integration
- [ ] Ableton Live integration
- [ ] Mobile app

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Test MCP tools
python tests/test_mcp_tools.py

# Test with mock API
python tests/test_with_mock.py

# Manual integration test
python tests/manual_test.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
ELEVENLABS_API_KEY=sk-...

# Optional
MUSIC_OUTPUT_DIR=/Users/jeremybradford/Music/ElevenLabs/generated
JOURNAL_OUTPUT_DIR=/Users/jeremybradford/Music/ElevenLabs/journal
ENABLE_PREFERENCE_LEARNING=true
LOG_LEVEL=INFO
```

### Configuration File

`config/settings.json`:
```json
{
  "output": {
    "music_dir": "/Users/jeremybradford/Music/ElevenLabs/generated",
    "journal_dir": "/Users/jeremybradford/Music/ElevenLabs/journal",
    "default_format": "mp3_44100_128"
  },
  "generation": {
    "default_duration_ms": 60000,
    "max_duration_ms": 300000,
    "min_duration_ms": 10000
  },
  "learning": {
    "enable_preference_learning": true,
    "feedback_weight": 0.7
  }
}
```

## 📚 Related Projects

- **P033_resonance-prime**: Betty Memory MCP (reference implementation)
- **P050_ableton-mcp**: Ableton Live integration
- **P167_dj-claude-mcp**: DJ Claude (future collaboration)

## 🐛 Troubleshooting

### "API Key Not Found"
```bash
# Set environment variable
export ELEVENLABS_API_KEY="your-key-here"

# Or add to shell profile
echo 'export ELEVENLABS_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### "MCP Server Not Responding"
1. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`
2. Verify Python path in config
3. Test server standalone: `python src/music_mcp_server.py --test`

### "Copyright Error from API"
API detected copyrighted content in prompt. The response includes a suggestion—use that instead.

### "File Not Saved"
Check output directory exists and permissions:
```bash
mkdir -p /Users/jeremybradford/Music/ElevenLabs/generated
chmod 755 /Users/jeremybradford/Music/ElevenLabs/generated
```

## 🤝 Contributing

This is a personal project, but ideas welcome! If you build something similar:
1. Reference the MCP protocol specs
2. Check out the Betty MCP server pattern
3. Share what you learned

## 📄 License

Personal project - see main SyncedProjects LICENSE

## 🎯 Success Metrics

**Phase 1 Complete When:**
- ✅ Claude Desktop generates music on request
- ✅ Files saved with proper organization
- ✅ Errors handled gracefully
- ✅ Composition plans captured

**Ultimate Success:**
- 🎵 One year of daily journal soundtracks
- 💭 Music captures forgotten emotional moments
- 🤖 AI agents deeply understand your emotional landscape

## 📞 Support

Built by Jeremy Bradford using Claude Code Web.

For questions or issues:
1. Check troubleshooting section above
2. Review ElevenLabs API docs: https://elevenlabs.io/docs
3. Refer back to Jeremy's main Claude instance for architecture questions

## 🎉 Quick Win

**Your first generated track:**

1. Start Claude Desktop
2. Say: "Generate me some chill lo-fi beats for coding, 30 seconds"
3. Smile when you hear it! 🎵

---

*"Not just music generation—an emotional memory system, a sonic journal of your life."*

**Status**: 🟡 In Development (Phase 1)  
**Last Updated**: 2025-11-16  
**Next Milestone**: MVP Complete