"""
Theme configuration for ContentForge AI
Dark mode with vibrant accents
"""

# Color palette
COLORS = {
    # Base colors
    "bg_dark": "#0a0a0a",
    "bg_card": "#1a1a1a",
    "bg_input": "#252525",
    "bg_hover": "#2a2a2a",
    
    # Text colors
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_muted": "#666666",
    
    # Accent colors
    "accent_primary": "#6366f1",    # Indigo
    "accent_secondary": "#8b5cf6",  # Purple
    "accent_success": "#22c55e",    # Green
    "accent_warning": "#f59e0b",    # Amber
    "accent_error": "#ef4444",      # Red
    
    # Social network colors
    "facebook": "#1877F2",
    "instagram": "#E4405F",
    "tiktok": "#000000",
    "twitter": "#1DA1F2",
    "youtube": "#FF0000",
    "telegram": "#0088CC",
    "linkedin": "#0A66C2",
    "pinterest": "#E60023",
    
    # Gradients (for buttons)
    "gradient_start": "#6366f1",
    "gradient_end": "#8b5cf6",
}

# Dark theme configuration
DARK_THEME = {
    "appearance_mode": "dark",
    "color_theme": "dark-blue",
    
    # Main window
    "window_bg": COLORS["bg_dark"],
    
    # Frames
    "frame_fg": COLORS["bg_card"],
    "frame_border": COLORS["bg_hover"],
    
    # Buttons
    "button_fg": COLORS["accent_primary"],
    "button_hover": COLORS["accent_secondary"],
    "button_text": COLORS["text_primary"],
    
    # Inputs
    "input_fg": COLORS["bg_input"],
    "input_border": COLORS["bg_hover"],
    "input_text": COLORS["text_primary"],
    
    # Labels
    "label_text": COLORS["text_primary"],
    "label_secondary": COLORS["text_secondary"],
}

# Font configuration
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "mono": ("Consolas", 11),
}
