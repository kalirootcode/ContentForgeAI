"""
Main Application Window for ContentForge AI
Professional desktop GUI with collapsible network menus, PNG icons, and media generation
"""

import customtkinter as ctk
from typing import Optional, Dict
import pyperclip
import threading
from pathlib import Path
from PIL import Image

from ..config import APP_NAME, APP_VERSION, SOCIAL_NETWORKS, CONTENT_TYPES, validate_config
from ..content_engine import ContentEngine
from ..media_generator import get_media_generator
from ..settings_manager import get_settings_manager
from ..web_researcher import get_web_researcher
from ..retention_generator import get_retention_generator
from .themes import COLORS, FONTS
from .icons import get_network_icon, get_content_icon

# Common emojis organized by category
EMOJI_CATEGORIES = {
    "💬 Expresiones": ["😀", "😂", "🤣", "😊", "😍", "🥰", "😎", "🤩", "😇", "🥳", "😏", "🤔", "🤯", "😱", "🔥", "💯", "✨", "💫", "⭐", "🌟"],
    "👍 Gestos": ["👍", "👎", "👏", "🙌", "🤝", "✌️", "🤞", "💪", "🖐️", "👋", "🙏", "💅", "🤙", "👊", "✊", "🤟", "👆", "👇", "👈", "👉"],
    "❤️ Corazones": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "♥️", "🫶"],
    "🚀 Tech": ["🚀", "💻", "🖥️", "⌨️", "🖱️", "💾", "📡", "🔌", "🔋", "🛡️", "🔐", "🔓", "🐛", "🤖", "👾", "🕷️", "🕸️", "⚡", "🌐", "📶"],
    "✅ Símbolos": ["✅", "❌", "⭕", "❗", "❓", "‼️", "⁉️", "💡", "📢", "📣", "🔔", "🔕", "⚠️", "🚫", "🔴", "🟢", "🔵", "🟡", "🟣", "⚫"],
    "🎉 Celebración": ["🎉", "🎊", "🎈", "🎁", "🎀", "🎄", "🎃", "🎆", "🎇", "🧨", "🪅", "🏅", "🏆", "🥂", "🍾", "🥳", "🎂", "🍰", "🧁", "🎵"],
}


class EmojiPicker(ctk.CTkToplevel):
    """Popup window for emoji selection."""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Selector de Emojis")
        self.geometry("420x380")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        
        # Wait for window to be ready before grabbing focus
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        """Setup content after window is ready."""
        self.grab_set()
        
        # Main scrollable container
        container = ctk.CTkScrollableFrame(
            self, 
            fg_color="#252540",
            corner_radius=10,
            scrollbar_button_color="#4a4a6a",
            scrollbar_button_hover_color="#6a6a8a"
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        for category_name, emojis in EMOJI_CATEGORIES.items():
            # Category label
            cat_label = ctk.CTkLabel(
                container, 
                text=category_name, 
                font=("Inter", 12, "bold"), 
                text_color="#a0a0c0"
            )
            cat_label.pack(anchor="w", padx=5, pady=(12, 5))
            
            # Emoji grid frame
            emoji_frame = ctk.CTkFrame(container, fg_color="#1e1e35", corner_radius=8)
            emoji_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            for i, emoji in enumerate(emojis):
                btn = ctk.CTkButton(
                    emoji_frame, 
                    text=emoji, 
                    width=32, 
                    height=32, 
                    font=("Segoe UI Emoji", 16),
                    fg_color="#2a2a4a", 
                    hover_color="#4a4a7a",
                    border_width=0,
                    corner_radius=6,
                    command=lambda e=emoji: self._select(e)
                )
                btn.grid(row=i // 10, column=i % 10, padx=2, pady=2)
        
        # Force update
        self.update_idletasks()
    
    def _select(self, emoji: str):
        self.callback(emoji)
        self.destroy()


class ImagePreview(ctk.CTkToplevel):
    """Popup window for image preview."""
    
    def __init__(self, parent, image_path: str):
        super().__init__(parent)
        self.title("Vista Previa de Imagen")
        self.geometry("600x500")
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        
        try:
            img = Image.open(image_path)
            img.thumbnail((580, 420), Image.Resampling.LANCZOS)
            self.ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            ctk.CTkLabel(self, image=self.ctk_image, text="").pack(pady=10)
            ctk.CTkLabel(self, text=Path(image_path).name, font=FONTS["small"], text_color=COLORS["text_secondary"]).pack()
            
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="📁 Abrir Carpeta", font=FONTS["small"], command=lambda: self._open_folder(image_path)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="Cerrar", font=FONTS["small"], fg_color=COLORS["bg_hover"], command=self.destroy).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error: {e}", text_color=COLORS["accent_error"]).pack(pady=20)
    
    def _open_folder(self, path: str):
        import subprocess
        subprocess.run(["xdg-open", str(Path(path).parent)])


# Image format options
IMAGE_FORMATS = {
    "1:1": {"name": "Cuadrado (1:1)", "desc": "Instagram, Facebook", "ratio": "1:1"},
    "4:3": {"name": "Horizontal (4:3)", "desc": "Presentaciones", "ratio": "4:3"},
    "16:9": {"name": "Widescreen (16:9)", "desc": "YouTube, Twitter", "ratio": "16:9"},
    "9:16": {"name": "Vertical (9:16)", "desc": "Stories, TikTok, Reels", "ratio": "9:16"},
    "3:4": {"name": "Retrato (3:4)", "desc": "Pinterest, Posts", "ratio": "3:4"},
}


class FormatPicker(ctk.CTkToplevel):
    """Dialog for selecting image/video format."""
    
    def __init__(self, parent, callback, title="Selecciona Formato"):
        super().__init__(parent)
        self.callback = callback
        self.title(title)
        self.geometry("350x380")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        self.selected_format = None
        
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        self.grab_set()
        
        ctk.CTkLabel(
            self, text="📐 Selecciona el formato", 
            font=("Inter", 16, "bold"), 
            text_color="#ffffff"
        ).pack(pady=(20, 15))
        
        container = ctk.CTkFrame(self, fg_color="#252540", corner_radius=10)
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for fmt_id, fmt_info in IMAGE_FORMATS.items():
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)
            
            btn = ctk.CTkButton(
                frame,
                text=f"  {fmt_info['name']}",
                font=("Inter", 13),
                height=45,
                anchor="w",
                fg_color="#2a2a4a",
                hover_color="#4a4a7a",
                corner_radius=8,
                command=lambda f=fmt_id: self._select(f)
            )
            btn.pack(fill="x", side="left", expand=True)
            
            ctk.CTkLabel(
                frame, text=fmt_info['desc'],
                font=("Inter", 10),
                text_color="#8080a0",
                width=100
            ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            self, text="Cancelar", 
            fg_color="#3a3a5a", 
            hover_color="#4a4a6a",
            command=self.destroy
        ).pack(pady=10)
    
    def _select(self, format_id: str):
        self.callback(format_id, IMAGE_FORMATS[format_id]["ratio"])
        self.destroy()


# Professional Media Styles
IMAGE_STYLES = {
    "minimalist": {
        "name": "🎯 Minimalista",
        "desc": "Diseño limpio, un elemento focal",
        "prompt": "Minimalist design, clean composition, single focal element, lots of negative space, professional, elegant"
    },
    "with_text": {
        "name": "📝 Con Texto",
        "desc": "Overlay con título/quote",
        "prompt": "Design with space for text overlay, bold typography area, contrasting background for readability, social media quote style"
    },
    "infographic": {
        "name": "📊 Infográfica",
        "desc": "Datos visuales, estadísticas",
        "prompt": "Infographic style, data visualization, icons, charts, step-by-step layout, educational, informative design"
    },
    "illustration": {
        "name": "🎨 Ilustración",
        "desc": "Estilo artístico, ilustrado",
        "prompt": "Artistic illustration style, hand-drawn feel, creative, colorful, unique artistic interpretation"
    },
    "mockup_ui": {
        "name": "💻 Mockup/UI",
        "desc": "Estilo interfaz, código, terminal",
        "prompt": "Tech mockup, code editor style, terminal interface, UI design, developer aesthetic, screen display"
    },
    "meme_viral": {
        "name": "😂 Meme/Viral",
        "desc": "Formato trending, engagement",
        "prompt": "Meme format, viral social media style, humorous, relatable, trending format, high engagement design"
    },
}

