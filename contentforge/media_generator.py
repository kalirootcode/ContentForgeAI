"""
Media Generator for ContentForge AI
Uses Gemini API to generate images and video prompts based on content
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import Image
import io

from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, APP_DIR
from .database import get_connection

logger = logging.getLogger(__name__)

# Media directories
MEDIA_DIR = APP_DIR / "media"
IMAGES_DIR = MEDIA_DIR / "images"
VIDEOS_DIR = MEDIA_DIR / "videos"

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


class MediaGenerator:
    """Handles AI-powered media generation using Gemini."""
    
    def __init__(self):
        self.client = None
        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def _get_branding_instructions(self, network: str, media_type: str = 'image') -> str:
        """Get branding instructions from database."""
        conn = get_connection()
        cursor = conn.cursor()
        
        table = 'image_prompts' if media_type == 'image' else 'video_prompts'
        cursor.execute(f"""
            SELECT branding_instructions FROM {table}
            WHERE network = ?
            LIMIT 1
        """, (network,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['branding_instructions']
        return ""
    
    def analyze_content_for_image(self, content: str, network: str) -> str:
        """Analyze content and generate an optimized image prompt."""
        if not self.client:
            return ""
        
        branding = self._get_branding_instructions(network, 'image')
        
        system_prompt = f"""
Eres un experto en crear prompts para generación de imágenes AI.
Analiza el siguiente contenido de redes sociales y crea un prompt detallado
para generar una imagen que complemente perfectamente el contenido.

{branding}

REGLAS:
1. El prompt debe ser en inglés (mejor para AI de imágenes)
2. Incluir estilo visual específico
3. Mencionar colores, iluminación, composición
4. Especificar el formato (16:9 para posts, 9:16 para stories)
5. Mantener el branding cyberpunk/hacker
6. NO incluir texto en la imagen (difícil de generar correctamente)

