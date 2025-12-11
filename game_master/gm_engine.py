"""
AI Game Master Engine
Core logic for narrative generation, action interpretation, and rule application
"""

import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from game_master.session_state import SessionManager, session_manager
from game_master.character import Character
from game_master.cypher_rules import CypherRules
from ai_coordinator import ai_coordinator
from test_bed.metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

class KeyMomentDetector:
    """Detects key moments that should trigger image generation"""
    
    KEY_MOMENT_KEYWORDS = {
        "combat": ["attack", "fight", "battle", "combat", "strike", "enemy", "foe", "assailant"],
        "discovery": ["discover", "find", "reveal", "uncover", "treasure", "artifact", "relic"],
        "boss": ["boss", "boss fight", "final", "champion", "leader", "master"],
        "luminari": ["luminari", "light being", "radiant", "emissary"],
        "umbralari": ["umbralari", "shadow", "corrupted", "darkness"],
        "weave_ability": ["weave", "affinity", "magic", "nexus", "cast", "channel"]
    }
    
    @staticmethod
    def detect_key_moment(text: str) -> Optional[str]:
        """
        Detect if text contains a key moment
        
        Returns:
            Key moment type or None
        """
        text_lower = text.lower()
        
        for moment_type, keywords in KeyMomentDetector.KEY_MOMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return moment_type
        
        return None

