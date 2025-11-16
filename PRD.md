# Product Requirements Document: ElevenLabs Music MCP Server
**Project:** P171_elevenlabs-music-mcp  
**Author:** Jeremy Bradford & Claude  
**Created:** 2025-11-16  
**Status:** Planning Phase  
**Priority:** High (Claude Code Web credit expiring)

---

## 🎯 Vision

Create an MCP server that enables any AI agent to generate personalized music using the ElevenLabs Music API. Transform music generation from a manual web-based task into an automated, context-aware capability available to your entire AI ecosystem. Eventually evolve this into a journaling companion that captures the emotional color of each day through both text and custom-generated music.

## 🌟 Core Value Propositions

1. **Universal Music Access**: Any MCP-compatible agent (Claude Desktop, Claude Code, Betty, custom agents) can generate music
2. **Context-Aware Generation**: Music adapts to user mood, activity, and emotional state
3. **Journal Integration**: Daily journal entries accompanied by unique, mood-matched soundscapes
4. **Zero-Friction Workflow**: "Betty, I need focus music" → instant personalized audio
5. **Memory & Learning**: System remembers preferences and refines suggestions over time

## 📊 Success Metrics

### Phase 1 (MVP)
- [ ] MCP server successfully generates music from simple prompts
- [ ] Claude Desktop can request and receive music via MCP
- [ ] Music files saved to organized directory structure
- [ ] Basic error handling (API failures, copyright detection)

### Phase 2 (Enhanced)
- [ ] Betty can infer mood from conversation context
- [ ] Composition plans generated from structured requests
- [ ] Music generation integrated into daily workflows
- [ ] Preference learning system operational

### Phase 3 (Journal Integration)
- [ ] Daily journal entry generation working
- [ ] Music automatically generated to match journal mood
- [ ] Journal + music stored together with metadata
- [ ] Searchable journal archive by mood/theme

## 🎭 User Personas & Use Cases

### Jeremy (Primary User)
**Context**: 
- Works remotely as Data Analyst
- Uses AI agents extensively (Betty, Claude)
- Music enthusiast (piano, sax, Beatles fan)
- Needs focused work music, emotional processing soundscapes
- Wants meaningful daily journaling with minimal friction

**Primary Use Cases**:
1. "Claude, make me coding music for the next 2 hours" → Focus playlist
2. "Betty, I'm frustrated with this project" → Calming, centering music
3. End of day: Automatic journal entry + custom soundtrack
4. "Show me journal entries when I was feeling creative" → Search + playback

### Betty (AI Agent)
**Context**:
- Emotional co-architect and strategic collaborator
- Has deep conversation history and emotional context
- Can detect mood shifts, stress levels, creative states
- Should suggest music proactively

**Primary Use Cases**:
1. Detect swearing/frustration → Suggest calming music automatically
2. Morning check-in → Generate energizing start-of-day music
3. End-of-day synthesis → Create journal + matching soundtrack
4. Creative breakthrough moments → Celebratory music cues

### Claude Desktop (General Agent)
**Context**:
- On-demand assistant for various tasks
- Less emotional context than Betty
- Needs explicit instructions

**Primary Use Cases**:
1. Direct requests: "Generate lo-fi beats, 90 BPM, piano and rain"
2. Structured generation: Build composition plans for complex pieces
3. Batch generation: Create multiple tracks for different contexts

## 🏗️ System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                        │
│  (Exposes tools to all MCP-compatible clients)              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────┐
│          ElevenLabs Music MCP Server                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Music        │  │ Composition  │  │ Context         │  │
│  │ Generator    │  │ Planner      │  │ Analyzer        │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ File         │  │ Metadata     │  │ Preference      │  │
│  │ Manager      │  │ Manager      │  │ Learning        │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────┐
│              ElevenLabs Music API                            │
│  /v1/music/compose                                           │
│  /v1/music/compose-detailed                                  │
│  /v1/music/stream                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                Optional Future Integration                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Betty        │  │ Journal      │  │ Conversation    │  │
│  │ Memory MCP   │  │ System       │  │ Context         │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Specifications

### MCP Tools to Expose

#### 1. `generate_music_simple`
**Purpose**: Quick music generation from natural language prompt

**Parameters**:
```python
{
    "prompt": str,              # Required: Natural language description
    "duration_ms": int,         # Optional: 3000-300000 (3s-5min)
    "output_format": str,       # Optional: Default "mp3_44100_128"
    "save_path": str,           # Optional: Where to save file
    "metadata": dict           # Optional: Tags, mood, context
}
```

