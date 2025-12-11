"""
Echo Bot Memory Layer - Mem0 Platform Integration
Handles persistent memory storage and retrieval for user context
Uses Mem0 Platform (hosted service) - memories shared across projects
"""

import logging
from typing import List, Dict, Any, Optional
from mem0 import MemoryClient
from config import Config

logger = logging.getLogger(__name__)

class EchoMemory:
    """Wrapper for Mem0 Platform memory operations"""
    
    def __init__(self):
        """Initialize Mem0 Platform client"""
        try:
            # Initialize Mem0 Platform client with API key
            # This connects to mem0.ai hosted service - no OpenAI needed
            self.client = MemoryClient(api_key=Config.MEM0_API_KEY)
            logger.info("Mem0 Platform client initialized - memories shared across projects")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            raise
    
    async def store_memory(
        self, 
        user_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a memory for a specific user
        
        Args:
            user_id: Discord user ID
            content: Memory content to store
            metadata: Optional metadata dict (e.g., {"type": "worldbuilding", "category": "character"})
        
        Returns:
            bool: True if successful
        """
        try:
            # Prepare metadata
            meta = metadata or {}
            meta["user_id"] = user_id
            
            # Store in Mem0 Platform
            self.client.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                metadata=meta
            )
            
            logger.info(f"Stored memory for user {user_id}: {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory for user {user_id}: {e}")
            return False
    
    async def search_memory(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories for a specific user
        
        Args:
            user_id: Discord user ID
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of memory dictionaries
        """
        try:
            # Search Mem0 Platform
            results = self.client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            logger.info(f"Found {len(results)} memories for user {user_id} with query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memories for user {user_id}: {e}")
            return []
    
    async def get_user_context(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent context/memories for a user
        
        Args:
            user_id: Discord user ID
            limit: Maximum number of memories to retrieve
        
        Returns:
            List of recent memory dictionaries
        """
        try:
            # Get all memories for user from Platform
            memories = self.client.get_all(user_id=user_id)
            
            # Return most recent memories (limited)
            recent = memories[:limit] if memories else []
            
            logger.info(f"Retrieved {len(recent)} context memories for user {user_id}")
            return recent
            
        except Exception as e:
            logger.error(f"Failed to get context for user {user_id}: {e}")
            return []
    
    async def clear_user_memory(self, user_id: str) -> bool:
        """
        Clear all memories for a specific user
        
        Args:
            user_id: Discord user ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete all memories for user
            self.client.delete_all(user_id=user_id)
            
            logger.info(f"Cleared all memories for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memories for user {user_id}: {e}")
            return False

# Global memory instance
echo_memory = EchoMemory()
