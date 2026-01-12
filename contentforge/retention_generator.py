"""
Retention Comment Generator for ContentForge AI
Generates AI-powered comments that create curiosity and drive engagement
"""

import logging
from typing import Dict, List, Optional

from .gemini_handler import GeminiHandler

logger = logging.getLogger(__name__)


# Retention comment prompts by platform
RETENTION_PROMPTS = {
    "facebook": """
Eres un experto en marketing de retención y engagement en Facebook.
Tu objetivo es crear comentarios que generen CURIOSIDAD TÉCNICA sin ser spam.

REGLAS:
1. El comentario debe ser técnico pero accesible
2. Debe generar intriga sin revelar todo
3. No ser promocional directo - ser sutil
4. Usar lenguaje que haga pensar al lector
5. Incluir una pregunta o afirmación intrigante
6. Máximo 2-3 líneas

TONO: Profesional, técnico, curioso, que invite a investigar más.

EJEMPLOS DE BUENOS COMENTARIOS:
- "Interesante enfoque, aunque hay una técnica con IA que automatiza esto en segundos. La diferencia en eficiencia es brutal."
- "Esto me recuerda a un wrapper que analiza estos outputs automáticamente. El tiempo que se ahorra es increíble."
- "Buen punto. Aunque si combinas esto con análisis de IA, los resultados cambian completamente."
""",

    "twitter": """
Eres un experto en engagement en Twitter/X.
Crea respuestas cortas que generen curiosidad técnica.

REGLAS:
1. Máximo 280 caracteres
2. Técnico pero intrigante
3. Que invite a preguntar más
4. Sin links directos
5. Una afirmación que haga pensar

TONO: Conciso, técnico, misterioso.
""",

    "linkedin": """
Eres un experto en networking profesional en LinkedIn.
Crea comentarios que posicionen como experto y generen curiosidad.

REGLAS:
1. Tono profesional y serio
2. Demostrar conocimiento técnico
3. Ofrecer perspectiva única
4. Invitar a la conversación
5. No ser promocional

TONO: Profesional, experto, thought leader.
""",

    "default": """
Eres un experto en engagement en redes sociales.
Crea un comentario que genere curiosidad técnica sobre ciberseguridad.

El comentario debe:
1. Ser relevante al tema del post
2. Aportar valor técnico
3. Generar intriga para que quieran saber más
4. No ser spam ni promocional directo
5. Sonar natural y auténtico
"""
}


class RetentionGenerator:
    """Generates retention comments using AI analysis."""
    
    def __init__(self):
        self.ai = GeminiHandler()
    
    def analyze_post(self, post_content: str, platform: str = "facebook") -> Dict:
        """
        Analyze a post to understand its context and audience.
        
        Args:
            post_content: The content of the post to analyze
            platform: Social platform
            
        Returns:
            Analysis dict with topic, sentiment, audience, etc.
        """
        analysis_prompt = f"""
Analiza el siguiente post de {platform} y extrae:
1. TEMA PRINCIPAL: ¿De qué habla?
2. NIVEL TÉCNICO: ¿Básico, intermedio, avanzado?
3. AUDIENCIA: ¿A quién va dirigido?
4. TONO: ¿Informal, profesional, educativo?
5. OPORTUNIDAD: ¿Cómo puedo aportar valor con un comentario?
6. PALABRAS CLAVE: Lista de términos importantes

POST:
{post_content}

Responde en formato estructurado.
"""
        try:
            response = self.ai.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=analysis_prompt
            )
            
            return {
                "post_content": post_content,
                "platform": platform,
                "analysis": response.text.strip(),
                "success": True
            }
        except Exception as e:
            logger.error(f"Post analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_retention_comment(
        self, 
        post_content: str, 
        platform: str = "facebook",
        style: str = "curious"
    ) -> str:
        """
        Generate a retention comment for a post.
        
        Args:
            post_content: The post to comment on
            platform: Target platform
            style: Comment style ('curious', 'expert', 'helpful')
            
        Returns:
            Generated comment string
        """
        base_prompt = RETENTION_PROMPTS.get(platform, RETENTION_PROMPTS["default"])
        
        style_instructions = {
            "curious": "Genera CURIOSIDAD. Haz que quieran saber más sobre la herramienta/técnica que mencionas.",
            "expert": "Posiciónate como EXPERTO. Comenta con autoridad técnica.",
            "helpful": "Sé ÚTIL pero intrigante. Ofrece ayuda de forma que genere interés."
        }
        
        style_instruction = style_instructions.get(style, style_instructions["curious"])
        
        full_prompt = f"""
{base_prompt}

ESTILO ESPECÍFICO: {style_instruction}

CONTEXTO: Promocionar KR-CLI DOMINION (herramienta de ciberseguridad con IA) de forma SUTIL.
- Nunca mencionar el nombre directamente
- Referirse como "una herramienta con IA", "un wrapper inteligente", "un análisis automático"
- Crear curiosidad para que busquen más información

POST ORIGINAL:
{post_content}

Genera UN comentario de retención que cumpla todas las reglas.
Responde SOLO con el comentario, sin explicaciones.
"""
        
        try:
            response = self.ai.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Comment generation error: {e}")
            return ""
    
    def generate_multiple_comments(
        self, 
        post_content: str, 
        platform: str = "facebook",
        count: int = 3
    ) -> List[str]:
        """
        Generate multiple comment variations.
        
        Args:
            post_content: The post to comment on
            platform: Target platform
            count: Number of variations
            
        Returns:
            List of generated comments
        """
        styles = ["curious", "expert", "helpful"]
        comments = []
        
        for i in range(min(count, len(styles))):
            comment = self.generate_retention_comment(post_content, platform, styles[i])
            if comment:
                comments.append(comment)
        
        return comments
    
    def generate_from_search_results(
        self, 
        search_results: List[Dict], 
        platform: str = "facebook"
    ) -> List[Dict]:
        """
        Generate retention comments from search results.
        
        Args:
            search_results: List of search result dicts with 'title' and 'body'
            platform: Target platform
            
        Returns:
            List of dicts with original content and generated comment
        """
        results = []
        
        for result in search_results[:5]:  # Limit to 5
            content = f"{result.get('title', '')}\n{result.get('body', '')}"
            comment = self.generate_retention_comment(content, platform)
            
            results.append({
                "original_title": result.get('title', ''),
                "original_body": result.get('body', ''),
                "original_url": result.get('href', ''),
                "generated_comment": comment
            })
        
        return results


# Convenience function
def get_retention_generator() -> RetentionGenerator:
    """Get a RetentionGenerator instance."""
    return RetentionGenerator()
