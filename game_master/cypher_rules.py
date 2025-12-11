"""
Cypher System Rules Engine
Implements core Cypher System mechanics for Nexus Arcanum
"""

import random
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StatPool:
    """Represents a stat pool (Might, Speed, Intellect)"""
    current: int
    maximum: int
    edge: int  # Reduces cost of spending from this pool
    
    def spend(self, amount: int) -> int:
        """Spend points from pool, accounting for edge. Returns actual cost."""
        if amount <= self.edge:
            return 0  # Edge covers the cost
        actual_cost = amount - self.edge
        self.current = max(0, self.current - actual_cost)
        return actual_cost
    
    def restore(self, amount: int):
        """Restore points to pool (up to maximum)"""
        self.current = min(self.maximum, self.current + amount)
    
    def is_depleted(self) -> bool:
        """Check if pool is at zero"""
        return self.current <= 0

@dataclass
class CharacterStats:
    """Complete character stat block"""
    might: StatPool
    speed: StatPool
    intellect: StatPool
    tier: int = 1  # Character tier (1-6)
    xp: int = 0  # Experience points
    
    def get_pool(self, pool_name: str) -> Optional[StatPool]:
        """Get a stat pool by name"""
        pools = {
            "might": self.might,
            "speed": self.speed,
            "intellect": self.intellect
        }
        return pools.get(pool_name.lower())

class CypherRules:
    """Cypher System rules engine"""
    
    # Difficulty to target number mapping
    DIFFICULTY_TARGETS = {
        0: 0,   # Routine
        1: 3,   # Simple
        2: 6,   # Standard
        3: 9,   # Difficult
        4: 12,  # Challenging
        5: 15,  # Formidable
        6: 18,  # Daunting
        7: 21,  # Intimidating
        8: 24,  # Overwhelming
        9: 27,  # Nearly Impossible
        10: 30  # Impossible
    }
    
    @staticmethod
    def get_target_number(difficulty: int) -> int:
        """Convert difficulty (0-10) to target number"""
        difficulty = max(0, min(10, difficulty))
        return CypherRules.DIFFICULTY_TARGETS[difficulty]
    
    @staticmethod
    def roll_d20() -> int:
        """Roll a d20"""
        return random.randint(1, 20)
    
    @staticmethod
    def roll_d6() -> int:
        """Roll a d6"""
        return random.randint(1, 6)
    
    @staticmethod
    def calculate_effective_difficulty(
        base_difficulty: int,
        skills: int = 0,  # 0 = untrained, 1 = trained, 2 = specialized
        assets: int = 0,  # Additional assets (equipment, circumstances)
        effort: int = 0   # Effort being applied
    ) -> int:
        """
        Calculate effective difficulty after modifiers
        
        Args:
            base_difficulty: Base task difficulty (0-10)
            skills: Skill level (0=untrained, 1=trained, 2=specialized)
            assets: Number of assets (reduce difficulty by 1 each)
            effort: Effort being applied (reduce difficulty by 1 per level)
        
        Returns:
            Effective difficulty (0-10)
        """
        effective = base_difficulty
        
        # Skills reduce difficulty
        effective -= skills
        
        # Assets reduce difficulty (max 2 assets typically)
        effective -= min(assets, 2)
        
        # Effort reduces difficulty
        effective -= effort
        
        # Clamp to valid range
        return max(0, min(10, effective))
    
    @staticmethod
    def resolve_task(
        base_difficulty: int,
        pool_name: str,
        character: CharacterStats,
        skills: int = 0,
        assets: int = 0,
        effort_level: int = 0
    ) -> Tuple[bool, Dict]:
        """
        Resolve a task roll
        
        Args:
            base_difficulty: Base task difficulty (0-10)
            pool_name: Which pool to use ("might", "speed", "intellect")
            character: Character stats
            skills: Skill level (0-2)
            assets: Number of assets
            effort_level: How many levels of effort to apply
        
        Returns:
            Tuple of (success: bool, result_dict: Dict)
        """
        pool = character.get_pool(pool_name)
        if not pool:
            return False, {"error": f"Invalid pool: {pool_name}"}
        
        # Calculate effective difficulty
        effective_diff = CypherRules.calculate_effective_difficulty(
            base_difficulty, skills, assets, effort_level
        )
        
        # Spend effort cost (Cypher System: each level costs 3 points, reduced by edge)
        # Edge reduces the cost per level
        cost_per_level = max(1, 3 - pool.edge)  # Minimum 1 point per level
        effort_cost = effort_level * cost_per_level
        if effort_cost > 0:
            pool.spend(effort_cost)
        
        # Get target number
        target = CypherRules.get_target_number(effective_diff)
        
        # Roll d20
        roll = CypherRules.roll_d20()
        
        # Check for special results
        is_critical = (roll == 19 or roll == 20)
        is_fumble = (roll == 1)
        
        # Determine success
        success = roll >= target or is_critical
        
        result = {
            "success": success,
            "roll": roll,
            "target": target,
            "effective_difficulty": effective_diff,
            "base_difficulty": base_difficulty,
            "pool_used": pool_name,
            "pool_remaining": pool.current,
            "effort_applied": effort_level,
            "effort_cost": effort_cost,
            "is_critical": is_critical,
            "is_fumble": is_fumble,
            "margin": roll - target if success else target - roll
        }
        
        return success, result
    
    @staticmethod
    def recovery_roll(tier: int) -> int:
        """
        Make a recovery roll (1d6 + tier)
        Returns points restored
        """
        roll = CypherRules.roll_d6() + tier
        return roll
    
    @staticmethod
    def gm_intrusion_cost(character: CharacterStats) -> int:
        """Calculate XP cost for accepting a GM Intrusion"""
        # Base cost is 2 XP, but can be modified
        return 2
    
    @staticmethod
    def apply_damage(
        character: CharacterStats,
        damage: int,
        pool_name: str
    ) -> Dict:
        """
        Apply damage to a stat pool
        
        Args:
            character: Character to damage
            damage: Amount of damage
            pool_name: Which pool takes damage
        
        Returns:
            Dict with damage result
        """
        pool = character.get_pool(pool_name)
        if not pool:
            return {"error": f"Invalid pool: {pool_name}"}
        
        pool.current = max(0, pool.current - damage)
        
        return {
            "damage_dealt": damage,
            "pool": pool_name,
            "remaining": pool.current,
            "depleted": pool.is_depleted()
        }