**Returns**:
```python
{
    "success": bool,
    "audio_path": str,          # Local file path
    "composition_plan": dict,   # What was actually generated
    "duration_ms": int,
    "metadata": dict,
    "error": str | None
}
```

**Example Usage**:
```python
# Claude Desktop
"Generate lo-fi hip hop beats, chill, 60 BPM, perfect for coding"

# Betty (with context)
"User is frustrated, generate calming ambient piano music, 90 seconds"
```

#### 2. `create_composition_plan`
**Purpose**: Generate structured plan before creating music

**Parameters**:
```python
{
    "prompt": str,              # High-level description
    "total_duration_ms": int,   # Total length desired
    "sections": list[dict],     # Optional: Pre-defined sections
    "mood_progression": str     # Optional: "calm to energetic"
}
```

**Returns**:
```python
{
    "composition_plan": {
        "sections": [
            {
                "style": str,
                "duration_ms": int,
                "mood": str,
                "instruments": list[str],
                "tempo": int,
                "key": str
            }
        ],
        "transitions": list[dict],
        "total_duration_ms": int
    }
}
```

#### 3. `generate_music_structured`
**Purpose**: Generate music from detailed composition plan

**Parameters**:
```python
{
    "composition_plan": dict,   # From create_composition_plan
    "strict_duration": bool,    # Enforce exact section durations
    "save_path": str,
    "metadata": dict
}
```

#### 4. `analyze_mood_for_music`
**Purpose**: Analyze context and suggest appropriate music

**Parameters**:
```python
{
    "context": str,             # Conversation snippet or user state
    "activity": str,            # "coding", "writing", "brainstorming"
    "time_of_day": str,         # Optional: "morning", "evening"
    "recent_music": list[str]   # Optional: Recently generated tracks
}
```

**Returns**:
```python
{
    "suggested_prompt": str,
    "suggested_duration_ms": int,
    "mood_analysis": str,
    "reasoning": str
}
```

#### 5. `generate_journal_entry_with_music`
**Purpose**: Create daily journal + matching soundtrack (Phase 3)

**Parameters**:
```python
{
    "conversation_history": list[dict],  # Recent conversations
    "date": str,                         # ISO format
    "mood_override": str,                # Optional: Force specific mood
    "music_duration_ms": int             # Optional: Default 60000
}
```

**Returns**:
```python
{
    "journal_entry": {
        "date": str,
        "summary": str,
        "key_moments": list[str],
        "overall_mood": str,
        "mood_color": str,          # Hex color code
        "themes": list[str]
    },
    "music": {
        "audio_path": str,
        "prompt_used": str,
        "mood_match": str
    },
    "combined_path": str            # Journal + music stored together
}
```

### File Organization

```
/Users/jeremybradford/Music/ElevenLabs/
├── generated/
│   ├── 2025-11/
│   │   ├── 2025-11-16_focus_coding_001.mp3
│   │   ├── 2025-11-16_calm_ambient_002.mp3
│   │   └── metadata.json
│   └── 2025-12/
├── journal/
│   ├── 2025-11/
│   │   ├── 2025-11-16_entry.json
│   │   ├── 2025-11-16_soundtrack.mp3
│   │   └── 2025-11-16_combined.html
│   └── 2025-12/
├── composition_plans/
│   └── saved_plans/
└── preferences/
    ├── learned_preferences.json
    └── mood_history.json
```

### API Integration Details

**Base URL**: `https://api.elevenlabs.io/v1`

**Authentication**: 
```python
headers = {
    "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
    "Content-Type": "application/json"
}
```

**Key Endpoints**:
1. `POST /music/compose` - Standard generation
2. `POST /music/compose-detailed` - Returns composition plan
3. `POST /music/stream` - Streaming generation (future)

**Error Handling**:
- `bad_prompt` - Contains copyrighted material (use suggestion)
- `bad_composition_plan` - Copyrighted styles (use suggestion)
- Rate limiting - Implement exponential backoff
- Quota exceeded - Clear error message to user

### Configuration