VIDEO_STYLES = {
    "representative": {
        "name": "🎬 Representativo",
        "desc": "Ilustra visualmente el concepto",
        "prompt": "Visual representation of the concept, cinematic, smooth motion, professional footage style"
    },
    "kinetic_text": {
        "name": "✨ Texto Animado",
        "desc": "Typography cinética, títulos",
        "prompt": "Kinetic typography, animated text, dynamic titles, motion graphics, bold typography animation"
    },
    "tutorial": {
        "name": "📚 Tutorial",
        "desc": "Paso a paso visual",
        "prompt": "Tutorial style, step-by-step visual guide, educational, clear demonstration, how-to format"
    },
    "promo_teaser": {
        "name": "🚀 Promo/Teaser",
        "desc": "Estilo trailer, impactante",
        "prompt": "Promotional teaser, trailer style, dramatic, impactful, exciting reveal, call to action"
    },
    "loop": {
        "name": "🔄 Loop Animado",
        "desc": "Animación que repite",
        "prompt": "Seamless loop animation, satisfying repeat, mesmerizing motion, perfect for stories and reels"
    },
    "prompt_only": {
        "name": "📋 Solo Prompt",
        "desc": "Genera prompt para otras plataformas",
        "prompt": "",
        "is_prompt_only": True
    },
}

# Add prompt_only to IMAGE_STYLES
IMAGE_STYLES["prompt_only"] = {
    "name": "📋 Solo Prompt",
    "desc": "Genera prompt para otras plataformas",
    "prompt": "",
    "is_prompt_only": True
}

# Script Types
SCRIPT_TYPES = {
    "reel": {
        "name": "📱 Reel/Short",
        "desc": "15-60 segundos, viral",
        "duration": "15-60s",
        "structure": "Hook → Contenido → CTA"
    },
    "long_video": {
        "name": "🎥 Video Largo",
        "desc": "3-10 minutos, completo",
        "duration": "3-10 min",
        "structure": "Intro → Secciones → Cierre"
    },
    "tutorial": {
        "name": "📚 Tutorial",
        "desc": "Paso a paso detallado",
        "duration": "Variable",
        "structure": "Problema → Pasos → Resultado"
    },
    "storytelling": {
        "name": "📖 Storytelling",
        "desc": "Narrativa con giro",
        "duration": "Variable",
        "structure": "Inicio → Conflicto → Resolución"
    },
}

# External Platforms for Prompts
IMAGE_PLATFORMS = {
    "midjourney": {"name": "🎨 Midjourney", "format": "--ar {ratio} --v 6.1"},
    "dalle": {"name": "🖼️ DALL-E 3", "format": "Aspect ratio: {ratio}"},
    "grok": {"name": "⚡ Grok/Flux", "format": "Format: {ratio}"},
    "stable": {"name": "🔥 Stable Diffusion", "format": "Resolution: {ratio}"},
}

VIDEO_PLATFORMS = {
    "runway": {"name": "🎬 Runway ML", "format": "Duration: 5s, Aspect: {ratio}"},
    "pika": {"name": "🎥 Pika Labs", "format": "Aspect ratio: {ratio}"},
    "kling": {"name": "🚀 Kling AI", "format": "Format: {ratio}, Duration: 5s"},
}


class MediaStylePicker(ctk.CTkToplevel):
    """Dialog for selecting image/video style."""
    
    def __init__(self, parent, callback, media_type="image", title="Selecciona Estilo"):
        super().__init__(parent)
        self.callback = callback
        self.media_type = media_type
        self.styles = IMAGE_STYLES if media_type == "image" else VIDEO_STYLES
        self.title(title)
        self.geometry("400x450")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        self.grab_set()
        
        icon = "🖼️" if self.media_type == "image" else "🎬"
        ctk.CTkLabel(
            self, text=f"{icon} Selecciona el estilo", 
            font=("Inter", 16, "bold"), 
            text_color="#ffffff"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self, text="El estilo define cómo se generará tu contenido", 
            font=("Inter", 11), 
            text_color="#8080a0"
        ).pack(pady=(0, 15))
        
        container = ctk.CTkScrollableFrame(self, fg_color="#252540", corner_radius=10)
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for style_id, style_info in self.styles.items():
            frame = ctk.CTkFrame(container, fg_color="#1e1e35", corner_radius=8)
            frame.pack(fill="x", padx=5, pady=4)
            
            btn = ctk.CTkButton(
                frame,
                text=f"  {style_info['name']}",
                font=("Inter", 13),
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color="#3a3a6a",
                corner_radius=6,
                command=lambda s=style_id: self._select(s)
            )
            btn.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(
                frame, text=style_info['desc'],
                font=("Inter", 10),
                text_color="#7070a0",
            ).pack(anchor="w", padx=15, pady=(0, 8))
        
        ctk.CTkButton(
            self, text="Cancelar", 
            fg_color="#3a3a5a", 
            hover_color="#4a4a6a",
            command=self.destroy
        ).pack(pady=10)
    
    def _select(self, style_id: str):
        style_info = self.styles[style_id]
        is_prompt_only = style_info.get("is_prompt_only", False)
        self.callback(style_id, style_info["prompt"], is_prompt_only)
        self.destroy()


class ScriptTypePicker(ctk.CTkToplevel):
    """Dialog for selecting script type."""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Tipo de Guión")
        self.geometry("420x450")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        self.grab_set()
        
        ctk.CTkLabel(
            self, text="📜 Selecciona tipo de guión", 
            font=("Inter", 16, "bold"), 
            text_color="#ffffff"
        ).pack(pady=(20, 15))
        
        container = ctk.CTkScrollableFrame(self, fg_color="#252540", corner_radius=10)
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for script_id, script_info in SCRIPT_TYPES.items():
            frame = ctk.CTkFrame(container, fg_color="#1e1e35", corner_radius=8)
            frame.pack(fill="x", padx=5, pady=4)
            
            btn = ctk.CTkButton(
                frame,
                text=f"  {script_info['name']}",
                font=("Inter", 13),
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color="#3a3a6a",
                corner_radius=6,
                command=lambda s=script_id: self._select(s)
            )
            btn.pack(fill="x", padx=5, pady=2)
            
            info_frame = ctk.CTkFrame(frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(0, 8))
            
            ctk.CTkLabel(
                info_frame, text=f"⏱️ {script_info['duration']}",
                font=("Inter", 10), text_color="#7070a0"
            ).pack(side="left", padx=(0, 15))
            
            ctk.CTkLabel(
                info_frame, text=script_info['structure'],
                font=("Inter", 10), text_color="#9090b0"
            ).pack(side="left")
        
        ctk.CTkButton(
            self, text="Cancelar", 
            fg_color="#3a3a5a", hover_color="#4a4a6a",
            command=self.destroy
        ).pack(pady=10)
    
    def _select(self, script_id: str):
        self.callback(script_id, SCRIPT_TYPES[script_id])
        self.destroy()


