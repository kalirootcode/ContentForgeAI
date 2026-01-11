"""
Icon Loader for ContentForge AI
Loads individual PNG icons for social networks and content types
"""

from pathlib import Path
from typing import Dict, Optional
from PIL import Image
import customtkinter as ctk

# Icons directory
ICONS_DIR = Path(__file__).parent.parent.parent / "assets" / "icons"


class IconLoader:
    """Loads and caches application icons from individual PNG files."""
    
    # Icon sizes for display
    NETWORK_SIZE = (24, 24)
    CONTENT_SIZE = (20, 20)
    
    def __init__(self):
        self._cache: Dict[str, ctk.CTkImage] = {}
    
    def _load_icon(self, name: str, size: tuple) -> Optional[ctk.CTkImage]:
        """Load a single icon from file."""
        icon_path = ICONS_DIR / f"{name}.png"
        
        if not icon_path.exists():
            return None
        
        try:
            img = Image.open(icon_path)
            # Convert to RGBA to handle transparency properly
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            # Resize to target size with high quality
            img = img.resize(size, Image.Resampling.LANCZOS)
            # Create CTkImage for both light and dark modes
            ctk_icon = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            return ctk_icon
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
            return None
    
    def get_network_icon(self, network_id: str) -> Optional[ctk.CTkImage]:
        """Get a social network icon."""
        cache_key = f"network_{network_id}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        icon = self._load_icon(network_id, self.NETWORK_SIZE)
        if icon:
            self._cache[cache_key] = icon
        return icon
    
    def get_content_icon(self, content_type: str) -> Optional[ctk.CTkImage]:
        """Get a content type icon."""
        cache_key = f"content_{content_type}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try aliases for content types (e.g., thread -> hilo)
        aliases = {"thread": "hilo"}
        icon_name = aliases.get(content_type, content_type)
        
        icon = self._load_icon(icon_name, self.CONTENT_SIZE)
        if icon:
            self._cache[cache_key] = icon
        return icon


# Global icon loader instance
_icon_loader: Optional[IconLoader] = None


def get_icon_loader() -> IconLoader:
    """Get or create the global icon loader."""
    global _icon_loader
    if _icon_loader is None:
        _icon_loader = IconLoader()
    return _icon_loader


def get_network_icon(network_id: str) -> Optional[ctk.CTkImage]:
    """Convenience function to get network icon."""
    return get_icon_loader().get_network_icon(network_id)


def get_content_icon(content_type: str) -> Optional[ctk.CTkImage]:
    """Convenience function to get content icon."""
    return get_icon_loader().get_content_icon(content_type)
