"""
Metrics Collector
Captures all LLM interactions, performance data, and quality metrics
Dual persistence: Log files + Mem0
"""

import logging
import json
import time
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from mem0_layer import echo_memory

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores metrics for LLM evaluation"""
    
    def __init__(self, log_file: str = "logs/gm_metrics.log"):
        """Initialize metrics collector"""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory = echo_memory
        logger.info(f"MetricsCollector initialized, logging to {log_file}")
    
    async def capture_ai_interaction(
        self,
        session_id: str,
        user_id: str,
        provider: str,
        prompt: str,
        response: str,
        response_time_ms: float,
        token_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Capture an AI interaction with full metrics
        
        Args:
            session_id: Game session ID
            user_id: User ID
            provider: AI provider name (mistral, claude, gemini, grok)
            prompt: Input prompt
            response: AI response
            response_time_ms: Response time in milliseconds
            token_count: Estimated token count (optional)
            metadata: Additional metadata
        """
        timestamp = datetime.now().isoformat()
        
        metric = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "provider": provider,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "response_time_ms": response_time_ms,
            "token_count": token_count,
            "metadata": metadata or {}
        }
        
        # Log to file (JSON lines format)
        await self._log_to_file(metric, prompt, response)
        
        # Store structured metrics in Mem0
        await self._store_in_memory(user_id, metric)
        
        logger.debug(f"Captured metrics for {provider} interaction in session {session_id}")
    
    async def capture_quality_metric(
        self,
        session_id: str,
        user_id: str,
        metric_type: str,
        value: Any,
        context: Optional[str] = None
    ):
        """
        Capture a quality metric (creativity, lore accuracy, etc.)
        
        Args:
            session_id: Game session ID
            user_id: User ID
            metric_type: Type of metric (creativity, lore_accuracy, rule_compliance, etc.)
            value: Metric value
            context: Optional context description
        """
        timestamp = datetime.now().isoformat()
        
        metric = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "metric_type": metric_type,
            "value": value,
            "context": context
        }
        
        # Log to file
        await self._log_to_file(metric, context or "", "")
        
        # Store in Mem0
        await self._store_in_memory(user_id, metric)
    
    async def capture_context_retention(
        self,
        session_id: str,
        user_id: str,
        turns_since_reference: int,
        recall_success: bool,
        reference_text: str,
        recalled_text: Optional[str] = None
    ):
        """
        Capture context retention test result
        
        Args:
            session_id: Game session ID
            user_id: User ID
            turns_since_reference: How many turns ago the reference was made
            recall_success: Whether the AI successfully recalled the reference
            reference_text: Original reference text
            recalled_text: What the AI recalled (if successful)
        """
        timestamp = datetime.now().isoformat()
        
        metric = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "metric_type": "context_retention",
            "turns_since_reference": turns_since_reference,
            "recall_success": recall_success,
            "reference_text": reference_text,
            "recalled_text": recalled_text
        }
        
        # Log to file
        await self._log_to_file(metric, reference_text, recalled_text or "")
        
        # Store in Mem0
        await self._store_in_memory(user_id, metric)
    
    async def capture_rule_compliance(
        self,
        session_id: str,
        user_id: str,
        rule_name: str,
        compliant: bool,
        expected: str,
        actual: str
    ):
        """
        Capture Cypher System rule compliance check
        
        Args:
            session_id: Game session ID
            user_id: User ID
            rule_name: Name of the rule being checked
            compliant: Whether the AI followed the rule
            expected: Expected behavior
            actual: Actual behavior
        """
        timestamp = datetime.now().isoformat()
        
        metric = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "metric_type": "rule_compliance",
            "rule_name": rule_name,
            "compliant": compliant,
            "expected": expected,
            "actual": actual
        }
        
        # Log to file
        await self._log_to_file(metric, expected, actual)
        
        # Store in Mem0
        await self._store_in_memory(user_id, metric)
    
    async def _log_to_file(self, metric: Dict, prompt: str, response: str):
        """Log metric to JSON lines file (async-safe)"""
        try:
            log_entry = {
                **metric,
                "prompt": prompt[:500] if prompt else "",  # Truncate for storage
                "response": response[:500] if response else ""
            }
            
            # Use async-safe file writing (run in executor to avoid blocking)
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._write_log_entry,
                log_entry
            )
        except Exception as e:
            logger.error(f"Failed to log metric to file: {e}")
    
    def _write_log_entry(self, log_entry: Dict):
        """Synchronous helper for file writing"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    async def _store_in_memory(self, user_id: str, metric: Dict):
        """Store metric in Mem0 for queryable access"""
        try:
            # Format metric as searchable text
            metric_text = f"Metric: {metric.get('metric_type', 'interaction')}"
            if 'provider' in metric:
                metric_text += f" | Provider: {metric['provider']}"
            if 'value' in metric:
                metric_text += f" | Value: {metric['value']}"
            if 'response_time_ms' in metric:
                metric_text += f" | Response Time: {metric['response_time_ms']}ms"
            
            await self.memory.store_memory(
                user_id=user_id,
                content=metric_text,
                metadata={
                    "type": "gm_metric",
                    "metric_data": metric
                }
            )
        except Exception as e:
            logger.error(f"Failed to store metric in Mem0: {e}")

class PerformanceTimer:
    """Context manager for timing AI operations"""
    
    def __init__(self, collector: MetricsCollector, session_id: str, user_id: str, provider: str):
        """Initialize timer"""
        self.collector = collector
        self.session_id = session_id
        self.user_id = user_id
        self.provider = provider
        self.start_time = None
        self.prompt = None
        self.response = None
    
    async def __aenter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End timing and capture metrics"""
        if self.start_time and self.prompt and self.response:
            response_time_ms = (time.time() - self.start_time) * 1000
            await self.collector.capture_ai_interaction(
                session_id=self.session_id,
                user_id=self.user_id,
                provider=self.provider,
                prompt=self.prompt,
                response=self.response,
                response_time_ms=response_time_ms
            )

# Global metrics collector instance
metrics_collector = MetricsCollector()

