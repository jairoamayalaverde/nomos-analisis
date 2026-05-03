from pytrends.request import TrendReq
from config import Config
from datetime import datetime
import time
from typing import List, Dict
from collections import Counter

class GoogleTrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='es-CO', tz=360)
        self.source_name = 'google_trends'
    
    def collect(self) -> List[Dict]:
        """
        Collect signals by tactic from Google Trends
        
        Returns:
            List of signal dictionaries with tactic_id assigned
        """
        all_signals = []
        
        print(f"\n🔍 Google Trends - Collecting by tactic...")
        print(f"   Timeframe: {Config.GOOGLE_TRENDS_TIMEFRAME}")
        print(f"   Geo: {Config.GOOGLE_TRENDS_GEO}")
        
        # Iterar por cada tactic
        for tactic_id, keywords in Config.GOOGLE_TRENDS_KEYWORDS_BY_TACTIC.items():
            print(f"\n📊 Tactic: {tactic_id}")
            tactic_signals = []
            
            for keyword in keywords:
                try:
                    print(f"  → '{keyword}'...", end=" ", flush=True)
                    
                    # Build payload
                    self.pytrends.build_payload(
                        [keyword], 
                        timeframe=Config.GOOGLE_TRENDS_TIMEFRAME,
                        geo=Config.GOOGLE_TRENDS_GEO
                    )
                    
                    # Get related queries
                    related = self.pytrends.related_queries()
                    
                    count = 0
                    
                    if keyword in related:
                        # TOP QUERIES (las más buscadas)
                        top = related[keyword]['top']
                        if top is not None:
                            for _, row in top.iterrows():
                                query_text = row['query']
                                
                                # Filtrar queries irrelevantes
                                if self._is_valid_signal(query_text):
                                    signal = self._create_signal(
                                        text=query_text,
                                        tactic_id=tactic_id,
                                        base_keyword=keyword,
                                        query_type='top_query',
                                        value=int(row['value'])
                                    )
                                    if signal:
                                        tactic_signals.append(signal)
                                        count += 1
                        
                        # RISING QUERIES (tendencias emergentes)
                        rising = related[keyword]['rising']
                        if rising is not None:
                            for _, row in rising.iterrows():
                                query_text = row['query']
                                
                                if self._is_valid_signal(query_text):
                                    # El valor puede ser 'Breakout' (str) o un número
                                    value_raw = row['value']
                                    value_str = str(value_raw)
                                    
                                    signal = self._create_signal(
                                        text=query_text,
                                        tactic_id=tactic_id,
                                        base_keyword=keyword,
                                        query_type='rising_query',
                                        value=value_str,
                                        is_breakout=(value_str == 'Breakout')
                                    )
                                    if signal:
                                        tactic_signals.append(signal)
                                        count += 1
                    
                    print(f"✓ {count} signals")
                    
                    # Rate limiting (evitar bloqueo de Google)
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"✗ Error: {str(e)[:60]}")
                    continue
            
            print(f"  ✅ Subtotal {tactic_id}: {len(tactic_signals)} signals")
            all_signals.extend(tactic_signals)
        
        print(f"\n✅ TOTAL: {len(all_signals)} signals from Google Trends")
        
        # Mostrar distribución
        self._print_distribution(all_signals)
        
        return all_signals
    
    def _create_signal(self, text: str, tactic_id: str, base_keyword: str, 
                       query_type: str, value, is_breakout: bool = False) -> Dict:
        """
        Create a signal dictionary with all metadata
        """
        # Filtrar texto vacío o muy corto
        if not text or len(text.strip()) < 5:
            return None
        
        # Crear metadata
        metadata = {
            'type': query_type,
            'base_keyword': base_keyword,
        }
        
        # Agregar valor según tipo
        if query_type == 'top_query':
            metadata['interest_score'] = value  # 0-100
        elif query_type == 'rising_query':
            if is_breakout:
                metadata['trend'] = 'breakout'  # Crecimiento explosivo
                metadata['growth'] = 'breakout'
            else:
                metadata['trend'] = 'rising'
                metadata['growth_percentage'] = value  # Ej: "+150%"
        
        return {
            'raw_text': text.strip(),
            'source': self.source_name,
            'tactic_id': tactic_id,
            'source_metadata': metadata,
            'timestamp': datetime.utcnow().isoformat(),
            'language': 'es'
        }
    
    def _is_valid_signal(self, query: str) -> bool:
        """
        Filtra queries irrelevantes
        
        RECHAZA:
        - Queries de aprendizaje ("curso", "tutorial", "como hacer")
        - Queries de búsqueda de proveedores ("mejor", "agencia", "empresa")
        - Queries informacionales puras ("que es", "definicion")
        - Queries de descarga/piratería
        
        ACEPTA:
        - Queries con dolor/problema ("no funciona", "no vendo", "falta")
        - Queries de situación ("tengo X pero no Y")
        - Queries de necesidad urgente ("necesito", "urgente", "como solucionar")
        """
        query_lower = query.lower()
        
        # ============================================
        # BLACKLIST - Rechazar automáticamente
        # ============================================
        blacklist = [
            # Aprendizaje
            'curso', 'tutorial', 'gratis', 'pdf', 'descargar', 'download',
            'como hacer', 'que es', 'definicion', 'significado',
            
            # Búsqueda de proveedores
            'mejor agencia', 'empresa de', 'contratar',
            'top 10', 'mejores empresas', 'ranking',
            
            # Comercial/Spam
            'precio', 'costo', 'cuanto cuesta', 'barato',
            'oferta', 'descuento', 'promocion',
            
            # Tech/Apps
            'login', 'app', 'software gratis', 'crack',
            'descargar programa', 'instalar',
            
            # Demasiado genérico
            'ejemplos de', 'tipos de', 'caracteristicas de'
        ]
        
        for term in blacklist:
            if term in query_lower:
                return False
        
        # ============================================
        # WHITELIST - Aceptar automáticamente
        # ============================================
        # Patrones de dolor/problema
        pain_patterns = [
            # Negación de resultados
            'no funciona', 'no genera', 'no vendo', 'no convierte',
            'no tengo', 'sin clientes', 'sin ventas', 'sin resultados',
            'cero clientes', 'cero ventas',
            
            # Situaciones problemáticas
            'tengo pero no', 'mucho pero poco', 'gasto pero',
            'invierto pero', 'publico pero',
            
            # Necesidad/Urgencia
            'falta', 'necesito', 'urgente', 'como solucionar',
            'como resolver', 'problema con', 'ayuda con',
            
            # Frustración
            'por que no', 'porque no', 'que hago si',
            'como arreglar', 'como mejorar'
        ]
        
        for pattern in pain_patterns:
            if pattern in query_lower:
                return True
        
        # ============================================
        # ANÁLISIS CONTEXTUAL
        # ============================================
        # Si contiene "pero" generalmente es una señal de dolor
        # Ej: "tengo tráfico pero no vendo"
        if 'pero' in query_lower or 'pero no' in query_lower:
            return True
        
        # Si es una pregunta de "por qué" suele ser dolor
        # Ej: "por qué mi web no convierte"
        if query_lower.startswith('por que') or query_lower.startswith('porque'):
            return True
        
        # Si menciona "mi" + negación = problema personal
        # Ej: "mi web no genera clientes"
        if 'mi ' in query_lower and any(neg in query_lower for neg in ['no ', 'sin ', 'cero ']):
            return True
        
        # Por defecto, RECHAZAR (conservative approach)
        # Solo aceptamos señales que pasaron los filtros de dolor
        return False
    
    def _print_distribution(self, signals: List[Dict]):
        """
        Muestra distribución de señales por tactic
        """
        distribution = Counter([s['tactic_id'] for s in signals])
        
        print("\n📊 DISTRIBUCIÓN POR TACTIC:")
        for tactic_id, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tactic_id}: {count} señales")
        
        # Estadísticas adicionales
        total = len(signals)
        if total > 0:
            print(f"\n📈 ESTADÍSTICAS:")
            print(f"  Total señales: {total}")
            print(f"  Promedio por tactic: {total / len(distribution):.1f}")
            print(f"  Tactic con más señales: {distribution.most_common(1)[0][0]} ({distribution.most_common(1)[0][1]})")
            print(f"  Tactic con menos señales: {distribution.most_common()[-1][0]} ({distribution.most_common()[-1][1]})")
