"""
KR-CLI DOMINION Knowledge Base
Complete technical and marketing data for AI-powered content creation
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_PRODUCT = {
    "name": "KR-CLI DOMINION",
    "full_name": "KaliRoot CLI Dominion",
    "tagline": "La Suite de Ciberseguridad Definitiva Impulsada por IA",
    "description": "Transforma tu terminal en un Centro de Operaciones de Seguridad Ofensiva (SOC) personal. Un copiloto de ciberseguridad que entiende comandos, explica herramientas y automatiza tareas.",
    "version": "5.3.x",
    "author": "KaliRootCode",
    "website": "https://github.com/kalirootcode/KaliRootCLI",
    "pypi": "https://pypi.org/project/kr-cli-dominion/",
    "license": "MIT",
}

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALLATION GUIDE
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_INSTALLATION = {
    "basic": {
        "command": "pip install kr-cli-dominion",
        "run": "kr-clidn",
        "description": "Instalación directa desde PyPI. Compatible con Kali Linux, Parrot OS, Ubuntu y Termux.",
    },
    "virtual_env": {
        "steps": [
            "python3 -m venv venv",
            "source venv/bin/activate",
            "pip install kr-cli-dominion",
            "kr-clidn"
        ],
        "description": "Recomendado para evitar conflictos con paquetes del sistema.",
    },
    "termux": {
        "dependencies": "pkg install python libxml2 libxslt clang cmake rust build-essential",
        "install": "pip install kr-cli-dominion",
        "description": "Instalación en Android con Termux para pentesting móvil.",
    },
    "requirements": [
        "Python 3.8+",
        "Conexión a internet",
        "Terminal con soporte de colores",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# THE KR-CLI WRAPPER - KEY DIFFERENTIATOR
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_WRAPPER = {
    "name": "kr-cli",
    "description": "Un wrapper inteligente que intercepta cualquier comando de Linux, lo ejecuta, y envía el output a la IA para análisis automático.",
    
    "how_it_works": [
        "1. Escribe tu comando con 'kr-cli' delante: kr-cli nmap -sV target.com",
        "2. El comando se ejecuta normalmente mostrando el output",
        "3. Al terminar, la IA analiza el resultado automáticamente",
        "4. Recibes explicación detallada, riesgos y siguientes pasos",
    ],
    
    "examples": {
        "nmap": {
            "normal": "nmap -sV -sC 192.168.1.1",
            "with_wrapper": "kr-cli nmap -sV -sC 192.168.1.1",
            "benefit": "La IA explica cada puerto encontrado, versiones vulnerables, y sugiere exploits específicos.",
        },
        "nikto": {
            "normal": "nikto -h https://target.com",
            "with_wrapper": "kr-cli nikto -h https://target.com",
            "benefit": "Recibe un resumen de las vulnerabilidades web encontradas con prioridad de riesgo.",
        },
        "sqlmap": {
            "normal": "sqlmap -u 'http://target.com?id=1' --dbs",
            "with_wrapper": "kr-cli sqlmap -u 'http://target.com?id=1' --dbs",
            "benefit": "Explicación del tipo de inyección, bases de datos extraídas y pasos de explotación.",
        },
        "gobuster": {
            "normal": "gobuster dir -u http://target.com -w wordlist.txt",
            "with_wrapper": "kr-cli gobuster dir -u http://target.com -w wordlist.txt",
            "benefit": "Análisis de directorios interesantes encontrados y recomendaciones de investigación.",
        },
        "hydra": {
            "normal": "hydra -l admin -P rockyou.txt ssh://192.168.1.1",
            "with_wrapper": "kr-cli hydra -l admin -P rockyou.txt ssh://192.168.1.1",
            "benefit": "La IA registra los intentos y explica las credenciales encontradas.",
        },
    },
    
    "special_commands": {
        "kr-cli auto": "Modo autónomo - la IA sugiere y ejecuta comandos automáticamente",
        "kr-cli report": "Genera un reporte profesional de la sesión actual",
        "kr-cli listen": "Modo escucha - analiza comandos ejecutados en tiempo real",
    },
    
    "value_proposition": "Sin el wrapper, ejecutas comandos y tienes que interpretar todo manualmente. Con kr-cli, tienes un experto en ciberseguridad analizando cada resultado en tiempo real.",
}

# ═══════════════════════════════════════════════════════════════════════════════
# MODES OF OPERATION
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_MODES = {
    "consultation": {
        "name": "Modo Consulta",
        "plan": "Free",
        "description": "Tu mentor de seguridad. Explica vulnerabilidades, sugiere comandos y te ayuda a aprender.",
        "features": [
            "Consultas de ciberseguridad ilimitadas",
            "Explicación de comandos y herramientas",
            "Búsqueda web en tiempo real",
            "Historial de conversación",
        ],
        "limitations": [
            "Consume créditos por consulta",
            "Sin generación de scripts automáticos",
            "Sin acceso a herramientas premium",
        ],
    },
    "operational": {
        "name": "Modo Operativo",
        "plan": "Premium ($20/mes)",
        "description": "Tu socio de ataque. Genera scripts, planifica auditorías y desbloquea todas las herramientas.",
        "features": [
            "Créditos ilimitados",
            "Generación automática de scripts Python/Bash",
            "14 herramientas premium de pentesting",
            "Modelo IA superior (Llama 3.3 70B)",
            "Scaffolding de proyectos",
            "Soporte VIP",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM TOOLS (14 HERRAMIENTAS)
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_TOOLS = {
    "port_scanner": {
        "name": "Port Scanner",
        "icon": "🔍",
        "category": "Reconocimiento",
        "description": "Escaneo rápido e inteligente de puertos con análisis integrado.",
        "use_case": "Descubrir servicios expuestos en un objetivo.",
        "example": "Escanea los 1000 puertos más comunes en segundos.",
    },
    "top_100_repos": {
        "name": "Top 100 Repositorios",
        "icon": "💯",
        "category": "Recursos",
        "description": "Acceso directo a las mejores herramientas de hacking de GitHub.",
        "use_case": "Encontrar la herramienta perfecta para cada tarea.",
        "example": "Lista curada de repos como Impacket, BloodHound, SecLists.",
    },
    "cve_lookup": {
        "name": "CVE Lookup",
        "icon": "🛡️",
        "category": "Investigación",
        "description": "Búsqueda de vulnerabilidades en tiempo real con contexto de explotación.",
        "use_case": "Investigar CVEs por producto, versión o keyword.",
        "example": "Buscar CVEs de Apache 2.4.49 con exploits disponibles.",
    },
    "gdrive_downloader": {
        "name": "GDrive Downloader",
        "icon": "📥",
        "category": "Utilidades",
        "description": "Descarga archivos grandes de Google Drive sin límites.",
        "use_case": "Descargar wordlists, ISOs, datasets grandes.",
        "example": "Descargar rockyou.txt sin interrupciones.",
    },
    "hacking_labs": {
        "name": "Hacking Labs",
        "icon": "🧠",
        "category": "Práctica",
        "description": "Scripts listos para HackTheBox, VulnHub y CTFs.",
        "use_case": "Automatizar tareas comunes en labs de práctica.",
        "example": "Enum scripts, reverse shells, privesc checkers.",
    },
    "digital_forensics": {
        "name": "Digital Forensics",
        "icon": "🕵️",
        "category": "Forense",
        "description": "Herramientas de análisis forense y recuperación de datos.",
        "use_case": "Analizar dumps de memoria, discos, logs.",
        "example": "Volatility helpers, timeline generators.",
    },
    "metasploit_resources": {
        "name": "Metasploit Resources",
        "icon": "⚡",
        "category": "Explotación",
        "description": "Cheatsheets, exploits y recursos de Metasploit.",
        "use_case": "Referencia rápida de módulos y payloads.",
        "example": "msfvenom one-liners, post-exploitation guides.",
    },
    "termux_utilities": {
        "name": "Termux Utilities",
        "icon": "📱",
        "category": "Móvil",
        "description": "Optimización para pentesting desde Android.",
        "use_case": "Hacking en movimiento desde el teléfono.",
        "example": "Config especial para herramientas en Termux.",
    },
    "anonymity_tools": {
        "name": "Anonymity Tools",
        "icon": "🎭",
        "category": "Privacidad",
        "description": "Gestión de Tor, Proxychains y VPNs.",
        "use_case": "Mantener anonimato durante operaciones.",
        "example": "Tor browser launcher, proxychains config.",
    },
    "osint_dashboard": {
        "name": "OSINT Dashboard",
        "icon": "🦅",
        "category": "Inteligencia",
        "description": "Panel de herramientas OSINT: Sherlock, Osintgram, etc.",
        "use_case": "Investigación de personas y organizaciones.",
        "example": "Buscar usuario en 300+ redes sociales.",
    },
    "wifi_auditing": {
        "name": "WiFi Auditing",
        "icon": "📡",
        "category": "Wireless",
        "description": "Launchers para Aircrack-ng, Wifite, Fluxion.",
        "use_case": "Auditoría de redes WiFi.",
        "example": "Captura de handshakes automatizada.",
    },
    "password_cracking": {
        "name": "Password Cracking",
        "icon": "🔑",
        "category": "Cracking",
        "description": "Helpers para Hydra, John, Hashcat.",
        "use_case": "Crackeo de contraseñas y hashes.",
        "example": "Comandos optimizados para cada tipo de hash.",
    },
    "social_engineering": {
        "name": "Social Engineering",
        "icon": "🎣",
        "category": "Ingeniería Social",
        "description": "Herramientas de phishing y SE.",
        "use_case": "Campañas de concienciación o red team.",
        "example": "Templates de phishing, pretexting guides.",
    },
    "fsociety_framework": {
        "name": "Fsociety Framework",
        "icon": "🎭",
        "category": "Framework",
        "description": "Suite modular completa de pentesting.",
        "use_case": "Acceso a múltiples herramientas desde un menú.",
        "example": "Mr. Robot style hacking toolkit.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMMON SECURITY TOOLS + KR-CLI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

SECURITY_TOOLS_CONTEXT = {
    "nmap": {
        "name": "Nmap",
        "category": "Network Scanner",
        "description": "El escáner de red más popular. Descubre hosts, puertos y servicios.",
        "normal_usage": "nmap -sV -sC -p- target.com",
        "kr_cli_usage": "kr-cli nmap -sV -sC -p- target.com",
        "kr_cli_benefit": "Después del escaneo, la IA analiza automáticamente cada puerto, identifica versiones vulnerables, y sugiere exploits específicos. No tienes que googlear cada servicio.",
        "pain_point": "Normalmente tienes que investigar cada puerto manualmente en Google.",
        "common_flags": "-sV (versiones), -sC (scripts), -p- (todos los puertos), -Pn (skip ping)",
    },
    "gobuster": {
        "name": "Gobuster",
        "category": "Web Fuzzer",
        "description": "Fuzzer de directorios y subdominios web.",
        "normal_usage": "gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt",
        "kr_cli_usage": "kr-cli gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt",
        "kr_cli_benefit": "La IA prioriza los directorios encontrados por nivel de interés: admin panels, backups, configs expuestos.",
        "pain_point": "El output es una lista enorme sin contexto de qué es más importante.",
    },
    "nikto": {
        "name": "Nikto",
        "category": "Web Vulnerability Scanner",
        "description": "Escáner de vulnerabilidades web clásico.",
        "normal_usage": "nikto -h https://target.com",
        "kr_cli_usage": "kr-cli nikto -h https://target.com",
        "kr_cli_benefit": "Resumen ejecutivo de vulnerabilidades con scoring de riesgo y pasos de remediación.",
        "pain_point": "Genera cientos de líneas de output sin priorización.",
    },
    "sqlmap": {
        "name": "SQLmap",
        "category": "SQL Injection",
        "description": "La herramienta definitiva para inyección SQL automatizada.",
        "normal_usage": "sqlmap -u 'http://target.com?id=1' --dbs --batch",
        "kr_cli_usage": "kr-cli sqlmap -u 'http://target.com?id=1' --dbs --batch",
        "kr_cli_benefit": "Explicación del tipo de inyección, técnicas usadas, y guía para extracción de datos.",
        "pain_point": "El output técnico es difícil de interpretar para principiantes.",
    },
    "hydra": {
        "name": "Hydra",
        "category": "Brute Force",
        "description": "Cracker de contraseñas para múltiples protocolos.",
        "normal_usage": "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.1",
        "kr_cli_usage": "kr-cli hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.1",
        "kr_cli_benefit": "Al encontrar credenciales, la IA sugiere los siguientes pasos de post-explotación.",
        "pain_point": "Encontrar la contraseña es solo el primer paso, ¿qué hago después?",
    },
    "metasploit": {
        "name": "Metasploit",
        "category": "Exploitation Framework",
        "description": "El framework de explotación más completo.",
        "normal_usage": "msfconsole → search exploit → use → set options → exploit",
        "kr_cli_usage": "Pregunta a la IA: 'Necesito explotar un Apache 2.4.49 path traversal'",
        "kr_cli_benefit": "La IA te guía paso a paso con los comandos exactos y configuración de payload.",
        "pain_point": "Cientos de módulos, difícil encontrar el correcto.",
    },
    "burpsuite": {
        "name": "Burp Suite",
        "category": "Web Proxy",
        "description": "Proxy de interceptación para testing de aplicaciones web.",
        "normal_usage": "Configurar proxy, interceptar requests, analizar manualmente",
        "kr_cli_usage": "Pega el request en la consola AI para análisis",
        "kr_cli_benefit": "La IA identifica parámetros vulnerables, sugiere payloads y técnicas de bypass.",
        "pain_point": "Requiere experiencia para saber qué buscar.",
    },
    "john": {
        "name": "John the Ripper",
        "category": "Password Cracker",
        "description": "Cracker de hashes histórico y potente.",
        "normal_usage": "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
        "kr_cli_usage": "kr-cli john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
        "kr_cli_benefit": "Identifica el tipo de hash automáticamente y sugiere la configuración óptima.",
        "pain_point": "Hay que identificar el formato del hash primero.",
    },
    "hashcat": {
        "name": "Hashcat",
        "category": "GPU Password Cracker", 
        "description": "El cracker más rápido usando GPU.",
        "normal_usage": "hashcat -m 0 -a 0 hashes.txt wordlist.txt",
        "kr_cli_usage": "Pregunta: 'Tengo este hash: $1$xyz... ¿cómo lo crackeo?'",
        "kr_cli_benefit": "La IA identifica el hash mode (-m) correcto y optimiza el ataque.",
        "pain_point": "Los modos de hash son confusos (-m 0, -m 1000, etc.).",
    },
    "wireshark": {
        "name": "Wireshark",
        "category": "Network Analyzer",
        "description": "Analizador de paquetes de red.",
        "normal_usage": "Capturar tráfico → Aplicar filtros → Analizar",
        "kr_cli_usage": "Exporta los paquetes interesantes y pégalos en la consola AI",
        "kr_cli_benefit": "Explicación del protocolo, detección de anomalías, credenciales en texto plano.",
        "pain_point": "Miles de paquetes, difícil encontrar lo relevante.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PRICING & PACKAGES
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_PRICING = {
    "subscription": {
        "name": "Premium (Modo Operativo)",
        "price": 20.0,
        "currency": "USD",
        "period": "mes",
        "payment_method": "USDT (TRC-20)",
        "benefits": [
            "Créditos ilimitados",
            "14 herramientas premium",
            "Modelo IA superior (Llama 3.3 70B)",
            "Generación de scripts automáticos",
            "Soporte VIP prioritario",
        ],
    },
    "credit_packages": [
        {"name": "Starter", "credits": 500, "price": 10.0, "ideal": "Estudiantes, consultas puntuales"},
        {"name": "Hacker Pro", "credits": 1200, "price": 20.0, "ideal": "Uso diario intensivo"},
        {"name": "Elite", "credits": 2500, "price": 35.0, "ideal": "Power users y profesionales"},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT MARKETING HOOKS
# ═══════════════════════════════════════════════════════════════════════════════

CONTENT_HOOKS = {
    "pain_points": [
        "¿Cansado de buscar la sintaxis de comandos en Google?",
        "¿El output de nmap te parece jeroglíficos?",
        "¿Pasas horas leyendo documentación de herramientas?",
        "¿No sabes qué hacer después de encontrar un puerto abierto?",
        "¿Tus reportes de pentesting tardan más que el test?",
        "¿Te pierdes entre tantos módulos de Metasploit?",
        "¿Sientes que la curva de aprendizaje es infinita?",
    ],
    
    "solutions": [
        "Una IA que entiende cada herramienta de Kali Linux",
        "Análisis automático de resultados en español",
        "De 30 minutos de investigación a 3 segundos de IA",
        "Tu mentor personal de ciberseguridad 24/7",
        "El experto que siempre quisiste tener al lado",
        "Aprende mientras hackeas, no después",
    ],
    
    "comparisons": [
        {"before": "Googlear 'nmap output explained'", "after": "La IA te lo explica al instante"},
        {"before": "Buscar 'CVE-2021-XXXX exploit'", "after": "CVE Lookup con exploits listos"},
        {"before": "Recordar flags de cada herramienta", "after": "La IA te sugiere el comando perfecto"},
        {"before": "Copiar comandos de Medium/blogs", "after": "Comandos generados para tu caso"},
        {"before": "Interpretar output técnico", "after": "Análisis automático con próximos pasos"},
    ],
    
    "testimonial_angles": [
        "Pasé mi primera certificación OSCP gracias a practicar con KR-CLI",
        "Encontré mi primer bug bounty en la primera semana de uso",
        "Reduje el tiempo de auditoría un 60%",
        "Finalmente entiendo qué hace cada herramienta",
        "Es como tener un senior pentester siempre disponible",
    ],
    
    "cta_variations": [
        "Instala gratis: pip install kr-cli-dominion",
        "500 créditos gratis al registrarte",
        "Prueba el modo consulta sin límites",
        "Tu terminal nunca volverá a ser igual",
        "Únete a los hackers que ya dominan su terminal",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# TARGET AUDIENCE
# ═══════════════════════════════════════════════════════════════════════════════

TARGET_AUDIENCE = {
    "primary": [
        {
            "persona": "Estudiante de Ciberseguridad",
            "pain": "Curva de aprendizaje empinada, mucha teoría sin práctica",
            "solution": "Aprende haciendo con explicaciones en tiempo real",
            "message": "Deja de memorizar, empieza a entender",
        },
        {
            "persona": "Pentester Junior",
            "pain": "Falta de experiencia, miedo a errores",
            "solution": "La IA valida tus comandos y te guía",
            "message": "Tu socio senior virtual",
        },
        {
            "persona": "Bug Bounty Hunter",
            "pain": "Velocidad de reconocimiento, competencia alta",
            "solution": "Automatización + análisis rápido",
            "message": "Encuentra vulnerabilidades más rápido",
        },
    ],
    "secondary": [
        {
            "persona": "Administrador de Sistemas",
            "pain": "Necesita auditar sin ser experto en seguridad",
            "solution": "Herramientas guiadas paso a paso",
            "message": "Seguridad sin PhD en hacking",
        },
        {
            "persona": "Red Team Professional",
            "pain": "Documentación y reportes consumen tiempo",
            "solution": "Reportes automáticos de sesión",
            "message": "Más hacking, menos papeleo",
        },
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED KNOWLEDGE EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

KR_CLI_KNOWLEDGE = {
    "product": KR_CLI_PRODUCT,
    "installation": KR_CLI_INSTALLATION,
    "wrapper": KR_CLI_WRAPPER,
    "modes": KR_CLI_MODES,
    "tools": KR_CLI_TOOLS,
    "security_tools": SECURITY_TOOLS_CONTEXT,
    "pricing": KR_CLI_PRICING,
    "content_hooks": CONTENT_HOOKS,
    "target_audience": TARGET_AUDIENCE,
}


def get_tool_context(tool_name: str) -> dict:
    """Get context for a specific security tool."""
    return SECURITY_TOOLS_CONTEXT.get(tool_name.lower(), {})


def get_kr_tool(tool_id: str) -> dict:
    """Get info about a KR-CLI premium tool."""
    return KR_CLI_TOOLS.get(tool_id, {})


def get_full_context() -> str:
    """Get full knowledge base as formatted string for AI context."""
    context = f"""
