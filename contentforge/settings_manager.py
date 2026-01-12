"""
Settings Manager for ContentForge AI
Manages user configuration including social media links for research
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Default settings directory
SETTINGS_DIR = Path.home() / ".contentforge"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


class SettingsManager:
    """Manages user settings and social media links for research."""
    
    DEFAULT_SETTINGS = {
        "facebook_groups": [],
        "facebook_pages": [],
        "twitter_accounts": [],
        "linkedin_pages": [],
        "other_links": [],
        "research_settings": {
            "max_posts_to_analyze": 5,
            "include_comments": True,
            "language": "es"
        }
    }
    
    def __init__(self):
        self._ensure_settings_dir()
        self.settings = self._load_settings()
    
    def _ensure_settings_dir(self):
        """Create settings directory if not exists."""
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_settings(self) -> Dict:
        """Load settings from file."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = self.DEFAULT_SETTINGS.copy()
                    merged.update(loaded)
                    return merged
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
        return self.DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save settings to file."""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    # Link Management
    def add_link(self, section: str, name: str, url: str) -> bool:
        """Add a link to a section."""
        if section not in self.settings:
            logger.error(f"Unknown section: {section}")
            return False
        
        link = {"name": name, "url": url}
        if link not in self.settings[section]:
            self.settings[section].append(link)
            self.save()
            return True
        return False
    
    def remove_link(self, section: str, url: str) -> bool:
        """Remove a link from a section."""
        if section not in self.settings:
            return False
        
        original_len = len(self.settings[section])
        self.settings[section] = [l for l in self.settings[section] if l.get("url") != url]
        
        if len(self.settings[section]) < original_len:
            self.save()
            return True
        return False
    
    def get_links(self, section: str) -> List[Dict]:
        """Get all links from a section."""
        return self.settings.get(section, [])
    
    def get_all_links(self) -> Dict[str, List[Dict]]:
        """Get all links organized by section."""
        return {
            "facebook_groups": self.get_links("facebook_groups"),
            "facebook_pages": self.get_links("facebook_pages"),
            "twitter_accounts": self.get_links("twitter_accounts"),
            "linkedin_pages": self.get_links("linkedin_pages"),
            "other_links": self.get_links("other_links"),
        }
    
    def get_total_links_count(self) -> int:
        """Get total number of configured links."""
        return sum(len(v) for v in self.get_all_links().values())
    
    # Research Settings
    def get_research_setting(self, key: str, default=None):
        """Get a research setting."""
        return self.settings.get("research_settings", {}).get(key, default)
    
    def set_research_setting(self, key: str, value):
        """Set a research setting."""
        if "research_settings" not in self.settings:
            self.settings["research_settings"] = {}
        self.settings["research_settings"][key] = value
        self.save()


# Global instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get or create the global settings manager."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
