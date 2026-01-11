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
    
    def analyze_content_for_image(self, content: str, network: str, style_prompt: str = "") -> str:
        """Analyze content and generate an optimized image prompt with style."""
        if not self.client:
            return ""
        
        branding = self._get_branding_instructions(network, 'image')
        
        # Build style instructions
        style_instruction = f"\nESTILO REQUERIDO: {style_prompt}\n" if style_prompt else ""
        
        system_prompt = f"""
Eres un experto en crear prompts para generación de imágenes AI.
Analiza el siguiente contenido de redes sociales y crea un prompt detallado
para generar una imagen que complemente perfectamente el contenido.

{branding}
{style_instruction}
REGLAS:
1. El prompt debe ser en inglés (mejor para AI de imágenes)
2. Incluir estilo visual específico según el estilo requerido
3. Mencionar colores, iluminación, composición
4. Mantener el branding cyberpunk/hacker con acentos de neón
5. Adaptar el diseño al estilo seleccionado
6. Ser muy específico y descriptivo

Responde SOLO con el prompt de imagen, sin explicaciones."""
        
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
    
    def generate_video(self, content: str, network: str, aspect_ratio: str = "16:9", content_id: Optional[int] = None, style_prompt: str = "") -> Optional[str]:
        """Generate a video using Gemini Veo API with style."""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        branding = self._get_branding_instructions(network, 'video')
        
        # Build style instruction
        style_instruction = f"Style: {style_prompt}. " if style_prompt else ""
        
        # Create video prompt from content with style
        video_prompt = f"""Cyberpunk tech video: {content[:200]}
{style_instruction}Background: Dark, neon purple/cyan/green accents, futuristic, professional.
Motion: Smooth camera movements, dynamic transitions, tech-inspired elements.
Suitable for {network}. Aspect ratio: {aspect_ratio}."""
        
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
            
            # Poll for completion (Veo is async - videos take 30-90 seconds)
            import time
            max_wait = 180  # 3 minutes max for video generation
            waited = 0
            
            while waited < max_wait:
                time.sleep(5)
                waited += 5
                operation = self.client.operations.get(operation)
                logger.info(f"Video generation progress: {waited}s... done={operation.done}")
                
                if operation.done:
                    break
            
            # Check result
            if operation.done:
                logger.info(f"Operation completed. Checking response...")
                
                # Try to get video from response
                if hasattr(operation, 'response') and operation.response:
                    response = operation.response
                    logger.info(f"Response type: {type(response)}")
                    
                    # Handle generated_videos
                    if hasattr(response, 'generated_videos') and response.generated_videos:
                        for video in response.generated_videos:
                            video_bytes = None
                            
                            # Debug: Log the video object structure
                            logger.info(f"Video object attrs: {dir(video)}")
                            
                            # Try different ways to get video data
                            if hasattr(video, 'video') and video.video:
                                video_obj = video.video
                                logger.info(f"Video.video attrs: {dir(video_obj)}")
                                
                                # Check for URI first (Veo returns URI that requires auth)
                                if hasattr(video_obj, 'uri') and video_obj.uri:
                                    logger.info(f"Downloading video from URI: {video_obj.uri}")
                                    import requests
                                    
                                    # Add API key to URI (GEMINI_API_KEY imported at top)
                                    download_url = video_obj.uri
                                    if '?' in download_url:
                                        download_url += f"&key={GEMINI_API_KEY}"
                                    else:
                                        download_url += f"?key={GEMINI_API_KEY}"
                                    
                                    resp = requests.get(download_url, timeout=120)
                                    if resp.status_code == 200:
                                        video_bytes = resp.content
                                        logger.info(f"Downloaded {len(video_bytes)} bytes from URI")
                                    else:
                                        logger.error(f"Failed to download: {resp.status_code} - {resp.text[:200]}")
                                
                                # Try video_bytes if URI didn't work
                                if not video_bytes and hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                                    video_bytes = video_obj.video_bytes
                                    logger.info(f"Got {len(video_bytes)} bytes from video_bytes")
                                
                                # Try data attribute
                                if not video_bytes and hasattr(video_obj, 'data') and video_obj.data:
                                    video_bytes = video_obj.data
                                    logger.info(f"Got {len(video_bytes)} bytes from data")
                            
                            if video_bytes and len(video_bytes) > 10000:  # Minimum size check
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
                                
                                logger.info(f"Video generated and saved: {filepath} ({len(video_bytes)} bytes)")
                                return str(filepath)
                    
                    logger.warning(f"No videos found in response. Response attrs: {dir(response)}")
                else:
                    logger.warning(f"No response in operation. Error: {getattr(operation, 'error', 'unknown')}")
            
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
    
    def generate_external_prompt(self, content: str, network: str, media_type: str, 
                                  platform: str, aspect_ratio: str) -> str:
        """Generate an optimized prompt for external platforms like Midjourney, DALL-E, Runway, etc."""
        if not self.client:
            return ""
        
        # Platform-specific formatting
        platform_formats = {
            # Image platforms
            "midjourney": f"--ar {aspect_ratio.replace(':', ':')} --v 6.1 --style raw",
            "dalle": f"Aspect ratio: {aspect_ratio}",
            "grok": f"[Format: {aspect_ratio}]",
            "stable": f"Resolution: {aspect_ratio}, CFG: 7",
            # Video platforms
            "runway": f"Duration: 5 seconds, Aspect ratio: {aspect_ratio}",
            "pika": f"Aspect: {aspect_ratio}, Style: cinematic",
            "kling": f"Format: {aspect_ratio}, Duration: 5s, Motion: smooth",
        }
        
        platform_suffix = platform_formats.get(platform, "")
        
        media_context = "imagen" if media_type == "image" else "video"
        
        system_prompt = f"""
Eres un experto en crear prompts optimizados para plataformas de generación de {media_context} con IA.
Analiza el contenido y crea un prompt profesional optimizado para {platform.upper()}.

CONTENIDO ORIGINAL:
{content}

ESTILO: Cyberpunk/hacker, colores neón (púrpura, cian, verde), fondo oscuro, profesional, futurista.
RED SOCIAL: {network}

REGLAS:
1. El prompt debe estar en INGLÉS
2. Ser muy descriptivo y específico
3. Incluir detalles de iluminación, composición, estilo
4. Optimizar para {platform.upper()}
5. Mantener la estética cyberpunk/tech

Responde SOLO con el prompt listo para usar, seguido del formato:
{platform_suffix}
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating external prompt: {e}")
            return ""
    
    def generate_script(self, content: str, network: str, script_type: str, 
                        duration: str = "") -> str:
        """Generate a professional video script based on content and type."""
        if not self.client:
            return ""
        
        script_templates = {
            "reel": """
