"""
Scene Image Generation
Uses Gemini API for generating images at key moments
"""

import logging
from typing import Optional
from ai_coordinator import ai_coordinator

logger = logging.getLogger(__name__)

class SceneImageGenerator:
    """Generates images for key game moments"""
    
    def __init__(self):
        """Initialize image generator"""
        self.ai_coordinator = ai_coordinator
        logger.info("SceneImageGenerator initialized")
    
    async def generate_scene_image(
        self,
        scene_description: str,
        moment_type: str,
        user_id: str,
        character_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate an image for a scene
        
        Args:
            scene_description: Description of the current scene
            moment_type: Type of key moment (combat, discovery, boss, etc.)
            user_id: User ID for logging
            character_name: Optional character name to include
        
        Returns:
            Image URL or data, or None if generation failed
        """
        # Build image prompt based on moment type
        if moment_type == "combat":
            prompt = f"Epic combat scene in post-apocalyptic Melbourne: {scene_description}. Dynamic action, dramatic lighting, Nexus Arcanum aesthetic."
        elif moment_type == "discovery":
            prompt = f"Discovery moment in Nexus Arcanum world: {scene_description}. Sense of wonder, magical elements, detailed environment."
        elif moment_type == "boss":
            prompt = f"Boss encounter in Nexus Arcanum: {scene_description}. Intense, dramatic, high stakes, cinematic composition."
        elif moment_type == "luminari":
            prompt = f"Luminari encounter - ethereal light beings in Nexus Arcanum: {scene_description}. Radiant, mystical, otherworldly."
        elif moment_type == "umbralari":
            prompt = f"Umbralari encounter - corrupted shadow beings in Nexus Arcanum: {scene_description}. Dark, menacing, corrupted energy."
        elif moment_type == "weave_ability":
            prompt = f"Nexus Weave magic in action: {scene_description}. Magical energy, Nexus threads visible, powerful moment."
        else:
            prompt = f"Scene from Nexus Arcanum: {scene_description}. Post-apocalyptic Melbourne, urban fantasy, atmospheric."
        
        if character_name:
            prompt += f" Featuring {character_name}."
        
        try:
            image_data = await self.ai_coordinator.generate_image(
                prompt=prompt,
                user_id=user_id
            )
            
            if image_data:
                logger.info(f"Generated image for {moment_type} moment for user {user_id}")
            else:
                logger.warning(f"Image generation returned None for user {user_id}")
            
            return image_data
            
        except Exception as e:
            logger.error(f"Error generating scene image: {e}")
            return None
    
    def should_generate_image(self, moment_type: Optional[str]) -> bool:
        """Determine if an image should be generated for this moment"""
        if not moment_type:
            return False
        
        # Generate images for key moments
        key_moments = ["combat", "discovery", "boss", "luminari", "umbralari", "weave_ability"]
        return moment_type in key_moments

# Global image generator instance
image_generator = SceneImageGenerator()

