import os

class Config:
    # Supabase (desde GitHub Secrets)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Google Trends Keywords
    GOOGLE_TRENDS_KEYWORDS = [
        "marketing digital",
        "seo",
        "estrategia marketing",
        "publicidad online",
        "redes sociales empresas",
        "aumentar ventas",
        "contenido digital"
    ]
    
    # Reddit
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = "NOMOS-Analisis/1.0"
    REDDIT_SUBREDDITS = [
        "marketing",
        "entrepreneur", 
        "smallbusiness",
        "digital_marketing",
        "SEO"
    ]
