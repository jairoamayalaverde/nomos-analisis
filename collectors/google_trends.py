"""
Google Trends Collector v4.4.2
Recolecta señales de intención de búsqueda desde Google Trends
FIX: Rate limiting agresivo + retry con backoff exponencial
"""
import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

class GoogleTrendsCollector:
    """
    Recolecta señales de Google Trends por tactic
    Rate limiting: 8-10s entre requests + retry exponencial
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.pytrends = TrendReq(hl='es-CO', tz=300)
        self.timeframe = config.get('TRENDS_TIMEFRAME', 'today 3-m')
        self.geo = config.get('TRENDS_GEO', 'CO')
        
        # Rate limiting settings
        self.base_delay = 8  # Segundos entre requests (aumentado de 2 a 8)
        self.max_delay = 15  # Delay máximo
        self.max_retries = 3  # Reintentos por query
    
    # KEYWORDS POR TACTIC (Reducidos de 8 a 4-5)
    TACTIC_KEYWORDS = {
        'web_no_convierte': [
            'mi web no genera clientes',
            'tráfico web sin ventas',
            'engagement sin conversiones',
            'visitas sin compras'
        ],
        
        'autoridad_sector': [
            'no aparezco en google',
            'aumentar autoridad digital',
            'posicionamiento experto',
            'ser referente sector'
        ],
        
        'dominio_local': [
            'aparecer google maps',
            'seo local negocio',
            'búsquedas cerca de mi',
            'visibilidad local google'
        ],
        
        'superar_competencia': [
            'análisis competencia digital',
            'competencia me supera online'
        ],
        
        'ideas_sin_plan': [
            'falta disciplina ejecución',
            'priorizar proyectos',
            'como organizar ideas negocio'
        ],
        
        'proyectos_estancados': [
            'no termino proyectos',
            'falta accountability',
            'proyectos sin avanzar'
        ],
        
        'mensaje_confuso': [
            'propuesta valor poco clara',
            'clientes no entienden oferta'
        ],
        
        'embudo_desordenado': [
            'embudo ventas desorganizado',
            'crm desorganizado'
        ],
        
        'marca_no_escala': [
            'marca depende de mi',
            'negocio sin sistemas',
            'no puedo delegar'
        ],
        
        'modernizacion_rapida': [
            'actualizar sistemas negocio'
        ],
        
        'metodo_equipo': [
            'equipo desorganizado'
        ],
        
        'servicios_premium': [
            'propuesta valor poco clara',
            'servicios mal empaquetados'
        ],
        
        'escalar_contenido': [
            'publico mucho no vendo',
            'escalar producción contenido',
            'contenido no genera ventas'
        ],
        
        'estetica_visual': [
            'diseño no convierte'
        ],
        
        'ads_convertir': [
            'ads sin conversiones',
            'anuncios no convierten'
        ],
        
        'automatizacion': [
            'procesos manuales repetitivos',
            'trabajo manual lento'
        ]
    }
    
    def _safe_request(self, keyword: str) -> Dict:
        """
        Request con retry exponencial y rate limiting
        """
        for attempt in range(self.max_retries):
            try:
                # Build payload
                self.pytrends.build_payload(
                    [keyword],
                    cat=0,
                    timeframe=self.timeframe,
                    geo=self.geo,
                    gprop=''
                )
                
                # Get interest over time
                df = self.pytrends.interest_over_time()
                
                # Get related queries
                related = self.pytrends.related_queries()
                
                # Delay ANTES del siguiente request
                delay = random.uniform(self.base_delay, self.max_delay)
                time.sleep(delay)
                
                return {
                    'success': True,
                    'interest': df,
                    'related': related,
                    'keyword': keyword
                }
                
            except ResponseError as e:
                if '429' in str(e):
                    # Rate limited - backoff exponencial
                    wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                    print(f"    ⚠️  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Otro error
                    return {
                        'success': False,
                        'error': str(e),
                        'keyword': keyword
                    }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'keyword': keyword
                }
        
        # Si llegamos aquí, se acabaron los retries
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'keyword': keyword
        }
    
    def _extract_signals(self, result: Dict, tactic_id: str) -> List[Dict]:
        """
        Extrae señales de los resultados de Trends
        """
        signals = []
        
        if not result.get('success'):
            return signals
        
        keyword = result['keyword']
        related = result.get('related', {})
        
        # Related queries (rising + top)
        if keyword in related:
            queries_data = related[keyword]
            
            # Rising queries
            if 'rising' in queries_data and queries_data['rising'] is not None:
                for _, row in queries_data['rising'].head(3).iterrows():
                    query = row.get('query', '')
                    if query:
                        signals.append({
                            'raw_text': query,
                            'source': 'google_trends',
                            'tactic_id': tactic_id,
                            'source_url': f'https://trends.google.com/trends/explore?q={keyword}&geo={self.geo}',
                            'source_metadata': {
                                'type': 'rising_query',
                                'seed_keyword': keyword,
                                'value': row.get('value', 0)
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'language': 'es'
                        })
            
            # Top queries
            if 'top' in queries_data and queries_data['top'] is not None:
                for _, row in queries_data['top'].head(2).iterrows():
                    query = row.get('query', '')
                    if query:
                        signals.append({
                            'raw_text': query,
                            'source': 'google_trends',
                            'tactic_id': tactic_id,
                            'source_url': f'https://trends.google.com/trends/explore?q={keyword}&geo={self.geo}',
                            'source_metadata': {
                                'type': 'top_query',
                                'seed_keyword': keyword,
                                'value': row.get('value', 0)
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'language': 'es'
                        })
        
        return signals
    
    def collect(self) -> List[Dict]:
        """
        Recolecta señales de Google Trends
        """
        all_signals = []
        
        print("\n[GOOGLE TRENDS]")
        print("-" * 60)
        print(f"\n🔍 Google Trends - Collecting by tactic...")
        print(f"   Timeframe: {self.timeframe}")
        print(f"   Geo: {self.geo}")
        print(f"   Rate limiting: {self.base_delay}-{self.max_delay}s between requests")
        
        for tactic_id, keywords in self.TACTIC_KEYWORDS.items():
            print(f"\n📊 Tactic: {tactic_id}")
            tactic_signals = []
            
            for keyword in keywords:
                print(f"  → '{keyword}'...", end=' ')
                
                result = self._safe_request(keyword)
                
                if result['success']:
                    signals = self._extract_signals(result, tactic_id)
                    tactic_signals.extend(signals)
                    print(f"✓ {len(signals)} signals")
                else:
                    print(f"✗ Error: {result['error']}")
            
            all_signals.extend(tactic_signals)
            print(f"  ✅ Subtotal {tactic_id}: {len(tactic_signals)} signals")
        
        print(f"\n✅ TOTAL: {len(all_signals)} signals from Google Trends")
        
        # Distribution
        if all_signals:
            print(f"\n📊 DISTRIBUCIÓN POR TACTIC:")
            distribution = {}
            for signal in all_signals:
                tactic = signal['tactic_id']
                distribution[tactic] = distribution.get(tactic, 0) + 1
            
            for tactic, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
                print(f"  {tactic}: {count}")
        else:
            print(f"\n⚠️  No signals collected")
        
        return all_signals
