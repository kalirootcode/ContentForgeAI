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


def run_api_server(port: int = 5678):
    """Start the API server."""
    load_extracted_content()
    print(f"🌐 ContentForge API Server iniciado en http://localhost:{port}")
    print("📥 Esperando contenido de la extensión Chrome...")
    app.run(host='localhost', port=port, debug=False, threaded=True)


def get_extracted_content() -> list:
    """Get extracted content for use in the main app."""
    load_extracted_content()
    return EXTRACTED_CONTENT


if __name__ == '__main__':
    run_api_server()
