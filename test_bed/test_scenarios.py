"""
Test Scenarios
Predefined test scenarios for evaluating AI GM performance
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TestStep:
    """A single step in a test scenario"""
    turn: int
    input: str
    expected_behavior: str
    check_type: str  # "context", "lore", "rule", "quality"
    metadata: Dict[str, Any] = None

@dataclass
class TestScenario:
    """A complete test scenario"""
    scenario_id: str
    name: str
    description: str
    steps: List[TestStep]
    expected_outcomes: Dict[str, Any]

# Test Scenarios

CONTEXT_RETENTION_NPC = TestScenario(
    scenario_id="context_retention_npc",
    name="NPC Context Retention",
    description="Test if GM remembers NPC introduced 5 turns ago",
    steps=[
        TestStep(
            turn=1,
            input="I enter the tavern",
            expected_behavior="GM introduces NPC 'Kira, a scarred Weaver with fire affinity'",
            check_type="context",
            metadata={"inject_npc": "Kira, a scarred Weaver with fire affinity"}
        ),
        TestStep(
            turn=2,
            input="I explore the ruins",
            expected_behavior="GM generates exploration scene",
            check_type="quality"
        ),
        TestStep(
            turn=3,
            input="I search for supplies",
            expected_behavior="GM generates search scene",
            check_type="quality"
        ),
        TestStep(
            turn=4,
            input="I investigate the Nexus energy",
            expected_behavior="GM generates investigation scene",
            check_type="quality"
        ),
        TestStep(
            turn=5,
            input="I ask about the Weaver I met earlier",
            expected_behavior="GM references Kira, mentions fire affinity and scarred descriptor",
            check_type="context",
            metadata={"reference_check": "Kira", "attributes": ["fire affinity", "scarred"]}
        )
    ],
    expected_outcomes={
        "context_retention_5_turns": True,
        "npc_name_recalled": True,
        "npc_attributes_recalled": True
    }
)

LORE_CONSISTENCY_LUMINARI = TestScenario(
    scenario_id="lore_consistency_luminari",
    name="Luminari Lore Consistency",
    description="Test if GM accurately describes Luminari according to Nexus Arcanum lore",
    steps=[
        TestStep(
            turn=1,
            input="I encounter a being of light",
            expected_behavior="GM describes Luminari accurately: ethereal light beings, revealed Year 10, guardians/emissaries",
            check_type="lore",
            metadata={"lore_check": "luminari", "expected_attributes": ["ethereal", "light", "Year 10", "guardian"]}
        )
    ],
    expected_outcomes={
        "lore_accurate": True,
        "year_10_mentioned": True,
        "guardian_role_mentioned": True
    }
)

RULE_COMPLIANCE_DIFFICULTY = TestScenario(
    scenario_id="rule_compliance_difficulty",
    name="Cypher System Difficulty Rules",
    description="Test if GM applies Cypher System difficulty rules correctly",
    steps=[
        TestStep(
            turn=1,
            input="I attempt to climb the wall (difficulty 4)",
            expected_behavior="GM correctly applies difficulty 4 (target number 12), asks for roll",
            check_type="rule",
            metadata={"rule_check": "difficulty", "expected_difficulty": 4, "expected_target": 12}
        )
    ],
    expected_outcomes={
        "difficulty_applied": True,
        "target_number_correct": True
    }
)

GM_INTRUSION_TEST = TestScenario(
    scenario_id="gm_intrusion_test",
    name="GM Intrusion Mechanics",
    description="Test if GM triggers appropriate GM Intrusions and offers XP",
    steps=[
        TestStep(
            turn=1,
            input="I attempt a risky action",
            expected_behavior="GM offers GM Intrusion with 2 XP, describes complication",
            check_type="rule",
            metadata={"rule_check": "gm_intrusion", "expected_xp": 2}
        )
    ],
    expected_outcomes={
        "intrusion_offered": True,
        "xp_mentioned": True,
        "xp_amount_correct": True
    }
)

COMBAT_RESOLUTION = TestScenario(
    scenario_id="combat_resolution",
    name="Combat Scene Generation",
    description="Test if GM generates appropriate combat scenes with key moment detection",
    steps=[
        TestStep(
            turn=1,
            input="I attack the enemy",
            expected_behavior="GM generates vivid combat scene, detects key moment for image generation",
            check_type="quality",
            metadata={"key_moment_check": "combat"}
        )
    ],
    expected_outcomes={
        "combat_scene_generated": True,
        "key_moment_detected": True
    }
)

# Registry of all test scenarios
TEST_SCENARIOS = {
    "context_retention_npc": CONTEXT_RETENTION_NPC,
    "lore_consistency_luminari": LORE_CONSISTENCY_LUMINARI,
    "rule_compliance_difficulty": RULE_COMPLIANCE_DIFFICULTY,
    "gm_intrusion_test": GM_INTRUSION_TEST,
    "combat_resolution": COMBAT_RESOLUTION
}

def get_scenario(scenario_id: str) -> TestScenario:
    """Get a test scenario by ID"""
    return TEST_SCENARIOS.get(scenario_id)

def list_scenarios() -> List[str]:
    """List all available test scenario IDs"""
    return list(TEST_SCENARIOS.keys())

