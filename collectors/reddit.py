import requests
from config import Config
from datetime import datetime
import time
from typing import List, Dict

class RedditCollector:
    def __init__(self):
        self.source_name = 'reddit'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def collect(self, limit_per_sub: int = None) -> List[Dict]:
        """
        Collect signals from Reddit with tactic assignment and relevance filtering
        
        Returns:
            List of signal dictionaries with tactic_id assigned
        """
        if limit_per_sub is None:
            limit_per_sub = Config.REDDIT_POST_LIMIT
        
        all_signals = []
        
        print(f"\n🔍 Reddit - Collecting by tactic...")
        print(f"   Limit per subreddit: {limit_per_sub}")
        
        # Iterar por cada tactic
        for tactic_id, subreddits in Config.REDDIT_SUBREDDITS_BY_TACTIC.items():
            print(f"\n📊 Tactic: {tactic_id}")
            tactic_signals = []
            
            for sub_name in subreddits:
                try:
                    print(f"  → r/{sub_name}...", end=" ", flush=True)
                    
                    # Endpoint público .json
                    url = f"https://www.reddit.com/r/{sub_name}/new.json?limit={limit_per_sub}"
                    
                    response = requests.get(url, headers=self.headers, timeout=15)
                    
                    if response.status_code != 200:
                        print(f"✗ HTTP {response.status_code}")
                        continue
                    
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    count = 0
                    for post in posts:
                        post_data = post.get('data', {})
                        
                        # Extract title
                        title = post_data.get('title', '')
                        if title and self._is_relevant_to_tactic(title, tactic_id):
                            signal = self._create_signal(
                                text=title,
                                tactic_id=tactic_id,
                                post_data=post_data,
                                signal_type='post_title'
                            )
                            if signal:
                                tactic_signals.append(signal)
                                count += 1
                        
                        # Extract selftext (body)
                        selftext = post_data.get('selftext', '')
                        if selftext and len(selftext) > 50:  # Mínimo 50 chars
                            # Limitar a 800 caracteres
                            selftext_trimmed = selftext[:800]
                            
                            if self._is_relevant_to_tactic(selftext_trimmed, tactic_id):
                                signal = self._create_signal(
                                    text=selftext_trimmed,
                                    tactic_id=tactic_id,
                                    post_data=post_data,
                                    signal_type='post_body'
                                )
                                if signal:
                                    tactic_signals.append(signal)
                                    count += 1
                    
                    print(f"✓ {count} signals")
                    
                    # Rate limiting educado (2 segundos entre requests)
                    time.sleep(2)
                    
                except requests.exceptions.Timeout:
                    print(f"✗ Timeout")
                    continue
                except Exception as e:
                    print(f"✗ Error: {str(e)[:50]}")
                    continue
            
            print(f"  ✅ Subtotal {tactic_id}: {len(tactic_signals)} signals")
            all_signals.extend(tactic_signals)
        
        print(f"\n✅ TOTAL: {len(all_signals)} signals from Reddit")
        
        # Mostrar distribución
        self._print_distribution(all_signals)
        
        return all_signals
    
    def _create_signal(self, text: str, tactic_id: str, post_data: dict, signal_type: str) -> Dict:
        """
        Create a signal dictionary with all metadata
        """
        # Filtrar texto vacío o muy corto
        if not text or len(text.strip()) < 20:
            return None
        
        # Filtrar posts de bots/spam
        if self._is_spam(text):
            return None
        
        return {
            'raw_text': text.strip(),
            'source': self.source_name,
            'tactic_id': tactic_id,
            'source_url': f"https://reddit.com{post_data.get('permalink', '')}",
            'source_metadata': {
                'type': signal_type,
                'subreddit': post_data.get('subreddit', ''),
                'score': post_data.get('ups', 0),
                'num_comments': post_data.get('num_comments', 0),
                'created_utc': post_data.get('created_utc', 0),
                'author': post_data.get('author', '[deleted]')
            },
            'timestamp': datetime.utcnow().isoformat(),
            'language': 'en'  # Correctamente marcado como inglés
        }
    
    def _is_relevant_to_tactic(self, text: str, tactic_id: str) -> bool:
        """
        Verifica si el texto es relevante para el tactic específico
        
        Usa keywords en inglés para filtrar contenido relevante
        """
        text_lower = text.lower()
        
        # Obtener keywords del tactic
        keywords = Config.REDDIT_KEYWORDS_EN.get(tactic_id, [])
        
        # Buscar coincidencia con cualquier keyword
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        
        # Si no hay match directo, buscar patrones de dolor/problema genéricos
        pain_patterns = [
            "problem with",
            "struggling with",
            "can't figure out",
            "not working",
            "no results",
            "failing at",
            "stuck with",
            "help with",
            "how to fix",
            "why isn't"
        ]
        
        for pattern in pain_patterns:
            if pattern in text_lower:
                # Tiene patrón de dolor, verificar si menciona tema relacionado
                tactic_themes = self._get_tactic_themes(tactic_id)
                for theme in tactic_themes:
                    if theme in text_lower:
                        return True
        
        return False
    
    def _get_tactic_themes(self, tactic_id: str) -> List[str]:
        """
        Retorna temas/conceptos generales relacionados con cada tactic
        """
        themes = {
            "web_no_convierte": ["website", "conversion", "traffic", "sales", "visitors"],
            "autoridad_sector": ["authority", "credibility", "expert", "brand", "thought leader"],
            "dominio_local": ["local", "google business", "maps", "nearby", "location"],
            "superar_competencia": ["competitor", "competition", "rival", "outrank"],
            "ideas_sin_plan": ["ideas", "execution", "priorities", "focus", "planning"],
            "proyectos_estancados": ["project", "stuck", "incomplete", "stalled", "finish"],
            "mensaje_confuso": ["message", "positioning", "value prop", "unclear", "confusing"],
            "embudo_desordenado": ["funnel", "leads", "conversion", "crm", "pipeline"],
            "marca_no_escala": ["scale", "delegate", "systems", "depends on me"],
            "modernizacion_rapida": ["automation", "outdated", "manual", "efficient", "modern"],
            "metodo_equipo": ["team", "priorities", "methodology", "organized", "workflow"],
            "servicios_premium": ["pricing", "value", "premium", "packaging", "services"],
            "escalar_contenido": ["content", "posting", "social media", "leads", "engagement"],
            "estetica_visual": ["design", "website", "traffic", "visitors", "beautiful"],
            "ads_convertir": ["ads", "facebook", "google", "roi", "conversion", "campaign"],
            "automatizacion": ["automation", "manual", "tools", "integration", "workflow"]
        }
        
        return themes.get(tactic_id, [])
    
    def _is_spam(self, text: str) -> bool:
        """
        Detecta spam o contenido de baja calidad
        """
        text_lower = text.lower()
        
        spam_patterns = [
            "click here",
            "buy now",
            "limited time",
            "act now",
            "make money fast",
            "work from home",
            "100% guaranteed",
            "risk free",
            "discount code",
            "promo code"
        ]
        
        for pattern in spam_patterns:
            if pattern in text_lower:
                return True
        
        # Detectar exceso de URLs
        if text.count('http') > 3:
            return True
        
        # Detectar exceso de emojis
        emoji_count = sum(1 for char in text if ord(char) > 127000)
        if emoji_count > 10:
            return True
        
        return False
    
    def _print_distribution(self, signals: List[Dict]):
        """
        Muestra distribución de señales por tactic
        """
        from collections import Counter
        
        distribution = Counter([s['tactic_id'] for s in signals])
        
        print("\n📊 DISTRIBUCIÓN POR TACTIC:")
        for tactic_id, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tactic_id}: {count} señales")
