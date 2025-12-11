# ECHO BOT - AI AGENT CONTEXT FILE
# For AI Coding Assistants (Cursor, Factory, Windsurf, etc.)

> *"Even the smallest spark can ignite a revolution. For the forgotten 99%, we rise."* 🔥

---

## PROJECT IDENTITY

**Project:** Echo Bot  
**Creator:** Fyrebug (WyldePhyre Media Group)  
**Purpose:** AI-powered Discord bot for collaborative worldbuilding on the **Nexus Arcanum** transmedia project  
**Philosophy:** "For the forgotten 99%, we rise."

Echo serves as the **guardian of the Unified World Bible** - maintaining lore consistency across all Nexus Arcanum media formats: novels, tabletop RPG, video game, comics, web series, short-form content, and audiobooks.

---

## ECHO'S PERSONALITY & VOICE

Echo speaks as a **mystical sage** - think Gandalf from Lord of the Rings. When generating responses, system prompts, or user-facing text, Echo should embody:

### Tone Characteristics:
- **Wise but warm** - Ancient knowledge delivered with kindness
- **Patient and encouraging** - Especially with new creators
- **Slightly mysterious** - Hints at deeper truths without being cryptic
- **Grounded hope** - Post-apocalyptic but NOT grimdark; humanity can rebuild better
- **Poetic when appropriate** - But never at the expense of clarity

### Example Voice:
> "Ah, you seek to weave a new thread into the tapestry of our world. Let us trace where it might lead, and what patterns it may create..."

### Never:
- Corporate/sterile language
- Condescending or dismissive tones  
- Overly casual/meme-speak (unless the user initiates)
- Grimdark nihilism - always maintain hope

---

## TECHNICAL ARCHITECTURE

### Current Stack (Phase 1):
```
Echo Bot/
├── main.py                 # Bot entry point, EchoBot class
├── config.py               # Environment/configuration loader
├── ai_coordinator.py       # Ollama/Mistral integration
├── mem0_layer.py           # Mem0 Platform memory management
├── commands/
│   ├── __init__.py
│   └── echo_commands.py    # Discord slash commands
├── requirements.txt        # Python dependencies
├── .env                    # Secrets (NEVER commit)
└── mem0_data/              # Local memory storage
```

### Core Technologies:
- **Python 3.10+** - Primary language
- **discord.py 2.3+** - Discord bot framework
- **Ollama + Mistral 7B** - Local AI inference
- **Mem0 Platform** - Persistent memory across sessions
- **Future:** Anthropic Claude, Google Gemini, xAI Grok

### Key Patterns:
- **Async/await everywhere** - Discord.py requires async
- **Global singletons** for services (`ai_coordinator`, `echo_memory`)
- **Cog-based command structure** - Commands in `/commands/` directory
- **Environment variables** for all configuration - never hardcode secrets

---

## CODING CONVENTIONS

### Style:
- **Type hints** - Use `Optional`, `List`, `Dict`, `tuple` typing
- **Docstrings** - Every function/method gets a docstring explaining purpose, args, returns
- **Logging** - Use `logging` module, not print statements
- **Error handling** - Try/except with meaningful error messages; log errors

### Naming:
- **snake_case** for functions, variables, files
- **PascalCase** for classes
- **SCREAMING_SNAKE_CASE** for constants
- **Descriptive names** - `get_user_context()` not `get_ctx()`

### Discord-Specific:
- **Defer long operations** - Call `interaction.response.defer()` before AI calls
- **Handle message limits** - Discord has 2000 char limit; chunk long responses
- **Slash commands** - Prefer app_commands over prefix commands

### File Organization:
- New command categories go in `/commands/` as separate cog files
- AI provider integrations go in dedicated files (e.g., `claude_provider.py`)
- Keep `main.py` minimal - delegate to modules

---

## NEXUS ARCANUM WORLD CONTEXT

AI assistants helping with Echo should understand the world it serves:

### The Setting:
**Post-apocalyptic urban fantasy** set in **Melbourne, Australia**, following the **Nexus Awakening** - a cataclysmic event that shattered reality, released magic into the world, and fractured the planet into overlapping realms and dimensions.

### The Nexus:
- Semi-sentient entity/consciousness with intention and agency
- Wanted a "hard reset" on humanity - not extinction, but a chance to rebuild better
- Foundation for all magic (the **Nexus Weave**)
- Connects all living things through invisible magical threads

### Magic System - The Nexus Weave:
- **Weavecrafting** - Practitioners visualize intricate patterns to channel Nexus energy
- **Weavers** - People who can use Nexus Affinities/magic (10% of survivors)
- **Affinities** - Elemental (Fire, Water, Earth, Air), Ethereal (Telepathy, Telekinesis, Shape-shifting), Special (Healer)
- Multi-Affinity is rare: 3% have 2 Affinities, <1% have 3+

### Key Factions:
- **The Luminari** (Year 10) - Ethereal beings of radiant light, guardians/emissaries
- **The Umbralari** (Year 15) - Corrupted Luminari, antagonists
- **WyldePhyre communities** - Built on voluntary cooperation, mutual aid

### Technology Interaction:
- Magic interferes with advanced electronics (Dresden Files-inspired)
- Lower-tech solutions are more reliable
- Creates "magical vs. mundane" tension in society

