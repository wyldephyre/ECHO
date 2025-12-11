"""
Echo Bot - Slash Commands
Multi-AI commands for Discord integration
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from ai_coordinator import ai_coordinator
from mem0_layer import echo_memory

logger = logging.getLogger(__name__)

class EchoCommands(commands.Cog):
    """Echo bot commands - Multi-AI enabled"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def _send_response(self, interaction: discord.Interaction, response: str):
        """Helper to send responses, handling Discord's 2000 char limit"""
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            await interaction.followup.send(response)
    
    # =========================================================================
    # MISTRAL (LOCAL) - Default AI
    # =========================================================================
    @app_commands.command(name="echo", description="Ask Echo (Mistral) - Local AI")
    async def echo(self, interaction: discord.Interaction, message: str):
        """Default AI command using local Mistral"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            response = await ai_coordinator.ask_mistral(
                prompt=message,
                user_id=user_id,
                use_memory=True
            )
            await self._send_response(interaction, f"**Mistral:**\n{response}")
            logger.info(f"Echo command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in echo: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # CLAUDE (ANTHROPIC) - Deep reasoning
    # =========================================================================
    @app_commands.command(name="ask-claude", description="Ask Claude - Deep reasoning & worldbuilding")
    async def ask_claude(self, interaction: discord.Interaction, message: str):
        """Claude for deep reasoning and detailed responses"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            response = await ai_coordinator.ask_claude(
                prompt=message,
                user_id=user_id,
                use_memory=True
            )
            await self._send_response(interaction, f"**Claude:**\n{response}")
            logger.info(f"Ask-claude command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in ask-claude: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # GROK (X.AI) - Unique perspective
    # =========================================================================
    @app_commands.command(name="ask-grok", description="Ask Grok - Unique perspective & humor")
    async def ask_grok(self, interaction: discord.Interaction, message: str):
        """Grok for different perspectives and current info"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            response = await ai_coordinator.ask_grok(
                prompt=message,
                user_id=user_id,
                use_memory=True
            )
            await self._send_response(interaction, f"**Grok:**\n{response}")
            logger.info(f"Ask-grok command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in ask-grok: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # GEMINI (GOOGLE) - Fast multi-modal
    # =========================================================================
    @app_commands.command(name="ask-gemini", description="Ask Gemini - Fast responses")
    async def ask_gemini(self, interaction: discord.Interaction, message: str):
        """Gemini for fast, multi-modal responses"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            response = await ai_coordinator.ask_gemini(
                prompt=message,
                user_id=user_id,
                use_memory=True
            )
            await self._send_response(interaction, f"**Gemini:**\n{response}")
            logger.info(f"Ask-gemini command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in ask-gemini: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # MEMORY COMMANDS
    # =========================================================================
    @app_commands.command(name="remember", description="Store a fact in Echo's memory")
    async def remember(self, interaction: discord.Interaction, fact: str):
        """Store a fact in Mem0"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            success = await echo_memory.store_memory(
                user_id=user_id,
                content=fact,
                metadata={"type": "manual_fact", "source": "remember_command"}
            )
            
            if success:
                await interaction.followup.send(f"Remembered: *{fact}*")
            else:
                await interaction.followup.send("Failed to store memory. Check logs.")
            
            logger.info(f"Remember command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in remember: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="recall", description="Search Echo's memory")
    async def recall(self, interaction: discord.Interaction, query: str):
        """Search stored memories"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            memories = await echo_memory.search_memory(
                user_id=user_id,
                query=query,
                limit=5
            )
            
            if not memories:
                await interaction.followup.send(f"No memories found for: *{query}*")
                return
            
            response = f"**Memories matching '{query}':**\n\n"
            for idx, mem in enumerate(memories, 1):
                memory_text = mem.get('memory', mem.get('text', 'No content'))
                response += f"{idx}. {memory_text}\n\n"
            
            await self._send_response(interaction, response)
            logger.info(f"Recall command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in recall: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="forget-me", description="Clear all your memories from Echo")
    async def forget_me(self, interaction: discord.Interaction):
        """Clear all user memories"""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            success = await echo_memory.clear_user_memory(user_id)
            
            if success:
                await interaction.followup.send("All your memories have been cleared.")
            else:
                await interaction.followup.send("Failed to clear memories. Check logs.")
            
            logger.info(f"Forget-me command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in forget-me: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # STATUS & INFO
    # =========================================================================
    @app_commands.command(name="status", description="Check Echo's status and available AIs")
    async def status(self, interaction: discord.Interaction):
        """Display bot status and AI availability"""
        await interaction.response.defer()
        
        try:
            # Test local AI
            ai_connected, ai_msg = await ai_coordinator.test_connection()
            
            # Get available AIs
            available_ais = ai_coordinator.get_available_ais()
            
            # Get user's memory count
            user_id = str(interaction.user.id)
            user_memories = await echo_memory.get_user_context(user_id, limit=100)
            memory_count = len(user_memories)
            
            # Build status message
            status_msg = "**Echo Bot Status**\n\n"
            status_msg += f"**Discord:** Connected\n"
            status_msg += f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
            status_msg += f"**Your Memories:** {memory_count} stored\n\n"
            
            status_msg += "**AI Providers:**\n"
            for ai_name, info in available_ais.items():
                icon = "[ON]" if info['available'] else "[OFF]"
                ai_type = info['type'].upper()
                status_msg += f"{icon} **{ai_name.capitalize()}** ({ai_type}) - {info['model']}\n"
            
            status_msg += f"\n**Local AI Test:** {ai_msg}"
            
            await interaction.followup.send(status_msg)
            logger.info(f"Status command by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in status: {e}")
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    """Setup function to add cog to bot"""
    await bot.add_cog(EchoCommands(bot))