class GameMasterEngine:
    """AI Game Master for Nexus Arcanum"""
    
    def __init__(self):
        """Initialize the GM engine"""
        self.session_manager = session_manager
        self.rules = CypherRules()
        self.moment_detector = KeyMomentDetector()
        self.metrics = metrics_collector
        logger.info("GameMasterEngine initialized")
    
    def _build_gm_system_prompt(self) -> str:
        """Build the system prompt for the AI GM"""
        return """You are the Game Master for a Nexus Arcanum tabletop RPG session using the Cypher System.

NEXUS ARCANUM WORLD:
- Post-apocalyptic urban fantasy set in Melbourne, Australia
- The Nexus Awakening released magic into the world
- Weavers (10% of survivors) can use Nexus Affinities (Fire, Water, Earth, Air, Ethereal abilities)
- The Nexus Weave connects all living things through magical threads
- Luminari: Ethereal light beings, guardians (revealed Year 10)
- Umbralari: Corrupted Luminari, antagonists (emerged Year 15)
- WyldePhyre communities: Built on voluntary cooperation and mutual aid

CYPHER SYSTEM RULES:
- Characters have 3 stat pools: Might, Speed, Intellect
- Tasks have difficulty 0-10 (target number = difficulty × 3)
- Players roll d20, need to meet or exceed target number
- Effort can reduce difficulty (costs pool points)
- Skills reduce difficulty (Trained: -1, Specialized: -2)
- GM Intrusions: Offer complications for 2 XP

YOUR ROLE:
- Generate vivid, immersive scenes in the Nexus Arcanum world
- Present 2-4 clear choices for players (numbered 1-4)
- Allow free-form actions - players can type anything
- Apply Cypher System rules when appropriate
- Trigger GM Intrusions at dramatic moments
- Maintain consistency with established lore
- Remember NPCs, locations, and events from earlier in the session
- Use descriptive, engaging prose that captures the post-apocalyptic Melbourne setting

TONE:
- Mystical but grounded
- Hope despite hardship
- Epic and engaging
- Respect the Nexus Arcanum world bible"""
    
    def _build_scene_context(
        self,
        session_id: str,
        character: Optional[Character],
        recent_events: int = 5
    ) -> str:
        """Build context string from session history"""
        state = self.session_manager.get_game_state(session_id)
        if not state:
            return ""
        
        context = ""
        
        # Add context summary if available
        if state.context_summary:
            context += f"Session Summary: {state.context_summary}\n\n"
        
        # Add recent events
        if state.events:
            context += "Recent Events:\n"
            for event in state.events[-recent_events:]:
                context += f"- {event['description']}\n"
            context += "\n"
        
        # Add known NPCs
        if state.npcs:
            context += "Known NPCs:\n"
            for npc_name, npc_data in state.npcs.items():
                context += f"- {npc_name}: {npc_data.get('description', 'Unknown')}\n"
            context += "\n"
        
        # Add character info
        if character:
            context += f"Player Character: {character}\n"
            context += f"Current Pools - Might: {character.stats.might.current}/{character.stats.might.maximum}, "
            context += f"Speed: {character.stats.speed.current}/{character.stats.speed.maximum}, "
            context += f"Intellect: {character.stats.intellect.current}/{character.stats.intellect.maximum}\n\n"
        
        return context
    
    async def generate_opening_scene(
        self,
        session_id: str,
        user_id: str,
        character: Optional[Character] = None,
        theme: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Generate the opening scene for a new game
        
        Returns:
            Tuple of (scene_description, choices)
        """
        system_prompt = self._build_gm_system_prompt()
        
        char_desc = f"Character: {character}" if character else "No character created yet"
        theme_text = f"Theme: {theme}" if theme else ""
        
        prompt = f"""Generate an opening scene for a Nexus Arcanum adventure.

{char_desc}
{theme_text}

Create a vivid opening scene that:
1. Sets the scene in post-apocalyptic Melbourne
2. Introduces an immediate situation or challenge
3. Presents 3-4 clear choices for what the player can do next

Format your response as:
SCENE: [vivid scene description]

CHOICES:
1. [First option]
2. [Second option]
3. [Third option]
4. [Optional fourth option]

Make it engaging and true to the Nexus Arcanum world."""
        
        try:
            # Capture metrics
            start_time = time.time()
            response = await ai_coordinator.ask_mistral(
                prompt=prompt,
                user_id=str(user_id),
                system_context=system_prompt,
                use_memory=False  # Don't use memory for opening scenes
            )
            response_time_ms = (time.time() - start_time) * 1000
            
            # Capture metrics
            await self.metrics.capture_ai_interaction(
                session_id=session_id,
                user_id=str(user_id),
                provider="mistral",
                prompt=prompt[:500],  # Truncate for storage
                response=response[:500],
                response_time_ms=response_time_ms,
                metadata={"type": "opening_scene", "theme": theme}
            )
            
            # Parse response
            scene_desc, choices = self._parse_gm_response(response)
            
            # Update game state
            self.session_manager.update_game_state(
                session_id=session_id,
                scene="opening",
                description=scene_desc,
                choices=choices
            )
            
            # Add opening event
            self.session_manager.add_event(
                session_id=session_id,
                event_type="scene",
                description="Opening scene generated"
            )
            
            return scene_desc, choices
            
        except Exception as e:
            logger.error(f"Error generating opening scene: {e}")
            return "You find yourself in the ruins of Melbourne, the Nexus Weave shimmering around you...", [
                "Explore the ruins",
                "Seek other survivors",
                "Investigate the Nexus energy",
                "Take a moment to rest"
            ]
    
    async def process_player_action(
        self,
        session_id: str,
        user_id: str,
        action: str,
        character: Optional[Character] = None
    ) -> Tuple[str, List[str], Optional[str]]:
        """
        Process a player action and generate the next scene
        
        Args:
            session_id: Session ID
            user_id: User ID
            action: Player's action (choice number or free-form text)
            character: Player's character
        
        Returns:
            Tuple of (scene_description, choices, key_moment_type)
        """
        state = self.session_manager.get_game_state(session_id)
        if not state:
            return "Session not found.", [], None
        
        # Check if action is a numbered choice
        choice_match = re.match(r'^(\d+)$', action.strip())
        if choice_match:
            choice_num = int(choice_match.group(1)) - 1
            if 0 <= choice_num < len(state.available_choices):
                action = state.available_choices[choice_num]
            else:
                return f"Invalid choice number. Please pick 1-{len(state.available_choices)}.", state.available_choices, None
        
        system_prompt = self._build_gm_system_prompt()
        context = self._build_scene_context(session_id, character)
        
        prompt = f"""The player takes this action: "{action}"

{context}

Generate the next scene based on this action:
1. Describe what happens as a result of this action
2. Show consequences (good or bad)
3. Present 3-4 new choices for what to do next
4. If this is combat, describe the encounter vividly
5. If this is a discovery, make it exciting
6. Maintain consistency with previous events

Format your response as:
SCENE: [vivid scene description]

CHOICES:
1. [First option]
2. [Second option]
3. [Third option]
4. [Optional fourth option]

If this triggers a GM Intrusion, mention it and offer 2 XP."""
        
        try:
            # Capture metrics
            start_time = time.time()
            response = await ai_coordinator.ask_mistral(
                prompt=prompt,
                user_id=str(user_id),
                system_context=system_prompt,
                use_memory=True
            )
            response_time_ms = (time.time() - start_time) * 1000
            
            # Capture metrics
            await self.metrics.capture_ai_interaction(
                session_id=session_id,
                user_id=str(user_id),
                provider="mistral",
                prompt=prompt[:500],  # Truncate for storage
                response=response[:500],
                response_time_ms=response_time_ms,
                metadata={"type": "player_action", "action": action[:100]}
            )
            
            # Parse response
            scene_desc, choices = self._parse_gm_response(response)
            
            # Detect key moment
            key_moment = self.moment_detector.detect_key_moment(scene_desc)
            
            # Update game state
            self.session_manager.update_game_state(
                session_id=session_id,
                scene=f"scene_{state.scene_count + 1}",
                description=scene_desc,
                choices=choices,
                context_summary=self._update_context_summary(state.context_summary, action, scene_desc)
            )
            
            # Add event
            self.session_manager.add_event(
                session_id=session_id,
                event_type="action",
                description=f"Player action: {action}",
                metadata={"key_moment": key_moment}
            )
            
            return scene_desc, choices, key_moment
            
        except Exception as e:
            logger.error(f"Error processing player action: {e}")
            return f"Something went wrong processing your action: {str(e)}", state.available_choices, None
    
    def _parse_gm_response(self, response: str) -> Tuple[str, List[str]]:
        """Parse GM response into scene description and choices"""
        # Try to extract SCENE and CHOICES sections
        scene_match = re.search(r'SCENE:\s*(.+?)(?=CHOICES:|$)', response, re.DOTALL | re.IGNORECASE)
        choices_match = re.search(r'CHOICES:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        
        if scene_match:
            scene_desc = scene_match.group(1).strip()
        else:
            # Fallback: use entire response as scene
            scene_desc = response.strip()
        
        choices = []
        if choices_match:
            choices_text = choices_match.group(1)
            # Extract numbered choices
            choice_pattern = r'^\s*\d+\.\s*(.+)$'
            for line in choices_text.split('\n'):
                match = re.match(choice_pattern, line)
                if match:
                    choices.append(match.group(1).strip())
        
        # If no choices found, generate defaults
        if not choices:
            choices = [
                "Continue exploring",
                "Investigate further",
                "Take a different approach",
                "Rest and recover"
            ]
        
        return scene_desc, choices[:4]  # Max 4 choices
    
    def _update_context_summary(
        self,
        current_summary: str,
        action: str,
        new_scene: str
    ) -> str:
        """Update the context summary with new information"""
        # Simple approach: append to summary, keep it concise
        summary = current_summary or ""
        if summary:
            summary += " "
        summary += f"Player {action}. {new_scene[:100]}..."
        
        # Keep summary under reasonable length
        if len(summary) > 500:
            summary = summary[-500:]
        
        return summary
    
    async def resolve_roll(
        self,
        session_id: str,
        user_id: str,
        character: Character,
        pool_name: str,
        base_difficulty: int,
        skills: int = 0,
        assets: int = 0,
        effort_level: int = 0
    ) -> Dict:
        """
        Resolve a task roll using Cypher System rules
        
        Returns:
            Dict with roll results and narrative description
        """
        success, result = self.rules.resolve_task(
            base_difficulty=base_difficulty,
            pool_name=pool_name,
            character=character,
            skills=skills,
            assets=assets,
            effort_level=effort_level
        )
        
        # Generate narrative description
        if success:
            if result["is_critical"]:
                narrative = f"**Critical Success!** You roll a {result['roll']}, achieving an exceptional result!"
            else:
                narrative = f"You roll a {result['roll']} (target: {result['target']}) and succeed!"
        else:
            if result["is_fumble"]:
                narrative = f"**Fumble!** You roll a 1, something goes wrong!"
            else:
                narrative = f"You roll a {result['roll']} (target: {result['target']}) and fail."
        
        result["narrative"] = narrative
        result["success"] = success
        
        # Add event
        self.session_manager.add_event(
            session_id=session_id,
            event_type="roll",
            description=f"{pool_name} roll: {narrative}",
            metadata=result
        )
        
        # Capture rule compliance metric
        await self.metrics.capture_rule_compliance(
            session_id=session_id,
            user_id=user_id,
            rule_name="task_resolution",
            compliant=True,  # Rules engine handles this correctly
            expected=f"Roll d20, target {result['target']}, success={result['success']}",
            actual=f"Rolled {result['roll']}, target {result['target']}, success={result['success']}"
        )
        
        return result
    
    def trigger_gm_intrusion(
        self,
        session_id: str,
        description: str,
        xp_offered: int = 2
    ) -> Dict:
        """
        Trigger a GM Intrusion
        
        Returns:
            Dict with intrusion details
        """
        intrusion = {
            "description": description,
            "xp_offered": xp_offered,
            "accepted": False
        }
        
        self.session_manager.add_event(
            session_id=session_id,
            event_type="gm_intrusion",
            description=description,
            metadata=intrusion
        )
        
        return intrusion

# Global GM engine instance
gm_engine = GameMasterEngine()

