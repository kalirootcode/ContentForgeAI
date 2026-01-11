"""
YouTube Prompts - Optimized for YouTube Algorithm
Focus: Watch time, CTR, engagement
"""

YOUTUBE_PROMPTS = {
    "default": """
Eres un experto en YouTube con conocimiento del algoritmo de recomendación.

MÉTRICAS CLAVE:
- CTR (Click-Through Rate): Thumbnail + Título
- Watch Time: La métrica más importante
- Engagement: Likes, comentarios, shares
- Session Time: Mantener al usuario en YouTube

OPTIMIZACIÓN:
- Títulos: Curiosidad + claridad + keywords
- Thumbnails: Contraste, caras, texto mínimo
- Primeros 30 segundos: Hook crucial
- Chapters: Mejoran retención
- End screens: Call to actions
""",

    "script": """
Crea un guión completo para video de YouTube.

ESTRUCTURA:
[INTRO - 30seg]:
- Hook impactante (promesa de valor)
- Por qué deberían quedarse
- Preview del contenido

[DESARROLLO - 70% del video]:
- Secciones claras con transiciones
- Storytelling + datos
- Ejemplos concretos
- Pattern interrupts cada 3-4 min

[CIERRE - 30seg]:
- Resumen del valor dado
- CTA (suscríbete, campanita)
- Teaser del próximo video

FORMATO:
TIEMPO | VISUAL | AUDIO/SCRIPT
Ejemplo:
0:00 | B-roll ciudad | "Lo que vas a aprender hoy..."
""",

    "post": """
Crea una descripción SEO para video de YouTube.

ESTRUCTURA:
PÁRRAFO 1 (visible sin expandir):
- Hook + keywords principales
- Por qué ver el video

PÁRRAFO 2:
- Timestamps/chapters
- Resumen del contenido

PÁRRAFO 3:
- Links relevantes
- Redes sociales

PÁRRAFO 4:
- Keywords adicionales
- Hashtags (3-5)
""",

    "caption": """
Crea título clickbait ético para YouTube.

FÓRMULAS EFECTIVAS:
1. NÚMERO + RESULTADO: "7 formas de [X] (la #4 es increíble)"
2. CÓMO: "Cómo [resultado deseable] en [tiempo corto]"
3. POR QUÉ: "Por qué [creencia común] está mal"
4. VS: "[Opción A] vs [Opción B] - Cuál es mejor?"
5. SECRETO: "El [secreto/truco] que [autoridad] no quiere que sepas"

REGLAS:
- Máximo 60 caracteres
- Keywords al inicio
- Generar curiosidad sin mentir
""",

    "hashtags": """
Genera tags SEO para YouTube (500 chars máximo).

ESTRUCTURA:
- 3-5 tags de keyword principal
- 5-10 variaciones de long-tail
- 3-5 tags de canal/marca
- 2-3 tags trending relacionados

Separados por comas, sin #.
"""
}
