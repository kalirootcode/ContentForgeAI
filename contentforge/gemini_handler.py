"""
Gemini AI Handler for ContentForge AI
Professional content generation using Google Gemini API
Using the new google.genai package
"""

import logging
import os
from typing import Optional, Dict, List

from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, GEMINI_MODEL_FAST, GEMINI_MODEL_PRO

logger = logging.getLogger(__name__)

# Configure client
_client: Optional[genai.Client] = None

if GEMINI_API_KEY:
    _client = genai.Client(api_key=GEMINI_API_KEY)


class GeminiHandler:
    """
    Advanced AI Handler for Social Media Content Generation.
    Uses Gemini API with specialized prompts per network.
    """
    
    def __init__(self):
        self.client = _client
        self.model_fast = GEMINI_MODEL_FAST
        self.model_pro = GEMINI_MODEL_PRO
    
    def is_configured(self) -> bool:
        """Check if Gemini API is configured."""
        return self.client is not None
    
    def generate_content(
        self, 
        topic: str, 
        network: str, 
        content_type: str,
        network_prompt: str,
        use_pro: bool = False
    ) -> str:
        """
        Generate content for a specific social network.
        
        Args:
            topic: Main topic/idea for content
            network: Social network ID
            content_type: Type of content (post, story, script, etc.)
            network_prompt: Specialized prompt for the network
            use_pro: Use Pro model for longer content
            
        Returns:
            Generated content string
        """
        if not self.is_configured():
            return "❌ Error: API de Gemini no configurada. Agrega tu GEMINI_API_KEY en .env"
        
        try:
            model = self.model_pro if use_pro else self.model_fast
            
            full_prompt = f"""
{network_prompt}

TEMA/IDEA DEL USUARIO: {topic}

TIPO DE CONTENIDO: {content_type}

Genera el contenido ahora, listo para publicar. Responde SOLO con el contenido, sin explicaciones adicionales.
"""
            
            response = self.client.models.generate_content(
                model=model,
                contents=full_prompt
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"❌ Error al generar contenido: {str(e)}"
    
    def generate_video_script(
        self, 
        topic: str, 
        duration: int,
        network: str,
        network_prompt: str
    ) -> Dict:
        """
        Generate a complete video script with sections.
        
        Args:
            topic: Video topic
            duration: Duration in seconds (15, 30, 60, etc.)
            network: Target network
            network_prompt: Specialized prompt
            
        Returns:
            Dictionary with hook, body, cta sections
        """
        if not self.is_configured():
            return {"error": "API de Gemini no configurada"}
        
        try:
            prompt = f"""
{network_prompt}

GENERA UN GUIÓN DE VIDEO DE {duration} SEGUNDOS SOBRE: {topic}

Formato de respuesta JSON:
{{
    "hook": "Los primeros 3 segundos para captar atención (CRUCIAL)",
    "body": "Contenido principal del video",
    "cta": "Llamada a la acción final",
    "text_overlay": "Texto para poner en pantalla",
    "hashtags": ["lista", "de", "hashtags"]
}}

Responde SOLO con el JSON, sin explicaciones.
"""
            
            response = self.client.models.generate_content(
                model=self.model_pro,
                contents=prompt
            )
            import json
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return {"error": str(e)}
    
    def generate_captions(self, context: str, style: str = "profesional") -> List[str]:
        """
        Generate multiple caption options.
        
        Args:
            context: Description of the content
            style: Caption style (profesional, casual, viral)
            
        Returns:
            List of caption options
        """
        if not self.is_configured():
            return ["❌ API no configurada"]
        
        try:
            prompt = f"""
Genera 5 opciones de captions/pies de foto para:
{context}

Estilo: {style}

Reglas:
- Cada caption debe ser único y atractivo
- Incluir emojis relevantes
- Variedad de longitudes (corto, medio, largo)
- Al menos uno con pregunta para engagement

Responde SOLO con los 5 captions, numerados del 1 al 5.
"""
            
            response = self.client.models.generate_content(
                model=self.model_fast,
                contents=prompt
            )
            lines = [l.strip() for l in response.text.split('\n') if l.strip()]
            return lines[:5]
            
        except Exception as e:
            logger.error(f"Error generating captions: {e}")
            return [f"❌ Error: {str(e)}"]
    
    def improve_content(self, original: str, suggestions: str) -> str:
        """
        Improve existing content based on suggestions.
        
        Args:
            original: Original content
            suggestions: User suggestions for improvement
            
        Returns:
            Improved content
        """
        if not self.is_configured():
            return original
        
        try:
            prompt = f"""
CONTENIDO ORIGINAL:
{original}

SUGERENCIAS DE MEJORA:
{suggestions}

Mejora el contenido según las sugerencias. Mantén la esencia pero hazlo más efectivo.
Responde SOLO con el contenido mejorado.
"""
            
            response = self.client.models.generate_content(
                model=self.model_fast,
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error improving content: {e}")
            return original
    
    def generate_hashtags(self, topic: str, network: str, count: int = 30) -> List[str]:
        """
        Generate optimized hashtags for a topic.
        
        Args:
            topic: Content topic
            network: Target network
            count: Number of hashtags
            
        Returns:
            List of hashtags
        """
        if not self.is_configured():
            return ["#error"]
        
        try:
            prompt = f"""
Genera {count} hashtags optimizados para {network} sobre: {topic}

Reglas:
- Mezcla hashtags populares y nicho
- Incluir hashtags en español e inglés
- Sin el símbolo # (solo la palabra)
- Ordenar por relevancia

Responde SOLO con los hashtags, uno por línea.
"""
            
            response = self.client.models.generate_content(
                model=self.model_fast,
                contents=prompt
            )
            hashtags = [f"#{h.strip().replace('#', '')}" for h in response.text.split('\n') if h.strip()]
            return hashtags[:count]
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return ["#error"]
    
    def generate(self, prompt: str, use_pro: bool = False) -> str:
        """
        Simple text generation with a custom prompt.
        
        Args:
            prompt: The prompt to generate from
            use_pro: Use Pro model
            
        Returns:
            Generated text
        """
        if not self.is_configured():
            return "❌ API no configurada"
        
        try:
            model = self.model_pro if use_pro else self.model_fast
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error in generate: {e}")
            return f"❌ Error: {str(e)}"
    
    def generate_with_image(self, prompt: str, image_base64: str, mime_type: str = "image/jpeg") -> str:
        """
        Generate content based on an image using Gemini Vision.
        
        Args:
            prompt: Text prompt describing what to analyze
            image_base64: Base64 encoded image data
            mime_type: MIME type of the image
            
        Returns:
            Generated analysis/content
        """
        if not self.is_configured():
            return "❌ API no configurada"
        
        try:
            # Create inline data for the image
            image_part = types.Part.from_bytes(
                data=__import__('base64').b64decode(image_base64),
                mime_type=mime_type
            )
            
            response = self.client.models.generate_content(
                model=self.model_pro,  # Use Pro for vision
                contents=[prompt, image_part]
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error in generate_with_image: {e}")
            return f"❌ Error: {str(e)}"


# Singleton instance
_handler_instance: Optional[GeminiHandler] = None


def get_gemini_handler() -> GeminiHandler:
    """Get singleton GeminiHandler instance."""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = GeminiHandler()
    return _handler_instance


def test_connection() -> bool:
    """Test Gemini API connection."""
    handler = GeminiHandler()
    if not handler.is_configured():
        print("❌ Gemini API no configurada")
        return False
    
    try:
        response = handler.client.models.generate_content(
            model=handler.model_fast,
            contents="Di 'Hola, ContentForge!'"
        )
        print(f"✅ Conexión exitosa: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
