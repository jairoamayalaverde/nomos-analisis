"""
Google Trends Collector v4.5.0
Recolecta señales de intención de búsqueda desde Google Trends
FIX: __init__ sin argumento config — lee settings internamente
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
    Rate limiting: 8-15s entre requests + retry exponencial
    """

    def __init__(self):
        self.pytrends = TrendReq(hl='es-CO', tz=300)
        self.timeframe = 'today 3-m'
        self.geo = 'CO'

        # Rate limiting settings
        self.base_delay = 8
        self.max_delay = 15
        self.max_retries = 3

    # KEYWORDS POR TACTIC
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
        """Request con retry exponencial y rate limiting"""
        for attempt in range(self.max_retries):
            try:
                self.pytrends.build_payload(
                    [keyword],
                    cat=0,
                    timeframe=self.timeframe,
                    geo=self.geo,
                    gprop=''
                )

                df = self.pytrends.interest_over_time()
                related = self.pytrends.related_queries()

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
                    wait_time = (2 ** attempt) * 10
                    print(f"    ⚠️  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {'success': False, 'error': str(e), 'keyword': keyword}

            except Exception as e:
                return {'success': False, 'error': str(e), 'keyword': keyword}

        return {'success': False, 'error': 'Max retries exceeded', 'keyword': keyword}

    def _extract_signals(self, result: Dict, tactic_id: str) -> List[Dict]:
        """Extrae señales de los resultados de Trends"""
        signals = []

        if not result.get('success'):
            return signals

        keyword = result['keyword']
        related = result.get('related', {})

        if keyword in related:
            queries_data = related[keyword]

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
        """Recolecta señales de Google Trends por tactic"""
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
