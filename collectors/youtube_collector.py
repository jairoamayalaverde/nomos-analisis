import requests
from collectors.config import Config  # ← CORREGIDO
from datetime import datetime
import time
from typing import List, Dict

class YouTubeCollector:
    def __init__(self):
        self.source_name = 'youtube'
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.api_key = Config.YOUTUBE_API_KEY
        
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables")

    # ─────────────────────────────────────────────
    # QUERIES mapeadas directamente a tactics NOMO
    # Cada query busca videos donde viven los comentarios
    # con los pain points reales del cliente
    # ─────────────────────────────────────────────
    QUERY_TACTIC_MAP = [
        # web_no_convierte
        {'query': 'tengo visitas pero no ventas',         'tactic': 'web_no_convierte'},
        {'query': 'mi página web no genera clientes',     'tactic': 'web_no_convierte'},
        {'query': 'por qué no vendo en internet',         'tactic': 'web_no_convierte'},
        {'query': 'invertí en web y no tengo visitas',    'tactic': 'web_no_convierte'},

        # ads_convertir
        {'query': 'gasté en ads y no funcionó',           'tactic': 'ads_convertir'},
        {'query': 'por qué mis anuncios no convierten',   'tactic': 'ads_convertir'},
        {'query': 'facebook ads no vendo',                'tactic': 'ads_convertir'},
        {'query': 'google ads sin resultados',            'tactic': 'ads_convertir'},

        # escalar_contenido
        {'query': 'publico contenido todos los días y no vendo', 'tactic': 'escalar_contenido'},
        {'query': 'cómo crecer en redes sociales negocios',      'tactic': 'escalar_contenido'},
        {'query': 'contenido viral emprendedores',                'tactic': 'escalar_contenido'},

        # embudo_desordenado
        {'query': 'embudo de ventas no funciona',         'tactic': 'embudo_desordenado'},
        {'query': 'cómo convertir seguidores en clientes','tactic': 'embudo_desordenado'},
        {'query': 'por qué no cierro ventas',             'tactic': 'embudo_desordenado'},

        # autoridad_sector
        {'query': 'cómo posicionar mi marca',             'tactic': 'autoridad_sector'},
        {'query': 'cómo ser referente en mi industria',   'tactic': 'autoridad_sector'},
        {'query': 'contraté agencia y no vendí',          'tactic': 'autoridad_sector'},

        # superar_competencia
        {'query': 'cómo superar a la competencia online', 'tactic': 'superar_competencia'},
        {'query': 'SEO vs publicidad pagada',             'tactic': 'superar_competencia'},
        {'query': 'mi competencia me está ganando',       'tactic': 'superar_competencia'},

        # dominio_local
        {'query': 'cómo aparecer en Google Maps negocios','tactic': 'dominio_local'},
        {'query': 'posicionamiento local empresas',       'tactic': 'dominio_local'},

        # ideas_sin_plan
        {'query': 'tengo ideas de negocio pero no sé por dónde empezar', 'tactic': 'ideas_sin_plan'},
        {'query': 'cómo organizar mi negocio',            'tactic': 'ideas_sin_plan'},
        {'query': 'empiezo proyectos y no los termino',   'tactic': 'ideas_sin_plan'},

        # proyectos_estancados
        {'query': 'mi negocio no crece qué hago',         'tactic': 'proyectos_estancados'},
        {'query': 'estancado en mi negocio',              'tactic': 'proyectos_estancados'},
        {'query': 'cómo salir del estancamiento empresarial', 'tactic': 'proyectos_estancados'},

        # mensaje_confuso
        {'query': 'cómo comunicar mi propuesta de valor', 'tactic': 'mensaje_confuso'},
        {'query': 'nadie entiende qué vendo',             'tactic': 'mensaje_confuso'},
        {'query': 'cómo diferenciarse de la competencia', 'tactic': 'mensaje_confuso'},

        # marca_no_escala
        {'query': 'cómo escalar mi negocio',              'tactic': 'marca_no_escala'},
        {'query': 'negocio con potencial que no crece',   'tactic': 'marca_no_escala'},
        {'query': 'por qué mi negocio no escala',         'tactic': 'marca_no_escala'},

        # modernizacion_rapida
        {'query': 'automatizar mi negocio con IA',        'tactic': 'modernizacion_rapida'},
        {'query': 'herramientas IA para emprendedores',   'tactic': 'modernizacion_rapida'},
        {'query': 'digitalizar mi empresa',               'tactic': 'modernizacion_rapida'},

        # automatizacion
        {'query': 'automatización marketing digital',     'tactic': 'automatizacion'},
        {'query': 'reducir tiempo producción contenido',  'tactic': 'automatizacion'},

        # servicios_premium
        {'query': 'cómo vender servicios caros',          'tactic': 'servicios_premium'},
        {'query': 'cómo subir precios sin perder clientes','tactic': 'servicios_premium'},

        # metodo_equipo
        {'query': 'cómo organizar equipo de trabajo',     'tactic': 'metodo_equipo'},
        {'query': 'productividad equipos pequeños',       'tactic': 'metodo_equipo'},

        # estetica_visual
        {'query': 'imagen de marca profesional',          'tactic': 'estetica_visual'},
        {'query': 'diseño para redes sociales negocios',  'tactic': 'estetica_visual'},
    ]

    def _search_videos(self, query: str, max_results: int = 5) -> List[str]:
        """Busca videos por query y retorna lista de video IDs"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'relevanceLanguage': 'es',
                'regionCode': 'CO',
                'maxResults': max_results,
                'order': 'relevance',
                'key': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []

            items = response.json().get('items', [])
            return [item['id']['videoId'] for item in items]

        except Exception as e:
            print(f"    ✗ Error buscando videos: {e}")
            return []

    def _get_comments(self, video_id: str, tactic: str, max_comments: int = 30) -> List[Dict]:
        """Extrae comentarios de un video y los mapea al tactic correspondiente"""
        signals = []
        try:
            url = f"{self.base_url}/commentThreads"
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': max_comments,
                'order': 'relevance',
                'key': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)

            # Comentarios desactivados en algunos videos — no es un error
            if response.status_code == 403:
                return []
            if response.status_code != 200:
                return []

            items = response.json().get('items', [])

            for item in items:
                comment = item['snippet']['topLevelComment']['snippet']
                text = comment.get('textDisplay', '').strip()

                # Filtro de calidad: mínimo 20 chars, máximo 500
                if len(text) < 20 or len(text) > 500:
                    continue

                # Filtro de relevancia: el comentario debe expresar un problema
                pain_patterns = [
                    'no vendo', 'no vende', 'no tengo clientes', 'no funciona',
                    'no crece', 'no convierte', 'no sé qué', 'no entiendo',
                    'gasté', 'invertí', 'perdí', 'fracasé', 'no sirve',
                    'hago todo y', 'publico y no', 'tengo pero no',
                    'me pasa', 'soy yo', 'mi caso', 'igual yo',
                    'estancado', 'estancada', 'no escala', 'sin resultados',
                    'no sé por qué', 'alguien sabe', 'qué hago',
                    'ayuda', 'consejo', 'cómo hago', 'cómo puedo'
                ]

                text_lower = text.lower()
                is_relevant = any(p in text_lower for p in pain_patterns)

                if not is_relevant:
                    continue

                signals.append({
                    'raw_text': text,
                    'source': self.source_name,
                    'tactic_id': tactic,  # ← Ya asignado automáticamente
                    'source_url': f"https://youtube.com/watch?v={video_id}",
                    'source_metadata': {
                        'type': 'comment',
                        'video_id': video_id,
                        'likes': comment.get('likeCount', 0),
                        'author': comment.get('authorDisplayName', 'Anonymous')
                    },
                    'timestamp': datetime.utcnow().isoformat(),
                    'language': 'es'
                })

        except Exception as e:
            print(f"    ✗ Error extrayendo comentarios: {str(e)[:50]}")

        return signals

    def collect(self, videos_per_query: int = 5, comments_per_video: int = 30) -> List[Dict]:
        """
        Flujo principal:
        1. Por cada query → busca videos
        2. Por cada video → extrae comentarios relevantes
        3. Mapea cada comentario al tactic correspondiente
        """
        all_signals = []
        seen_texts = set()  # Deduplicación

        print(f"\n🎬 YouTube - Collecting by tactic...")
        print(f"   Queries: {len(self.QUERY_TACTIC_MAP)}")
        print(f"   Videos per query: {videos_per_query}")
        print(f"   Comments per video: {comments_per_video}")

        for item in self.QUERY_TACTIC_MAP:
            query = item['query']
            tactic = item['tactic']

            print(f"\n📊 Tactic: {tactic}")
            print(f"  → Query: '{query}'...", end=" ", flush=True)

            # Buscar videos
            video_ids = self._search_videos(query, max_results=videos_per_query)
            if not video_ids:
                print("✗ No videos")
                continue

            tactic_count = 0
            for video_id in video_ids:
                comments = self._get_comments(video_id, tactic, max_comments=comments_per_video)

                for signal in comments:
                    # Deduplicar por texto
                    text_key = signal['raw_text'][:100].lower()
                    if text_key in seen_texts:
                        continue
                    seen_texts.add(text_key)
                    all_signals.append(signal)
                    tactic_count += 1

                time.sleep(0.5)  # Rate limiting suave entre videos

            print(f"✓ {tactic_count} signals")
            time.sleep(1)  # Rate limiting entre queries

        print(f"\n✅ TOTAL: {len(all_signals)} signals from YouTube")
        
        # Mostrar distribución
        self._print_distribution(all_signals)
        
        return all_signals
    
    def _print_distribution(self, signals: List[Dict]):
        """Muestra distribución de señales por tactic"""
        from collections import Counter
        
        distribution = Counter([s['tactic_id'] for s in signals])
        
        print("\n📊 DISTRIBUCIÓN POR TACTIC:")
        for tactic_id, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tactic_id}: {count} señales")
