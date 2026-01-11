"""
Main Application Window for ContentForge AI
Professional desktop GUI using CustomTkinter
"""

import customtkinter as ctk
from typing import Optional
import pyperclip
import threading

from ..config import APP_NAME, APP_VERSION, SOCIAL_NETWORKS, CONTENT_TYPES, validate_config
from ..content_engine import ContentEngine
from .themes import COLORS, FONTS, DARK_THEME


class ContentForgeApp(ctk.CTk):
    """Main application window."""
    
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
        self.selected_network = "instagram"
        self.selected_content_type = "post"
        
        # Build UI
        self._create_layout()
        self._check_api_status()
    
    def _create_layout(self):
        """Create main layout with sidebar and content area."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self._create_sidebar()
        
        # Main content area
        self._create_main_area()
    
    def _create_sidebar(self):
        """Create left sidebar with network selection."""
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=COLORS["bg_card"]
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=("Segoe UI", 40)
        )
        logo_label.pack()
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="ContentForge",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="AI Content Generator",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack()
        
        # Divider
        divider = ctk.CTkFrame(sidebar, height=2, fg_color=COLORS["bg_hover"])
        divider.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        # Networks label
        networks_label = ctk.CTkLabel(
            sidebar,
            text="REDES SOCIALES",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        networks_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Network buttons with colored icons
        self.network_buttons = {}
        for i, network in enumerate(SOCIAL_NETWORKS):
            btn_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
            btn_frame.grid(row=3+i, column=0, padx=10, pady=2, sticky="ew")
            btn_frame.grid_columnconfigure(1, weight=1)
            
            # Create colored icon label
            icon_label = ctk.CTkLabel(
                btn_frame,
                text=network['icon'],
                font=("Segoe UI", 16, "bold"),
                text_color=network['color'],
                width=30
            )
            icon_label.grid(row=0, column=0, padx=(5, 2))
            
            # Create button
            btn = ctk.CTkButton(
                btn_frame,
                text=network['name'],
                font=FONTS["body"],
                height=36,
                anchor="w",
                fg_color=COLORS["accent_primary"] if network['id'] == self.selected_network else "transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_primary"],
                command=lambda n=network['id']: self._select_network(n)
            )
            btn.grid(row=0, column=1, sticky="ew", padx=(0, 5))
            self.network_buttons[network['id']] = btn
        
        # Status indicator at bottom
        self.status_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.status_frame.grid(row=11, column=0, padx=20, pady=20, sticky="sew")
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="⚪ Verificando API...",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self.status_indicator.pack(anchor="w")
    
    def _create_main_area(self):
        """Create main content generation area."""
        main_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_dark"],
            corner_radius=0
        )
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        
        # Header with current network
        self.header_label = ctk.CTkLabel(
            main_frame,
            text="📷 Instagram - Crear Contenido",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Topic input
        input_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="📝 Tema o idea principal:",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        input_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
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
        self.topic_entry.insert("0.0", "Escribe aquí tu idea, tema o concepto...")
        self.topic_entry.bind("<FocusIn>", self._clear_placeholder)
        
        # Content type buttons
        types_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        types_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        types_label = ctk.CTkLabel(
            types_frame,
            text="TIPO DE CONTENIDO:",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        types_label.pack(anchor="w", pady=(0, 10))
        
        buttons_container = ctk.CTkFrame(types_frame, fg_color="transparent")
        buttons_container.pack(fill="x")
        
        self.type_buttons = {}
        for i, (type_id, type_info) in enumerate(CONTENT_TYPES.items()):
            btn = ctk.CTkButton(
                buttons_container,
                text=f"{type_info['icon']} {type_info['name']}",
                font=FONTS["body"],
                width=100,
                height=40,
                fg_color=COLORS["accent_primary"] if type_id == self.selected_content_type else COLORS["bg_card"],
                hover_color=COLORS["accent_secondary"],
                command=lambda t=type_id: self._select_content_type(t)
            )
            btn.pack(side="left", padx=(0, 8), pady=5)
            self.type_buttons[type_id] = btn
        
        # Generate button
        generate_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        generate_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        self.generate_btn = ctk.CTkButton(
            generate_frame,
            text="✨ GENERAR CONTENIDO",
            font=FONTS["heading"],
            height=50,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            command=self._generate_content
        )
        self.generate_btn.pack(fill="x")
        
        # Output area
        output_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        output_frame.grid(row=4, column=0, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        
        output_header = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_header.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        output_header.grid_columnconfigure(0, weight=1)
        
        output_label = ctk.CTkLabel(
            output_header,
            text="📄 CONTENIDO GENERADO:",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        output_label.grid(row=0, column=0, sticky="w")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(output_header, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        self.copy_btn = ctk.CTkButton(
            actions_frame,
            text="📋 Copiar",
            width=80,
            height=30,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            command=self._copy_content
        )
        self.copy_btn.pack(side="left", padx=5)
        
        self.regenerate_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Regenerar",
            width=100,
            height=30,
            font=FONTS["small"],
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            command=self._regenerate_content
        )
        self.regenerate_btn.pack(side="left", padx=5)
        
        # Output textbox
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=FONTS["body"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            wrap="word"
        )
        self.output_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.output_text.insert("0.0", "Tu contenido generado aparecerá aquí...")
        self.output_text.configure(state="disabled")
    
    def _select_network(self, network_id: str):
        """Handle network selection."""
        self.selected_network = network_id
        self.engine.set_network(network_id)
        
        # Update button styles
        for nid, btn in self.network_buttons.items():
            if nid == network_id:
                btn.configure(fg_color=COLORS["accent_primary"])
            else:
                btn.configure(fg_color="transparent")
        
        # Update header
        network = next((n for n in SOCIAL_NETWORKS if n['id'] == network_id), None)
        if network:
            self.header_label.configure(text=f"{network['icon']} {network['name']} - Crear Contenido")
    
    def _select_content_type(self, type_id: str):
        """Handle content type selection."""
        self.selected_content_type = type_id
        self.engine.set_content_type(type_id)
        
        # Update button styles
        for tid, btn in self.type_buttons.items():
            if tid == type_id:
                btn.configure(fg_color=COLORS["accent_primary"])
            else:
                btn.configure(fg_color=COLORS["bg_card"])
    
    def _clear_placeholder(self, event):
        """Clear placeholder text on focus."""
        current = self.topic_entry.get("0.0", "end").strip()
        if current == "Escribe aquí tu idea, tema o concepto...":
            self.topic_entry.delete("0.0", "end")
    
    def _generate_content(self):
        """Generate content in background thread."""
        topic = self.topic_entry.get("0.0", "end").strip()
        if not topic or topic == "Escribe aquí tu idea, tema o concepto...":
            self._show_output("❌ Por favor, escribe un tema o idea primero.")
            return
        
        # Show loading state
        self.generate_btn.configure(text="⏳ Generando...", state="disabled")
        self._show_output("⏳ Generando contenido con IA...")
        
        # Run in background
        def generate():
            result = self.engine.generate(topic)
            self.after(0, lambda: self._on_generation_complete(result))
        
        thread = threading.Thread(target=generate)
        thread.start()
    
    def _on_generation_complete(self, result: str):
        """Handle generation completion."""
        self.generate_btn.configure(text="✨ GENERAR CONTENIDO", state="normal")
        self._show_output(result)
    
    def _regenerate_content(self):
        """Regenerate with same topic."""
        self._generate_content()
    
    def _show_output(self, text: str):
        """Display text in output area."""
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", text)
        self.output_text.configure(state="disabled")
    
    def _copy_content(self):
        """Copy content to clipboard."""
        content = self.output_text.get("0.0", "end").strip()
        if content and content != "Tu contenido generado aparecerá aquí...":
            try:
                pyperclip.copy(content)
                # Visual feedback
                original_text = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✅ Copiado!")
                self.after(1500, lambda: self.copy_btn.configure(text=original_text))
            except Exception as e:
                self._show_output(f"❌ Error al copiar: {e}")
    
    def _check_api_status(self):
        """Check Gemini API status."""
        missing = validate_config()
        if missing:
            self.status_indicator.configure(
                text="🔴 API no configurada",
                text_color=COLORS["accent_error"]
            )
        else:
            self.status_indicator.configure(
                text="🟢 Gemini API conectada",
                text_color=COLORS["accent_success"]
            )


def run_app():
    """Run the ContentForge application."""
    app = ContentForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
