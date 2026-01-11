"""
Gemini AI Handler for ContentForge AI
Professional content generation using Google Gemini API
"""

import logging
from typing import Optional, Dict, List
import google.generativeai as genai

from .config import GEMINI_API_KEY, GEMINI_MODEL_FAST, GEMINI_MODEL_PRO

logger = logging.getLogger(__name__)

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiHandler:
    """
    Advanced AI Handler for Social Media Content Generation.
    Uses Gemini API with specialized prompts per network.
    """
    
    def __init__(self):
        self.model_fast = None
        self.model_pro = None
        
        if GEMINI_API_KEY:
            self.model_fast = genai.GenerativeModel(GEMINI_MODEL_FAST)
            self.model_pro = genai.GenerativeModel(GEMINI_MODEL_PRO)
    
    def is_configured(self) -> bool:
        """Check if Gemini API is configured."""
        return self.model_fast is not None
    
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
            
            response = model.generate_content(full_prompt)
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
            
            response = self.model_pro.generate_content(prompt)
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
            
            response = self.model_fast.generate_content(prompt)
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
            
            response = self.model_fast.generate_content(prompt)
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
            
            response = self.model_fast.generate_content(prompt)
            hashtags = [f"#{h.strip().replace('#', '')}" for h in response.text.split('\n') if h.strip()]
            return hashtags[:count]
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return ["#error"]


def test_connection() -> bool:
    """Test Gemini API connection."""
    handler = GeminiHandler()
    if not handler.is_configured():
        print("❌ Gemini API no configurada")
        return False
    
    try:
        response = handler.model_fast.generate_content("Di 'Hola, ContentForge!'")
        print(f"✅ Conexión exitosa: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
