"""
Media Processor for ContentForge AI
Handles video download, audio extraction, and image analysis using AI
"""

import os
import logging
import tempfile
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

logger = logging.getLogger(__name__)

# Storage directory for downloaded media
MEDIA_DIR = Path.home() / ".contentforge" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


class MediaProcessor:
    """Process media files for AI analysis."""
    
    def __init__(self, gemini_handler=None):
        from contentforge.gemini_handler import get_gemini_handler
        self.gemini = gemini_handler or get_gemini_handler()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required external tools are installed."""
        self.has_ytdlp = self._check_command("yt-dlp --version")
        self.has_ffmpeg = self._check_command("ffmpeg -version")
        
        if not self.has_ytdlp:
            logger.warning("yt-dlp not found. Video download will be limited.")
        if not self.has_ffmpeg:
            logger.warning("ffmpeg not found. Audio extraction will be limited.")
    
    def _check_command(self, cmd: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(cmd.split(), capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def download_video(self, url: str) -> Optional[Path]:
        """
        Download video from URL using yt-dlp.
        
        Args:
            url: Video URL (TikTok, YouTube, Facebook, etc.)
            
        Returns:
            Path to downloaded video or None
        """
        if not self.has_ytdlp:
            logger.error("yt-dlp not installed. Run: pip install yt-dlp")
            return None
        
        try:
            output_path = MEDIA_DIR / "video_%(id)s.%(ext)s"
            cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", str(output_path),
                "--no-playlist",
                "--max-filesize", "100M",
                url
            ]
            
            logger.info(f"Downloading video from: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find the downloaded file
                for f in MEDIA_DIR.glob("video_*"):
                    if f.is_file():
                        logger.info(f"Video downloaded: {f}")
                        return f
            else:
                logger.error(f"yt-dlp error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Video download timed out")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def extract_audio(self, video_path: Path) -> Optional[Path]:
        """
        Extract audio from video using ffmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file or None
        """
        if not self.has_ffmpeg:
            logger.error("ffmpeg not installed")
            return None
        
        try:
            audio_path = video_path.with_suffix(".mp3")
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",  # No video
                "-acodec", "mp3",
                "-ab", "128k",
                "-y",  # Overwrite
                str(audio_path)
            ]
            
            logger.info(f"Extracting audio from: {video_path}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if audio_path.exists():
                logger.info(f"Audio extracted: {audio_path}")
                return audio_path
            else:
                logger.error(f"ffmpeg error: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return None
    
    def download_image(self, url: str) -> Optional[Path]:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Path to downloaded image or None
        """
        try:
            import urllib.request
            
            # Determine extension from URL
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            elif ".gif" in url.lower():
                ext = ".gif"
            elif ".webp" in url.lower():
                ext = ".webp"
            
            image_path = MEDIA_DIR / f"image_{hash(url)}{ext}"
            
            logger.info(f"Downloading image from: {url}")
            urllib.request.urlretrieve(url, image_path)
            
            if image_path.exists():
                logger.info(f"Image downloaded: {image_path}")
                return image_path
            return None
            
        except Exception as e:
            logger.error(f"Image download error: {e}")
            return None
    
    def analyze_image(self, image_path: Path, context: str = "") -> Dict[str, Any]:
        """
        Analyze image using Gemini Vision.
        
        Args:
            image_path: Path to image file
            context: Additional context about the image
            
        Returns:
            Dict with analysis results
        """
        try:
            # Read image and encode to base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Get mime type
            ext = image_path.suffix.lower()
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }
            mime_type = mime_types.get(ext, "image/jpeg")
            
            prompt = f"""Analiza esta imagen en detalle y proporciona:

1. **Descripción**: ¿Qué se ve en la imagen?
2. **Contexto**: ¿De qué trata el contenido?
3. **Temas principales**: Lista de temas o keywords
4. **Tono/Estilo**: ¿Qué emociones o estilo transmite?
5. **Sugerencia de contenido**: 3 ideas de posts/comentarios relevantes

Contexto adicional: {context if context else 'No hay contexto adicional'}

Responde en español, de forma concisa y útil para crear contenido de redes sociales."""

            # Use Gemini with image
            response = self.gemini.generate_with_image(prompt, image_data, mime_type)
            
            return {
                "success": True,
                "analysis": response,
                "image_path": str(image_path)
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_audio(self, audio_path: Path, context: str = "") -> Dict[str, Any]:
        """
        Analyze audio/video content.
        For now, this uses the file name and context.
        Full audio transcription requires additional setup.
        
        Args:
            audio_path: Path to audio file
            context: Additional context
            
        Returns:
            Dict with analysis results
        """
        try:
            # For audio, we'll send a prompt with context
            # Full transcription would require speech-to-text API
            prompt = f"""Basándote en el contexto de un video/audio de redes sociales:

Contexto: {context}
Archivo: {audio_path.name}

Genera:
1. **Resumen probable del contenido**: Basado en el contexto
2. **Comentario de engagement**: Un comentario que genere interacción
3. **Ideas de respuesta**: 3 formas de responder a este contenido
4. **Hashtags sugeridos**: 5 hashtags relevantes

Responde en español, de forma concisa y orientada a redes sociales."""

            response = self.gemini.generate(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "audio_path": str(audio_path)
            }
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_video_url(self, url: str, context: str = "") -> Dict[str, Any]:
        """
        Full pipeline: download video, extract audio, analyze.
        
        Args:
            url: Video URL
            context: Additional context about the video
            
        Returns:
            Dict with full analysis
        """
        result = {
            "url": url,
            "success": False,
            "video_path": None,
            "audio_path": None,
            "analysis": None
        }
        
        # Download video
        video_path = self.download_video(url)
        if not video_path:
            result["error"] = "No se pudo descargar el video"
            return result
        
        result["video_path"] = str(video_path)
        
        # Extract audio
        audio_path = self.extract_audio(video_path)
        if audio_path:
            result["audio_path"] = str(audio_path)
        
        # Analyze
        analysis = self.analyze_audio(audio_path or video_path, context)
        result["analysis"] = analysis.get("analysis", "")
        result["success"] = True
        
        return result
    
    def generate_content_from_analysis(self, analysis: str, content_type: str = "comment") -> str:
        """
        Generate specific content based on analysis.
        
        Args:
            analysis: Previous analysis result
            content_type: 'comment', 'post', 'thread'
            
        Returns:
            Generated content string
        """
        type_prompts = {
            "comment": "Genera un comentario de máximo 280 caracteres que genere curiosidad técnica y engagement.",
            "post": "Genera un post de redes sociales (máximo 500 caracteres) basado en este análisis.",
            "thread": "Genera un hilo de 5 tweets conectados basados en este análisis."
        }
        
        prompt = f"""Basado en este análisis de contenido:

{analysis}

{type_prompts.get(content_type, type_prompts['comment'])}

El contenido debe:
- Ser en español
- Generar interacción y curiosidad
- Ser técnicamente interesante
- NO ser promocional directo

Responde solo con el contenido, sin explicaciones."""

        return self.gemini.generate(prompt)
    
    def cleanup_old_files(self, hours: int = 24):
        """Remove media files older than specified hours."""
        import time
        
        cutoff = time.time() - (hours * 3600)
        for f in MEDIA_DIR.glob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                logger.info(f"Cleaned up: {f}")


def get_media_processor() -> MediaProcessor:
    """Get MediaProcessor instance."""
    return MediaProcessor()
