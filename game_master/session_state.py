"""
Game Session State Management
Handles active game sessions, player tracking, and state persistence
"""

import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from game_master.character import Character

logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Information about a game session"""
    session_id: str
    channel_id: int
    mode: str  # "solo" or "party"
    status: str  # "active", "paused", "completed"
    created_at: datetime
    last_activity: datetime
    user_ids: List[int] = field(default_factory=list)
    turn_count: int = 0
    scene_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SessionInfo":
        """Create from dictionary"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        return cls(**data)

@dataclass
class GameState:
    """Complete game state for a session"""
    session_id: str
    current_scene: str
    scene_description: str
    available_choices: List[str] = field(default_factory=list)
    npcs: Dict[str, Dict] = field(default_factory=dict)  # NPC name -> NPC data
    locations: List[str] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)  # History of events
    context_summary: str = ""  # Summary of what's happened so far
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "GameState":
        """Create from dictionary"""
        return cls(**data)

class SessionManager:
    """Manages active game sessions"""
    
    def __init__(self):
        """Initialize session manager"""
        # In-memory storage for active sessions
        self._active_sessions: Dict[str, SessionInfo] = {}
        self._session_states: Dict[str, GameState] = {}
        self._player_characters: Dict[str, Dict[int, Character]] = {}  # session_id -> {user_id: Character}
        logger.info("SessionManager initialized")
    
    def create_session(
        self,
        session_id: str,
        channel_id: int,
        user_id: int,
        mode: str = "solo"
    ) -> SessionInfo:
        """
        Create a new game session
        
        Args:
            session_id: Unique session identifier
            channel_id: Discord channel ID
            user_id: Creator user ID
            mode: "solo" or "party"
        
        Returns:
            SessionInfo for the new session
        """
        now = datetime.now()
        session = SessionInfo(
            session_id=session_id,
            channel_id=channel_id,
            mode=mode,
            status="active",
            created_at=now,
            last_activity=now,
            user_ids=[user_id]
        )
        
        self._active_sessions[session_id] = session
        
        # Initialize game state
        game_state = GameState(
            session_id=session_id,
            current_scene="opening",
            scene_description="",
            available_choices=[]
        )
        self._session_states[session_id] = game_state
        
        # Initialize player characters dict
        self._player_characters[session_id] = {}
        
        logger.info(f"Created session {session_id} in channel {channel_id} ({mode} mode)")
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session info by ID"""
        return self._active_sessions.get(session_id)
    
    def get_game_state(self, session_id: str) -> Optional[GameState]:
        """Get game state for a session"""
        return self._session_states.get(session_id)
    
    def get_player_character(
        self,
        session_id: str,
        user_id: int
    ) -> Optional[Character]:
        """Get a player's character in a session"""
        session_chars = self._player_characters.get(session_id, {})
        return session_chars.get(user_id)
    
    def set_player_character(
        self,
        session_id: str,
        user_id: int,
        character: Character
    ):
        """Set a player's character in a session"""
        if session_id not in self._player_characters:
            self._player_characters[session_id] = {}
        self._player_characters[session_id][user_id] = character
        logger.info(f"Set character for user {user_id} in session {session_id}")
    
    def add_player(self, session_id: str, user_id: int) -> bool:
        """Add a player to a party session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if session.mode != "party":
            logger.warning(f"Tried to add player to non-party session {session_id}")
            return False
        
        if user_id not in session.user_ids:
            session.user_ids.append(user_id)
            session.last_activity = datetime.now()
            logger.info(f"Added user {user_id} to session {session_id}")
            return True
        return False
    
    def update_game_state(
        self,
        session_id: str,
        scene: str,
        description: str,
        choices: List[str],
        context_summary: str = ""
    ):
        """Update the game state for a session"""
        state = self.get_game_state(session_id)
        if not state:
            logger.error(f"No game state found for session {session_id}")
            return
        
        state.current_scene = scene
        state.scene_description = description
        state.available_choices = choices
        if context_summary:
            state.context_summary = context_summary
        
        # Update session activity
        session = self.get_session(session_id)
        if session:
            session.last_activity = datetime.now()
            session.turn_count += 1
            session.scene_count += 1
    
    def add_event(
        self,
        session_id: str,
        event_type: str,
        description: str,
        metadata: Optional[Dict] = None
    ):
        """Add an event to the game history"""
        state = self.get_game_state(session_id)
        if not state:
            return
        
        event = {
            "type": event_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        state.events.append(event)
    
    def add_npc(self, session_id: str, npc_name: str, npc_data: Dict):
        """Add an NPC to the current scene"""
        state = self.get_game_state(session_id)
        if not state:
            return
        state.npcs[npc_name] = npc_data
    
    def get_npc(self, session_id: str, npc_name: str) -> Optional[Dict]:
        """Get NPC data by name"""
        state = self.get_game_state(session_id)
        if not state:
            return None
        return state.npcs.get(npc_name)
    
    def pause_session(self, session_id: str) -> bool:
        """Pause a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        session.status = "paused"
        logger.info(f"Paused session {session_id}")
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        session = self.get_session(session_id)
        if not session:
            return False
        if session.status == "paused":
            session.status = "active"
            session.last_activity = datetime.now()
            logger.info(f"Resumed session {session_id}")
            return True
        return False
    
    def end_session(self, session_id: str) -> bool:
        """End a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        session.status = "completed"
        logger.info(f"Ended session {session_id}")
        return True
    
    def get_session_for_user(self, user_id: int, channel_id: Optional[int] = None) -> Optional[str]:
        """
        Find active session for a user
        
        Args:
            user_id: Discord user ID
            channel_id: Optional channel ID to filter by
        
        Returns:
            Session ID if found, None otherwise
        """
        for session_id, session in self._active_sessions.items():
            if session.status != "active":
                continue
            if user_id in session.user_ids:
                if channel_id is None or session.channel_id == channel_id:
                    return session_id
        return None
    
    def get_all_active_sessions(self) -> List[SessionInfo]:
        """Get all active sessions"""
        return [s for s in self._active_sessions.values() if s.status == "active"]
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        
        for session_id, session in self._active_sessions.items():
            age = (now - session.last_activity).total_seconds() / 3600
            if age > max_age_hours and session.status != "active":
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self._active_sessions[session_id]
            if session_id in self._session_states:
                del self._session_states[session_id]
            if session_id in self._player_characters:
                del self._player_characters[session_id]
            logger.info(f"Cleaned up old session {session_id}")
    
    def export_session(self, session_id: str) -> Optional[Dict]:
        """Export session data for persistence"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        state = self.get_game_state(session_id)
        characters = self._player_characters.get(session_id, {})
        
        # Convert characters to dicts
        char_dicts = {}
        for user_id, char in characters.items():
            # Store character as dict (would need to implement to_dict on Character)
            char_dicts[str(user_id)] = {
                "name": char.name,
                "descriptor": char.descriptor,
                "type": char.type,
                "focus": char.focus,
                "tier": char.stats.tier,
                "xp": char.stats.xp,
                "might": {"current": char.stats.might.current, "max": char.stats.might.maximum, "edge": char.stats.might.edge},
                "speed": {"current": char.stats.speed.current, "max": char.stats.speed.maximum, "edge": char.stats.speed.edge},
                "intellect": {"current": char.stats.intellect.current, "max": char.stats.intellect.maximum, "edge": char.stats.intellect.edge},
                "inventory": char.inventory,
                "skills": char.skills
            }
        
        return {
            "session": session.to_dict(),
            "game_state": state.to_dict() if state else None,
            "characters": char_dicts
        }
    
    def import_session(self, data: Dict) -> Optional[str]:
        """Import session data from persistence"""
        try:
            session_data = data["session"]
            session = SessionInfo.from_dict(session_data)
            session_id = session.session_id
            
            self._active_sessions[session_id] = session
            
            if "game_state" in data and data["game_state"]:
                self._session_states[session_id] = GameState.from_dict(data["game_state"])
            
            # Reconstruct characters (simplified - would need Character.from_dict)
            if "characters" in data:
                self._player_characters[session_id] = {}
                # Note: Full character reconstruction would require CharacterBuilder
            
            logger.info(f"Imported session {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return None

# Global session manager instance
session_manager = SessionManager()

