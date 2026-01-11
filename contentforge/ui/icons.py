"""
Icon Loader for ContentForge AI
Loads and manages PNG icons for social networks and content types
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image
import customtkinter as ctk

# Icons directory
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"


class IconLoader:
    """Loads and caches application icons."""
    
    # Icon sizes
    NETWORK_SIZE = (24, 24)
    CONTENT_SIZE = (20, 20)
    
    # Social network icon positions in sprite (x, y, width, height)
    SOCIAL_ICONS = {
        "facebook": (0, 0, 128, 128),
        "instagram": (128, 0, 128, 128),
        "tiktok": (256, 0, 128, 128),
        "twitter": (384, 0, 128, 128),
        "youtube": (0, 128, 128, 128),
        "telegram": (128, 128, 128, 128),
        "linkedin": (256, 128, 128, 128),
        "pinterest": (384, 128, 128, 128),
    }
    
    # Content type icon positions (approximate based on 4-column layout)
    CONTENT_ICONS = {
        "post": (0, 0, 128, 128),
        "story": (128, 0, 128, 128),
        "script": (256, 0, 128, 128),
        "carousel": (384, 0, 128, 128),
        "thread": (0, 128, 128, 128),
        "caption": (128, 128, 128, 128),
        "bio": (256, 128, 128, 128),
        "hashtags": (384, 128, 128, 128),
    }
    
    def __init__(self):
        self._cache: Dict[str, ctk.CTkImage] = {}
        self._social_sprite: Optional[Image.Image] = None
        self._content_sprite: Optional[Image.Image] = None
        self._load_sprites()
    
    def _load_sprites(self):
        """Load sprite sheets."""
        social_path = ASSETS_DIR / "social_icons.png"
        content_path = ASSETS_DIR / "content_icons.png"
        
        if social_path.exists():
            self._social_sprite = Image.open(social_path)
        
        if content_path.exists():
            self._content_sprite = Image.open(content_path)
    
    def _crop_icon(self, sprite: Image.Image, region: Tuple[int, int, int, int], size: Tuple[int, int]) -> Image.Image:
        """Crop and resize an icon from sprite sheet."""
        x, y, w, h = region
        # Scale region based on actual sprite size
        sprite_w, sprite_h = sprite.size
        scale_x = sprite_w / 512  # Assuming 512px sprite width
        scale_y = sprite_h / 256  # Assuming 256px sprite height
        
        scaled_region = (
            int(x * scale_x),
            int(y * scale_y),
            int((x + w) * scale_x),
            int((y + h) * scale_y)
        )
        
        icon = sprite.crop(scaled_region)
        icon = icon.resize(size, Image.Resampling.LANCZOS)
        return icon
    
    def get_network_icon(self, network_id: str) -> Optional[ctk.CTkImage]:
        """Get a social network icon."""
        cache_key = f"network_{network_id}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if self._social_sprite is None or network_id not in self.SOCIAL_ICONS:
            return None
        
        try:
            region = self.SOCIAL_ICONS[network_id]
            icon = self._crop_icon(self._social_sprite, region, self.NETWORK_SIZE)
            ctk_icon = ctk.CTkImage(light_image=icon, dark_image=icon, size=self.NETWORK_SIZE)
            self._cache[cache_key] = ctk_icon
            return ctk_icon
        except Exception as e:
            print(f"Error loading network icon {network_id}: {e}")
            return None
    
    def get_content_icon(self, content_type: str) -> Optional[ctk.CTkImage]:
        """Get a content type icon."""
        cache_key = f"content_{content_type}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if self._content_sprite is None or content_type not in self.CONTENT_ICONS:
            return None
        
        try:
            region = self.CONTENT_ICONS[content_type]
            icon = self._crop_icon(self._content_sprite, region, self.CONTENT_SIZE)
            ctk_icon = ctk.CTkImage(light_image=icon, dark_image=icon, size=self.CONTENT_SIZE)
            self._cache[cache_key] = ctk_icon
            return ctk_icon
        except Exception as e:
            print(f"Error loading content icon {content_type}: {e}")
            return None


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
