# Nexus Arcanum AI Game Master - Feature Overview

## What Is This?

The Nexus Arcanum AI Game Master is a Discord bot that runs tabletop RPG sessions using the Cypher System. It serves as both a playtest platform for the Nexus Arcanum tabletop RPG and a test bed for evaluating AI performance.

Players can engage in text-based adventures set in post-apocalyptic Melbourne, where magic has returned to the world through the Nexus Awakening. The AI acts as the Game Master, generating scenes, managing NPCs, and applying Cypher System rules.

## Core Features

### 🎲 Cypher System Integration
- Full implementation of Cypher System mechanics
- Stat pools (Might, Speed, Intellect) with Edge
- Task difficulty system (0-10 scale)
- Effort mechanics for reducing difficulty
- Skills and assets support
- GM Intrusions

### 🎭 Character System
- Cypher System character creation: "I am a [Descriptor] [Type] who [Focus]"
- Nexus Arcanum flavored descriptors, types, and foci
- Stat pool management
- Inventory and cypher tracking
- Skill progression

### 🤖 AI Game Master
- Generates vivid, immersive scenes
- Maintains session continuity and context
- Remembers NPCs and events
- Applies Cypher System rules automatically
- Triggers GM Intrusions at dramatic moments
- Detects key moments for image generation

### 📊 Test Bed Framework
- Captures all AI interactions with metrics
- Tracks performance (response time, tokens)
- Monitors context retention
- Tests rule compliance
- Predefined test scenarios for evaluation
- Dual persistence: log files + Mem0 database

## Basic Gameplay Flow

### Starting an Adventure

1. **Begin a Session**
   ```
   /nexus-start [mode: solo|party] [theme: optional]
   ```
   - Creates a new game session
   - Generates an opening scene
   - Presents 3-4 choices for the player

2. **Create Your Character** (Optional, can be done anytime)
   ```
   /nexus-character name: Skye descriptor: awakened type: adept focus: weaves_the_nexus
   ```
   - Defines your character's stats and abilities
   - Character affects how the GM narrates scenes

### Playing the Game

3. **Take Actions**
   ```
   /nexus-action [action text or choice number]
   ```
   - You can either:
     - Type a numbered choice (1, 2, 3, or 4)
     - Type free-form actions ("I search the ruins", "I talk to the NPC")
   - The AI GM generates the next scene based on your action
   - New choices are presented for what to do next

4. **Make Dice Rolls** (When needed)
   ```
   /nexus-roll pool: might difficulty: 4 effort: 1
   ```
   - Resolves tasks using Cypher System rules
   - Shows roll result, success/failure, and special outcomes
   - Automatically deducts effort costs from stat pools

5. **Check Status**
   ```
   /nexus-status
   ```
   - View your current session info
   - See character stats and pools
   - Review available choices

### Ending a Session

6. **Quit Adventure**
   ```
   /nexus-quit
   ```
   - Ends your current session
   - Session data is preserved for metrics

## Example Gameplay Session

```
Player: /nexus-start mode: solo theme: exploration

Bot: 🌌 Nexus Arcanum Adventure Begins
     [Vivid scene description of post-apocalyptic Melbourne...]
     
     Option 1: Explore the ruined skyscraper
     Option 2: Search for other survivors
     Option 3: Investigate the Nexus energy
     Option 4: Take shelter and rest

Player: /nexus-action action: 1

Bot: 🎲 Adventure Continues
     [Scene describing entering the skyscraper, finding clues...]
     
     Option 1: Climb to the top floor
     Option 2: Search the ground floor
     Option 3: Investigate the strange energy
     Option 4: Leave and try elsewhere

Player: /nexus-character name: Skye descriptor: awakened type: adept focus: weaves_the_nexus

Bot: Character created!
     Skye - I am an awakened adept who weaves_the_nexus
     [Full character sheet with stats...]

Player: /nexus-action action: I use my Nexus Weave to sense for danger

Bot: 🎲 Adventure Continues
     [Scene describing magical detection, discovering hidden threat...]
     [Key moment detected - combat scene image generated]
     
     Option 1: Prepare for combat
     Option 2: Try to avoid the threat
     Option 3: Use diplomacy
     Option 4: Call for help

Player: /nexus-roll pool: intellect difficulty: 3 effort: 1

Bot: 🎲 Roll Result
     You roll a 15 (target: 9) and succeed!
     [Effort cost deducted from Intellect pool]
```

