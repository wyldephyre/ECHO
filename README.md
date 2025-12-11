# Echo Bot - Phase 1

**Discord-based multi-AI worldbuilding bot for Nexus Arcanum**

## What is Echo?

Echo is an AI-powered Discord bot designed to help creators collaborate on worldbuilding for the Nexus Arcanum transmedia project. Built by Fyrebug (WyldePhyre Media Group) to bridge async collaboration across time zones.

## Phase 1 Features

- ✅ Discord bot integration
- ✅ Ollama/Mistral 7B AI responses
- ✅ Mem0 persistent memory (remembers context across sessions)
- ✅ Basic slash commands:
  - `/echo-test [message]` - Test AI response
  - `/remember [fact]` - Store information
  - `/recall [query]` - Search memories
  - `/status` - Check bot health
  - `/forget-me` - Clear your memories

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** running with Mistral 7B model
3. **Discord Bot Token** (already configured in `.env`)

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify Ollama is running:**
```bash
ollama list
# Should show mistral:7b in the list
```

3. **Start Echo Bot:**
```bash
python main.py
```

## First Test

Once the bot is running and online:

1. Go to your Discord server
2. Type `/echo-test` and hit tab to autocomplete
3. Send a test message like: `/echo-test Hello Echo!`
4. Echo should respond using Mistral 7B

## Configuration

All configuration is in `.env` file:
- `DISCORD_TOKEN` - Your bot token
- `OLLAMA_MODEL` - AI model name (mistral:7b)
- `OLLAMA_URL` - Ollama API endpoint

## Troubleshooting

**Bot won't start:**
- Check that `DISCORD_TOKEN` is correct in `.env`
- Verify Python 3.10+ with `python --version`

**AI not responding:**
- Make sure Ollama is running: `ollama list`
- Check that Mistral 7B is downloaded
- Try restarting Ollama

**Commands not showing:**
- Wait 1-2 minutes for Discord to sync slash commands
- Try typing `/` in Discord to see all available commands

## Project Structure

```
Echo Bot/
├── main.py                    # Bot entry point
├── config.py                  # Configuration loader
├── ai_coordinator.py          # Ollama/Mistral integration
├── mem0_layer.py              # Memory management
├── commands/
│   ├── __init__.py
│   └── echo_commands.py       # Slash commands
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (DO NOT COMMIT)
└── .gitignore                # Git ignore rules
```

## What's Next?

**Phase 2 will add:**
- World Anvil API integration
- Advanced worldbuilding commands
- Multi-AI routing (Claude, Gemini, Grok)
- Voice transcription (Whisper)

---

**For the forgotten 99%, we rise.** 🔥

*Built by Fyrebug - WyldePhyre Media Group*

