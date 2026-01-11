"""
Content Engine for ContentForge AI
Central orchestrator for content generation with KR-CLI knowledge injection
"""

import logging
from typing import Optional, Dict, List

from .gemini_handler import GeminiHandler
from .prompts import get_prompt
from .database import save_content, get_content_history
from .config import CONTENT_TYPES
from .knowledge.kr_cli_data import get_full_context, SECURITY_TOOLS_CONTEXT, KR_CLI_WRAPPER

logger = logging.getLogger(__name__)

# KR-CLI Knowledge context to inject into every prompt
KR_CLI_CONTEXT = """
=== CONTEXTO KR-CLI DOMINION ===

Eres un experto en marketing de contenido para KR-CLI DOMINION, una herramienta de ciberseguridad con IA.

PRODUCTO:
- KR-CLI DOMINION: Suite de ciberseguridad impulsada por IA
- Instalación: pip install kr-cli-dominion
- Ejecución: kr-clidn (modo interactivo) o kr-cli [comando] (wrapper)

EL WRAPPER MÁGICO (kr-cli):
El wrapper intercepta cualquier comando de Linux, lo ejecuta, y la IA analiza el resultado automáticamente.

EJEMPLOS:
- SIN kr-cli: nmap -sV target.com → output crudo que tienes que interpretar solo
- CON kr-cli: kr-cli nmap -sV target.com → la IA explica cada puerto, versiones vulnerables, y sugiere exploits

ESTO APLICA A TODAS LAS HERRAMIENTAS:
- kr-cli gobuster → análisis de directorios encontrados
- kr-cli sqlmap → explicación del tipo de inyección
- kr-cli nikto → resumen de vulnerabilidades con prioridad
- kr-cli hydra → qué hacer después de encontrar credenciales

BENEFICIO PRINCIPAL:
Convierte horas de investigación manual en segundos de análisis automático.

14 HERRAMIENTAS PREMIUM:
Port Scanner, CVE Lookup, OSINT Dashboard, WiFi Auditing, Password Cracking, y más.

PRICING:
- Gratis: 500 créditos al registrarse
- Premium: $20/mes (ilimitado)
- Paquetes de créditos desde $10

REGLAS PARA EL CONTENIDO:
1. SIEMPRE mencionar cómo KR-CLI simplifica la tarea
2. Mostrar el ANTES (forma tradicional) vs DESPUÉS (con kr-cli)
3. Incluir el comando de instalación cuando sea relevante
4. Usar hooks que conecten con el dolor del usuario
5. CTAs claros: probar gratis, instalar, etc.
"""


class ContentEngine:
    """
    Main content generation engine.
    Coordinates between UI, AI handler, prompts, and database.
    Injects KR-CLI knowledge into every generation.
    """
    
    def __init__(self):
        self.ai = GeminiHandler()
        self.current_network = "instagram"
        self.current_content_type = "post"
        self.last_generated = ""
        self.last_topic = ""
    
    def is_ready(self) -> bool:
        """Check if engine is ready to generate content."""
        return self.ai.is_configured()
    
    def set_network(self, network: str):
        """Set current social network."""
        self.current_network = network
    
    def set_content_type(self, content_type: str):
        """Set current content type."""
        self.current_content_type = content_type
    
    def _detect_tool_context(self, topic: str) -> str:
        """Detect if topic mentions a security tool and add specific context."""
        topic_lower = topic.lower()
        extra_context = ""
        
        for tool_name, tool_data in SECURITY_TOOLS_CONTEXT.items():
            if tool_name in topic_lower:
                extra_context += f"""

=== CONTEXTO ESPECÍFICO: {tool_data['name']} ===
Herramienta: {tool_data['name']} ({tool_data['category']})
Descripción: {tool_data['description']}
Uso normal: {tool_data['normal_usage']}
Con KR-CLI: {tool_data['kr_cli_usage']}
Beneficio KR-CLI: {tool_data['kr_cli_benefit']}
Pain point del usuario: {tool_data['pain_point']}

IMPORTANTE: Muestra cómo KR-CLI simplifica el uso de {tool_data['name']}.
"""
                break
        
        return extra_context
    
    def generate(self, topic: str, save: bool = True) -> str:
        """
        Generate content for the current network and type.
        Automatically injects KR-CLI knowledge context.
        
        Args:
            topic: User's topic/idea
            save: Whether to save to database
            
        Returns:
            Generated content string
        """
        if not topic.strip():
            return "❌ Por favor, ingresa un tema o idea para generar contenido."
        
        self.last_topic = topic
        
        # Get specialized prompt for the network
        network_prompt = get_prompt(self.current_network, self.current_content_type)
        if not network_prompt:
            network_prompt = get_prompt(self.current_network, "default")
        
        # Detect if topic mentions a specific tool
        tool_context = self._detect_tool_context(topic)
        
        # Build enhanced prompt with KR-CLI knowledge
        enhanced_prompt = f"""
{KR_CLI_CONTEXT}
{tool_context}

=== INSTRUCCIONES DE RED SOCIAL ===
{network_prompt}
"""
        
        # Determine if we need pro model (for scripts/long content)
        use_pro = self.current_content_type in ["script", "thread"]
        
        # Generate content
        content = self.ai.generate_content(
            topic=topic,
            network=self.current_network,
            content_type=self.current_content_type,
            network_prompt=enhanced_prompt,
            use_pro=use_pro
        )
        
        self.last_generated = content
        
        # Save to database
        if save and not content.startswith("❌"):
            save_content(
                network=self.current_network,
                content_type=self.current_content_type,
                topic=topic,
                content=content
            )
        
        return content
    
    def regenerate(self, topic: str = None) -> str:
        """Regenerate content with same or new topic."""
        return self.generate(topic or self.last_topic, save=True)
    
    def improve(self, suggestions: str) -> str:
        """Improve last generated content."""
        if not self.last_generated:
            return "❌ No hay contenido previo para mejorar."
        
        improved = self.ai.improve_content(self.last_generated, suggestions)
        self.last_generated = improved
        return improved
    
    def generate_hashtags(self, topic: str) -> List[str]:
        """Generate hashtags for topic."""
        return self.ai.generate_hashtags(topic, self.current_network)
    
    def generate_captions(self, context: str) -> List[str]:
        """Generate caption options."""
        return self.ai.generate_captions(context)
    
    def generate_video_script(self, topic: str, duration: int = 30) -> Dict:
        """Generate structured video script."""
        prompt = get_prompt(self.current_network, "script")
        return self.ai.generate_video_script(topic, duration, self.current_network, prompt)
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get content generation history."""
        return get_content_history(limit)
    
    def get_available_content_types(self) -> Dict:
        """Get available content types with metadata."""
        return CONTENT_TYPES.copy()