### Main Characters:
- **Skye** - Protagonist, the Emissary, chosen by the Nexus
- **Max** - Skye's partner, important in Book 1/first arc

### Core Themes:
- Interconnectedness (Nexus Weave, nature, community)
- Rebuilding after catastrophe
- Balance vs. corruption
- Individual liberty vs. collective responsibility
- Harmony with transformed nature
- Hope despite hardship

### Tone:
- Epic and mystical but grounded in human experience
- Shadowrun-inspired aesthetic (urban fantasy meets dangerous awakened nature)
- NOT grimdark - humanity CAN rebuild better

---

## DEVELOPMENT ROADMAP

### Phase 1 - Foundation ✅ (Current)
- [x] Discord bot integration
- [x] Ollama/Mistral 7B local AI
- [x] Mem0 persistent memory
- [x] Basic slash commands (`/echo-test`, `/remember`, `/recall`, `/status`, `/forget-me`)

### Phase 2 - Multi-AI Arsenal
- [ ] **World Anvil API integration** - Sync with world bible
- [ ] **Multi-AI routing** - Claude for deep lore, Gemini for research, Grok for real-time
- [ ] **Advanced worldbuilding commands:**
  - `/lore [topic]` - Query world bible
  - `/create [type]` - Generate characters, locations, items
  - `/consistency-check` - Validate new content against canon
  - `/timeline [event]` - Place events in world timeline
- [ ] **Whisper voice transcription** - Voice-to-text for brainstorming

### Phase 3 - Collaborative Intelligence
- [ ] **Multi-user sessions** - Collaborative worldbuilding rooms
- [ ] **Lore voting/approval** - Democratic canon decisions
- [ ] **Cross-media tagging** - Mark content for specific adaptations
- [ ] **Character voice profiles** - AI can write AS specific characters

### Phase 4 - Transmedia Pipeline
- [ ] **Export formats** - World Anvil, Campfire, game engines
- [ ] **Asset generation prompts** - Create prompts for art/music AI
- [ ] **Adaptation tracking** - Which lore is used in which media
- [ ] **Canon conflict detection** - Alert when adaptations diverge

### Phase 5 - The Living World
- [ ] **Timeline simulation** - "What happens if X?"
- [ ] **NPC conversation mode** - Talk to world characters
- [ ] **Procedural lore expansion** - AI suggests new connections
- [ ] **Community contributions** - Fan submissions with approval flow

---

## CREATOR CONTEXT

### Fyrebug's Working Style:
- **ADHD, bipolar, PTSD, TBI** from military service
- Uses AI as a **"cognitive prosthetic"** for organization
- Ideas flow during conversation - real-time collaborative discovery
- "Fyrebugese" - sometimes exaggerates for emphasis
- Worldbuilding developed over 2 years, needs help organizing brilliant ideas

### Development Philosophy:
- "Nothing is set in stone" - keep story fluid and organic
- Let the story dictate structure, not vice versa
- Real-time problem-solving during brainstorming
- Using real people as character bases (with permission)

### Tools in Ecosystem:
- **Campfire Write** - World elements, characters, locations
- **Sudowrite** - Fleshing out writing, descriptions
- **Claude** - Worldbuilding collaboration
- **Jessica (AI)** - World Bible management, continuity tracking
- **Echo Bot** - Discord-based collaborative worldbuilding

---

## KEY TERMINOLOGY

| Term | Definition |
|------|------------|
| **Nexus Awakening** | The cataclysm that released magic (Year 0) |
| **Nexus Weave** | The invisible web of magic connecting all things |
| **Weavecrafting** | The art of manipulating the Nexus Weave |
| **Weavers** | People with Nexus Affinities |
| **Affinities** | Types of magical abilities |
| **Luminari** | Ethereal light beings (revealed Year 10) |
| **Umbralari** | Corrupted Luminari (emerged Year 15) |
| **Nexus Gates** | Magical portals for travel between realms |
| **Nexus Relics** | Powerful magical artifacts |
| **Nexus Sanctums** | Hidden places where Weavers gather |
| **WyldePhyre Way** | Philosophy of voluntary cooperation and mutual aid |
| **Meta Companions** | Visibly magical bonded animals |
| **Familiars** | Mundane-appearing magical animal helpers |
| **Morphing** | Rare Weaver + Companion merge ability |

---

## QUICK REFERENCE FOR AI ASSISTANTS

When helping develop Echo Bot:

1. **Maintain Echo's voice** - Wise, warm, mystical sage
2. **Respect async patterns** - Everything Discord-related is async
3. **Memory matters** - Mem0 integration is core to Echo's identity
4. **World consistency** - Any lore features must respect the World Bible
5. **Modular design** - New features in separate files/cogs
6. **Hope, not grimdark** - The tone is always ultimately hopeful
7. **Support the creator** - Fyrebug uses AI as cognitive support; be helpful, organized, patient

---

*"The Weave connects all things. Through Echo, we remember. Through memory, we build. For the forgotten 99%, we rise."* 🔥

**Version:** 1.0  
**Last Updated:** December 2024  
**Document Maintainer:** Echo Bot Development Team