Responde SOLO con el prompt de imagen, sin explicaciones.
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{system_prompt}\n\nCONTENIDO:\n{content}",
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating image prompt: {e}")
            return ""
    
    def generate_image(self, prompt: str, network: str, content_id: Optional[int] = None, aspect_ratio: str = "16:9") -> Optional[str]:
        """Generate an image using Gemini's image generation capability."""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        branding = self._get_branding_instructions(network, 'image')
        
        # Map aspect ratio to dimensions for prompt guidance
        ratio_desc = {
            "1:1": "square format",
            "4:3": "horizontal 4:3 format",
            "16:9": "widescreen 16:9 format",
            "9:16": "vertical portrait format (for stories/reels)",
            "3:4": "vertical 3:4 format"
        }
        
        full_prompt = f"""Generate an image for this request:
{prompt}

Format: {ratio_desc.get(aspect_ratio, 'widescreen')}

Style guidelines:
{branding}

Important: Create a visually striking, professional image suitable for social media. 
Use cyberpunk/tech aesthetic with dark backgrounds and neon accents (purple, cyan, green).
"""
        
        try:
            # Use Gemini 2.0 Flash with image generation
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                )
            )
            
            # Check if image was generated
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Save the image
                        image_data = part.inline_data.data
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        ratio_suffix = aspect_ratio.replace(":", "x")
                        filename = f"{network}_{ratio_suffix}_{timestamp}.png"
                        filepath = IMAGES_DIR / filename
                        
                        # Decode and save
                        import base64
                        if isinstance(image_data, str):
                            image_bytes = base64.b64decode(image_data)
                        else:
                            image_bytes = image_data
                        
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        
                        # Save to database
                        self._save_media_record(
                            content_id=content_id,
                            media_type='image',
                            prompt_used=f"[{aspect_ratio}] {prompt}",
                            file_path=str(filepath),
                            network=network
                        )
                        
                        logger.info(f"Image generated and saved: {filepath}")
                        return str(filepath)
            
            logger.warning("No image generated in response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    def generate_video(self, content: str, network: str, aspect_ratio: str = "16:9", content_id: Optional[int] = None) -> Optional[str]:
        """Generate a video using Gemini Veo API."""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        branding = self._get_branding_instructions(network, 'video')
        
        # Create video prompt from content - summarized for Veo
        video_prompt = f"""Cyberpunk tech video: {content[:200]}
Style: Dark background, neon purple/cyan/green accents, futuristic, professional.
Motion: Smooth camera movements, subtle glitch effects, tech elements.
Suitable for {network}."""
        
        try:
            # Map aspect ratio to Veo format
            veo_aspect = "16:9"  # Default
            if aspect_ratio == "9:16":
                veo_aspect = "9:16"
            elif aspect_ratio == "1:1":
                veo_aspect = "1:1"
            
            # Use generate_videos for Veo
            operation = self.client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=video_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=veo_aspect,
                    number_of_videos=1,
                    duration_seconds=5,
                )
            )
            
            # Poll for completion (Veo is async)
            import time
            max_wait = 120  # 2 minutes max
            waited = 0
            
            while not operation.done and waited < max_wait:
                time.sleep(5)
                waited += 5
                operation = self.client.operations.get(operation)
                logger.info(f"Video generation progress: {waited}s...")
            
            if operation.done and operation.response:
                # Get the generated video
                for video in operation.response.generated_videos:
                    if video.video and video.video.video_bytes:
                        video_bytes = video.video.video_bytes
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        ratio_suffix = aspect_ratio.replace(":", "x")
                        filename = f"{network}_{ratio_suffix}_{timestamp}.mp4"
                        filepath = VIDEOS_DIR / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(video_bytes)
                        
                        self._save_media_record(
                            content_id=content_id,
                            media_type='video',
                            prompt_used=f"[{aspect_ratio}] {content[:100]}...",
                            file_path=str(filepath),
                            network=network
                        )
                        
                        logger.info(f"Video generated and saved: {filepath}")
                        return str(filepath)
            
            logger.warning("Video generation timed out or failed")
            return None
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return None
    
    def generate_video_prompt(self, content: str, network: str) -> str:
        """Generate a detailed video script/storyboard prompt."""
        if not self.client:
            return ""
        
        branding = self._get_branding_instructions(network, 'video')
        
        system_prompt = f"""
Eres un experto en crear guiones y storyboards para videos de redes sociales.
Analiza el contenido y crea un prompt detallado para generar un video.

{branding}

FORMATO DE RESPUESTA:
## CONCEPTO
[Descripción breve del video]

## ESCENAS
1. [Duración] - [Descripción visual] - [Texto en pantalla]
2. ...

## ESTILO VISUAL
[Colores, transiciones, efectos]

## MÚSICA SUGERIDA
[Género, tempo, mood]

## CALL TO ACTION
[Cierre del video]

Responde con el storyboard completo.
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{system_prompt}\n\nCONTENIDO:\n{content}",
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating video prompt: {e}")
            return ""
    
    def _save_media_record(self, content_id: Optional[int], media_type: str, 
                           prompt_used: str, file_path: str, network: str):
        """Save generated media record to database."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO generated_media 
            (content_id, media_type, prompt_used, file_path, network)
            VALUES (?, ?, ?, ?, ?)
        """, (content_id, media_type, prompt_used, file_path, network))
        
        conn.commit()
        conn.close()
    
    def get_media_gallery(self, limit: int = 20) -> list:
        """Get recent generated media."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM generated_media
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_media(self, media_id: int) -> bool:
        """Delete a generated media file and its record."""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get file path
        cursor.execute("SELECT file_path FROM generated_media WHERE id = ?", (media_id,))
        row = cursor.fetchone()
        
        if row:
            file_path = Path(row['file_path'])
            if file_path.exists():
                file_path.unlink()
            
            cursor.execute("DELETE FROM generated_media WHERE id = ?", (media_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False


# Global instance
_media_generator: Optional[MediaGenerator] = None


def get_media_generator() -> MediaGenerator:
    """Get or create the global media generator."""
    global _media_generator
    if _media_generator is None:
        _media_generator = MediaGenerator()
    return _media_generator
