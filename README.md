<div align="center">

# 🚀 ContentForge AI

### **Generador de Contenido Viral para Redes Sociales**

[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Gemini](https://img.shields.io/badge/AI-Gemini%20API-blue.svg)](https://ai.google.dev/)

**Crea contenido profesional y viral para todas las redes sociales con el poder de la IA.**

[🚀 Instalación](#-instalación) • [⚡ Uso](#-uso) • [🎯 Características](#-características)

---

</div>

## �� ¿Qué es ContentForge AI?

ContentForge AI es una aplicación de escritorio que utiliza **Google Gemini AI** para generar contenido optimizado para cada plataforma social. Cada red tiene prompts especializados que entienden el algoritmo y las mejores prácticas.

### 📱 Redes Soportadas

| Red | Tipos de Contenido |
|-----|-------------------|
| 📘 Facebook | Posts, Stories, Carruseles, Scripts |
| 📸 Instagram | Posts, Reels, Stories, Carruseles, Bio, Hashtags |
| 🎵 TikTok | Scripts virales, Captions, Hashtags |
| 𝕏 X (Twitter) | Tweets, Threads, Hot takes |
| ▶️ YouTube | Guiones, Títulos, Descripciones SEO |
| ✈️ Telegram | Posts, Contenido de canal |
| 💼 LinkedIn | Posts profesionales, Carruseles |
| 📌 Pinterest | Pins SEO, Descripciones |

---

## 🚀 Instalación

### 1. Clonar y configurar

```bash
cd ContentForgeAI
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configurar API Key

1. Obtén tu API key gratis en [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea el archivo `.env`:

```bash
cp .env.template .env
# Edita .env y agrega tu GEMINI_API_KEY
```

### 3. Ejecutar

```bash
python -m contentforge.main
```

---

## ⚡ Uso

1. **Selecciona una red social** en el panel izquierdo
2. **Escribe tu tema o idea** en el campo de texto
3. **Elige el tipo de contenido** (Post, Story, Script, etc.)
4. **Click en "Generar Contenido"**
5. **Copia o regenera** según necesites

---

## 🎯 Características

### 🧠 IA Especializada por Red
Cada plataforma tiene prompts optimizados para:
- Hooks que capturan atención
- Formato óptimo para el algoritmo
- Mejores prácticas de engagement
- Hashtags y keywords estratégicos

### 💾 Base de Datos Local
- Historial de todo tu contenido generado
- Templates guardados
- Estadísticas de uso por red

### 🎨 Interfaz Profesional
- Tema oscuro elegante
- Diseño intuitivo
- Copiar con un click
- Regenerar contenido fácilmente

---

## 📁 Estructura del Proyecto

```
ContentForgeAI/
├── contentforge/           # Módulo principal
│   ├── main.py            # Entry point
│   ├── config.py          # Configuración
│   ├── database.py        # SQLite manager
│   ├── gemini_handler.py  # API de Gemini
│   ├── content_engine.py  # Motor de generación
│   ├── prompts/           # Prompts por red social
│   ├── ui/                # Componentes GUI
│   └── knowledge/         # Base de conocimiento
├── data/                  # Base de datos local
└── assets/                # Recursos
```

---

## 🔧 Requisitos

- Python 3.8+
- API Key de Gemini (gratis en Google AI Studio)
- Dependencias: CustomTkinter, google-generativeai, etc.

---

<div align="center">

**Hecho con 💜 para creadores de contenido**

*Powered by Google Gemini AI*

</div>
