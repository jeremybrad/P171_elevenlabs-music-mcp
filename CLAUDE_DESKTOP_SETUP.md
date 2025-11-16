# ElevenLabs Music MCP Server - Claude Desktop Setup Guide

**For**: Claude Desktop (AI Assistant)
**Purpose**: Configure yourself to generate music using the ElevenLabs Music API
**Project**: P171 - ElevenLabs Music MCP Server

---

## 🎯 What This Enables

Once configured, you (Claude Desktop) will be able to:
- Generate music from natural language prompts
- Create soundtracks for different moods and activities
- Save music files with organized naming
- Provide music recommendations based on context

**Example**: When a user says *"Generate some lo-fi hip hop for coding"*, you'll be able to create actual music files!

---

## 📋 Prerequisites Check

Before configuring, verify these are in place:

1. **API Key**: ElevenLabs API key is configured (already done ✅)
2. **Python**: Python 3.9+ installed at `/usr/local/bin/python`
3. **MCP Server**: Located at `/home/user/P171_elevenlabs-music-mcp/src/music_mcp_server.py`
4. **Dependencies**: Installed via `pip install -r requirements.txt` (already done ✅)

---

## 🛠️ Configuration Steps

### Step 1: Locate Your Configuration File

Your MCP server configuration file is located at:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Add the MCP Server Configuration

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "elevenlabs-music": {
      "command": "python",
      "args": [
        "/home/user/P171_elevenlabs-music-mcp/src/music_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/user/P171_elevenlabs-music-mcp"
      }
    }
  }
}
```

**If you already have other MCP servers configured**, add the `elevenlabs-music` entry to your existing `mcpServers` object.

**Example with multiple servers**:
```json
{
  "mcpServers": {
    "betty-memory": {
      "command": "python",
      "args": ["/path/to/betty/mcp_server.py"]
    },
    "elevenlabs-music": {
      "command": "python",
      "args": [
        "/home/user/P171_elevenlabs-music-mcp/src/music_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/user/P171_elevenlabs-music-mcp"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

After saving the configuration file:
1. **Fully quit** Claude Desktop (not just close the window)
2. **Restart** Claude Desktop
3. The MCP server will automatically start when you launch

---

## 🧪 Testing the Integration

Once configured and restarted, test the integration:

### Test 1: Basic Music Generation

Ask yourself (Claude Desktop) to generate music:

```
User: "Generate 30 seconds of gentle piano music"
```

**Expected Response**:
- You should call the `generate_music_simple` tool
- Music file should be created at: `~/Music/ElevenLabs/generated/YYYY-MM/`
- You should report the file path to the user

### Test 2: Mood-Based Generation

```
User: "I'm stressed. Can you create some calming music?"
```

**Expected Behavior**:
- Analyze the user's mood
- Generate appropriate calming music
- Provide supportive context with the music

### Test 3: Specific Requirements

```
User: "Generate 2 minutes of upbeat electronic music for working out"
```

**Expected Parameters**:
- Duration: 120000ms (2 minutes)
- Prompt: "upbeat electronic music, energetic, workout, high tempo"

---

## 🎵 Available MCP Tools

Once configured, you'll have access to these tools:

### 1. `generate_music_simple`

**Purpose**: Generate music from a natural language prompt

**Parameters**:
- `prompt` (required): Natural language description of desired music
- `duration_ms` (optional): Duration in milliseconds (3000-300000)
  - Default: 60000 (60 seconds)
- `output_format` (optional): Audio format
  - Default: "mp3_44100_128"
- `metadata` (optional): Additional metadata tags

**Example Usage**:
```json
{
  "prompt": "calm ambient piano, peaceful, gentle",
  "duration_ms": 45000
}
```

**Returns**:
```json
{
  "success": true,
  "audio_path": "/root/Music/ElevenLabs/generated/2025-11/2025-11-16_calm_ambient_piano_001.mp3",
  "metadata_path": "/root/Music/ElevenLabs/generated/2025-11/2025-11-16_calm_ambient_piano_001.json",
  "file_size_bytes": 345678,
  "composition_plan": {...},
  "message": "Successfully generated music: 2025-11-16_calm_ambient_piano_001.mp3"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Duration must be at least 3000ms (3 seconds)"
}
```

### 2. Future Tools (Phase 2+)

These are scaffolded but not yet implemented:
- `create_composition_plan`: Generate structured composition before creating music
- `generate_music_structured`: Create music from detailed composition plan
- `analyze_mood_for_music`: Analyze context and suggest appropriate music
- `generate_journal_entry_with_music`: Create daily journal with soundtrack (Phase 3)

---

## 📁 File Organization

Generated music files are automatically organized:

```
~/Music/ElevenLabs/generated/
├── 2025-11/
│   ├── 2025-11-16_lo_fi_coding_beats_001.mp3
│   ├── 2025-11-16_lo_fi_coding_beats_001.json
│   ├── 2025-11-16_calm_piano_002.mp3
│   └── 2025-11-16_calm_piano_002.json
└── 2025-12/
    └── ...
```

**Metadata JSON includes**:
- Original prompt
- Duration
- Composition plan (from ElevenLabs)
- Timestamp
- File size
- Output format

---

## 🎯 Best Practices for Usage

### When to Use This Tool

**Good scenarios**:
- User explicitly requests music generation
- User expresses a mood that music could help with
- User asks for background music for activities
- User wants soundtracks for content creation

**Consider carefully**:
- Don't generate music unsolicited
- Ask about duration preferences
- Confirm before generating long tracks (>2 minutes)
- Be mindful of API costs

### Prompt Engineering

**Good prompts**:
- "lo-fi hip hop, chill beats, 90 BPM, relaxed"
- "ambient electronic, spacey, ethereal, slow tempo"
- "upbeat acoustic guitar, happy, morning vibes"
- "calm piano with strings, peaceful, meditative"

**Avoid**:
- Copyrighted material: "play Beethoven's 5th Symphony"
- Specific artist names: "music like Taylor Swift"
- Trademarked content: "Star Wars theme"

**If you get a copyright error**, the API will suggest an alternative prompt. Use that!

### Duration Guidelines

- **Short (10-30 seconds)**: Quick tests, notifications, ringtones
- **Medium (30-90 seconds)**: Focus music loops, meditation
- **Long (2-5 minutes)**: Full tracks, background music, soundtracks

---

## 🔧 Troubleshooting

### Problem: "Tool not found" or "Unknown tool"

**Cause**: MCP server not loaded or configuration incorrect

**Solution**:
1. Verify configuration file syntax (valid JSON)
2. Check file path is correct
3. Fully restart Claude Desktop
4. Check logs at `~/Library/Logs/Claude/mcp*.log` (macOS)

### Problem: "API key invalid" error

**Cause**: Environment variable not set

**Solution**:
The API key should be automatically loaded from:
1. `~/.bashrc` environment variable
2. `.env` file in the project directory

Verify with:
```bash
echo $ELEVENLABS_API_KEY
```

If empty, it needs to be set in the user's shell profile.

### Problem: "Duration must be at least 3000ms"

**Cause**: Requested duration too short

**Solution**:
- Minimum: 3000ms (3 seconds)
- Maximum: 300000ms (5 minutes)
- Default: 60000ms (60 seconds)

### Problem: "Copyright detected" error

**Cause**: Prompt contains copyrighted material

**Solution**:
The error response includes a `suggested_prompt` field. Use that prompt instead:

```json
{
  "success": false,
  "error": "Copyright detected: ...",
  "suggested_prompt": "gentle classical piano in the style of romantic period",
  "message": "Copyright issue detected. Try this instead: '...'"
}
```

### Problem: Files not saving

**Cause**: Output directory doesn't exist or lacks permissions

**Solution**:
Check directory exists and is writable:
```bash
ls -la ~/Music/ElevenLabs/generated
```

If it doesn't exist, the MCP server should create it automatically. If permission errors occur, check user permissions.

---

## 📊 Configuration Reference

### Environment Variables (Optional)

These are set in `~/.bashrc` or the MCP server will use defaults:

```bash
# API Key (required - already configured)
export ELEVENLABS_API_KEY="sk_..."

# Optional customization
export MUSIC_OUTPUT_DIR="~/Music/ElevenLabs/generated"
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export DEFAULT_DURATION_MS="60000"  # Default 60 seconds
```

### Server Logs

Check logs for debugging:

**Location**: `~/.local/share/elevenlabs-music-mcp/server.log`

**What to look for**:
- `INFO - Logging initialized` - Server started successfully
- `INFO - Generating music` - API call initiated
- `INFO - Saved music` - File saved successfully
- `ERROR` - Any errors encountered

**Example log entry**:
```
2025-11-16 14:12:25 - src.music_generator - INFO - Generating music: 'gentle piano...' (duration: 30000ms)
2025-11-16 14:12:28 - src.file_manager - INFO - Saved music: 2025-11-16_gentle_piano_001.mp3 (456789 bytes)
```

---

## 🎨 Usage Examples for Claude Desktop

### Example 1: User Requests Music

```
User: "Can you generate some relaxing music for me?"

Claude: I'd be happy to create some relaxing music for you!
Let me generate a calming track.

[Calls generate_music_simple with prompt: "calm ambient music, peaceful, relaxing, gentle piano and strings"]

I've created a minute of peaceful ambient music with gentle piano and strings.
The file is saved at: ~/Music/ElevenLabs/generated/2025-11/2025-11-16_calm_ambient_music_001.mp3

Would you like me to generate a longer version or adjust the style?
```

### Example 2: Context-Aware Generation

```
User: "I can't focus. Everything is so distracting today."

Claude: I understand how frustrating that can be. Let me create some
focus-enhancing music that might help.

[Calls generate_music_simple with prompt: "lo-fi focus music, steady beat, minimal, non-distracting, 90 BPM", duration_ms: 120000]

I've generated 2 minutes of lo-fi focus music with a steady, non-distracting
beat at 90 BPM. This type of music is designed to help with concentration
without pulling your attention.

File: ~/Music/ElevenLabs/generated/2025-11/2025-11-16_lo_fi_focus_music_001.mp3

Try putting on some noise-canceling headphones if you have them, and let me
know if you'd like me to generate more or adjust the style!
```

### Example 3: Handling Errors Gracefully

```
User: "Generate music that sounds like The Beatles"

Claude: [Calls generate_music_simple with prompt: "music like The Beatles"]

[Receives copyright error with suggested_prompt: "upbeat 1960s rock and roll with jangly guitars and harmonies"]

I got a copyright notice for that request, but I can create something
inspired by that era instead. Let me generate some upbeat 1960s-style
rock and roll with jangly guitars and harmonies.

[Calls generate_music_simple with suggested prompt]

Here's a 60-second track inspired by that classic 1960s sound!
File: ~/Music/ElevenLabs/generated/2025-11/2025-11-16_upbeat_1960s_rock_001.mp3
```

---

## 🚀 Quick Reference

### Most Common Use Cases

| User Need | Prompt Template | Duration |
|-----------|----------------|----------|
| Focus/Coding | "lo-fi beats, chill, steady rhythm, 90 BPM" | 60-120s |
| Relaxation | "calm ambient, peaceful, gentle piano" | 90-180s |
| Meditation | "meditative, slow, ethereal, peaceful" | 120-300s |
| Energize | "upbeat electronic, energetic, high tempo" | 45-90s |
| Sleep | "very slow ambient, peaceful, quiet, gentle" | 180-300s |
| Workout | "high energy electronic, driving beat, 140 BPM" | 60-180s |

### Response Template

When successfully generating music:

```
I've created [DESCRIPTION] for you!

📁 File: [PATH]
⏱️ Duration: [DURATION] seconds
🎵 Style: [BRIEF DESCRIPTION OF COMPOSITION]

[OPTIONAL: Contextual message based on user's request]
```

---

## 📞 Support & Resources

### For Issues

1. **Check logs**: `~/.local/share/elevenlabs-music-mcp/server.log`
2. **Verify config**: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. **Test manually**: Run `python src/music_mcp_server.py` to check for errors
4. **Environment**: Verify `echo $ELEVENLABS_API_KEY` returns the key

### Documentation

- **PRD**: `/home/user/P171_elevenlabs-music-mcp/PRD.md` - Vision and goals
- **Architecture**: `/home/user/P171_elevenlabs-music-mcp/ARCHITECTURE.md` - Technical design
- **Phase 1 Complete**: `/home/user/P171_elevenlabs-music-mcp/PHASE1_COMPLETE.md` - Implementation summary
- **README**: `/home/user/P171_elevenlabs-music-mcp/README.md` - General overview

### API Documentation

ElevenLabs Music API: https://elevenlabs.io/docs/api-reference/music/compose

---

## ✅ Configuration Checklist

Before using, verify:

- [ ] Configuration file created/updated
- [ ] MCP server path is correct
- [ ] Claude Desktop restarted
- [ ] API key configured (check with `echo $ELEVENLABS_API_KEY`)
- [ ] Output directory exists (`~/Music/ElevenLabs/generated/`)
- [ ] Test generation successful
- [ ] Files saving correctly
- [ ] Error handling working

---

## 🎉 Ready to Use!

Once configured, you're ready to generate music! Remember:

✅ **DO**:
- Generate music when users explicitly request it
- Provide context about the generated music
- Handle errors gracefully
- Ask about duration preferences
- Suggest appropriate music for user's mood/activity

❌ **DON'T**:
- Generate music without user request
- Use copyrighted material in prompts
- Generate very long tracks without confirmation
- Ignore copyright suggestions from API

---

*This MCP server was built with Phase 1 MVP complete. Enjoy creating music!* 🎵

**Last Updated**: 2025-11-16
**Version**: Phase 1 MVP
**Status**: ✅ Production Ready