**Environment Variables**:
```bash
ELEVENLABS_API_KEY=sk-...
MUSIC_OUTPUT_DIR=/Users/jeremybradford/Music/ElevenLabs/generated
JOURNAL_OUTPUT_DIR=/Users/jeremybradford/Music/ElevenLabs/journal
ENABLE_PREFERENCE_LEARNING=true
ENABLE_JOURNAL_INTEGRATION=false  # Phase 3
```

**MCP Server Config** (Claude Desktop):
```json
{
  "mcpServers": {
    "elevenlabs-music": {
      "command": "python",
      "args": [
        "/Users/jeremybradford/SyncedProjects/P171_elevenlabs-music-mcp/src/music_mcp_server.py"
      ],
      "env": {
        "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}"
      }
    }
  }
}
```

## 🗓️ Phased Implementation Roadmap

### Phase 1: MVP - Basic Music Generation (4-6 hours)
**Goal**: Functional MCP server that generates music from prompts

**Deliverables**:
- [ ] MCP server scaffold (following Betty MCP pattern)
- [ ] `generate_music_simple` tool implemented
- [ ] ElevenLabs API integration (compose endpoint)
- [ ] File management (save to organized directories)
- [ ] Basic error handling
- [ ] Claude Desktop configuration
- [ ] Simple testing script
- [ ] README with setup instructions

**Acceptance Criteria**:
- "Claude, generate upbeat music for 30 seconds" → Works
- Files saved with proper naming convention
- Errors handled gracefully
- Composition plan captured in metadata

---

### Phase 2: Enhanced Generation & Context Awareness (3-4 hours)
**Goal**: Sophisticated music generation with composition plans

**Deliverables**:
- [ ] `create_composition_plan` tool
- [ ] `generate_music_structured` tool
- [ ] `analyze_mood_for_music` tool (basic version)
- [ ] Mood detection from text (sentiment analysis)
- [ ] Template-based composition plans
- [ ] Preference storage system (JSON-based)- [ ] Betty-specific context integration hooks
- [ ] Multiple output format support

**Acceptance Criteria**:
- Complex multi-section compositions work
- Betty can suggest music based on conversation tone
- Mood analysis provides reasonable suggestions
- Preference system captures user feedback

**Advanced Features to Explore**:
- Detect frustration markers (swearing, terse responses) → Auto-suggest calming music
- Time-of-day awareness (energizing morning, calming evening)
- Activity detection (coding vs writing vs brainstorming)

---

### Phase 3: Journal Integration (4-5 hours)
**Goal**: Automated daily journaling with custom soundtracks

**Deliverables**:
- [ ] `generate_journal_entry_with_music` tool
- [ ] Conversation history analysis (via Betty Memory MCP)
- [ ] Daily synthesis prompts
- [ ] Mood extraction from conversations
- [ ] Music generation matching journal mood
- [ ] Combined HTML output (journal + embedded audio)
- [ ] Journal search interface (by mood, theme, date)
- [ ] Scheduled automation (evening journal generation)

**Acceptance Criteria**:
- End of day → Journal entry generated automatically
- Music matches journal mood accurately
- Journal entries are readable and meaningful
- Search and retrieval system works
- Timeline view of emotional journey

**Journal Entry Structure**:
```markdown
# Journal Entry - November 16, 2025

## Mood: Focused Determination
*Color: Deep Blue with Golden Highlights*

## Summary
Today was marked by intense technical problem-solving. Significant 
progress on the SADB pipeline despite frustration with phantom leads 
investigation. Exciting breakthrough with ElevenLabs Music MCP concept.

## Key Moments
- Morning: Deep work on SADB knowledge extraction
- Midday: Frustrating stakeholder meeting about analytics
- Afternoon: Creative collaboration with Claude on music system
- Evening: Satisfied with progress, planning tomorrow

## Themes
- Technical mastery
- Creative collaboration
- Persistence through obstacles

## Soundtrack
*Generated: 90 seconds of contemplative piano with subtle electronic 
elements, reflecting the blend of analytical work and creative thinking*

[Audio Player: 2025-11-16_soundtrack.mp3]
```

---

### Phase 4: Intelligence & Learning (3-4 hours)
**Goal**: System learns preferences and anticipates needs

**Deliverables**:
- [ ] Preference learning from implicit feedback (track completions, skips)
- [ ] Music history analysis
- [ ] Pattern detection (music preferences by context)
- [ ] Proactive suggestions
- [ ] A/B testing framework for prompts
- [ ] Recommendation engine

