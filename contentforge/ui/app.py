"""
Main Application Window for ContentForge AI
Professional desktop GUI with collapsible network menus
"""

import customtkinter as ctk
from typing import Optional, Dict
import pyperclip
import threading

from ..config import APP_NAME, APP_VERSION, SOCIAL_NETWORKS, CONTENT_TYPES, validate_config
from ..content_engine import ContentEngine
from .themes import COLORS, FONTS

# Common emojis organized by category
EMOJI_CATEGORIES = {
    "💬 Expresiones": ["😀", "😂", "🤣", "😊", "😍", "🥰", "😎", "🤩", "😇", "🥳", "😏", "🤔", "🤯", "😱", "��", "💯", "✨", "💫", "⭐", "🌟"],
    "👍 Gestos": ["👍", "👎", "👏", "🙌", "🤝", "✌️", "🤞", "💪", "🖐️", "👋", "🙏", "💅", "🤙", "👊", "✊", "🤟", "👆", "👇", "👈", "👉"],
    "❤️ Corazones": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "♥️", "🫶"],
    "🎯 Objetos": ["🎯", "🎨", "🎬", "📱", "💻", "🖥️", "📸", "🎥", "🎤", "🎧", "📖", "📝", "✏️", "📌", "📎", "🔗", "🔒", "🔓", "🔑", "��️"],
    "🚀 Tech/Hacking": ["🚀", "💻", "🖥️", "⌨️", "🖱️", "💾", "📡", "🔌", "🔋", "🛡️", "🔐", "🔓", "🐛", "🤖", "👾", "🕷️", "🕸️", "⚡", "🌐", "��"],
    "📊 Business": ["📊", "📈", "📉", "💰", "💵", "💸", "💳", "🏆", "🎖️", "🥇", "🥈", "🥉", "��", "📁", "📂", "🗂️", "📅", "📆", "🗓️", "⏰"],
    "✅ Símbolos": ["✅", "❌", "⭕", "❗", "❓", "‼️", "⁉️", "💡", "📢", "📣", "🔔", "🔕", "⚠️", "🚫", "🔴", "🟢", "🔵", "🟡", "🟣", "⚫"],
    "🎉 Celebración": ["🎉", "🎊", "🎈", "🎁", "🎀", "🎄", "🎃", "🎆", "🎇", "🧨", "🪅", "🏅", "🏆", "🥂", "🍾", "🥳", "🎂", "🍰", "🧁", "🎵"],
}


