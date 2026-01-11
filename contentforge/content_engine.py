"""
Content Engine for ContentForge AI
Central orchestrator for content generation
"""

import logging
from typing import Optional, Dict, List

from .gemini_handler import GeminiHandler
from .prompts import get_prompt
from .database import save_content, get_content_history
from .config import CONTENT_TYPES

logger = logging.getLogger(__name__)


class ContentEngine:
    """
    Main content generation engine.
    Coordinates between UI, AI handler, prompts, and database.
    """
    
    def __init__(self):
        self.ai = GeminiHandler()
        self.current_network = "instagram"
        self.current_content_type = "post"
        self.last_generated = ""
    
    def is_ready(self) -> bool:
        """Check if engine is ready to generate content."""
        return self.ai.is_configured()
    
    def set_network(self, network: str):
        """Set current social network."""
        self.current_network = network
    
    def set_content_type(self, content_type: str):
        """Set current content type."""
        self.current_content_type = content_type
    
    def generate(self, topic: str, save: bool = True) -> str:
        """
        Generate content for the current network and type.
        
        Args:
            topic: User's topic/idea
            save: Whether to save to database
            
        Returns:
            Generated content string
        """
        if not topic.strip():
            return "❌ Por favor, ingresa un tema o idea para generar contenido."
        
        # Get specialized prompt
        prompt = get_prompt(self.current_network, self.current_content_type)
        if not prompt:
            prompt = get_prompt(self.current_network, "default")
        
        # Determine if we need pro model (for scripts/long content)
        use_pro = self.current_content_type in ["script", "thread"]
        
        # Generate content
        content = self.ai.generate_content(
            topic=topic,
            network=self.current_network,
            content_type=self.current_content_type,
            network_prompt=prompt,
            use_pro=use_pro
        )
        
        self.last_generated = content
        
        # Save to database
        if save and not content.startswith("❌"):
            save_content(
                network=self.current_network,
                content_type=self.current_content_type,
                topic=topic,
                content=content
            )
        
        return content
    
    def regenerate(self, topic: str) -> str:
        """Regenerate content with same parameters."""
        return self.generate(topic, save=True)
    
    def improve(self, suggestions: str) -> str:
        """Improve last generated content."""
        if not self.last_generated:
            return "❌ No hay contenido previo para mejorar."
        
        improved = self.ai.improve_content(self.last_generated, suggestions)
        self.last_generated = improved
        return improved
    
    def generate_hashtags(self, topic: str) -> List[str]:
        """Generate hashtags for topic."""
        return self.ai.generate_hashtags(topic, self.current_network)
    
    def generate_captions(self, context: str) -> List[str]:
        """Generate caption options."""
        return self.ai.generate_captions(context)
    
    def generate_video_script(self, topic: str, duration: int = 30) -> Dict:
        """Generate structured video script."""
        prompt = get_prompt(self.current_network, "script")
        return self.ai.generate_video_script(topic, duration, self.current_network, prompt)
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get content generation history."""
        return get_content_history(limit)
    
    def get_available_content_types(self) -> Dict:
        """Get available content types with metadata."""
        return CONTENT_TYPES.copy()