## GUIÓN PARA REEL/SHORT (15-60s)

### HOOK (0-3s)
[Gancho inicial que capture atención]

### CONTENIDO (3-45s)
[Información principal dividida en puntos rápidos]

### CTA (45-60s)
[Llamada a la acción final]

### MÚSICA/SFX
[Sugerencias de audio]
""",
            "long_video": """
## GUIÓN PARA VIDEO LARGO (3-10 min)

### INTRO (0-30s)
[Presentación y gancho]

### SECCIÓN 1: [Título]
[Contenido detallado]

### SECCIÓN 2: [Título]
[Contenido detallado]

### SECCIÓN 3: [Título]
[Contenido detallado]

### CIERRE
[Resumen y CTA]

### B-ROLL SUGERIDO
[Visuales complementarios]
""",
            "tutorial": """
## GUIÓN TUTORIAL

### PROBLEMA
[Qué resolveremos]

### REQUISITOS PREVIOS
[Lo que necesitas]

### PASO 1: [Título]
[Instrucciones detalladas]

### PASO 2: [Título]
[Instrucciones detalladas]

### PASO 3: [Título]
[Instrucciones detalladas]

### RESULTADO FINAL
[Demostración del resultado]

### TIPS ADICIONALES
[Consejos extra]
""",
            "storytelling": """
## GUIÓN STORYTELLING

### INICIO - El Contexto
[Presentación de la situación/personaje]

### CONFLICTO - El Problema
[El desafío o punto de inflexión]

### DESARROLLO - La Jornada
[Cómo se enfrenta el desafío]

### CLÍMAX - El Momento Clave
[El punto más intenso]

### RESOLUCIÓN - El Aprendizaje
[Conclusión y mensaje]

### MÚSICA/MOOD
[Tono emocional sugerido]
"""
        }
        
        template = script_templates.get(script_type, script_templates["reel"])
        
        system_prompt = f"""
Eres un guionista experto en contenido para redes sociales.
Crea un guión profesional basado en el siguiente contenido.

CONTENIDO BASE:
{content}

RED SOCIAL: {network}
TIPO DE GUIÓN: {script_type}
DURACIÓN: {duration}

USA ESTE FORMATO:
{template}

ESTILO: Profesional, engaging, con ganchos efectivos.
Incluye timestamps aproximados donde sea relevante.
Responde con el guión completo y listo para usar.
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating script: {e}")
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
