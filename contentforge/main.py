"""
ContentForge AI - Main Entry Point
Social Media Content Generator powered by Gemini AI
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for ContentForge AI."""
    try:
        # Check for test mode
        if "--test" in sys.argv:
            print("✅ ContentForge AI - Test mode")
            from .config import validate_config, get_config_status
            
            missing = validate_config()
            if missing:
                print(f"⚠️ Variables faltantes: {missing}")
            else:
                print("✅ Configuración completa")
            
            status = get_config_status()
            print(f"📊 Estado: {status}")
            return 0
        
        # Check for API test
        if "--test-api" in sys.argv:
            from .gemini_handler import test_connection
            return 0 if test_connection() else 1
        
        # Import and run GUI
        from .ui.app import run_app
        print("🚀 Iniciando ContentForge AI...")
        run_app()
        return 0
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
