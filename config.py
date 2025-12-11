"""
Echo Bot Configuration Loader
Loads environment variables and provides centralized config access
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Echo Bot"""
    
    # Discord Settings
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Ollama Settings (Local AI - Mistral)
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Mem0 Settings
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    MEM0_STORAGE_PATH = os.getenv("MEM0_STORAGE_PATH", "./mem0_data")
    
    # External AI API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Claude
    XAI_API_KEY = os.getenv("XAI_API_KEY")              # Grok
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")        # Gemini
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration values"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN not found in .env file")
        
        # Create Mem0 storage directory if it doesn't exist
        Path(cls.MEM0_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        
        return True

# Validate config on import
Config.validate()