=== KR-CLI DOMINION - BASE DE CONOCIMIENTO ===

PRODUCTO: {KR_CLI_PRODUCT['name']} - {KR_CLI_PRODUCT['tagline']}
{KR_CLI_PRODUCT['description']}

INSTALACIÓN:
{KR_CLI_INSTALLATION['basic']['command']}
Luego ejecutar: {KR_CLI_INSTALLATION['basic']['run']}

EL WRAPPER KR-CLI:
{KR_CLI_WRAPPER['description']}

Ejemplo de uso:
- Sin KR-CLI: {KR_CLI_WRAPPER['examples']['nmap']['normal']}
- Con KR-CLI: {KR_CLI_WRAPPER['examples']['nmap']['with_wrapper']}
- Beneficio: {KR_CLI_WRAPPER['examples']['nmap']['benefit']}

HERRAMIENTAS PREMIUM (14 módulos):
"""
    for tool_id, tool in KR_CLI_TOOLS.items():
        context += f"- {tool['icon']} {tool['name']}: {tool['description']}\n"
    
    context += """

HOOKS DE CONTENIDO EFECTIVOS:
- PAIN POINTS: ¿Cansado de buscar comandos en Google? ¿El output te confunde?
- SOLUCIONES: IA que entiende cada herramienta, análisis automático
- CTA: pip install kr-cli-dominion (500 créditos gratis)

SIEMPRE INCLUIR:
1. Cómo la herramienta funciona NORMALMENTE
2. Cómo KR-CLI SIMPLIFICA el proceso
3. Ejemplo práctico con antes/después
4. Call-to-action para probar
"""
    return context