class PlatformPicker(ctk.CTkToplevel):
    """Dialog for selecting external platform for prompt."""
    
    def __init__(self, parent, callback, media_type="image"):
        super().__init__(parent)
        self.callback = callback
        self.media_type = media_type
        self.platforms = IMAGE_PLATFORMS if media_type == "image" else VIDEO_PLATFORMS
        self.title("Plataforma Externa")
        self.geometry("350x350")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        self.grab_set()
        
        icon = "🖼️" if self.media_type == "image" else "🎬"
        ctk.CTkLabel(
            self, text=f"{icon} Selecciona plataforma", 
            font=("Inter", 16, "bold"), 
            text_color="#ffffff"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self, text="El prompt se optimizará para esta plataforma", 
            font=("Inter", 11), text_color="#8080a0"
        ).pack(pady=(0, 15))
        
        container = ctk.CTkFrame(self, fg_color="#252540", corner_radius=10)
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for plat_id, plat_info in self.platforms.items():
            btn = ctk.CTkButton(
                container,
                text=f"  {plat_info['name']}",
                font=("Inter", 13),
                height=45,
                anchor="w",
                fg_color="#2a2a4a",
                hover_color="#4a4a7a",
                corner_radius=8,
                command=lambda p=plat_id: self._select(p)
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            self, text="Cancelar", 
            fg_color="#3a3a5a", hover_color="#4a4a6a",
            command=self.destroy
        ).pack(pady=10)
    
    def _select(self, platform_id: str):
        self.callback(platform_id, self.platforms[platform_id])
        self.destroy()


class PromptPreview(ctk.CTkToplevel):
    """Dialog to preview and copy generated prompt."""
    
    def __init__(self, parent, prompt: str, platform_name: str):
        super().__init__(parent)
        self.prompt = prompt
        self.title(f"Prompt para {platform_name}")
        self.geometry("600x450")
        self.configure(fg_color="#1a1a2e")
        self.transient(parent)
        
        self.after(100, self._setup_content)
    
    def _setup_content(self):
        self.grab_set()
        
        ctk.CTkLabel(
            self, text="📋 Prompt Generado", 
            font=("Inter", 16, "bold"), 
            text_color="#ffffff"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self, text="Copia este prompt para usarlo en la plataforma externa", 
            font=("Inter", 11), text_color="#8080a0"
        ).pack(pady=(0, 15))
        
        # Prompt text area
        self.text_box = ctk.CTkTextbox(
            self, fg_color="#252540", 
            font=("Consolas", 12),
            corner_radius=10
        )
        self.text_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.text_box.insert("0.0", self.prompt)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.copy_btn = ctk.CTkButton(
            btn_frame, text="📋 Copiar al Portapapeles",
            font=("Inter", 13),
            fg_color="#6a4aff",
            hover_color="#8a6aff",
            command=self._copy
        )
        self.copy_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="Cerrar",
            fg_color="#3a3a5a", hover_color="#4a4a6a",
            command=self.destroy
        ).pack(side="left", padx=5)
    
    def _copy(self):
        try:
            pyperclip.copy(self.prompt)
            self.copy_btn.configure(text="✅ Copiado!")
            self.after(1500, lambda: self.copy_btn.configure(text="📋 Copiar al Portapapeles"))
        except Exception:
            pass


