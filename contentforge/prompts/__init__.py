"""
Social Network Prompts for ContentForge AI
Each module contains specialized prompts optimized for platform algorithms
"""

from .facebook import FACEBOOK_PROMPTS
from .instagram import INSTAGRAM_PROMPTS
from .tiktok import TIKTOK_PROMPTS
from .twitter_x import TWITTER_PROMPTS
from .youtube import YOUTUBE_PROMPTS
from .telegram import TELEGRAM_PROMPTS
from .linkedin import LINKEDIN_PROMPTS
from .pinterest import PINTEREST_PROMPTS
from .threads import THREADS_PROMPTS

# Master prompt registry
NETWORK_PROMPTS = {
    "facebook": FACEBOOK_PROMPTS,
    "instagram": INSTAGRAM_PROMPTS,
    "tiktok": TIKTOK_PROMPTS,
    "twitter": TWITTER_PROMPTS,
    "youtube": YOUTUBE_PROMPTS,
    "telegram": TELEGRAM_PROMPTS,
    "linkedin": LINKEDIN_PROMPTS,
    "pinterest": PINTEREST_PROMPTS,
    "threads": THREADS_PROMPTS,
}


def get_prompt(network: str, content_type: str) -> str:
    """Get the specialized prompt for a network and content type."""
    network_prompts = NETWORK_PROMPTS.get(network, {})
    return network_prompts.get(content_type, network_prompts.get("default", ""))
