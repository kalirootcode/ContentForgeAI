"""
Configuration module for ContentForge AI
Loads environment variables and provides configuration constants
"""

import os
import pathlib
from dotenv import load_dotenv

# Load environment variables
APP_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(APP_DIR / ".env")

# ===== GEMINI API =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or None
GEMINI_MODEL_FAST = "gemini-2.0-flash"       # For quick content
GEMINI_MODEL_PRO = "gemini-2.5-pro"          # For detailed scripts

# ===== DATABASE =====
DATABASE_PATH = APP_DIR / "data" / "contentforge.db"

# ===== APP SETTINGS =====
APP_NAME = "ContentForge AI"
APP_VERSION = "1.0.0"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "es")
THEME = os.getenv("THEME", "dark")

# ===== SOCIAL NETWORKS =====
# Using proper Unicode/text representations
SOCIAL_NETWORKS = [
    {"id": "facebook", "name": "Facebook", "icon": "ⓕ", "color": "#1877F2"},
    {"id": "instagram", "name": "Instagram", "icon": "📷", "color": "#E4405F"},
    {"id": "tiktok", "name": "TikTok", "icon": "♪", "color": "#000000"},
    {"id": "twitter", "name": "X (Twitter)", "icon": "𝕏", "color": "#000000"},
    {"id": "youtube", "name": "YouTube", "icon": "▶", "color": "#FF0000"},
    {"id": "telegram", "name": "Telegram", "icon": "✈", "color": "#0088CC"},
    {"id": "linkedin", "name": "LinkedIn", "icon": "in", "color": "#0A66C2"},
    {"id": "pinterest", "name": "Pinterest", "icon": "📌", "color": "#E60023"},
    {"id": "threads", "name": "Threads", "icon": "@", "color": "#000000"},
]

# ===== CONTENT TYPES =====
CONTENT_TYPES = {
    "post": {"name": "Post", "icon": "📝", "desc": "Publicación estándar"},
    "story": {"name": "Story", "icon": "📱", "desc": "Historia efímera"},
    "script": {"name": "Script", "icon": "🎬", "desc": "Guión para video"},
    "carousel": {"name": "Carrusel", "icon": "🎠", "desc": "Múltiples slides"},
    "thread": {"name": "Hilo", "icon": "🧵", "desc": "Thread/Hilo"},
    "caption": {"name": "Caption", "icon": "💬", "desc": "Pie de foto"},
    "bio": {"name": "Bio", "icon": "��", "desc": "Biografía"},
    "hashtags": {"name": "Hashtags", "icon": "#", "desc": "Tags optimizados"},
}


def validate_config() -> list:
    """Validate configuration and return missing variables."""
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    return missing


def get_config_status() -> dict:
    """Get configuration status for display."""
    return {
        "gemini": bool(GEMINI_API_KEY),
        "database": DATABASE_PATH.parent.exists(),
    }