class SettingsWindow(ctk.CTkToplevel):
    """Settings window for managing social media links."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ Configuración - Links de Investigación")
        self.geometry("600x500")
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        
        self.settings = get_settings_manager()
        self._create_ui()
    
    def _create_ui(self):
        # Header
        ctk.CTkLabel(self, text="📋 Links para Investigación", font=FONTS["title"], text_color=COLORS["text_primary"]).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Agrega links de grupos/páginas para analizar", font=FONTS["small"], text_color=COLORS["text_muted"]).pack()
        
        # Add link section
        add_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        add_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(add_frame, text="Agregar Nuevo Link", font=FONTS["heading"], text_color=COLORS["text_primary"]).pack(anchor="w", padx=10, pady=(10, 5))
        
        input_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=10, pady=5)
        
        self.section_var = ctk.StringVar(value="facebook_groups")
        ctk.CTkOptionMenu(input_row, values=["facebook_groups", "facebook_pages", "twitter_accounts", "other_links"],
                          variable=self.section_var, width=150, fg_color=COLORS["bg_input"]).pack(side="left", padx=(0, 5))
        
        self.name_entry = ctk.CTkEntry(input_row, placeholder_text="Nombre", width=120, fg_color=COLORS["bg_input"])
        self.name_entry.pack(side="left", padx=5)
        
        self.url_entry = ctk.CTkEntry(input_row, placeholder_text="URL del link", width=200, fg_color=COLORS["bg_input"])
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(input_row, text="➕", width=40, fg_color=COLORS["accent_primary"], command=self._add_link).pack(side="left", padx=5)
        
        # Links list
        ctk.CTkLabel(self, text="Links Configurados", font=FONTS["heading"], text_color=COLORS["text_primary"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.links_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        self.links_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self._refresh_links()
    
    def _add_link(self):
        section = self.section_var.get()
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if name and url:
            self.settings.add_link(section, name, url)
            self.name_entry.delete(0, "end")
            self.url_entry.delete(0, "end")
            self._refresh_links()
    
    def _remove_link(self, section: str, url: str):
        self.settings.remove_link(section, url)
        self._refresh_links()
    
    def _refresh_links(self):
        for widget in self.links_frame.winfo_children():
            widget.destroy()
        
        all_links = self.settings.get_all_links()
        section_names = {"facebook_groups": "📘 Grupos FB", "facebook_pages": "📄 Páginas FB", 
                         "twitter_accounts": "🐦 Twitter", "other_links": "🔗 Otros"}
        
        for section, links in all_links.items():
            if links:
                ctk.CTkLabel(self.links_frame, text=section_names.get(section, section), 
                            font=FONTS["heading"], text_color=COLORS["accent_cyan"]).pack(anchor="w", pady=(10, 3))
                
                for link in links:
                    row = ctk.CTkFrame(self.links_frame, fg_color=COLORS["bg_input"], corner_radius=4)
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text=f"{link['name']}: {link['url'][:40]}...", font=FONTS["small"], 
                                text_color=COLORS["text_secondary"]).pack(side="left", padx=10, pady=5)
                    ctk.CTkButton(row, text="🗑️", width=30, fg_color=COLORS["accent_error"], height=24,
                                 command=lambda s=section, u=link['url']: self._remove_link(s, u)).pack(side="right", padx=5, pady=3)


class ResearchWindow(ctk.CTkToplevel):
    """Research window for analyzing content and generating retention comments."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🔍 Investigar y Generar Comentarios")
        self.geometry("950x650")
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        
        self.researcher = get_web_researcher()
        self.generator = get_retention_generator()
        self.settings = get_settings_manager()
        self._create_ui()
    
    def _create_ui(self):
        # Main container with 2 columns
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # LEFT PANEL - Configured Links
        left_panel = ctk.CTkFrame(main_container, width=280, fg_color=COLORS["bg_card"], corner_radius=8)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_propagate(False)
        
        ctk.CTkLabel(left_panel, text="📋 Links Guardados", font=FONTS["heading"], text_color=COLORS["accent_cyan"]).pack(pady=(15, 10))
        
        self.links_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.links_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        self._load_configured_links()
        
        ctk.CTkButton(left_panel, text="⚙️ Gestionar Links", height=30, fg_color=COLORS["bg_input"],
                      command=lambda: SettingsWindow(self)).pack(pady=10, padx=10, fill="x")
        
        # RIGHT PANEL - Search and Results
        right_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Search bar
        search_frame = ctk.CTkFrame(right_panel, fg_color=COLORS["bg_card"], corner_radius=8)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        search_row = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=10, pady=10)
        
        self.query_entry = ctk.CTkEntry(search_row, placeholder_text="Buscar tema o pegar URL/contenido...", 
                                        height=35, fg_color=COLORS["bg_input"])
        self.query_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.platform_var = ctk.StringVar(value="facebook")
        ctk.CTkOptionMenu(search_row, values=["facebook", "twitter", "linkedin", "general"], 
                          variable=self.platform_var, width=110, fg_color=COLORS["bg_input"]).pack(side="left", padx=5)
        
        ctk.CTkButton(search_row, text="🔍 Buscar", width=90, fg_color=COLORS["accent_primary"],
                      command=self._do_search).pack(side="left", padx=5)
        
        # Results header with actions
        results_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        results_header.grid(row=1, column=0, sticky="ew")
        
        ctk.CTkLabel(results_header, text="📊 Posts Encontrados", font=FONTS["heading"], 
                    text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(results_header, text="💬 Generar Comentario", width=150, height=28,
                      fg_color=COLORS["accent_cyan"], command=self._generate_comment).pack(side="right")
        
        # Extension listener button
        self.listen_btn = ctk.CTkButton(results_header, text="📡 Esperar Extensión", width=140, height=28,
                      fg_color="#22c55e", command=self._toggle_extension_listener)
        self.listen_btn.pack(side="right", padx=5)
        
        # Results text
        self.results_text = ctk.CTkTextbox(right_panel, fg_color=COLORS["bg_input"], 
                                           font=("Segoe UI", 11), wrap="word")
        self.results_text.grid(row=2, column=0, sticky="nsew", pady=10)
        self.results_text.insert("0.0", "📌 Selecciona un link guardado o busca un tema\n\n" +
                                 "• Haz clic en un link de la izquierda para investigarlo\n" +
                                 "• O escribe un tema en la barra de búsqueda\n" +
                                 "• 📡 'Esperar Extensión' para recibir contenido desde Chrome")
        
        # Comment section
        ctk.CTkLabel(right_panel, text="✨ Comentario de Retención", font=FONTS["heading"],
                    text_color=COLORS["text_primary"]).grid(row=3, column=0, sticky="w")
        
        self.comment_text = ctk.CTkTextbox(right_panel, fg_color="#0f1218", font=("Segoe UI", 13), 
                                            height=80, wrap="word")
        self.comment_text.grid(row=4, column=0, sticky="ew", pady=(5, 10))
        
        # Bottom buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.grid(row=5, column=0)
        
        ctk.CTkButton(btn_frame, text="📋 Copiar", fg_color=COLORS["accent_primary"],
                      command=self._copy_comment).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cerrar", fg_color=COLORS["bg_hover"], 
                      command=self._on_close).pack(side="left", padx=5)
        
        # Extension listener state
        self.listening = False
        self.last_content_id = 0
    
    def _on_close(self):
        """Handle window close, stop listener."""
        self.listening = False
        self.destroy()
    
    def _toggle_extension_listener(self):
        """Toggle extension content listener."""
        if self.listening:
            self.listening = False
            self.listen_btn.configure(text="📡 Esperar Extensión", fg_color="#22c55e")
            self.results_text.delete("0.0", "end")
            self.results_text.insert("0.0", "⏹️ Escucha detenida.\n\nHaz clic en '📡 Esperar Extensión' para reanudar.")
        else:
            self.listening = True
            self.listen_btn.configure(text="⏹️ Detener", fg_color="#ef4444")
            self.results_text.delete("0.0", "end")
            self.results_text.insert("0.0", "📡 ESCUCHANDO EXTENSIÓN...\n\n" +
                                     "╔════════════════════════════════════════════════════════╗\n" +
                                     "║   Esperando contenido desde Chrome Extension...        ║\n" +
                                     "║                                                        ║\n" +
                                     "║   1. Navega a cualquier página web                     ║\n" +
                                     "║   2. Haz clic en la extensión ContentForge             ║\n" +
                                     "║   3. Presiona 'Extraer' → 'Enviar a ContentForge'      ║\n" +
                                     "╚════════════════════════════════════════════════════════╝\n")
            self._poll_extension()
    
    def _poll_extension(self):
        """Poll API server for new content from extension."""
        if not self.listening:
            return
        
        def check_api():
            try:
                import urllib.request
                import json
                
                req = urllib.request.Request("http://localhost:5678/content/latest")
                with urllib.request.urlopen(req, timeout=2) as response:
                    data = json.loads(response.read().decode())
                    content = data.get("content")
                    
                    if content and content.get("id", 0) > self.last_content_id:
                        self.last_content_id = content["id"]
                        self.after(0, lambda: self._display_extension_content(content))
                        return
            except Exception as e:
                pass  # API not available or no new content
            
            # Continue polling if still listening
            if self.listening:
                self.after(2000, self._poll_extension)
        
        threading.Thread(target=check_api, daemon=True).start()
    
    def _display_extension_content(self, content: dict):
        """Display content received from Chrome extension."""
        self.results_text.delete("0.0", "end")
        
        title = content.get("title", "Sin título")
        url = content.get("url", "")
        text = content.get("text", "")[:2000]
        meta = content.get("meta", {})
        
        display = "╔" + "═" * 58 + "╗\n"
        display += f"║  📥 CONTENIDO RECIBIDO DE CHROME                         ║\n"
        display += "╠" + "═" * 58 + "╣\n"
        display += f"║  🏷️  {title[:50]:<50}  ║\n"
        display += "╚" + "═" * 58 + "╝\n\n"
        
        display += f"🔗 URL: {url}\n"
        display += "─" * 60 + "\n\n"
        display += "📄 CONTENIDO EXTRAÍDO:\n\n"
        display += text + "\n\n"
        display += "─" * 60 + "\n"
        display += "✅ ¡Listo para generar comentario de retención!\n"
        
        self.results_text.insert("0.0", display)
        
        # Stop listening after receiving
        self.listening = False
        self.listen_btn.configure(text="📡 Esperar Extensión", fg_color="#22c55e")
    
    def _load_configured_links(self):
        """Load and display configured links from settings."""
        for widget in self.links_scroll.winfo_children():
            widget.destroy()
        
        all_links = self.settings.get_all_links()
        section_icons = {"facebook_groups": "📘", "facebook_pages": "📄", 
                         "twitter_accounts": "🐦", "linkedin_pages": "💼", "other_links": "🔗"}
        
        has_links = False
        for section, links in all_links.items():
            for link in links:
                has_links = True
                icon = section_icons.get(section, "🔗")
                
                link_btn = ctk.CTkButton(
                    self.links_scroll, text=f"{icon} {link['name']}", 
                    anchor="w", fg_color=COLORS["bg_input"], hover_color=COLORS["bg_hover"],
                    height=32, font=FONTS["small"],
                    command=lambda u=link['url'], n=link['name']: self._research_link(u, n)
                )
                link_btn.pack(fill="x", pady=2)
        
        if not has_links:
            ctk.CTkLabel(self.links_scroll, text="No hay links configurados\n\nUsa ⚙️ Gestionar Links\npara agregar grupos/páginas",
                        font=FONTS["small"], text_color=COLORS["text_muted"]).pack(pady=20)
    
    def _research_link(self, url: str, name: str):
        """Research a configured link for popular posts."""
        self.results_text.delete("0.0", "end")
        self.results_text.insert("0.0", f"🔍 Investigando: {name}...\n\n⏳ Buscando contenido relacionado...")
        
        def research():
            # Detect if it's a Facebook group
            is_fb_group = "facebook.com/groups" in url
            
            if is_fb_group:
                # Use specialized Facebook group research
                data = self.researcher.research_facebook_group(name, url)
                results = data.get('related_posts', [])
                note = data.get('note', '')
            else:
                # Generic search
                results = self.researcher.find_trending_content(name)
                note = ""
            
            # Build elegant output
            text = "╔" + "═" * 58 + "╗\n"
            text += f"║  🎯 {name[:50]:<50}  ║\n"
            text += "╠" + "═" * 58 + "╣\n"
            text += f"║  🔗 {url[:50]:<50}  ║\n"
            text += "╚" + "═" * 58 + "╝\n\n"
            
            if note:
                text += f"{note}\n\n"
            
            text += "📊 CONTENIDO RELACIONADO ENCONTRADO:\n"
            text += "─" * 60 + "\n\n"
            
            for i, r in enumerate(results[:8], 1):
                title = r.get('title', 'Sin título')[:60]
                body = r.get('body', '')[:120]
                link = r.get('href', '')
                
                text += f"┌─ {i}. {title}\n"
                text += f"│  {body}...\n"
                text += f"└─ 🌐 {link}\n\n"
            
            if not results:
                text += "❌ No se encontraron resultados.\n"
                text += "💡 Intenta buscar manualmente con palabras clave del tema.\n"
            
            self.after(0, lambda: self.results_text.delete("0.0", "end"))
            self.after(0, lambda: self.results_text.insert("0.0", text))
        
        threading.Thread(target=research).start()
    
    def _do_search(self):
        query = self.query_entry.get().strip()
        if not query:
            return
        
        self.results_text.delete("0.0", "end")
        self.results_text.insert("0.0", "🔍 Buscando posts populares...")
        
        def search():
            platform = self.platform_var.get()
            
            # Search for posts with engagement
            if platform == "general":
                results = self.researcher.search(f"{query} popular viral", max_results=8)
            else:
                results = self.researcher.search_social(platform, f"{query} most comments popular", max_results=8)
            
            # Also get engagement patterns
            engagement = self.researcher.find_engagement_patterns(query)
            
            text = f"🔍 Resultados para: {query}\n"
            text += "─" * 50 + "\n\n"
            text += "📈 POSTS CON MÁS INTERACCIÓN:\n\n"
            
            all_results = results + engagement.get('high_engagement_content', [])[:3]
            
            for i, r in enumerate(all_results[:10], 1):
                text += f"{i}. {r.get('title', 'Sin título')}\n"
                text += f"   {r.get('body', '')[:150]}...\n"
                text += f"   🔗 {r.get('href', '')}\n\n"
            
            self.after(0, lambda: self.results_text.delete("0.0", "end"))
            self.after(0, lambda: self.results_text.insert("0.0", text if all_results else "No se encontraron resultados."))
        
        threading.Thread(target=search).start()
    
    def _generate_comment(self):
        content = self.results_text.get("0.0", "end").strip()
        if not content or "Buscando" in content or "Investigando" in content:
            return
        
        self.comment_text.delete("0.0", "end")
        self.comment_text.insert("0.0", "⏳ Generando comentario de retención...")
        
        def generate():
            platform = self.platform_var.get()
            comment = self.generator.generate_retention_comment(content, platform, style="curious")
            self.after(0, lambda: self.comment_text.delete("0.0", "end"))
            self.after(0, lambda: self.comment_text.insert("0.0", comment if comment else "Error al generar"))
        
        threading.Thread(target=generate).start()
    
    def _copy_comment(self):
        comment = self.comment_text.get("0.0", "end").strip()
        if comment:
            try:
                pyperclip.copy(comment)
            except:
                pass


