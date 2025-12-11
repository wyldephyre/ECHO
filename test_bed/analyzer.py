"""
Performance Analyzer
Generates reports and analyzes metrics from test bed data
"""

import logging
from typing import Dict, List, Any
from pathlib import Path
import json
from mem0_layer import echo_memory

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzes performance metrics and generates reports"""
    
    def __init__(self, log_file: str = "logs/gm_metrics.log"):
        """Initialize analyzer"""
        self.log_file = Path(log_file)
        self.memory = echo_memory
        logger.info("PerformanceAnalyzer initialized")
    
    async def analyze_session_metrics(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze metrics for a specific session
        
        Args:
            session_id: Session ID to analyze
            user_id: User ID
        
        Returns:
            Dict with analysis results
        """
        # Search memories for session metrics
        memories = await self.memory.search_memory(
            user_id=user_id,
            query=f"session {session_id}",
            limit=100
        )
        
        analysis = {
            "session_id": session_id,
            "total_interactions": 0,
            "providers_used": {},
            "avg_response_time": 0,
            "total_tokens": 0,
            "quality_scores": []
        }
        
        response_times = []
        token_counts = []
        
        for mem in memories:
            metadata = mem.get("metadata", {})
            metric_data = metadata.get("metric_data", {})
            
            if metric_data.get("session_id") == session_id:
                analysis["total_interactions"] += 1
                
                provider = metric_data.get("provider")
                if provider:
                    analysis["providers_used"][provider] = analysis["providers_used"].get(provider, 0) + 1
                
                if metric_data.get("response_time_ms"):
                    response_times.append(metric_data["response_time_ms"])
                
                if metric_data.get("token_count"):
                    token_counts.append(metric_data["token_count"])
                
                if metric_data.get("metric_type") == "quality":
                    analysis["quality_scores"].append(metric_data.get("value"))
        
        if response_times:
            analysis["avg_response_time"] = sum(response_times) / len(response_times)
            analysis["min_response_time"] = min(response_times)
            analysis["max_response_time"] = max(response_times)
        
        if token_counts:
            analysis["total_tokens"] = sum(token_counts)
            analysis["avg_tokens"] = sum(token_counts) / len(token_counts)
        
        return analysis
    
    async def generate_provider_comparison(
        self,
        user_id: str,
        providers: List[str]
    ) -> Dict[str, Any]:
        """
        Compare performance across AI providers
        
        Args:
            user_id: User ID
            providers: List of providers to compare
        
        Returns:
            Comparison report
        """
        comparison = {
            "providers": {},
            "best_provider": None,
            "fastest_provider": None,
            "most_accurate": None
        }
        
        for provider in providers:
            memories = await self.memory.search_memory(
                user_id=user_id,
                query=f"provider {provider}",
                limit=50
            )
            
            provider_data = {
                "interactions": len(memories),
                "response_times": [],
                "quality_scores": []
            }
            
            for mem in memories:
                metadata = mem.get("metadata", {})
                metric_data = metadata.get("metric_data", {})
                
                if metric_data.get("provider") == provider:
                    if metric_data.get("response_time_ms"):
                        provider_data["response_times"].append(metric_data["response_time_ms"])
                    if metric_data.get("metric_type") == "quality":
                        provider_data["quality_scores"].append(metric_data.get("value"))
            
            if provider_data["response_times"]:
                provider_data["avg_response_time"] = sum(provider_data["response_times"]) / len(provider_data["response_times"])
            
            if provider_data["quality_scores"]:
                provider_data["avg_quality"] = sum(provider_data["quality_scores"]) / len(provider_data["quality_scores"])
            
            comparison["providers"][provider] = provider_data
        
        # Determine best provider
        if comparison["providers"]:
            best = max(
                comparison["providers"].items(),
                key=lambda x: x[1].get("avg_quality", 0)
            )
            comparison["best_provider"] = best[0]
            
            fastest = min(
                comparison["providers"].items(),
                key=lambda x: x[1].get("avg_response_time", float('inf'))
            )
            comparison["fastest_provider"] = fastest[0]
        
        return comparison
    
    def read_log_file(self, limit: int = 100) -> List[Dict]:
        """
        Read metrics from log file
        
        Args:
            limit: Maximum number of entries to read
        
        Returns:
            List of metric dictionaries
        """
        if not self.log_file.exists():
            return []
        
        metrics = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:  # Read last N lines
                    try:
                        metric = json.loads(line.strip())
                        metrics.append(metric)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
        
        return metrics

# Global analyzer instance
analyzer = PerformanceAnalyzer()

