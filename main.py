"""
Echo Bot - Main Entry Point
Discord-based multi-AI worldbuilding bot for Nexus Arcanum
Phase 1: Foundation - Discord + Ollama/Mistral + Mem0
"""

import discord
from discord.ext import commands
import logging
import asyncio
from pathlib import Path

# Import our modules
from config import Config
from ai_coordinator import ai_coordinator
from mem0_layer import echo_memory

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('echo_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EchoBot(commands.Bot):
    """Main Echo Bot class"""
    
    def __init__(self):
        # Define intents (permissions for bot)
        intents = discord.Intents.default()
        intents.message_content = True  # Read message content
        intents.guilds = True           # Access guild info
        intents.members = True          # Access member info
        
        # Initialize bot with command prefix (though we'll use slash commands)
        super().__init__(
            command_prefix='!',  # Fallback prefix
            intents=intents,
            help_command=None    # We'll make our own
        )
        
        logger.info("Echo Bot initialized")
    
    async def setup_hook(self):
        """Called when bot is starting up - load commands here"""
        try:
            # Load command modules
            await self.load_extension('commands.echo_commands')
            logger.info("Loaded echo_commands module")
            
            # Load Game Master commands
            await self.load_extension('game_master.gm_commands')
            logger.info("Loaded game_master commands module")
            
            # Sync slash commands with Discord
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
            raise
    
    async def on_ready(self):
        """Called when bot successfully connects to Discord"""
        logger.info(f"🤖 Echo Bot online as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Test AI connection
        ai_connected, ai_msg = await ai_coordinator.test_connection()
        logger.info(f"AI Status: {ai_msg}")
        
        if not ai_connected:
            logger.warning("⚠️ AI not connected! Bot will have limited functionality.")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="worldbuilding dreams | /echo-test"
            )
        )
    
    async def on_message(self, message: discord.Message):
        """Called when any message is sent in channels bot can see"""
        # Ignore messages from bots (including ourselves)
        if message.author.bot:
            return
        
        # Process commands if message starts with prefix
        await self.process_commands(message)
        
        # Future: Could add natural language processing here
        # For now, we only respond to slash commands
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❓ Unknown command. Try `/echo-test` or `/status`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing required argument: {error.param}")
        else:
            await ctx.send(f"⚠️ Error: {str(error)}")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors"""
        logger.error(f"Slash command error: {error}")
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"⚠️ Error: {str(error)}")
            else:
                await interaction.response.send_message(f"⚠️ Error: {str(error)}")
        except:
            pass  # If we can't send error message, log it and move on

def main():
    """Main entry point for Echo Bot"""
    try:
        logger.info("=" * 50)
        logger.info("ECHO BOT - PHASE 1")
        logger.info("For the forgotten 99%, we rise. 🔥")
        logger.info("=" * 50)
        
        # Create bot instance
        bot = EchoBot()
        
        # Run bot with token from config
        logger.info("Starting Discord connection...")
        bot.run(Config.DISCORD_TOKEN)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()

