"""
Theme configuration for ContentForge AI
Dark mode with vibrant accents
"""

# Color palette - Skull theme (Black, Blue, Cyan)
COLORS = {
    # Base colors - Pure black background
    "bg_dark": "#000000",
    "bg_card": "#0d1117",
    "bg_input": "#161b22",
    "bg_hover": "#1f2937",
    
    # Text colors
    "text_primary": "#ffffff",
    "text_secondary": "#9ca3af",
    "text_muted": "#6b7280",
    
    # Accent colors - Blue & Cyan theme
    "accent_primary": "#2563eb",     # Blue
    "accent_secondary": "#3b82f6",   # Light blue
    "accent_cyan": "#00d9ff",        # Cyan
    "accent_success": "#10b981",     # Emerald
    "accent_warning": "#f59e0b",     # Amber
    "accent_error": "#ef4444",       # Red
    
    # Social network colors
    "facebook": "#1877F2",
    "instagram": "#E4405F",
    "tiktok": "#000000",
    "twitter": "#1DA1F2",
    "youtube": "#FF0000",
    "telegram": "#0088CC",
    "linkedin": "#0A66C2",
    "pinterest": "#E60023",
    
    # Gradients (for buttons and progress bar)
    "gradient_start": "#2563eb",
    "gradient_end": "#00d9ff",
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
