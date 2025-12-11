"""
Echo Bot AI Coordinator
Multi-AI routing system with Mistral as local coordinator
External APIs: Claude (Anthropic), Grok (X.AI), Gemini (Google)
"""

import logging
import ollama
import anthropic
import google.generativeai as genai
from openai import OpenAI
from typing import Optional
from config import Config
from mem0_layer import echo_memory

logger = logging.getLogger(__name__)

class AICoordinator:
    """Coordinates AI requests across multiple providers"""
    
    def __init__(self):
        """Initialize all AI clients"""
        # Local Ollama/Mistral client
        self.ollama_client = ollama.Client(host=Config.OLLAMA_URL)
        self.ollama_model = Config.OLLAMA_MODEL
        logger.info(f"Ollama initialized with model: {self.ollama_model}")
        
        # Anthropic (Claude) client
        if Config.ANTHROPIC_API_KEY:
            self.claude_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            logger.info("Claude (Anthropic) initialized")
        else:
            self.claude_client = None
            logger.warning("Claude not configured - missing ANTHROPIC_API_KEY")
        
        # X.AI (Grok) client - uses OpenAI-compatible API
        if Config.XAI_API_KEY:
            self.grok_client = OpenAI(
                api_key=Config.XAI_API_KEY,
                base_url="https://api.x.ai/v1"
            )
            logger.info("Grok (X.AI) initialized")
        else:
            self.grok_client = None
            logger.warning("Grok not configured - missing XAI_API_KEY")
        
        # Google (Gemini) client
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini (Google) initialized")
        else:
            self.gemini_model = None
            logger.warning("Gemini not configured - missing GOOGLE_API_KEY")
    
    # =========================================================================
    # MISTRAL (LOCAL) - Primary AI, always available
    # =========================================================================
    async def ask_mistral(
        self,
        prompt: str,
        user_id: str,
        system_context: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """
        Get response from local Mistral via Ollama
        """
        try:
            messages = []
            
            # System context
            if system_context:
                messages.append({"role": "system", "content": system_context})
            else:
                messages.append({
                    "role": "system",
                    "content": (
                        "You are Echo, an AI assistant for the Nexus Arcanum worldbuilding project. "
                        "You help creators develop a post-apocalyptic urban fantasy world set in Melbourne, Australia. "
                        "Be creative, supportive, and remember details from past conversations."
                    )
                })
            
            # Add memory context
            if use_memory:
                context_memories = await echo_memory.get_user_context(user_id, limit=5)
                if context_memories:
                    memory_text = "\n".join([
                        f"- {mem.get('memory', mem.get('text', ''))}" 
                        for mem in context_memories
                    ])
                    messages.append({
                        "role": "system",
                        "content": f"Previous context:\n{memory_text}"
                    })
            
            messages.append({"role": "user", "content": prompt})
            
            # Call Ollama
            response = self.ollama_client.chat(model=self.ollama_model, messages=messages)
            ai_response = response['message']['content']
            
            # Store in memory
            if use_memory:
                await echo_memory.store_memory(
                    user_id=user_id,
                    content=f"User asked: {prompt}\nMistral responded: {ai_response[:200]}...",
                    metadata={"type": "conversation", "ai": "mistral"}
                )
            
            logger.info(f"Mistral response for user {user_id}: {len(ai_response)} chars")
            return ai_response
            
        except Exception as e:
            logger.error(f"Mistral error: {e}")
            return f"Mistral error: {str(e)}\n\nCheck that Ollama is running."
    
    # =========================================================================
    # CLAUDE (ANTHROPIC) - Deep reasoning, long-form content
    # =========================================================================
    async def ask_claude(
        self,
        prompt: str,
        user_id: str,
        system_context: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """
        Get response from Claude (Anthropic)
        Best for: Deep reasoning, long-form writing, worldbuilding depth
        """
        if not self.claude_client:
            return "Claude not configured. Add ANTHROPIC_API_KEY to .env"
        
        try:
            # Build system message
            system_msg = system_context or (
                "You are helping with the Nexus Arcanum worldbuilding project - "
                "a post-apocalyptic urban fantasy set in Melbourne, Australia. "
                "Be creative, detailed, and helpful."
            )
            
            # Add memory context
            if use_memory:
                context_memories = await echo_memory.get_user_context(user_id, limit=5)
                if context_memories:
                    memory_text = "\n".join([
                        f"- {mem.get('memory', mem.get('text', ''))}" 
                        for mem in context_memories
                    ])
                    system_msg += f"\n\nContext from previous conversations:\n{memory_text}"
            
            # Call Claude
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_msg,
                messages=[{"role": "user", "content": prompt}]
            )
            
            ai_response = response.content[0].text
            
            # Store in memory
            if use_memory:
                await echo_memory.store_memory(
                    user_id=user_id,
                    content=f"User asked Claude: {prompt}\nClaude responded: {ai_response[:200]}...",
                    metadata={"type": "conversation", "ai": "claude"}
                )
            
            logger.info(f"Claude response for user {user_id}: {len(ai_response)} chars")
            return ai_response
            
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return f"Claude error: {str(e)}"
    
    # =========================================================================
    # GROK (X.AI) - Real-time info, different perspective
    # =========================================================================
    async def ask_grok(
        self,
        prompt: str,
        user_id: str,
        system_context: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """
        Get response from Grok (X.AI)
        Best for: Current events, different perspective, humor
        """
        if not self.grok_client:
            return "Grok not configured. Add XAI_API_KEY to .env"
        
        try:
            messages = []
            
            # System context
            system_msg = system_context or (
                "You are helping with the Nexus Arcanum worldbuilding project - "
                "a post-apocalyptic urban fantasy set in Melbourne, Australia. "
                "Be creative, insightful, and bring your unique perspective."
            )
            
            # Add memory context
            if use_memory:
                context_memories = await echo_memory.get_user_context(user_id, limit=5)
                if context_memories:
                    memory_text = "\n".join([
                        f"- {mem.get('memory', mem.get('text', ''))}" 
                        for mem in context_memories
                    ])
                    system_msg += f"\n\nContext from previous conversations:\n{memory_text}"
            
            messages.append({"role": "system", "content": system_msg})
            messages.append({"role": "user", "content": prompt})
            
            # Call Grok
            response = self.grok_client.chat.completions.create(
                model="grok-3-latest",
                messages=messages,
                max_tokens=4096
            )
            
            ai_response = response.choices[0].message.content
            
            # Store in memory
            if use_memory:
                await echo_memory.store_memory(
                    user_id=user_id,
                    content=f"User asked Grok: {prompt}\nGrok responded: {ai_response[:200]}...",
                    metadata={"type": "conversation", "ai": "grok"}
                )
            
            logger.info(f"Grok response for user {user_id}: {len(ai_response)} chars")
            return ai_response
            
        except Exception as e:
            logger.error(f"Grok error: {e}")
            return f"Grok error: {str(e)}"
    
    # =========================================================================
    # GEMINI (GOOGLE) - Multi-modal, fast responses
    # =========================================================================
    async def ask_gemini(
        self,
        prompt: str,
        user_id: str,
        system_context: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """
        Get response from Gemini (Google)
        Best for: Multi-modal tasks, fast responses, different reasoning
        """
        if not self.gemini_model:
            return "Gemini not configured. Add GOOGLE_API_KEY to .env"
        
        try:
            # Build full prompt with context
            full_prompt = system_context or (
                "You are helping with the Nexus Arcanum worldbuilding project - "
                "a post-apocalyptic urban fantasy set in Melbourne, Australia.\n\n"
            )
            
            # Add memory context
            if use_memory:
                context_memories = await echo_memory.get_user_context(user_id, limit=5)
                if context_memories:
                    memory_text = "\n".join([
                        f"- {mem.get('memory', mem.get('text', ''))}" 
                        for mem in context_memories
                    ])
                    full_prompt += f"Context from previous conversations:\n{memory_text}\n\n"
            
            full_prompt += f"User question: {prompt}"
            
            # Call Gemini
            response = self.gemini_model.generate_content(full_prompt)
            ai_response = response.text
            
            # Store in memory
            if use_memory:
                await echo_memory.store_memory(
                    user_id=user_id,
                    content=f"User asked Gemini: {prompt}\nGemini responded: {ai_response[:200]}...",
                    metadata={"type": "conversation", "ai": "gemini"}
                )
            
            logger.info(f"Gemini response for user {user_id}: {len(ai_response)} chars")
            return ai_response
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"Gemini error: {str(e)}"
    
    # =========================================================================
    # DEFAULT ROUTER - Main entry point (uses Mistral)
    # =========================================================================
    async def get_ai_response(
        self,
        prompt: str,
        user_id: str,
        system_context: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """
        Default AI response - routes to Mistral (local)
        Use specific ask_* methods for other AIs
        """
        return await self.ask_mistral(prompt, user_id, system_context, use_memory)
    
    # =========================================================================
    # CONNECTION TESTS
    # =========================================================================
    async def test_connection(self) -> tuple[bool, str]:
        """Test connection to local Ollama/Mistral"""
        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[{"role": "user", "content": "Say 'Echo online' if you can read this."}]
            )
            return True, f"Connected to {self.ollama_model}: {response['message']['content']}"
        except Exception as e:
            return False, f"Failed to connect to Ollama: {str(e)}"
    
    def get_available_ais(self) -> dict:
        """Return status of all available AI providers"""
        return {
            "mistral": {"available": True, "model": self.ollama_model, "type": "local"},
            "claude": {"available": self.claude_client is not None, "model": "claude-sonnet-4-20250514", "type": "api"},
            "grok": {"available": self.grok_client is not None, "model": "grok-3-latest", "type": "api"},
            "gemini": {"available": self.gemini_model is not None, "model": "gemini-1.5-flash", "type": "api"}
        }
    
    # =========================================================================
    # IMAGE GENERATION - Gemini Imagen
    # =========================================================================
    async def generate_image(
        self,
        prompt: str,
        user_id: str
    ) -> Optional[str]:
        """
        Generate an image using Gemini Imagen
        
        Args:
            prompt: Image generation prompt
            user_id: User ID for logging
        
        Returns:
            Image URL or base64 data, or None if failed
        """
        if not self.gemini_model:
            logger.warning("Gemini not configured - cannot generate images")
            return None
        
        try:
            # Note: Gemini 1.5 Flash doesn't have direct image generation
            # We'll use the text model to generate a detailed description
            # For actual image generation, you'd need Gemini Imagen API or another service
            # This is a placeholder that can be extended with actual Imagen integration
            
            # Enhanced prompt for image generation
            image_prompt = f"""Create a vivid, detailed description for an image generator:

{prompt}

The image should be:
- Set in post-apocalyptic Melbourne, Australia
- Nexus Arcanum world aesthetic (urban fantasy, magical elements)
- High quality, cinematic composition
- Detailed and atmospheric

Return only the enhanced image description, ready for an image generator."""
            
            # For now, return the enhanced prompt
            # In production, this would call Gemini Imagen API
            logger.info(f"Image generation requested for user {user_id}: {prompt[:50]}...")
            
            # TODO: Integrate with actual Gemini Imagen API when available
            # For now, return None to indicate image generation not fully implemented
            return None
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

# Global AI coordinator instance
ai_coordinator = AICoordinator()
