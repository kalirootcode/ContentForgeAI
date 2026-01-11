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
        self._create_sidebar()
        self._create_main_area()
    
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
        
        self.generate_btn = ctk.CTkButton(top_row, text="✨ Generar", font=FONTS["body"], width=120, height=32,
                                          fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_secondary"],
                                          command=self._generate_content)
        self.generate_btn.grid(row=0, column=1, sticky="e")
        
        self.topic_entry = ctk.CTkTextbox(input_frame, height=60, font=FONTS["body"],
                                          fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
                                          border_color=COLORS["bg_hover"], border_width=1)
        self.topic_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        self.topic_entry.insert("0.0", "Ej: cómo usar nmap para escanear puertos...")
        self.topic_entry.bind("<FocusIn>", self._clear_placeholder)
        
        output_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        
        header_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=12, pady=8, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_row, text="📄 Contenido Generado", font=FONTS["body"], text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
        
        actions = ctk.CTkFrame(header_row, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")
        
        btn_style = {"width": 75, "height": 26, "font": ("Inter", 10), "fg_color": COLORS["bg_input"], "hover_color": COLORS["bg_hover"]}
        self.emoji_btn = ctk.CTkButton(actions, text="😀 Emoji", command=self._open_emoji_picker, **btn_style)
        self.emoji_btn.pack(side="left", padx=2)
        self.copy_btn = ctk.CTkButton(actions, text="📋 Copiar", command=self._copy_content, **btn_style)
        self.copy_btn.pack(side="left", padx=2)
        self.regen_btn = ctk.CTkButton(actions, text="🔄 Nuevo", command=self._regenerate_content, **btn_style)
        self.regen_btn.pack(side="left", padx=2)
        
        self.output_text = ctk.CTkTextbox(output_frame, font=("Segoe UI Emoji", 12),
                                          fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"], wrap="word")
        self.output_text.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="nsew")
        self.output_text.insert("0.0", "Tu contenido aparecerá aquí...\n\n✏️ Editable\n😀 Agrega emojis")
        
        media_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        media_frame.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="ew")
        
        media_btn_style = {"height": 32, "font": FONTS["body"], "fg_color": COLORS["accent_secondary"], "hover_color": COLORS["accent_primary"]}
        self.gen_image_btn = ctk.CTkButton(media_frame, text="🖼️ Generar Imagen", width=150, command=self._generate_image, **media_btn_style)
        self.gen_image_btn.pack(side="left", padx=(0, 8))
        self.gen_video_btn = ctk.CTkButton(media_frame, text="🎬 Script Video", width=140, command=self._generate_video_prompt, **media_btn_style)
        self.gen_video_btn.pack(side="left", padx=(0, 8))
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
        
        def generate():
            result = self.engine.generate(topic)
            self.after(0, lambda: self._on_generate_complete(result))
        threading.Thread(target=generate).start()
    
    def _on_generate_complete(self, result: str):
        self.generate_btn.configure(text="✨ Generar", state="normal")
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == self.selected_network), {})
        type_info = CONTENT_TYPES.get(self.selected_content_type, {})
        header = f"{'─' * 40}\n{network.get('icon', '')} {network.get('name', '')} │ {type_info.get('icon', '')} {type_info.get('name', '')}\n{'─' * 40}\n\n"
        self._show_output(header + result)
    
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
        content = self.output_text.get("0.0", "end").strip()
        if not content or "Tu contenido" in content:
            self.media_status.configure(text="❌ Genera contenido primero", text_color=COLORS["accent_error"])
            return
        if not self.selected_network:
            self.media_status.configure(text="❌ Selecciona una red", text_color=COLORS["accent_error"])
            return
        
        self.gen_image_btn.configure(text="⏳...", state="disabled")
        self.media_status.configure(text="Analizando...", text_color=COLORS["text_muted"])
        
        def generate():
            try:
                prompt = self.media_gen.analyze_content_for_image(content, self.selected_network)
                if not prompt:
                    self.after(0, lambda: self._on_image_error("No se pudo generar prompt"))
                    return
                self.after(0, lambda: self.media_status.configure(text="Creando imagen..."))
                image_path = self.media_gen.generate_image(prompt, self.selected_network, self.current_content_id)
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
        ImagePreview(self, image_path)
    
    def _on_image_error(self, error: str):
        self.gen_image_btn.configure(text="🖼️ Generar Imagen", state="normal")
        self.media_status.configure(text=f"❌ {error}", text_color=COLORS["accent_error"])
    
    def _generate_video_prompt(self):
        content = self.output_text.get("0.0", "end").strip()
        if not content or "Tu contenido" in content:
            self.media_status.configure(text="❌ Genera contenido primero", text_color=COLORS["accent_error"])
            return
        if not self.selected_network:
            self.media_status.configure(text="❌ Selecciona una red", text_color=COLORS["accent_error"])
            return
        
        self.gen_video_btn.configure(text="⏳...", state="disabled")
        self.media_status.configure(text="Creando script...", text_color=COLORS["text_muted"])
        
        def generate():
            try:
                video_prompt = self.media_gen.generate_video_prompt(content, self.selected_network)
                self.after(0, lambda: self._on_video_complete(video_prompt))
            except Exception as e:
                self.after(0, lambda: self._on_video_error(str(e)))
        threading.Thread(target=generate).start()
    
    def _on_video_complete(self, video_prompt: str):
        self.gen_video_btn.configure(text="🎬 Script Video", state="normal")
        self.media_status.configure(text="✅ Script creado!", text_color=COLORS["accent_success"])
        if video_prompt:
            self._show_output(video_prompt)
    
    def _on_video_error(self, error: str):
        self.gen_video_btn.configure(text="🎬 Script Video", state="normal")
        self.media_status.configure(text=f"❌ {error}", text_color=COLORS["accent_error"])
    
    def _check_api_status(self):
        missing = validate_config()
        if missing:
            self.status_indicator.configure(text="🔴 API no configurada", text_color=COLORS["accent_error"])
        else:
            self.status_indicator.configure(text="🟢 Gemini API OK", text_color=COLORS["accent_success"])


def run_app():
    app = ContentForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
