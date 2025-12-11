"""
Character Model for Cypher System
"I am a [Descriptor] [Type] who [Focus]"
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from game_master.cypher_rules import CharacterStats, StatPool

logger = logging.getLogger(__name__)

# Nexus Arcanum Character Types
CHARACTER_TYPES = {
    "warrior": {
        "description": "A fighter who excels in physical combat",
        "starting_pools": {"might": 10, "speed": 9, "intellect": 7},
        "starting_edge": {"might": 1, "speed": 0, "intellect": 0}
    },
    "adept": {
        "description": "A Weaver who channels the Nexus Weave",
        "starting_pools": {"might": 7, "speed": 9, "intellect": 10},
        "starting_edge": {"might": 0, "speed": 0, "intellect": 1}
    },
    "explorer": {
        "description": "A wanderer who adapts to any situation",
        "starting_pools": {"might": 9, "speed": 10, "intellect": 7},
        "starting_edge": {"might": 0, "speed": 1, "intellect": 0}
    },
    "speaker": {
        "description": "A diplomat and leader who uses words and influence",
        "starting_pools": {"might": 7, "speed": 7, "intellect": 12},
        "starting_edge": {"might": 0, "speed": 0, "intellect": 1}
    }
}

# Nexus Arcanum Descriptors
DESCRIPTORS = {
    "awakened": "Recently discovered their Nexus Affinity",
    "scarred": "Bears physical and emotional scars from the Nexus Awakening",
    "luminous": "Has a connection to the Luminari",
    "shadow-touched": "Has encountered the Umbralari",
    "wild": "Raised in the transformed wilderness",
    "urban": "Survived in the ruins of Melbourne",
    "scholar": "Studies the Nexus Weave and its mysteries",
    "scavenger": "Expert at finding resources in the ruins"
}

# Nexus Arcanum Foci
FOCI = {
    "weaves_the_nexus": {
        "description": "Masters multiple Nexus Affinities",
        "abilities": ["Can use multiple elemental affinities", "Stronger Weavecrafting"]
    },
    "commands_fire": {
        "description": "Specializes in Fire Affinity",
        "abilities": ["Enhanced fire attacks", "Fire resistance"]
    },
    "speaks_for_the_land": {
        "description": "Communicates with transformed nature",
        "abilities": ["Talk to plants and animals", "Nature-based abilities"]
    },
    "shapes_the_weave": {
        "description": "Manipulates the Nexus Weave directly",
        "abilities": ["Create magical effects", "Sense Nexus energy"]
    },
    "bears_a_heavy_weapon": {
        "description": "Expert with powerful weapons",
        "abilities": ["Proficiency with heavy weapons", "Increased damage"]
    },
    "moves_like_a_ghost": {
        "description": "Extremely stealthy and agile",
        "abilities": ["Enhanced stealth", "Difficult to hit"]
    }
}

@dataclass
class Cypher:
    """A one-use magical ability"""
    name: str
    description: str
    level: int = 1
    used: bool = False

@dataclass
class Character:
    """Complete Cypher System character"""
    name: str
    descriptor: str
    type: str
    focus: str
    stats: CharacterStats
    inventory: List[str] = field(default_factory=list)
    cyphers: List[Cypher] = field(default_factory=list)
    skills: Dict[str, int] = field(default_factory=dict)  # skill_name -> level (0-2)
    special_abilities: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """Return character in Cypher format"""
        return f"I am a {self.descriptor} {self.type} who {self.focus}"
    
    def get_full_description(self) -> str:
        """Get full character description"""
        desc = f"**{self.name}**\n"
        desc += f"{self}\n\n"
        desc += f"**Tier:** {self.stats.tier} | **XP:** {self.stats.xp}\n\n"
        desc += f"**Stat Pools:**\n"
        desc += f"  Might: {self.stats.might.current}/{self.stats.might.maximum} (Edge: {self.stats.might.edge})\n"
        desc += f"  Speed: {self.stats.speed.current}/{self.stats.speed.maximum} (Edge: {self.stats.speed.edge})\n"
        desc += f"  Intellect: {self.stats.intellect.current}/{self.stats.intellect.maximum} (Edge: {self.stats.intellect.edge})\n"
        
        if self.skills:
            desc += f"\n**Skills:**\n"
            for skill, level in self.skills.items():
                level_name = ["Untrained", "Trained", "Specialized"][level]
                desc += f"  {skill}: {level_name}\n"
        
        if self.cyphers:
            desc += f"\n**Cyphers:**\n"
            for cypher in self.cyphers:
                if not cypher.used:
                    desc += f"  {cypher.name} (Level {cypher.level})\n"
        
        if self.inventory:
            desc += f"\n**Inventory:** {', '.join(self.inventory)}\n"
        
        return desc
    
    def add_skill(self, skill_name: str, level: int = 1):
        """Add or upgrade a skill"""
        self.skills[skill_name.lower()] = min(2, max(0, level))
    
    def add_cypher(self, cypher: Cypher):
        """Add a cypher (max 2 typically)"""
        if len(self.cyphers) < 2:
            self.cyphers.append(cypher)
        else:
            logger.warning(f"{self.name} already has 2 cyphers, replacing oldest")
            self.cyphers.pop(0)
            self.cyphers.append(cypher)
    
    def use_cypher(self, cypher_name: str) -> Optional[Cypher]:
        """Use a cypher by name"""
        for cypher in self.cyphers:
            if cypher.name.lower() == cypher_name.lower() and not cypher.used:
                cypher.used = True
                return cypher
        return None

class CharacterBuilder:
    """Build Cypher System characters"""
    
    @staticmethod
    def create_character(
        name: str,
        descriptor: str,
        type: str,
        focus: str,
        tier: int = 1
    ) -> Character:
        """
        Create a new character
        
        Args:
            name: Character name
            descriptor: Character descriptor (e.g., "awakened", "scarred")
            type: Character type (e.g., "warrior", "adept")
            focus: Character focus (e.g., "weaves_the_nexus")
            tier: Starting tier (default 1)
        
        Returns:
            New Character instance
        """
        # Validate and get type info
        type_lower = type.lower()
        if type_lower not in CHARACTER_TYPES:
            raise ValueError(f"Invalid character type: {type}. Available types: {', '.join(CHARACTER_TYPES.keys())}")
        type_info = CHARACTER_TYPES[type_lower]
        
        # Validate descriptor
        descriptor_lower = descriptor.lower()
        if descriptor_lower not in DESCRIPTORS:
            logger.warning(f"Unknown descriptor {descriptor}, continuing anyway")
        
        # Validate focus
        focus_lower = focus.lower().replace(" ", "_")
        if focus_lower not in FOCI:
            logger.warning(f"Unknown focus {focus}, continuing anyway")
        
        # Create stat pools
        pools = type_info["starting_pools"]
        edges = type_info["starting_edge"]
        
        # Adjust for tier (each tier adds 4 points to pools)
        pool_bonus = (tier - 1) * 4
        
        might = StatPool(
            current=pools["might"] + pool_bonus,
            maximum=pools["might"] + pool_bonus,
            edge=edges["might"]
        )
        speed = StatPool(
            current=pools["speed"] + pool_bonus,
            maximum=pools["speed"] + pool_bonus,
            edge=edges["speed"]
        )
        intellect = StatPool(
            current=pools["intellect"] + pool_bonus,
            maximum=pools["intellect"] + pool_bonus,
            edge=edges["intellect"]
        )
        
        stats = CharacterStats(
            might=might,
            speed=speed,
            intellect=intellect,
            tier=tier,
            xp=0
        )
        
        # Create character
        character = Character(
            name=name,
            descriptor=descriptor,
            type=type,
            focus=focus,
            stats=stats
        )
        
        # Add starting skills based on type
        if type.lower() == "warrior":
            character.add_skill("attacking", 1)
            character.add_skill("defending", 1)
        elif type.lower() == "adept":
            character.add_skill("weavecrafting", 1)
            character.add_skill("understanding the nexus", 1)
        elif type.lower() == "explorer":
            character.add_skill("climbing", 1)
            character.add_skill("navigation", 1)
        elif type.lower() == "speaker":
            character.add_skill("persuasion", 1)
            character.add_skill("social interaction", 1)
        
        logger.info(f"Created character: {character}")
        return character
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get list of available character types"""
        return list(CHARACTER_TYPES.keys())
    
    @staticmethod
    def get_available_descriptors() -> List[str]:
        """Get list of available descriptors"""
        return list(DESCRIPTORS.keys())
    
    @staticmethod
    def get_available_foci() -> List[str]:
        """Get list of available foci"""
        return list(FOCI.keys())