class EmojiPicker(ctk.CTkToplevel):
    """Popup window for emoji selection."""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Selector de Emojis")
        self.geometry("450x400")
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()
        
        # Create scrollable frame
        container = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=10
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add emoji categories
        for category_name, emojis in EMOJI_CATEGORIES.items():
            # Category label
            cat_label = ctk.CTkLabel(
                container,
                text=category_name,
                font=FONTS["heading"],
                text_color=COLORS["text_primary"]
            )
            cat_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Emoji grid
            emoji_frame = ctk.CTkFrame(container, fg_color="transparent")
            emoji_frame.pack(fill="x", padx=10)
            
            for i, emoji in enumerate(emojis):
                btn = ctk.CTkButton(
                    emoji_frame,
                    text=emoji,
                    width=35,
                    height=35,
                    font=("Segoe UI Emoji", 16),
                    fg_color=COLORS["bg_input"],
                    hover_color=COLORS["bg_hover"],
                    command=lambda e=emoji: self._select_emoji(e)
                )
                btn.grid(row=i // 10, column=i % 10, padx=2, pady=2)
    
    def _select_emoji(self, emoji: str):
        """Handle emoji selection."""
        self.callback(emoji)
        self.destroy()


class ContentForgeApp(ctk.CTk):
    """Main application window with collapsible network menus."""
    
    def __init__(self):
        super().__init__()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window setup
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Initialize engine
        self.engine = ContentEngine()
        self.selected_network = None
        self.selected_content_type = None
        self.expanded_network = None
        self.network_frames = {}
        self.content_type_frames = {}
        
        # Build UI
        self._create_layout()
        self._check_api_status()
    
    def _create_layout(self):
        """Create main layout with sidebar and content area."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_area()
    
    def _create_sidebar(self):
        """Create left sidebar with expandable network menus."""
        # Sidebar with scroll
        self.sidebar = ctk.CTkScrollableFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=COLORS["bg_card"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo/Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=("Segoe UI Emoji", 36)
        )
        logo_label.pack()
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="ContentForge",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="AI Content Generator",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack()
        
        # Divider
        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["bg_hover"]).pack(fill="x", padx=15, pady=15)
        
        # Section label
        ctk.CTkLabel(
            self.sidebar,
            text="SELECCIONA RED Y TIPO",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Create collapsible network sections
        for network in SOCIAL_NETWORKS:
            self._create_network_section(network)
        
        # Status at bottom
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="⚪ Verificando...",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self.status_indicator.pack(anchor="w")
    
    def _create_network_section(self, network: Dict):
        """Create a collapsible network section with content types."""
        network_id = network['id']
        
        # Container frame
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.pack(fill="x", padx=5, pady=2)
        
        # Network header button (expandable)
        header_btn = ctk.CTkButton(
            container,
            text=f"{network['icon']}  {network['name']}  ▼",
            font=FONTS["body"],
            height=40,
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            command=lambda n=network_id: self._toggle_network(n)
        )
        header_btn.pack(fill="x", padx=5)
        self.network_frames[network_id] = {"header": header_btn, "container": container}
        
        # Content types container (initially hidden)
        types_frame = ctk.CTkFrame(container, fg_color=COLORS["bg_input"], corner_radius=8)
        self.content_type_frames[network_id] = {"frame": types_frame, "buttons": {}}
        
        # Add content type buttons (will be shown when expanded)
        for type_id, type_info in CONTENT_TYPES.items():
            type_btn = ctk.CTkButton(
                types_frame,
                text=f"  {type_info['icon']} {type_info['name']}",
                font=FONTS["small"],
                height=32,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS["accent_primary"],
                text_color=COLORS["text_secondary"],
                command=lambda n=network_id, t=type_id: self._select_content_type(n, t)
            )
            type_btn.pack(fill="x", padx=8, pady=2)
            self.content_type_frames[network_id]["buttons"][type_id] = type_btn
    
    def _toggle_network(self, network_id: str):
        """Toggle network expansion."""
        # Collapse previously expanded network
        if self.expanded_network and self.expanded_network != network_id:
            old_frame = self.content_type_frames[self.expanded_network]["frame"]
            old_frame.pack_forget()
            old_header = self.network_frames[self.expanded_network]["header"]
            network = next(n for n in SOCIAL_NETWORKS if n['id'] == self.expanded_network)
            old_header.configure(text=f"{network['icon']}  {network['name']}  ▼")
        
        types_frame = self.content_type_frames[network_id]["frame"]
        header_btn = self.network_frames[network_id]["header"]
        network = next(n for n in SOCIAL_NETWORKS if n['id'] == network_id)
        
        if self.expanded_network == network_id:
            # Collapse
            types_frame.pack_forget()
            header_btn.configure(text=f"{network['icon']}  {network['name']}  ▼")
            self.expanded_network = None
        else:
            # Expand
            types_frame.pack(fill="x", padx=10, pady=(0, 5))
            header_btn.configure(
                text=f"{network['icon']}  {network['name']}  ▲",
                fg_color=COLORS["accent_primary"]
            )
            self.expanded_network = network_id
    
    def _select_content_type(self, network_id: str, content_type: str):
        """Handle content type selection."""
        self.selected_network = network_id
        self.selected_content_type = content_type
        self.engine.set_network(network_id)
        self.engine.set_content_type(content_type)
        
        # Update button styles
        for nid, data in self.content_type_frames.items():
            for tid, btn in data["buttons"].items():
                if nid == network_id and tid == content_type:
                    btn.configure(fg_color=COLORS["accent_primary"], text_color=COLORS["text_primary"])
                else:
                    btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])
        
        # Update header
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == network_id), None)
        type_info = CONTENT_TYPES.get(content_type, {})
        if network and type_info:
            self.header_label.configure(
                text=f"{network['icon']} {network['name']} → {type_info['icon']} {type_info['name']}"
            )
    
    def _create_main_area(self):
        """Create main content generation area."""
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        # Header
        self.header_label = ctk.CTkLabel(
            main_frame,
            text="👈 Selecciona una red social y tipo de contenido",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Topic input
        input_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            input_frame,
            text="📝 Tema o idea principal:",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.topic_entry = ctk.CTkTextbox(
            input_frame,
            height=80,
            font=FONTS["body"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["bg_hover"],
            border_width=1
        )
        self.topic_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.topic_entry.insert("0.0", "Escribe tu tema: nmap, gobuster, ciberseguridad...")
        self.topic_entry.bind("<FocusIn>", self._clear_placeholder)
        
        # Generate button
        self.generate_btn = ctk.CTkButton(
            main_frame,
            text="✨ GENERAR CONTENIDO",
            font=FONTS["heading"],
            height=50,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            command=self._generate_content
        )
        self.generate_btn.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Output area
        output_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        output_frame.grid(row=3, column=0, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        
        # Output header with action buttons
        header_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_row,
            text="📄 CONTENIDO GENERADO (editable):",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")
        
        # Action buttons
        actions = ctk.CTkFrame(header_row, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")
        
        self.emoji_btn = ctk.CTkButton(
            actions,
            text="😀 Emojis",
            width=90,
            height=30,
            font=("Segoe UI Emoji", 11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            command=self._open_emoji_picker
        )
        self.emoji_btn.pack(side="left", padx=3)
        
        self.copy_btn = ctk.CTkButton(
            actions,
            text="📋 Copiar",
            width=80,
            height=30,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            command=self._copy_content
        )
        self.copy_btn.pack(side="left", padx=3)
        
        self.regen_btn = ctk.CTkButton(
            actions,
            text="🔄 Regenerar",
            width=95,
            height=30,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            command=self._regenerate_content
        )
        self.regen_btn.pack(side="left", padx=3)
        
        # Editable output textbox
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=("Segoe UI Emoji", 12),  # Font that supports emojis
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            wrap="word"
        )
        self.output_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.output_text.insert("0.0", "Tu contenido aparecerá aquí.\n\n✏️ Puedes editarlo antes de copiar.\n😀 Usa el botón Emojis para agregar más.")
    
    def _clear_placeholder(self, event):
        """Clear placeholder text on focus."""
        current = self.topic_entry.get("0.0", "end").strip()
        if "Escribe tu tema" in current:
            self.topic_entry.delete("0.0", "end")
    
    def _open_emoji_picker(self):
        """Open emoji picker popup."""
        EmojiPicker(self, self._insert_emoji)
    
    def _insert_emoji(self, emoji: str):
        """Insert emoji at cursor position in output."""
        self.output_text.insert("insert", emoji)
    
    def _generate_content(self):
        """Generate content in background thread."""
        if not self.selected_network or not self.selected_content_type:
            self._show_output("❌ Primero selecciona una red social y tipo de contenido en el panel izquierdo.")
            return
        
        topic = self.topic_entry.get("0.0", "end").strip()
        if not topic or "Escribe tu tema" in topic:
            self._show_output("❌ Por favor, escribe un tema o idea primero.")
            return
        
        self.generate_btn.configure(text="⏳ Generando...", state="disabled")
        self._show_output("⏳ Generando contenido con IA...\n\nEsto puede tomar unos segundos...")
        
        def generate():
            result = self.engine.generate(topic)
            # Format content based on network
            formatted = self._format_for_network(result)
            self.after(0, lambda: self._on_generation_complete(formatted))
        
        thread = threading.Thread(target=generate)
        thread.start()
    
    def _format_for_network(self, content: str) -> str:
        """Apply network-specific formatting."""
        if not self.selected_network:
            return content
        
        # Add network-specific notes
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == self.selected_network), None)
        type_info = CONTENT_TYPES.get(self.selected_content_type, {})
        
        header = f"{'═' * 50}\n"
        header += f"{network['icon']} {network['name']} | {type_info['icon']} {type_info['name']}\n"
        header += f"{'═' * 50}\n\n"
        
        return header + content
    
    def _on_generation_complete(self, result: str):
        """Handle generation completion."""
        self.generate_btn.configure(text="✨ GENERAR CONTENIDO", state="normal")
        self._show_output(result)
    
    def _regenerate_content(self):
        """Regenerate content."""
        self._generate_content()
    
    def _show_output(self, text: str):
        """Display text in output area (editable)."""
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", text)
    
    def _copy_content(self):
        """Copy current content to clipboard."""
        content = self.output_text.get("0.0", "end").strip()
        if content:
            try:
                pyperclip.copy(content)
                orig = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✅ Copiado!")
                self.after(1500, lambda: self.copy_btn.configure(text=orig))
            except Exception as e:
                self._show_output(f"❌ Error al copiar: {e}")
    
    def _check_api_status(self):
        """Check Gemini API status."""
        missing = validate_config()
        if missing:
            self.status_indicator.configure(text="🔴 API no configurada", text_color=COLORS["accent_error"])
        else:
            self.status_indicator.configure(text="�� Gemini API OK", text_color=COLORS["accent_success"])


def run_app():
    """Run the ContentForge application."""
    app = ContentForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