class ContentForgeApp(ctk.CTk):
    """Main application window with collapsible network menus and media generation."""
    
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.engine = ContentEngine()
        self.media_gen = get_media_generator()
        self.selected_network = None
        self.selected_content_type = None
        self.expanded_network = None
        self.network_frames = {}
        self.content_type_frames = {}
        self.current_content_id = None
        
        self._create_layout()
        self._check_api_status()
    
    def _create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Footer row
        self._create_sidebar()
        self._create_main_area()
        self._create_footer()
    
    def _create_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color=COLORS["bg_card"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo - compact
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(12, 8))
        ctk.CTkLabel(title_frame, text="🚀 ContentForge", font=FONTS["title"], text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="AI Content Generator", font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w")
        
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["bg_hover"]).pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(self.sidebar, text="REDES SOCIALES", font=("Inter", 10, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(0, 6))
        
        for network in SOCIAL_NETWORKS:
            self._create_network_section(network)
        
        # Tools Section
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["bg_hover"]).pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(self.sidebar, text="HERRAMIENTAS", font=("Inter", 10, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(0, 6))
        
        tools_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        tools_frame.pack(fill="x", padx=8)
        
        tool_btn_style = {"font": FONTS["body"], "height": 32, "anchor": "w", "fg_color": "transparent", "hover_color": COLORS["bg_hover"], "text_color": COLORS["text_primary"]}
        
        self.research_btn = ctk.CTkButton(tools_frame, text="🔍 Investigar", command=self._open_research, **tool_btn_style)
        self.research_btn.pack(fill="x", pady=2)
        
        self.settings_btn = ctk.CTkButton(tools_frame, text="⚙️ Configuración", command=self._open_settings, **tool_btn_style)
        self.settings_btn.pack(fill="x", pady=2)
        
        # Status at bottom
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", padx=12, pady=12)
        self.status_indicator = ctk.CTkLabel(status_frame, text="⚪ Verificando...", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.status_indicator.pack(anchor="w")
    
    def _create_network_section(self, network: Dict):
        network_id = network['id']
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.pack(fill="x", padx=4, pady=1)
        
        icon = get_network_icon(network_id)
        if icon:
            header_btn = ctk.CTkButton(container, text=f"  {network['name']}  ▼", image=icon, compound="left",
                                       font=FONTS["body"], height=36, anchor="w", fg_color="transparent",
                                       hover_color=COLORS["bg_hover"], text_color=COLORS["text_primary"],
                                       command=lambda n=network_id: self._toggle_network(n))
        else:
            header_btn = ctk.CTkButton(container, text=f"{network['icon']}  {network['name']}  ▼",
                                       font=FONTS["body"], height=36, anchor="w", fg_color="transparent",
                                       hover_color=COLORS["bg_hover"], text_color=COLORS["text_primary"],
                                       command=lambda n=network_id: self._toggle_network(n))
        header_btn.pack(fill="x", padx=4)
        self.network_frames[network_id] = {"header": header_btn, "container": container, "icon": icon}
        
        types_frame = ctk.CTkFrame(container, fg_color=COLORS["bg_input"], corner_radius=6)
        self.content_type_frames[network_id] = {"frame": types_frame, "buttons": {}}
        
        for type_id, type_info in CONTENT_TYPES.items():
            content_icon = get_content_icon(type_id)
            if content_icon:
                type_btn = ctk.CTkButton(types_frame, text=f"  {type_info['name']}", image=content_icon, compound="left",
                                         font=FONTS["small"], height=28, anchor="w", fg_color="transparent",
                                         hover_color=COLORS["accent_primary"], text_color=COLORS["text_secondary"],
                                         command=lambda n=network_id, t=type_id: self._select_content_type(n, t))
            else:
                type_btn = ctk.CTkButton(types_frame, text=f"  {type_info['icon']} {type_info['name']}",
                                         font=FONTS["small"], height=28, anchor="w", fg_color="transparent",
                                         hover_color=COLORS["accent_primary"], text_color=COLORS["text_secondary"],
                                         command=lambda n=network_id, t=type_id: self._select_content_type(n, t))
            type_btn.pack(fill="x", padx=6, pady=1)
            self.content_type_frames[network_id]["buttons"][type_id] = {"btn": type_btn, "icon": content_icon}
    
    def _toggle_network(self, network_id: str):
        if self.expanded_network and self.expanded_network != network_id:
            old_frame = self.content_type_frames[self.expanded_network]["frame"]
            old_frame.pack_forget()
            old_header = self.network_frames[self.expanded_network]["header"]
            network = next(n for n in SOCIAL_NETWORKS if n['id'] == self.expanded_network)
            icon = self.network_frames[self.expanded_network].get("icon")
            if icon:
                old_header.configure(text=f"  {network['name']}  ▼", fg_color="transparent")
            else:
                old_header.configure(text=f"{network['icon']}  {network['name']}  ▼", fg_color="transparent")
        
        types_frame = self.content_type_frames[network_id]["frame"]
        header_btn = self.network_frames[network_id]["header"]
        network = next(n for n in SOCIAL_NETWORKS if n['id'] == network_id)
        icon = self.network_frames[network_id].get("icon")
        
        if self.expanded_network == network_id:
            types_frame.pack_forget()
            if icon:
                header_btn.configure(text=f"  {network['name']}  ▼", fg_color="transparent")
            else:
                header_btn.configure(text=f"{network['icon']}  {network['name']}  ▼", fg_color="transparent")
            self.expanded_network = None
        else:
            types_frame.pack(fill="x", padx=8, pady=(0, 4))
            if icon:
                header_btn.configure(text=f"  {network['name']}  ▲", fg_color=COLORS["accent_primary"])
            else:
                header_btn.configure(text=f"{network['icon']}  {network['name']}  ▲", fg_color=COLORS["accent_primary"])
            self.expanded_network = network_id
    
    def _select_content_type(self, network_id: str, content_type: str):
        self.selected_network = network_id
        self.selected_content_type = content_type
        self.engine.set_network(network_id)
        self.engine.set_content_type(content_type)
        
        for nid, data in self.content_type_frames.items():
            for tid, btn_data in data["buttons"].items():
                if nid == network_id and tid == content_type:
                    btn_data["btn"].configure(fg_color=COLORS["accent_primary"], text_color=COLORS["text_primary"])
                else:
                    btn_data["btn"].configure(fg_color="transparent", text_color=COLORS["text_secondary"])
        
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == network_id), None)
        type_info = CONTENT_TYPES.get(content_type, {})
        network_icon = self.network_frames[network_id].get("icon")
        content_icon = self.content_type_frames[network_id]["buttons"].get(content_type, {}).get("icon")
        self._update_header(network, type_info, network_icon, content_icon)
    
    def _update_header(self, network, type_info, network_icon, content_icon):
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        if network_icon:
            ctk.CTkLabel(self.header_frame, image=network_icon, text="").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(self.header_frame, text=network['name'], font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(self.header_frame, text=" → ", font=FONTS["subtitle"], text_color=COLORS["text_muted"]).pack(side="left")
        if content_icon:
            ctk.CTkLabel(self.header_frame, image=content_icon, text="").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(self.header_frame, text=type_info['name'], font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(side="left")
    
    def _create_main_area(self):
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        self.header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self.header_frame, text="👈 Selecciona red y contenido", font=FONTS["subtitle"], text_color=COLORS["text_muted"]).pack(side="left")
        
        input_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        top_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(top_row, text="📝 Tema:", font=FONTS["body"], text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
        
        # Length selection
        self.length_var = ctk.StringVar(value="Medio")
        self.length_seg = ctk.CTkSegmentedButton(
            top_row, values=["Corto", "Medio", "Largo"], variable=self.length_var,
            font=("Segoe UI", 11), height=28,
            fg_color=COLORS["bg_input"], selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["accent_secondary"]
        )
        self.length_seg.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        self.generate_btn = ctk.CTkButton(top_row, text="✨ Generar", font=FONTS["body"], width=120, height=32,
                                          fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"],
                                          command=self._generate_content)
        self.generate_btn.grid(row=0, column=2, sticky="e")
        
        self.topic_entry = ctk.CTkTextbox(input_frame, height=60, font=FONTS["body"],
                                          fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
                                          border_color=COLORS["bg_hover"], border_width=1)
        self.topic_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        self.topic_entry.insert("0.0", "Ej: cómo usar nmap para escanear puertos...")
        self.topic_entry.bind("<FocusIn>", self._clear_placeholder)
        
        # Professional Output Area
        output_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        
        header_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=12, pady=8, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_row, text="📄 Resultado", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
        
        actions = ctk.CTkFrame(header_row, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")
        
        btn_style = {"width": 80, "height": 28, "font": ("Segoe UI", 11), "fg_color": COLORS["bg_input"], "hover_color": COLORS["bg_hover"]}
        self.emoji_btn = ctk.CTkButton(actions, text="😀 Emoji", command=self._open_emoji_picker, **btn_style)
        self.emoji_btn.pack(side="left", padx=3)
        self.copy_btn = ctk.CTkButton(actions, text="📋 Copiar", command=self._copy_content, **btn_style)
        self.copy_btn.pack(side="left", padx=3)
        self.regen_btn = ctk.CTkButton(actions, text="🔄 Nuevo", command=self._regenerate_content, **btn_style)
        self.regen_btn.pack(side="left", padx=3)
        
        # Elegant output textbox
        self.output_text = ctk.CTkTextbox(
            output_frame, font=("Segoe UI Emoji", 13),
            fg_color="#0f1218", text_color="#e5e7eb", 
            wrap="word", border_width=1, border_color="#1f2937", corner_radius=4
        )
        self.output_text.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.output_text.insert("0.0", "Aquí aparecerá tu contenido generado por IA...\n\n1. Selecciona una red social\n2. Elige el tipo de contenido\n3. Escribe un tema y presiona Generar")
        
        media_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        media_frame.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="ew")
        
        media_btn_style = {"height": 32, "font": FONTS["body"], "fg_color": COLORS["accent_secondary"], "hover_color": COLORS["accent_primary"]}
        self.gen_image_btn = ctk.CTkButton(media_frame, text="🖼️ Generar Imagen", width=150, command=self._generate_image, **media_btn_style)
        self.gen_image_btn.pack(side="left", padx=(0, 8))
        self.gen_video_btn = ctk.CTkButton(media_frame, text="🎬 Crear Video", width=140, command=self._generate_video, **media_btn_style)
        self.gen_video_btn.pack(side="left", padx=(0, 8))
        self.gen_script_btn = ctk.CTkButton(media_frame, text="📜 Script", width=100, command=self._generate_script, **media_btn_style)
        self.gen_script_btn.pack(side="left", padx=(0, 8))
        self.media_status = ctk.CTkLabel(media_frame, text="", font=FONTS["small"], text_color=COLORS["text_muted"])
        self.media_status.pack(side="left", padx=10)
    
    def _clear_placeholder(self, event):
        current = self.topic_entry.get("0.0", "end").strip()
        if "Ej:" in current:
            self.topic_entry.delete("0.0", "end")
    
    def _open_emoji_picker(self):
        EmojiPicker(self, self._insert_emoji)
    
    def _insert_emoji(self, emoji: str):
        self.output_text.insert("insert", emoji)
    
    def _generate_content(self):
        if not self.selected_network or not self.selected_content_type:
            self._show_output("❌ Selecciona red social y tipo de contenido primero.")
            return
        topic = self.topic_entry.get("0.0", "end").strip()
        if not topic or "Ej:" in topic:
            self._show_output("❌ Escribe un tema primero.")
            return
        
        self.generate_btn.configure(text="⏳...", state="disabled")
        self._show_output("⏳ Generando contenido...\n\nEspera unos segundos...")
        self._start_progress("📝 Generando contenido...", 5.0)
        
        # Get selected length and map to engine format
        length_map = {"Corto": "short", "Medio": "medium", "Largo": "long"}
        selected_length = self.length_var.get()
        length_key = length_map.get(selected_length, "medium")
        
        def generate():
            result = self.engine.generate(topic, length=length_key)
            self.after(0, lambda: self._on_generate_complete(result))
        threading.Thread(target=generate).start()
    
    def _on_generate_complete(self, result: str):
        self.generate_btn.configure(text="✨ Generar", state="normal")
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == self.selected_network), {})
        type_info = CONTENT_TYPES.get(self.selected_content_type, {})
        header = f"{'─' * 40}\n{network.get('icon', '')} {network.get('name', '')} │ {type_info.get('icon', '')} {type_info.get('name', '')}\n{'─' * 40}\n\n"
        self._show_output(header + result)
        self._complete_progress("✅ Contenido generado")
    
    def _regenerate_content(self):
        self._generate_content()
    
    def _show_output(self, text: str):
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", text)
    
    def _copy_content(self):
        content = self.output_text.get("0.0", "end").strip()
        if content:
            try:
                pyperclip.copy(content)
                self.copy_btn.configure(text="✅ OK!")
                self.after(1500, lambda: self.copy_btn.configure(text="📋 Copiar"))
            except Exception as e:
                self._show_output(f"❌ Error: {e}")
    
    def _generate_image(self):
        """Show style picker, then format picker before generating image."""
        content = self.output_text.get("0.0", "end").strip()
        if not content or "Tu contenido" in content:
            self.media_status.configure(text="❌ Genera contenido primero", text_color=COLORS["accent_error"])
            return
        if not self.selected_network:
            self.media_status.configure(text="❌ Selecciona una red", text_color=COLORS["accent_error"])
            return
        
        # Step 1: Show style picker
        MediaStylePicker(self, self._on_image_style_selected, "image", "Estilo de Imagen")
    
    def _on_image_style_selected(self, style_id: str, style_prompt: str, is_prompt_only: bool = False):
        """Step 2: Show format/platform picker after style selection."""
        self.selected_image_style = style_id
        self.selected_style_prompt = style_prompt
        
        if is_prompt_only:
            # Show platform picker for external prompt
            PlatformPicker(self, self._on_image_platform_selected, "image")
        else:
            FormatPicker(self, self._on_format_selected_image, "Formato de Imagen")
    
    def _on_image_platform_selected(self, platform_id: str, platform_info: dict):
        """Generate prompt for external platform."""
        content = self.output_text.get("0.0", "end").strip()
        
        # Show format picker for aspect ratio
        self.selected_image_platform = platform_id
        self.selected_platform_info = platform_info
        FormatPicker(self, self._on_format_selected_for_prompt, "Formato de Imagen")
    
    def _on_format_selected_image(self, format_id: str, aspect_ratio: str):
        """Step 3: Generate image with style and format."""
        content = self.output_text.get("0.0", "end").strip()
        style_prompt = getattr(self, 'selected_style_prompt', '')
        style_id = getattr(self, 'selected_image_style', 'minimalist')
        
        style_name = IMAGE_STYLES.get(style_id, {}).get('name', style_id)
        self.gen_image_btn.configure(text="⏳...", state="disabled")
        self.media_status.configure(text=f"Creando {style_name} {aspect_ratio}...", text_color=COLORS["text_muted"])
        self._start_progress("🖼️ Generando imagen...", 8.0)
        
        def generate():
            try:
                prompt = self.media_gen.analyze_content_for_image(content, self.selected_network, style_prompt)
                if not prompt:
                    self.after(0, lambda: self._on_image_error("No se pudo generar prompt"))
                    return
                self.after(0, lambda: self.media_status.configure(text="Generando imagen..."))
                image_path = self.media_gen.generate_image(prompt, self.selected_network, self.current_content_id, aspect_ratio)
                if image_path:
                    self.after(0, lambda: self._on_image_complete(image_path))
                else:
                    self.after(0, lambda: self._on_image_error("Error al generar"))
            except Exception as e:
                self.after(0, lambda: self._on_image_error(str(e)))
        threading.Thread(target=generate).start()
    
    def _on_image_complete(self, image_path: str):
        self.gen_image_btn.configure(text="🖼️ Generar Imagen", state="normal")
        self.media_status.configure(text="✅ Imagen creada!", text_color=COLORS["accent_success"])
        self._complete_progress("✅ Imagen generada")
        ImagePreview(self, image_path)
    
    def _on_image_error(self, error: str):
        self.gen_image_btn.configure(text="🖼️ Generar Imagen", state="normal")
        self.media_status.configure(text=f"❌ {error}", text_color=COLORS["accent_error"])
        self._error_progress(f"❌ {error}")
    
    def _on_format_selected_for_prompt(self, format_id: str, aspect_ratio: str):
        """Generate prompt for external platform."""
        content = self.output_text.get("0.0", "end").strip()
        platform_id = getattr(self, 'selected_image_platform', 'midjourney')
        platform_info = getattr(self, 'selected_platform_info', IMAGE_PLATFORMS['midjourney'])
        
        self.media_status.configure(text="Generando prompt...", text_color=COLORS["text_muted"])
        
        def generate():
            try:
                # Generate optimized prompt for the platform
                prompt = self.media_gen.generate_external_prompt(
                    content, self.selected_network, "image", platform_id, aspect_ratio
                )
                self.after(0, lambda: self._show_prompt_preview(prompt, platform_info['name']))
            except Exception as e:
                self.after(0, lambda: self.media_status.configure(text=f"❌ {e}", text_color=COLORS["accent_error"]))
        threading.Thread(target=generate).start()
    
    def _show_prompt_preview(self, prompt: str, platform_name: str):
        self.media_status.configure(text="✅ Prompt generado!", text_color=COLORS["accent_success"])
        PromptPreview(self, prompt, platform_name)
    
    def _generate_video(self):
        """Show style picker, then format picker before generating video."""
        content = self.output_text.get("0.0", "end").strip()
        if not content or "Tu contenido" in content:
            self.media_status.configure(text="❌ Genera contenido primero", text_color=COLORS["accent_error"])
            return
        if not self.selected_network:
            self.media_status.configure(text="❌ Selecciona una red", text_color=COLORS["accent_error"])
            return
        
        # Step 1: Show style picker for video
        MediaStylePicker(self, self._on_video_style_selected, "video", "Estilo de Video")
    
    def _on_video_style_selected(self, style_id: str, style_prompt: str, is_prompt_only: bool = False):
        """Step 2: Show format/platform picker after style selection."""
        self.selected_video_style = style_id
        self.selected_video_style_prompt = style_prompt
        
        if is_prompt_only:
            # Show platform picker for external video prompt
            PlatformPicker(self, self._on_video_platform_selected, "video")
        else:
            FormatPicker(self, self._on_format_selected_video, "Formato de Video")
    
    def _on_video_platform_selected(self, platform_id: str, platform_info: dict):
        """Generate video prompt for external platform."""
        content = self.output_text.get("0.0", "end").strip()
        
        self.selected_video_platform = platform_id
        self.selected_video_platform_info = platform_info
        FormatPicker(self, self._on_format_selected_for_video_prompt, "Formato de Video")
    
    def _on_format_selected_for_video_prompt(self, format_id: str, aspect_ratio: str):
        """Generate video prompt for external platform."""
        content = self.output_text.get("0.0", "end").strip()
        platform_id = getattr(self, 'selected_video_platform', 'runway')
        platform_info = getattr(self, 'selected_video_platform_info', VIDEO_PLATFORMS['runway'])
        
        self.media_status.configure(text="Generando prompt...", text_color=COLORS["text_muted"])
        
        def generate():
            try:
                prompt = self.media_gen.generate_external_prompt(
                    content, self.selected_network, "video", platform_id, aspect_ratio
                )
                self.after(0, lambda: self._show_prompt_preview(prompt, platform_info['name']))
            except Exception as e:
                self.after(0, lambda: self.media_status.configure(text=f"❌ {e}", text_color=COLORS["accent_error"]))
        threading.Thread(target=generate).start()
    
    def _on_format_selected_video(self, format_id: str, aspect_ratio: str):
        """Step 3: Generate video with style and format."""
        content = self.output_text.get("0.0", "end").strip()
        style_prompt = getattr(self, 'selected_video_style_prompt', '')
        style_id = getattr(self, 'selected_video_style', 'representative')
        
        style_name = VIDEO_STYLES.get(style_id, {}).get('name', style_id)
        self.gen_video_btn.configure(text="⏳...", state="disabled")
        self.media_status.configure(text=f"Creando {style_name} {aspect_ratio}...", text_color=COLORS["text_muted"])
        self._start_progress("🎬 Generando video...", 60.0)  # Videos take longer
        
        def generate():
            try:
                video_path = self.media_gen.generate_video(content, self.selected_network, aspect_ratio, self.current_content_id, style_prompt)
                if video_path:
                    self.after(0, lambda: self._on_video_complete(video_path))
                else:
                    self.after(0, lambda: self._on_video_error("Error al generar video"))
            except Exception as e:
                self.after(0, lambda: self._on_video_error(str(e)))
        threading.Thread(target=generate).start()
    
    def _on_video_complete(self, video_path: str):
        self.gen_video_btn.configure(text="🎬 Crear Video", state="normal")
        self.media_status.configure(text="✅ Video creado!", text_color=COLORS["accent_success"])
        self._complete_progress("✅ Video generado")
        import subprocess
        subprocess.run(["xdg-open", str(Path(video_path).parent)])
    
    def _on_video_error(self, error: str):
        self.gen_video_btn.configure(text="🎬 Crear Video", state="normal")
        self.media_status.configure(text=f"❌ {error}", text_color=COLORS["accent_error"])
        self._error_progress(f"❌ {error}")
    
    def _generate_script(self):
        """Show script type picker before generating script."""
        content = self.output_text.get("0.0", "end").strip()
        if not content or "Tu contenido" in content:
            self.media_status.configure(text="❌ Genera contenido primero", text_color=COLORS["accent_error"])
            return
        if not self.selected_network:
            self.media_status.configure(text="❌ Selecciona una red", text_color=COLORS["accent_error"])
            return
        
        # Show script type picker
        ScriptTypePicker(self, self._on_script_type_selected)
    
    def _on_script_type_selected(self, script_id: str, script_info: dict):
        """Generate script after type selection."""
        content = self.output_text.get("0.0", "end").strip()
        
        self.gen_script_btn.configure(text="⏳...", state="disabled")
        self.media_status.configure(text=f"Creando {script_info['name']}...", text_color=COLORS["text_muted"])
        self._start_progress("📜 Generando guión...", 6.0)
        
        def generate():
            try:
                script = self.media_gen.generate_script(
                    content, self.selected_network, script_id, script_info['duration']
                )
                if script:
                    self.after(0, lambda: self._on_script_complete(script, script_info['name']))
                else:
                    self.after(0, lambda: self._on_script_error("Error al generar guión"))
            except Exception as e:
                self.after(0, lambda: self._on_script_error(str(e)))
        threading.Thread(target=generate).start()
    
    def _on_script_complete(self, script: str, script_name: str):
        self.gen_script_btn.configure(text="📜 Script", state="normal")
        self.media_status.configure(text="✅ Guión generado!", text_color=COLORS["accent_success"])
        self._complete_progress("✅ Guión generado")
        PromptPreview(self, script, script_name)
    
    def _on_script_error(self, error: str):
        self.gen_script_btn.configure(text="📜 Script", state="normal")
        self.media_status.configure(text=f"❌ {error}", text_color=COLORS["accent_error"])
        self._error_progress(f"❌ {error}")
    
    def _open_settings(self):
        """Open settings window for link management."""
        SettingsWindow(self)
    
    def _open_research(self):
        """Open research window for web search and retention comments."""
        ResearchWindow(self)
    
    def _check_api_status(self):
        missing = validate_config()
        if missing:
            self.footer_status.configure(text="🔴 API no configurada", text_color=COLORS["accent_error"])
        else:
            self.footer_status.configure(text="🟢 Gemini API OK", text_color=COLORS["accent_success"])
    
    def _create_footer(self):
        """Create footer bar with API status and animated progress bar."""
        # Footer spans both columns - Compact height (20-22px is approx 0.5cm)
        FOOTER_HEIGHT = 22
        
        footer = ctk.CTkFrame(self, height=FOOTER_HEIGHT, fg_color=COLORS["bg_card"], corner_radius=0)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_propagate(False) # STRICTLY enforce height
        
        # Left section - API Status (same width as sidebar: 250px)
        # MUST set height here because we use grid_propagate(False)
        status_section = ctk.CTkFrame(footer, width=250, height=FOOTER_HEIGHT, fg_color=COLORS["bg_input"], corner_radius=0)
        status_section.grid(row=0, column=0, sticky="nsew")
        status_section.grid_propagate(False) 
        
        self.footer_status = ctk.CTkLabel(
            status_section, text="⏳ Verificando API...", 
            font=("Segoe UI", 10), text_color=COLORS["text_secondary"]
        )
        self.footer_status.place(relx=0.5, rely=0.5, anchor="center") # Use place for centering in fixed frame
        
        # Separator
        ctk.CTkFrame(footer, width=1, height=FOOTER_HEIGHT, fg_color=COLORS["bg_hover"]).place(x=250, y=0)
        
        # Right section - Progress Bar
        progress_section = ctk.CTkFrame(footer, height=FOOTER_HEIGHT, fg_color="transparent")
        progress_section.grid(row=0, column=1, sticky="nsew", padx=10)
        progress_section.grid_columnconfigure(1, weight=1)
        
        self.progress_label = ctk.CTkLabel(
            progress_section, text="", 
            font=("Segoe UI", 9), text_color=COLORS["text_muted"]
        )
        self.progress_label.pack(side="left", padx=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_section, height=4, corner_radius=2,
            fg_color=COLORS["bg_input"], 
            progress_color=COLORS["accent_cyan"]
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, pady=9) # Center vertically with padding
        self.progress_bar.set(0)
        
        # Animation state
        self.progress_running = False
        self.progress_target = 0
        self.progress_current = 0
    
    def _start_progress(self, text: str, estimated_seconds: float = 5.0):
        """Start animated progress bar."""
        self.progress_running = True
        self.progress_current = 0
        self.progress_target = 0.95  # Don't reach 100% until complete
        self.progress_label.configure(text=text, text_color=COLORS["accent_cyan"])
        self.progress_bar.set(0)
        
        # Calculate step for smooth animation (60fps target)
        self.progress_step = (self.progress_target / estimated_seconds) / 60
        self._animate_progress()
    
    def _animate_progress(self):
        """Animate progress bar smoothly."""
        if not self.progress_running:
            return
        
        if self.progress_current < self.progress_target:
            # Ease out - slower as we approach target
            remaining = self.progress_target - self.progress_current
            increment = max(self.progress_step * (remaining / self.progress_target + 0.1), 0.001)
            self.progress_current = min(self.progress_current + increment, self.progress_target)
            self.progress_bar.set(self.progress_current)
            self.after(16, self._animate_progress)  # ~60fps
    
    def _complete_progress(self, text: str = "✅ Completado"):
        """Complete progress bar animation."""
        self.progress_running = False
        self.progress_current = 1.0
        self.progress_bar.set(1.0)
        self.progress_label.configure(text=text, text_color=COLORS["accent_success"])
        # Reset after delay
        self.after(3000, self._reset_progress)
    
    def _error_progress(self, text: str = "❌ Error"):
        """Show error state in progress bar."""
        self.progress_running = False
        self.progress_label.configure(text=text, text_color=COLORS["accent_error"])
        self.after(3000, self._reset_progress)
    
    def _reset_progress(self):
        """Reset progress bar to initial state."""
        self.progress_bar.set(0)
        self.progress_label.configure(text="", text_color=COLORS["text_muted"])


def run_app():
    app = ContentForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
