"""
Nexus Arcanum Game Master Discord Commands
Slash commands for playing the tabletop RPG
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import uuid

from game_master.gm_engine import gm_engine
from game_master.session_state import session_manager
from game_master.character import CharacterBuilder, Character
from game_master.scene_images import image_generator
from test_bed.test_runner import test_runner
from test_bed.test_scenarios import list_scenarios

logger = logging.getLogger(__name__)

class GameMasterCommands(commands.Cog):
    """Game Master commands for Nexus Arcanum RPG"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def _send_response(self, interaction: discord.Interaction, response: str, embed: Optional[discord.Embed] = None):
        """Helper to send responses, handling Discord's 2000 char limit"""
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            if embed:
                await interaction.followup.send(chunks[0], embed=embed)
            else:
                await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            if embed:
                await interaction.followup.send(response, embed=embed)
            else:
                await interaction.followup.send(response)
    
    # =========================================================================
    # GAME COMMANDS
    # =========================================================================
    
    @app_commands.command(name="nexus-start", description="Begin a new Nexus Arcanum adventure")
    @app_commands.describe(
        mode="Game mode: solo or party",
        theme="Optional theme for the adventure"
    )
    @app_commands.choices(mode=[
        app_commands.Choice(name="Solo", value="solo"),
        app_commands.Choice(name="Party", value="party")
    ])
    async def nexus_start(
        self,
        interaction: discord.Interaction,
        mode: str = "solo",
        theme: Optional[str] = None
    ):
        """Start a new game session"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            # Check if user already has an active session
            existing_session = session_manager.get_session_for_user(user_id, channel_id)
            if existing_session:
                await interaction.followup.send(
                    f"You already have an active session! Use `/nexus-action` to continue, or `/nexus-quit` to end it."
                )
                return
            
            # Create new session
            session_id = f"{channel_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            session = session_manager.create_session(
                session_id=session_id,
                channel_id=channel_id,
                user_id=user_id,
                mode=mode
            )
            
            # Generate opening scene
            character = session_manager.get_player_character(session_id, user_id)
            scene_desc, choices = await gm_engine.generate_opening_scene(
                session_id=session_id,
                user_id=str(user_id),  # Convert to str for consistency
                character=character,
                theme=theme
            )
            
            # Create embed for scene
            embed = discord.Embed(
                title="🌌 Nexus Arcanum Adventure Begins",
                description=scene_desc,
                color=discord.Color.purple()
            )
            
            # Add choices as fields
            for i, choice in enumerate(choices, 1):
                embed.add_field(name=f"Option {i}", value=choice, inline=False)
            
            embed.set_footer(text=f"Session: {session_id[:8]} | Mode: {mode}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Started new game session {session_id} for user {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in nexus-start: {e}")
            await interaction.followup.send(f"Error starting adventure: {str(e)}")
    
    @app_commands.command(name="nexus-action", description="Take an action in your adventure")
    @app_commands.describe(action="What you want to do (or choice number 1-4)")
    async def nexus_action(self, interaction: discord.Interaction, action: str):
        """Take an action in the game"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            # Find active session
            session_id = session_manager.get_session_for_user(user_id, channel_id)
            if not session_id:
                await interaction.followup.send(
                    "No active session found! Use `/nexus-start` to begin an adventure."
                )
                return
            
            # Get character
            character = session_manager.get_player_character(session_id, user_id)
            
            # Process action
            scene_desc, choices, key_moment = await gm_engine.process_player_action(
                session_id=session_id,
                user_id=str(user_id),
                action=action,
                character=character
            )
            
            # Create embed
            embed = discord.Embed(
                title="🎲 Adventure Continues",
                description=scene_desc,
                color=discord.Color.blue()
            )
            
            # Add choices
            for i, choice in enumerate(choices, 1):
                embed.add_field(name=f"Option {i}", value=choice, inline=False)
            
            # Generate image if key moment detected
            image_data = None
            if key_moment and image_generator.should_generate_image(key_moment):
                image_data = await image_generator.generate_scene_image(
                    scene_description=scene_desc,
                    moment_type=key_moment,
                    user_id=str(user_id),
                    character_name=character.name if character else None
                )
                if image_data:
                    embed.set_image(url=image_data)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Processed action for user {interaction.user.name} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error in nexus-action: {e}")
            await interaction.followup.send(f"Error processing action: {str(e)}")
    
    @app_commands.command(name="nexus-character", description="View or create your character")
    @app_commands.describe(
        name="Character name",
        descriptor="Character descriptor (e.g., awakened, scarred)",
        type="Character type (warrior, adept, explorer, speaker)",
        focus="Character focus (e.g., weaves_the_nexus, commands_fire)"
    )
    async def nexus_character(
        self,
        interaction: discord.Interaction,
        name: Optional[str] = None,
        descriptor: Optional[str] = None,
        type: Optional[str] = None,
        focus: Optional[str] = None
    ):
        """View or create character"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            # Find active session
            session_id = session_manager.get_session_for_user(user_id, channel_id)
            if not session_id:
                await interaction.followup.send(
                    "No active session found! Use `/nexus-start` to begin an adventure first."
                )
                return
            
            # If all parameters provided, create character
            if name and descriptor and type and focus:
                character = CharacterBuilder.create_character(
                    name=name,
                    descriptor=descriptor,
                    type=type,
                    focus=focus,
                    tier=1
                )
                session_manager.set_player_character(session_id, user_id, character)
                await interaction.followup.send(f"Character created!\n\n{character.get_full_description()}")
            else:
                # View existing character
                character = session_manager.get_player_character(session_id, user_id)
                if character:
                    await interaction.followup.send(character.get_full_description())
                else:
                    await interaction.followup.send(
                        "No character created yet. Use `/nexus-character` with all parameters to create one.\n\n"
                        "Example: `/nexus-character name: Skye descriptor: awakened type: adept focus: weaves_the_nexus`"
                    )
            
        except Exception as e:
            logger.error(f"Error in nexus-character: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="nexus-roll", description="Make a Cypher System roll")
    @app_commands.describe(
        pool="Which pool to use (might, speed, intellect)",
        difficulty="Task difficulty (0-10)",
        effort="Effort level (0-3)"
    )
    async def nexus_roll(
        self,
        interaction: discord.Interaction,
        pool: str,
        difficulty: int = 3,
        effort: int = 0
    ):
        """Make a stat roll"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            # Find active session
            session_id = session_manager.get_session_for_user(user_id, channel_id)
            if not session_id:
                await interaction.followup.send("No active session found!")
                return
            
            # Get character
            character = session_manager.get_player_character(session_id, user_id)
            if not character:
                await interaction.followup.send("No character created! Use `/nexus-character` first.")
                return
            
            # Validate inputs
            pool_lower = pool.lower()
            if pool_lower not in ["might", "speed", "intellect"]:
                await interaction.followup.send(f"Invalid pool: {pool}. Must be might, speed, or intellect.")
                return
            
            if not 0 <= difficulty <= 10:
                await interaction.followup.send(f"Invalid difficulty: {difficulty}. Must be between 0 and 10.")
                return
            
            if not 0 <= effort <= 3:
                await interaction.followup.send(f"Invalid effort: {effort}. Must be between 0 and 3.")
                return
            
            # Resolve roll
            result = await gm_engine.resolve_roll(
                session_id=session_id,
                user_id=str(user_id),
                character=character,
                pool_name=pool_lower,
                base_difficulty=difficulty,
                effort_level=effort
            )
            
            # Create embed
            embed = discord.Embed(
                title="🎲 Roll Result",
                description=result.get("narrative", "Roll completed"),
                color=discord.Color.green() if result.get("success") else discord.Color.red()
            )
            
            embed.add_field(name="Roll", value=str(result.get("roll", "N/A")), inline=True)
            embed.add_field(name="Target", value=str(result.get("target", "N/A")), inline=True)
            embed.add_field(name="Success", value="✅ Yes" if result.get("success") else "❌ No", inline=True)
            
            if result.get("is_critical"):
                embed.add_field(name="Special", value="🌟 Critical Success!", inline=False)
            elif result.get("is_fumble"):
                embed.add_field(name="Special", value="💥 Fumble!", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in nexus-roll: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="nexus-status", description="View your current game status")
    async def nexus_status(self, interaction: discord.Interaction):
        """View game status"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            # Find active session
            session_id = session_manager.get_session_for_user(user_id, channel_id)
            if not session_id:
                await interaction.followup.send("No active session found!")
                return
            
            session = session_manager.get_session(session_id)
            state = session_manager.get_game_state(session_id)
            character = session_manager.get_player_character(session_id, user_id)
            
            embed = discord.Embed(
                title="📊 Game Status",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Session ID", value=session_id[:16], inline=False)
            embed.add_field(name="Mode", value=session.mode, inline=True)
            embed.add_field(name="Turn", value=str(session.turn_count), inline=True)
            embed.add_field(name="Status", value=session.status, inline=True)
            
            if character:
                embed.add_field(
                    name="Character",
                    value=f"{character.name} - {character}",
                    inline=False
                )
                embed.add_field(
                    name="Stat Pools",
                    value=f"Might: {character.stats.might.current}/{character.stats.might.maximum}\n"
                          f"Speed: {character.stats.speed.current}/{character.stats.speed.maximum}\n"
                          f"Intellect: {character.stats.intellect.current}/{character.stats.intellect.maximum}",
                    inline=False
                )
            
            if state and state.available_choices:
                choices_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(state.available_choices)])
                embed.add_field(name="Available Choices", value=choices_text, inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in nexus-status: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="nexus-quit", description="End your current adventure")
    async def nexus_quit(self, interaction: discord.Interaction):
        """End game session"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = interaction.channel.id
            
            session_id = session_manager.get_session_for_user(user_id, channel_id)
            if not session_id:
                await interaction.followup.send("No active session to end.")
                return
            
            session_manager.end_session(session_id)
            await interaction.followup.send("Adventure ended. Thanks for playing!")
            logger.info(f"Ended session {session_id} for user {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in nexus-quit: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    # =========================================================================
    # TEST COMMANDS (Admin only - can be restricted)
    # =========================================================================
    
    @app_commands.command(name="nexus-test-run", description="Run a test scenario (admin)")
    @app_commands.describe(scenario="Test scenario ID to run")
    async def nexus_test_run(self, interaction: discord.Interaction, scenario: str):
        """Run a test scenario"""
        await interaction.response.defer()
        
        try:
            # Run test
            result = await test_runner.run_scenario(
                scenario_id=scenario,
                provider="mistral",
                user_id=str(interaction.user.id)
            )
            
            # Format results
            embed = discord.Embed(
                title=f"🧪 Test Results: {scenario}",
                color=discord.Color.green() if result.get("overall_pass") else discord.Color.red()
            )
            
            embed.add_field(name="Status", value="✅ PASS" if result.get("overall_pass") else "❌ FAIL", inline=False)
            embed.add_field(name="Steps Passed", value=str(result.get("steps_passed", 0)), inline=True)
            embed.add_field(name="Steps Failed", value=str(result.get("steps_failed", 0)), inline=True)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Test scenario {scenario} run by {interaction.user.name}")
            
        except Exception as e:
            logger.error(f"Error in nexus-test-run: {e}")
            await interaction.followup.send(f"Error: {str(e)}")
    
    @app_commands.command(name="nexus-test-list", description="List available test scenarios")
    async def nexus_test_list(self, interaction: discord.Interaction):
        """List test scenarios"""
        await interaction.response.defer()
        
        try:
            scenarios = list_scenarios()
            embed = discord.Embed(
                title="📋 Available Test Scenarios",
                description="\n".join([f"• `{s}`" for s in scenarios]),
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in nexus-test-list: {e}")
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    """Setup function to add cog to bot"""
    await bot.add_cog(GameMasterCommands(bot))

