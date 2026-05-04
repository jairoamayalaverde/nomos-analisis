import os

class Config:
    # ============================================
    # GITHUB (Primary storage)
    # ============================================
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = "jairoamayalaverde/nomos-analisis"
    GITHUB_JSON_PATH = "nomos_home_intelligence.json"
    
    # ============================================
    # SUPABASE (Legacy - mantener si aún se usa)
    # ============================================
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # ============================================
    # FEATURE FLAGS
    # ============================================
    ENABLE_GOOGLE_TRENDS = True
    ENABLE_REDDIT = True  # ← Ahora activado
    ENABLE_YOUTUBE = True
    
    # ============================================
    # GOOGLE TRENDS - KEYWORDS POR TACTIC
    # ============================================
    GOOGLE_TRENDS_KEYWORDS_BY_TACTIC = {
        # POSICIONAMIENTO DE MARCA
        "web_no_convierte": [
            "mi web no genera clientes",
            "tráfico web sin ventas",
            "engagement sin conversiones",
            "likes sin clientes",
            "visitas sin compras",
            "contenido viral no vende",
            "seguidores pero no ventas",
            "mucho tráfico cero ventas"
        ],
        "autoridad_sector": [
            "no aparezco en google",
            "aumentar autoridad digital",
            "posicionamiento experto",
            "ser referente sector",
            "como ser autoridad marca"
        ],
        "dominio_local": [
            "aparecer google maps",
            "seo local negocio",
            "búsquedas cerca de mi",
            "visibilidad local google",
            "aparecer google mi negocio"
        ],
        "superar_competencia": [
            "competencia en google ads",
            "superar competencia seo",
            "análisis competencia digital",
            "competencia me supera online"
        ],
        
        # DIRECCIÓN & PROYECTOS
        "ideas_sin_plan": [
            "ideas sin ejecutar",
            "falta disciplina ejecución",
            "priorizar proyectos",
            "como organizar ideas negocio"
        ],
        "proyectos_estancados": [
            "proyectos estancados",
            "no termino proyectos",
            "falta accountability",
            "proyectos sin avanzar"
        ],
        "mensaje_confuso": [
            "mensaje marca confuso",
            "falta urgencia comunicación",
            "propuesta valor poco clara",
            "clientes no entienden oferta"
        ],
        "embudo_desordenado": [
            "embudo ventas desorganizado",
            "fugas embudo conversión",
            "leads se pierden proceso",
            "crm desorganizado"
        ],
        
        # TRANSFORMA TU MARCA
        "marca_no_escala": [
            "marca depende de mi",
            "negocio sin sistemas",
            "no puedo delegar",
            "todo depende de mi negocio"
        ],
        "modernizacion_rapida": [
            "procesos manuales lento",
            "competencia usa automatización",
            "actualizar sistemas negocio",
            "herramientas obsoletas"
        ],
        "metodo_equipo": [
            "equipo sin prioridades claras",
            "todo es urgente nada avanza",
            "metodología trabajo equipo",
            "equipo desorganizado"
        ],
        "servicios_premium": [
            "propuesta valor poco clara",
            "empaquetar servicios premium",
            "competir por precio no valor",
            "servicios mal empaquetados"
        ],
        
        # FÁBRICA DE CONTENIDOS
        "escalar_contenido": [
            "contenido sin leads",
            "publico mucho no vendo",
            "escalar producción contenido",
            "contenido sin resultados",
            "contenido no genera ventas"
        ],
        "estetica_visual": [
            "diseño web sin visitas",
            "invertí diseño no funciona",
            "web bonita sin tráfico",
            "diseño no convierte"
        ],
        "ads_convertir": [
            "ads sin conversiones",
            "gasto publicidad roi bajo",
            "anuncios no convierten",
            "facebook ads no funciona",
            "google ads sin resultados"
        ],
        "automatizacion": [
            "procesos manuales repetitivos",
            "falta integración herramientas",
            "automatizar producción",
            "trabajo manual lento"
        ]
    }
    
    # ============================================
    # REDDIT - SUBREDDITS POR TACTIC
    # ============================================
    REDDIT_SUBREDDITS_BY_TACTIC = {
        # POSICIONAMIENTO DE MARCA
        "web_no_convierte": [
            "marketing",
            "ecommerce", 
            "webdev",
            "smallbusiness",
            "shopify",
            "Entrepreneur"
        ],
        "autoridad_sector": [
            "marketing",
            "SEO",
            "content_marketing",
            "entrepreneur",
            "PersonalBranding",
            "SocialMediaMarketing"
        ],
        "dominio_local": [
            "smallbusiness",
            "SEO",
            "LocalBusiness",
            "restaurantowners"
        ],
        "superar_competencia": [
            "marketing",
            "SEO",
            "PPC",
            "digital_marketing",
            "growthmarketing"
        ],
        
        # DIRECCIÓN & PROYECTOS
        "ideas_sin_plan": [
            "entrepreneur",
            "startups",
            "productivity",
            "getdisciplined"
        ],
        "proyectos_estancados": [
            "projectmanagement",
            "productivity",
            "entrepreneur",
            "startups"
        ],
        "mensaje_confuso": [
            "copywriting",
            "marketing",
            "branding",
            "marketing_design"
        ],
        "embudo_desordenado": [
            "sales",
            "marketing",
            "ecommerce",
            "SaaS",
            "B2BMarketing"
        ],
        
        # TRANSFORMA TU MARCA
        "marca_no_escala": [
            "entrepreneur",
            "startups",
            "smallbusiness",
            "business"
        ],
        "modernizacion_rapida": [
            "automation",
            "productivity",
            "saas",
            "nocode",
            "digitalnomad"
        ],
        "metodo_equipo": [
            "projectmanagement",
            "agile",
            "scrum",
            "managers",
            "leadership"
        ],
        "servicios_premium": [
            "consulting",
            "freelance",
            "entrepreneur",
            "B2BMarketing"
        ],
        
        # FÁBRICA DE CONTENIDOS
        "escalar_contenido": [
            "content_marketing",
            "copywriting",
            "socialmedia",
            "SocialMediaMarketing",
            "InstagramMarketing"
        ],
        "estetica_visual": [
            "web_design",
            "UI_Design",
            "webdev",
            "design_critiques"
        ],
        "ads_convertir": [
            "PPC",
            "facebookads",
            "googleads",
            "adops",
            "AskMarketing"
        ],
        "automatizacion": [
            "automation",
            "nocode",
            "zapier",
            "productivity",
            "SaaS"
        ]
    }
    
    # ============================================
    # REDDIT - KEYWORDS EN INGLÉS POR TACTIC
    # ============================================
    REDDIT_KEYWORDS_EN = {
        "web_no_convierte": [
            "traffic but no sales",
            "visitors no conversion",
            "engagement no revenue",
            "clicks but no customers",
            "website not converting",
            "high bounce rate",
            "traffic without sales"
        ],
        "autoridad_sector": [
            "build authority",
            "establish credibility",
            "thought leadership",
            "industry expert",
            "personal brand"
        ],
        "dominio_local": [
            "local seo",
            "google my business",
            "local search",
            "maps ranking",
            "local visibility"
        ],
        "superar_competencia": [
            "competitor analysis",
            "competitive advantage",
            "outrank competitors",
            "beating competition"
        ],
        "ideas_sin_plan": [
            "ideas but no execution",
            "can't prioritize",
            "too many ideas",
            "lack of focus",
            "execution problem"
        ],
        "proyectos_estancados": [
            "projects stuck",
            "can't finish projects",
            "stalled initiatives",
            "incomplete projects"
        ],
        "mensaje_confuso": [
            "unclear message",
            "confusing value prop",
            "messaging problem",
            "unclear positioning"
        ],
        "embudo_desordenado": [
            "funnel leaks",
            "losing leads",
            "conversion funnel",
            "sales process broken",
            "crm chaos"
        ],
        "marca_no_escala": [
            "can't scale",
            "business depends on me",
            "can't delegate",
            "stuck in business",
            "wearing all hats"
        ],
        "modernizacion_rapida": [
            "outdated systems",
            "manual processes",
            "need automation",
            "competitors more efficient"
        ],
        "metodo_equipo": [
            "team no priorities",
            "everything urgent",
            "team disorganized",
            "lack of methodology"
        ],
        "servicios_premium": [
            "price too low",
            "competing on price",
            "packaging services",
            "premium positioning"
        ],
        "escalar_contenido": [
            "content not converting",
            "posting but no leads",
            "content without sales",
            "social media no results",
            "content scaling"
        ],
        "estetica_visual": [
            "beautiful site no traffic",
            "design not converting",
            "pretty website no visitors",
            "design over function"
        ],
        "ads_convertir": [
            "ads not converting",
            "low roi ads",
            "facebook ads not working",
            "wasting money ads",
            "poor ad performance",
            "high cpc low conversions"
        ],
        "automatizacion": [
            "manual processes",
            "repetitive tasks",
            "need automation",
            "tools not integrated",
            "workflow automation"
        ]
    }
    
    # Reddit API (no usado actualmente - endpoint público)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = "NOMOS-Analisis/2.0"
    
    # ============================================
    # CONFIGURACIÓN DE RECOLECCIÓN
    # ============================================
    
    # Mínimo de señales por tactic
    MIN_SIGNALS_PER_TACTIC = 20
    
    # Máximo de señales a recolectar por ejecución
    MAX_SIGNALS_PER_RUN = 500
    
    # Timeframe de búsqueda (Reddit)
    REDDIT_TIMEFRAME = "week"  # new, hot, top
    REDDIT_POST_LIMIT = 50  # Posts por subreddit
    
    # Google Trends
    GOOGLE_TRENDS_TIMEFRAME = "today 3-m"  # 3 meses
    GOOGLE_TRENDS_GEO = "CO"  # Colombia
    
    # ============================================
    # YOUTUBE DATA API v3
    # ============================================
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