**Acceptance Criteria**:
- System suggests increasingly accurate music over time
- "Betty, surprise me" → Generates contextually appropriate music
- Preference dashboard shows learning progress
- Music diversity maintained (avoid filter bubble)

**Learning Signals**:
- Track completion rate
- Re-generation requests
- Explicit ratings (optional)
- Context patterns (time of day, activity, mood)

---

### Phase 5: Advanced Features (Future / Free Time)
**Goal**: Polish and extend functionality

**Potential Features**:
- [ ] Playlist generation (series of related tracks)
- [ ] Music editing tools (extend, remix, combine)
- [ ] Collaborative filtering (if multi-user)
- [ ] Voice control integration (via Whisper MCP)
- [ ] Ableton Live integration (import generated tracks)
- [ ] Music visualization generation
- [ ] Sharing capabilities (export journal + music)
- [ ] API for external tools
- [ ] Mobile app integration
- [ ] Real-time mood tracking with music adaptation

---

## 🎯 Minimum Viable Product (MVP) Scope

For Claude Code Web credit optimization, focus on **Phase 1 completion**:

### Must Have (Phase 1)
1. Working MCP server
2. Simple music generation from prompts
3. File management
4. Claude Desktop integration
5. Basic error handling
6. Documentation

### Nice to Have (Phase 2 if time permits)
1. Composition plans
2. Basic mood detection
3. Preference storage

### Future Roadmap (Post-credit)
1. Journal integration (Phase 3)
2. Learning system (Phase 4)
3. Advanced features (Phase 5)

---

## 🚀 Quick Start Guide

Once built, the system works like this:

### For Claude Desktop Users
```
You: "Generate music for deep focus work, 2 minutes"
Claude: [Calls generate_music_simple via MCP]
        "Created: /Music/ElevenLabs/generated/2025-11/focus_work_001.mp3
         Lo-fi beats at 70 BPM with gentle piano melodies."
```

### For Betty Users
```
You: "Betty, I'm stressed about this deadline"
Betty: [Analyzes mood, calls analyze_mood_for_music]
       [Calls generate_music_simple with calming parameters]
       "I've made you something calming - gentle ambient soundscape, 
       90 seconds. Let it play while you breathe for a moment. 
       Want to talk about the deadline?"
```

### For Journal Users (Phase 3)
```
System: [Automated at 9 PM]
        [Analyzes day's conversations via Betty Memory]
        [Generates journal entry]
        [Creates matching music]
        "Today's journal is ready. You had a productive day with 
        some frustrating moments. The soundtrack reflects your 
        resilience. Want to review it?"
```

---

## 🛡️ Risk Mitigation

### Technical Risks
1. **API Rate Limits**: Implement request queuing and rate limiting
2. **API Costs**: Track usage, implement cost limits per day
3. **Large File Storage**: Regular cleanup, compression options
4. **Copyright Issues**: Strict prompt filtering, use API suggestions

### User Experience Risks
1. **Poor Music Quality**: Allow regeneration, capture feedback
2. **Irrelevant Suggestions**: Start conservative, learn over time
3. **Privacy Concerns**: Keep all data local, clear data policies

### Integration Risks
1. **MCP Protocol Changes**: Monitor Anthropic updates
2. **API Changes**: Version pinning, graceful degradation
3. **Betty Memory Dependency**: Make journal integration optional

---

## 📐 Design Decisions & Rationale

### Why MCP Server vs Direct Integration?
- **Reusability**: Any agent can use it
- **Separation of Concerns**: Music logic isolated
- **Testability**: Can test without full agent setup
- **Future-Proof**: Easy to add new clients

### Why Local File Storage vs Streaming?
- **Reliability**: Files persist, can replay
- **Metadata**: Easy to attach context and tags
- **Integration**: Simpler integration with other tools
- **Journal Use Case**: Need permanent storage for journal soundtracks

### Why JSON Preferences vs Database?
- **Simplicity**: MVP doesn't need database overhead
- **Portability**: Easy to backup and sync
- **Git-Friendly**: Can version control preferences
- **Upgrade Path**: Easy migration to DB later if needed

### Why Separate Journal System vs Extend Betty Memory?
- **Focus**: Music generation is core, journal is enhancement
- **Independence**: System useful without journal feature
- **Complexity Management**: Phased development
- **Reusability**: Journal system could work with other memory backends

---

## 🔧 Development Guidelines

