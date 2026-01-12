"""
API Server for ContentForge AI
Receives content from Chrome extension and integrates with the main app
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

logger = logging.getLogger(__name__)

# Shared storage for extracted content
EXTRACTED_CONTENT = []
MAX_STORED = 50

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Storage file
STORAGE_DIR = Path.home() / ".contentforge"
STORAGE_FILE = STORAGE_DIR / "extracted_content.json"


def save_extracted_content():
    """Save extracted content to file for persistence."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(EXTRACTED_CONTENT[-MAX_STORED:], f, ensure_ascii=False, indent=2)


def load_extracted_content():
    """Load previously extracted content."""
    global EXTRACTED_CONTENT
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                EXTRACTED_CONTENT = json.load(f)
        except:
            EXTRACTED_CONTENT = []


@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "app": "ContentForge AI",
        "version": "1.0.0",
        "extracted_count": len(EXTRACTED_CONTENT)
    })


@app.route('/extract', methods=['POST'])
def extract():
    """Receive extracted content from Chrome extension."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Add metadata
        content = {
            "id": len(EXTRACTED_CONTENT) + 1,
            "url": data.get("url", ""),
            "title": data.get("title", "Sin título"),
            "text": data.get("text", ""),
            "meta": data.get("meta", {}),
            "received_at": datetime.now().isoformat()
        }
        
        EXTRACTED_CONTENT.append(content)
        save_extracted_content()
        
        logger.info(f"Received content from: {content['url']}")
        
        return jsonify({
            "success": True,
            "message": "Contenido recibido correctamente",
            "id": content["id"]
        })
        
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/content', methods=['GET'])
def get_content():
    """Get all extracted content."""
    return jsonify({
        "content": EXTRACTED_CONTENT[-20:],  # Last 20
        "total": len(EXTRACTED_CONTENT)
    })


@app.route('/content/latest', methods=['GET'])
def get_latest():
    """Get the most recent extracted content."""
    if EXTRACTED_CONTENT:
        return jsonify({"content": EXTRACTED_CONTENT[-1]})
    return jsonify({"content": None})


@app.route('/content/clear', methods=['POST'])
def clear_content():
    """Clear all extracted content."""
    global EXTRACTED_CONTENT
    EXTRACTED_CONTENT = []
    save_extracted_content()
    return jsonify({"success": True, "message": "Contenido eliminado"})


# ============ MEDIA ANALYSIS ENDPOINTS ============

@app.route('/analyze/video', methods=['POST'])
def analyze_video():
    """Download and analyze video from URL."""
    try:
        from contentforge.media_processor import get_media_processor
        
        data = request.get_json()
        url = data.get("url", "")
        context = data.get("context", "")
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        processor = get_media_processor()
        result = processor.process_video_url(url, context)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "analysis": result.get("analysis", ""),
                "video_path": result.get("video_path"),
                "audio_path": result.get("audio_path")
            })
        else:
            return jsonify({"success": False, "error": result.get("error")}), 400
            
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/analyze/image', methods=['POST'])
def analyze_image():
    """Analyze image from URL, base64 data, or generate from context."""
    try:
        from contentforge.gemini_handler import get_gemini_handler
        
        data = request.get_json()
        url = data.get("url", "")
        base64_data = data.get("base64", "")
        context = data.get("context", "")
        
        gemini = get_gemini_handler()
        
        if base64_data:
            # Direct base64 analysis
            prompt = f"""Analiza esta imagen y proporciona:
1. Descripción detallada
2. Temas principales
3. 3 ideas de comentarios que generen curiosidad y engagement
4. 5 hashtags relevantes

Contexto: {context if context else 'Imagen de redes sociales'}
Responde en español."""
            
            analysis = gemini.generate_with_image(prompt, base64_data)
            return jsonify({"success": True, "analysis": analysis})
            
        elif url:
            # Check if URL is a direct image or a page
            is_direct_image = any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
            
            if is_direct_image:
                from contentforge.media_processor import get_media_processor
                processor = get_media_processor()
                image_path = processor.download_image(url)
                if image_path:
                    result = processor.analyze_image(image_path, context)
                    # Store for main app polling
                    _store_analysis_result(url, result.get("analysis", ""), "image")
                    return jsonify(result)
            
            # For page URLs (Facebook photo pages, etc), generate analysis from context
            prompt = f"""Eres un experto en marketing de redes sociales. Basándote en esta URL y contexto:

URL: {url}
Contexto: {context if context else 'Publicación de redes sociales con imagen'}

Genera:

1. **3 Comentarios de Engagement:**
   - Comentarios que generen curiosidad técnica
   - Que inviten a la conversación
   - Máximo 280 caracteres cada uno

2. **Ideas de Contenido:**
   - 3 ideas para crear contenido relacionado

3. **Hashtags Sugeridos:**
   - 10 hashtags relevantes para mayor alcance

Responde en español, de forma profesional y útil."""
            
            analysis = gemini.generate(prompt)
            
            # Store for main app polling
            _store_analysis_result(url, analysis, "image")
            
            return jsonify({
                "success": True, 
                "analysis": analysis,
                "note": "Análisis basado en contexto (imagen no descargable directamente)"
            })
        else:
            return jsonify({"error": "URL or base64 data required"}), 400
            
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _store_analysis_result(url: str, analysis: str, media_type: str):
    """Store analysis result for main app polling."""
    global EXTRACTED_CONTENT
    content = {
        "id": len(EXTRACTED_CONTENT) + 1,
        "url": url,
        "title": f"📊 Análisis de {media_type.upper()}",
        "text": analysis,
        "meta": {"type": "analysis", "media_type": media_type},
        "received_at": datetime.now().isoformat()
    }
    EXTRACTED_CONTENT.append(content)
    save_extracted_content()
    logger.info(f"Analysis stored for: {url}")


@app.route('/analyze/generate', methods=['POST'])
def generate_from_analysis():
    """Generate content from previous analysis."""
    try:
        from contentforge.media_processor import get_media_processor
        
        data = request.get_json()
        analysis = data.get("analysis", "")
        content_type = data.get("type", "comment")  # comment, post, thread
        
        if not analysis:
            return jsonify({"error": "Analysis text required"}), 400
        
        processor = get_media_processor()
        content = processor.generate_content_from_analysis(analysis, content_type)
        
        return jsonify({
            "success": True,
            "content": content,
            "type": content_type
        })
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/analyze/status', methods=['GET'])
def analyze_status():
    """Check if media analysis dependencies are available."""
    try:
        from contentforge.media_processor import get_media_processor
        processor = get_media_processor()
        
        return jsonify({
            "yt_dlp": processor.has_ytdlp,
            "ffmpeg": processor.has_ffmpeg,
            "gemini": processor.gemini.is_configured()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_api_server(port: int = 5678):
    """Start the API server."""
    load_extracted_content()
    print(f"🌐 ContentForge API Server iniciado en http://localhost:{port}")
    print("📥 Esperando contenido de la extensión Chrome...")
    print("🎬 Endpoints de análisis de media disponibles")
    app.run(host='localhost', port=port, debug=False, threaded=True)


def get_extracted_content() -> list:
    """Get extracted content for use in the main app."""
    load_extracted_content()
    return EXTRACTED_CONTENT


if __name__ == '__main__':
    run_api_server()