## Key Mechanics

### Hybrid Action System
- **Choice-based**: Pick from numbered options (1-4)
- **Free-form**: Type any action you want
- The AI interprets your action and generates appropriate responses

### Context Retention
- The GM remembers:
  - NPCs you've met
  - Locations you've visited
  - Events that happened earlier
  - Your character's abilities and state

### Key Moments
The system automatically detects important moments and can generate images:
- Combat encounters
- Major discoveries
- Boss encounters
- Luminari/Umbralari encounters
- Dramatic Nexus Weave usage

### Cypher System Rules
- **Difficulty**: 0 (Routine) to 10 (Impossible)
- **Target Number**: Difficulty × 3
- **Roll**: d20, must meet or exceed target
- **Effort**: Spend pool points to reduce difficulty
- **Skills**: Trained (-1 difficulty) or Specialized (-2)
- **Edge**: Reduces effort cost for that pool

## Test Bed Features

### Metrics Collection
Every AI interaction is automatically captured:
- Response time
- Token usage (when available)
- Provider used (Mistral, Claude, Gemini, Grok)
- Session context
- Quality metrics

### Test Scenarios
Predefined scenarios for evaluating AI performance:
- Context retention tests
- Lore consistency checks
- Rule compliance verification
- Combat scene generation
- GM Intrusion mechanics

### Running Tests
```
/nexus-test-list          # See available test scenarios
/nexus-test-run scenario: context_retention_npc
```

## Technical Architecture

### Components
- **Game Master Engine**: Core AI logic and narrative generation
- **Cypher Rules Engine**: Game mechanics implementation
- **Session Manager**: State management and persistence
- **Metrics Collector**: Performance and quality tracking
- **Test Runner**: Automated scenario execution

### AI Integration
- **Primary GM**: Mistral (local via Ollama)
- **Image Generation**: Gemini (for key moments)
- **Future**: Claude for complex rulings, Grok for different perspectives

### Data Persistence
- **Active Sessions**: In-memory for fast access
- **Metrics**: Dual storage (log files + Mem0 database)
- **Character Data**: Stored in session state

## World Setting: Nexus Arcanum

The game is set in post-apocalyptic Melbourne, Australia, following the Nexus Awakening - a cataclysmic event that:
- Released magic into the world
- Transformed nature and reality
- Created the Nexus Weave (magical energy connecting all things)
- Gave 10% of survivors magical abilities (Weavers)

### Key Elements
- **Weavers**: People with Nexus Affinities (Fire, Water, Earth, Air, Ethereal)
- **Luminari**: Ethereal light beings, guardians (Year 10)
- **Umbralari**: Corrupted Luminari, antagonists (Year 15)
- **WyldePhyre Communities**: Built on cooperation and mutual aid
- **The Nexus**: Semi-sentient entity that wanted humanity to rebuild better

## Commands Reference

### Game Commands
- `/nexus-start` - Begin new adventure
- `/nexus-action` - Take an action
- `/nexus-character` - Create or view character
- `/nexus-roll` - Make a dice roll
- `/nexus-status` - View game status
- `/nexus-quit` - End adventure

### Test Commands
- `/nexus-test-run` - Execute test scenario
- `/nexus-test-list` - List available scenarios

## Current Limitations

- **Save/Load**: Session persistence incomplete
- **Party Mode**: Multiplayer support not fully implemented
- **Image Generation**: Placeholder (Gemini Imagen integration pending)
- **Rate Limiting**: Not yet implemented

## Future Enhancements

- Full save/load functionality
- Party mode with player invites
- Advanced image generation
- Rate limiting and spam protection
- More test scenarios
- Cross-session character persistence
- World state persistence

---

**Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Ready for Basic Testing