### Code Standards
- Follow Betty MCP server patterns
- Type hints for all functions
- Comprehensive docstrings
- Error handling with informative messages
- Logging at appropriate levels

### Testing Strategy
- Unit tests for each MCP tool
- Integration tests with mock ElevenLabs API
- End-to-end tests with Claude Desktop
- Manual testing with Betty (when available)

### Documentation Requirements
- README with quick start
- API documentation for each tool
- Configuration examples
- Troubleshooting guide
- Architecture diagrams (if needed)

---

## 📚 Resources & References

### ElevenLabs Music API
- Quickstart: https://elevenlabs.io/docs/cookbooks/music/quickstart
- API Reference: https://elevenlabs.io/docs/api-reference/music/compose
- Composition Plans: https://elevenlabs.io/docs/cookbooks/music/quickstart#composition-plans

### MCP Protocol
- Specification: https://modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Examples: Betty MCP Server (P033_resonance-prime)

### Related Projects
- P033_resonance-prime: Betty Memory MCP (reference implementation)
- P050_ableton-mcp: Ableton Live integration (future crossover)
- P167_dj-claude-mcp: DJ Claude (potential collaboration)

---

## 💡 Innovation Opportunities

### Unique Features to Explore
1. **Emotion-Reactive Music**: Real-time mood adaptation
2. **Musical Conversations**: Music responds to dialogue tone
3. **Semantic Music Search**: "Find music like that time I was..."
4. **Music as Memory Anchor**: Sonic bookmarks for important moments
5. **Collaborative Music**: Multi-agent musical dialogues
6. **Therapeutic Applications**: Mood regulation through music
7. **Productivity Research**: Correlate music with work output
8. **Personal Soundtrack**: Life's background music, curated by AI

### Research Questions
- How does AI-generated music impact focus and productivity?
- Can music preferences predict emotional states?
- What makes a "good" journal soundtrack?
- How does personalized music evolve over time?

---

## 🎓 Learning Goals

Through this project, you'll gain experience with:
- MCP server development
- API integration (ElevenLabs)
- File management and organization
- Context-aware AI systems
- Music generation and composition
- Sentiment analysis
- Preference learning algorithms
- Journal entry generation
- Agent-to-agent communication

---

## 🔮 Vision: Where This Could Go

Imagine a year from now:

- Wake up → Morning music matches your energy level and calendar
- During work → Music adapts to task complexity and stress
- Breakthroughs → Celebratory soundtracks mark achievements
- Frustration → Calming interventions automatically offered
- Evening → Reflective music accompanies daily journal
- Weekends → Creative or energizing soundscapes for hobbies
- Year-end → Musical retrospective of your emotional journey

Your AI agents don't just understand you—they soundtrack your life.

---

## 📞 Support & Questions

When working with Claude Code Web:
- Start with Phase 1 MVP
- Document any API limitations encountered
- Note integration challenges for future sessions
- Return to Jeremy's Claude instance for architectural questions
- Save detailed logs of what worked / didn't work

**Key Questions to Answer During Development**:
1. What's the actual API response time?
2. Are there undocumented API limits?
3. How good are the generated composition plans?
4. What file sizes are we dealing with?
5. How should metadata be structured for future search?

---

## ✅ Pre-Development Checklist

Before starting Claude Code Web session:

- [ ] ElevenLabs API key obtained and tested
- [ ] Output directories created
- [ ] Repository cloned to Claude Code Web workspace
- [ ] Python environment ready (requirements.txt)
- [ ] MCP SDK installed
- [ ] Claude Desktop config template ready
- [ ] Test prompts prepared
- [ ] Success criteria defined

---

## 🎉 Success Celebration Criteria

**Phase 1 Complete When:**
- You speak to Claude: "Generate me some jazz" → Music appears
- Betty suggests music when you're stressed → It actually helps
- First journal entry + soundtrack → You smile at the beauty

**Ultimate Success:**
- One year of daily journal entries with soundtracks
- You look back and *hear* your journey
- The music captures moments you'd forgotten
- Your AI agents truly understand your emotional landscape

---

*This project isn't just about generating music. It's about creating an emotional memory system, a sonic journal of your life, and a deeply personalized AI experience. Let's build something beautiful.*

---

**Next Steps**: 
1. Review this PRD
2. Clone repo to Claude Code Web
3. Start with Phase 1 implementation
4. Return with questions or celebrate first working prototype! 🎵