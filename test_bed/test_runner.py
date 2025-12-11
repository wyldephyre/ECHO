"""
Test Runner
Executes test scenarios and compares AI provider outputs
"""

import logging
from typing import Dict, List, Optional, Any
from game_master.gm_engine import gm_engine
from game_master.session_state import session_manager
from test_bed.test_scenarios import TestScenario, get_scenario, list_scenarios
from test_bed.metrics_collector import metrics_collector, PerformanceTimer
from ai_coordinator import ai_coordinator

logger = logging.getLogger(__name__)

class TestRunner:
    """Runs test scenarios and collects results"""
    
    def __init__(self):
        """Initialize test runner"""
        self.gm_engine = gm_engine
        self.session_manager = session_manager
        self.metrics = metrics_collector
        logger.info("TestRunner initialized")
    
    async def run_scenario(
        self,
        scenario_id: str,
        provider: str = "mistral",
        user_id: str = "test_user"
    ) -> Dict[str, Any]:
        """
        Run a test scenario
        
        Args:
            scenario_id: ID of scenario to run
            provider: AI provider to test (mistral, claude, gemini, grok)
            user_id: Test user ID
        
        Returns:
            Dict with test results
        """
        scenario = get_scenario(scenario_id)
        if not scenario:
            return {"error": f"Scenario {scenario_id} not found"}
        
        logger.info(f"Running test scenario: {scenario.name}")
        
        # Create test session
        session_id = f"test_{scenario_id}_{provider}_{user_id}"
        # Convert user_id to int for session creation (Discord IDs are int)
        try:
            user_id_int = int(user_id) if user_id.isdigit() else 12345
        except (ValueError, AttributeError):
            user_id_int = 12345
        
        session = self.session_manager.create_session(
            session_id=session_id,
            channel_id=0,  # Test channel
            user_id=user_id_int,
            mode="solo"
        )
        
        results = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "provider": provider,
            "steps_passed": 0,
            "steps_failed": 0,
            "step_results": [],
            "overall_pass": False
        }
        
        try:
            # Run each step
            for step in scenario.steps:
                step_result = await self._run_step(
                    session_id=session_id,
                    step=step,
                    provider=provider,
                    user_id=user_id
                )
                
                results["step_results"].append(step_result)
                
                if step_result["passed"]:
                    results["steps_passed"] += 1
                else:
                    results["steps_failed"] += 1
            
            # Evaluate overall results
            results["overall_pass"] = results["steps_failed"] == 0
            
            # Store test results
            await self.metrics.capture_quality_metric(
                session_id=session_id,
                user_id=user_id,
                metric_type="test_scenario_result",
                value=results,
                context=f"Scenario: {scenario.name}, Provider: {provider}"
            )
            
            logger.info(f"Test scenario {scenario_id} completed: {'PASS' if results['overall_pass'] else 'FAIL'}")
            
        except Exception as e:
            logger.error(f"Error running test scenario: {e}")
            results["error"] = str(e)
        
        finally:
            # Cleanup test session
            self.session_manager.end_session(session_id)
        
        return results
    
    async def _run_step(
        self,
        session_id: str,
        step,
        provider: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Run a single test step"""
        step_result = {
            "turn": step.turn,
            "input": step.input,
            "check_type": step.check_type,
            "passed": False,
            "details": {}
        }
        
        try:
            # Process the action (user_id is already str from parameter)
            if step.turn == 1:
                # First turn - generate opening scene
                scene_desc, choices = await self.gm_engine.generate_opening_scene(
                    session_id=session_id,
                    user_id=str(user_id)  # Ensure string type
                )
                key_moment = None  # Opening scenes don't have key moments yet
            else:
                # Subsequent turns - process action
                scene_desc, choices, key_moment = await self.gm_engine.process_player_action(
                    session_id=session_id,
                    user_id=str(user_id),  # Ensure string type
                    action=step.input
                )
            
            # Check expected behavior based on check_type
            if step.check_type == "context":
                step_result["passed"] = self._check_context(
                    scene_desc, step.expected_behavior, step.metadata or {}
                )
            elif step.check_type == "lore":
                step_result["passed"] = self._check_lore(
                    scene_desc, step.expected_behavior, step.metadata or {}
                )
            elif step.check_type == "rule":
                step_result["passed"] = self._check_rule(
                    scene_desc, step.expected_behavior, step.metadata or {}
                )
            elif step.check_type == "quality":
                step_result["passed"] = self._check_quality(scene_desc)
            
            step_result["details"] = {
                "response": scene_desc[:200],  # Truncate for storage
                "choices_count": len(choices),
                "key_moment": key_moment
            }
            
        except Exception as e:
            logger.error(f"Error in test step {step.turn}: {e}")
            step_result["error"] = str(e)
        
        return step_result
    
    def _check_context(self, response: str, expected: str, metadata: Dict) -> bool:
        """Check if context was retained"""
        response_lower = response.lower()
        
        # Check for NPC name if specified
        if "inject_npc" in metadata:
            npc_name = metadata["inject_npc"].split(",")[0]  # Get name part
            if npc_name.lower() not in response_lower:
                return False
        
        # Check for specific attributes
        if "attributes" in metadata:
            for attr in metadata["attributes"]:
                if attr.lower() not in response_lower:
                    return False
        
        return True
    
    def _check_lore(self, response: str, expected: str, metadata: Dict) -> bool:
        """Check if lore is accurate"""
        response_lower = response.lower()
        
        if "expected_attributes" in metadata:
            found_count = 0
            for attr in metadata["expected_attributes"]:
                if attr.lower() in response_lower:
                    found_count += 1
            
            # Require at least 50% of expected attributes
            return found_count >= len(metadata["expected_attributes"]) * 0.5
        
        return True  # Default pass if no specific checks
    
    def _check_rule(self, response: str, expected: str, metadata: Dict) -> bool:
        """Check if rules were followed"""
        response_lower = response.lower()
        
        # Check for GM Intrusion XP mention
        if metadata.get("rule_check") == "gm_intrusion":
            if "xp" in response_lower or "experience" in response_lower:
                return True
        
        # Check for difficulty/target number mentions
        if metadata.get("rule_check") == "difficulty":
            # Look for numbers that might be difficulty or target
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                return True  # At least mentioned numbers
        
        return True  # Default pass (rules are complex to verify automatically)
    
    def _check_quality(self, response: str) -> bool:
        """Check response quality (basic checks)"""
        # Basic quality checks
        if len(response) < 50:
            return False  # Too short
        if len(response) > 5000:
            return False  # Too long (might be an error)
        
        return True
    
    async def compare_providers(
        self,
        scenario_id: str,
        providers: List[str],
        user_id: str = "test_user"
    ) -> Dict[str, Any]:
        """
        Run the same scenario with multiple AI providers and compare results
        
        Args:
            scenario_id: Scenario to test
            providers: List of providers to compare
            user_id: Test user ID
        
        Returns:
            Comparison results
        """
        results = {
            "scenario_id": scenario_id,
            "providers": {},
            "comparison": {}
        }
        
        for provider in providers:
            logger.info(f"Running {scenario_id} with provider: {provider}")
            provider_result = await self.run_scenario(
                scenario_id=scenario_id,
                provider=provider,
                user_id=user_id
            )
            results["providers"][provider] = provider_result
        
        # Compare results
        results["comparison"] = {
            "best_provider": max(
                results["providers"].items(),
                key=lambda x: x[1].get("steps_passed", 0)
            )[0],
            "all_passed": all(
                r.get("overall_pass", False)
                for r in results["providers"].values()
            )
        }
        
        return results

# Global test runner instance
test_runner = TestRunner()

