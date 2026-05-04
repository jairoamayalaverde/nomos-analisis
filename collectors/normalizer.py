"""
NOMO NORMALIZATION LAYER v4.4
Convierte señales multi-source (ES + EN) a insights normalizados 100% en español
Elimina duplicación y calcula confidence por source weight
"""
import re
from typing import Dict, List, Optional
from datetime import datetime

class SignalNormalizer:
    """
    Normaliza señales de múltiples fuentes e idiomas a estructura semántica unificada
    INPUT: Español + Inglés (Reddit)
    OUTPUT: 100% Español
    """
    
    # ============================================
    # SOURCE WEIGHTS
    # ============================================
    SOURCE_WEIGHTS = {
        'reddit': 1.0,          # Crudo, honesto, sin filtro comercial
        'youtube': 0.7,         # Emocional pero real, comentarios filtrados
        'google_trends': 0.5    # Intención de búsqueda, no problema directo
    }
    
    # ============================================
    # SEMANTIC PATTERNS BY TACTIC
    # Captura: ES + EN | Output: 100% ES
    # ============================================
    SEMANTIC_PATTERNS = {
        'web_no_convierte': {
            'patterns': [
                # ESPAÑOL (YouTube, Trends)
                r'tengo (visitas|tráfico|tráfico|views|seguidores) (pero|y) no (vendo|ventas|clientes|compran)',
                r'mucho (tráfico|tráfico|visitas) (cero|sin|no) (clientes|ventas|conversiones)',
                r'(gente|usuarios|visitas) (entra|ve|visita|llega) (pero|y) no (compra|convierte|cierra)',
                r'(engagement|likes|comentarios) (pero|y) (cero|no|sin) (clientes|ventas|ingresos)',
                # INGLÉS (Reddit)
                r'(traffic|visitors|clicks) but no (sales|customers|conversions)',
                r'(high|lots of) traffic (but|with) no (sales|revenue)',
                r'engagement (but|with) no revenue'
            ],
            'normalized': 'Tienes tráfico pero no conviertes',
            'intent': 'frustración',
            'pattern_type': 'tengo X pero no Y'
        },
        
        'ads_convertir': {
            'patterns': [
                # ESPAÑOL
                r'gasté (en|$\d+) (ads|anuncios|publicidad) (y|pero) no (funciona|vendo|resulta)',
                r'(facebook|google|instagram) ads (no|sin) (conversiones|resultados|ventas)',
                r'(invierto|invertí|gasto) (en|$) (publicidad|ads) (bajo|sin|mal) roi',
                r'anuncios no (convierten|funcionan|generan)',
                # INGLÉS
                r'ads (not working|low roi|no conversions|wasting money)',
                r'spending on ads (but|with) no (results|sales|return)',
                r'(facebook|google|meta) ads (not converting|poor performance)'
            ],
            'normalized': 'Inviertes en ads pero el ROI es bajo o inconsistente',
            'intent': 'frustración',
            'pattern_type': 'invierto en X pero no funciona'
        },
        
        'escalar_contenido': {
            'patterns': [
                # ESPAÑOL
                r'publico (contenido|posts|todos los días) (pero|y) no (vendo|genero|consigo)',
                r'(creo|produzco|hago) contenido (y|pero) (sin|no) (leads|clientes|resultados)',
                r'(mucho|bastante) contenido (cero|sin|no) (ventas|conversiones)',
                # INGLÉS
                r'posting (daily|constantly|every day) (but|with) no (sales|leads|results)',
                r'content (not converting|no results|wasting time)',
                r'creating content (but|with) no (sales|revenue|leads)'
            ],
            'normalized': 'Produces contenido pero no genera leads ni ventas',
            'intent': 'frustración',
            'pattern_type': 'hago X pero no obtengo Y'
        },
        
        'embudo_desordenado': {
            'patterns': [
                # ESPAÑOL
                r'embudo (desorganizado|con fugas|roto|no funciona)',
                r'(leads|clientes potenciales) se pierden (en el|durante) (proceso|embudo)',
                r'(crm|proceso de ventas) (desorganizado|caótico)',
                # INGLÉS
                r'(funnel|conversion funnel) (leaks|broken|not working)',
                r'losing (leads|prospects) (in|during) (the )?(process|funnel)',
                r'(sales process|crm) (chaos|disorganized|broken)'
            ],
            'normalized': 'Tu embudo pierde leads en cada etapa',
            'intent': 'problema',
            'pattern_type': 'tengo problema en X'
        },
        
        'autoridad_sector': {
            'patterns': [
                # ESPAÑOL
                r'no aparezco en google',
                r'(nadie|no) me (conoce|encuentra) en (mi|el) (sector|industria|nicho)',
                r'(cómo|como) (ser|posicionarme como) (autoridad|referente|experto)',
                r'(construir|aumentar) autoridad',
                # INGLÉS
                r'(build|establish) (authority|credibility|expertise)',
                r'not (visible|known|recognized) in (my )?(industry|niche)',
                r'(thought leadership|industry expert)'
            ],
            'normalized': 'No tienes autoridad visible en tu sector',
            'intent': 'deseo',
            'pattern_type': 'quiero lograr X'
        },
        
        'superar_competencia': {
            'patterns': [
                # ESPAÑOL
                r'(mi )?competencia me (supera|gana|está ganando)',
                r'(cómo|como) superar (a la )?competencia',
                r'(análisis|estrategia) (de )?competencia',
                # INGLÉS
                r'(competitors|competition) (beating|outranking|ahead of) me',
                r'how to (beat|outrank|surpass) compet',
                r'competitive (advantage|analysis)'
            ],
            'normalized': 'Tu competencia te supera en visibilidad digital',
            'intent': 'problema',
            'pattern_type': 'X me está superando'
        },
        
        'dominio_local': {
            'patterns': [
                # ESPAÑOL
                r'(aparecer|posicionar) en (google maps|búsquedas locales|cerca de mí)',
                r'seo local',
                r'google (mi negocio|my business)',
                # INGLÉS
                r'(local search|google my business|maps ranking)',
                r'not (showing|visible) in local (searches|results)',
                r'local (seo|visibility)'
            ],
            'normalized': 'No apareces en búsquedas locales cuando el cliente está listo',
            'intent': 'problema',
            'pattern_type': 'no tengo X'
        },
        
        'ideas_sin_plan': {
            'patterns': [
                # ESPAÑOL
                r'(tengo|muchas) ideas (pero|y) no (ejecuto|sé|organizo|termino)',
                r'(falta|sin) (disciplina|enfoque|organización) (de )?ejecución',
                r'(cómo|como) (organizar|priorizar) (mis )?ideas',
                # INGLÉS
                r'(too many )?ideas but no (execution|follow through|completion)',
                r"can't (prioritize|focus|organize) (my )?(ideas|projects)",
                r'lack of (focus|execution|discipline)'
            ],
            'normalized': 'Tienes ideas pero no sistema de ejecución',
            'intent': 'frustración',
            'pattern_type': 'tengo X pero no Y'
        },
        
        'proyectos_estancados': {
            'patterns': [
                # ESPAÑOL
                r'proyectos? (estancados?|sin avanzar|no (avanzan|terminan))',
                r'empiezo (proyectos|cosas) (pero|y) no (termino|avanzo)',
                r'(mi )?negocio no (crece|avanza|escala)',
                # INGLÉS
                r'projects? (stuck|stalled|not finishing|incomplete)',
                r'business (not growing|stagnant|stuck)',
                r"can't finish (projects|initiatives)"
            ],
            'normalized': 'Empiezas proyectos pero se estancan sin avanzar',
            'intent': 'frustración',
            'pattern_type': 'hago X pero se detiene'
        },
        
        'mensaje_confuso': {
            'patterns': [
                # ESPAÑOL
                r'(nadie|clientes no) (entiende|entienden) (qué vendo|mi oferta|lo que hago)',
                r'(mi )?mensaje (confuso|poco claro|no es claro)',
                r'(falta|sin) (urgencia|escasez) en (mi )?comunicación',
                # INGLÉS
                r'(unclear|confusing) (message|value prop|positioning)',
                r"customers (don't understand|confused about) what I (sell|offer|do)",
                r'messaging (problem|unclear|confusing)'
            ],
            'normalized': 'Tu mensaje no genera urgencia ni claridad',
            'intent': 'problema',
            'pattern_type': 'tengo problema con X'
        },
        
        'marca_no_escala': {
            'patterns': [
                # ESPAÑOL
                r'(todo|negocio) depende de mí',
                r'no puedo (delegar|escalar|crecer) sin (trabajar más|estar presente)',
                r'(sin|falta de) sistemas',
                # INGLÉS
                r'business depends on me',
                r"can't (scale|delegate|grow) without (me|working more)",
                r'(wearing all|too many) hats',
                r'stuck in (the )?business'
            ],
            'normalized': 'Tu negocio depende de ti y no escala sin más horas tuyas',
            'intent': 'problema',
            'pattern_type': 'estoy atrapado en X'
        },
        
        'modernizacion_rapida': {
            'patterns': [
                # ESPAÑOL
                r'(procesos|sistemas|herramientas) (manuales|obsoletos|antiguos)',
                r'competencia (usa|tiene) (automatización|mejores sistemas)',
                r'(necesito|quiero) (automatizar|modernizar|digitalizar)',
                # INGLÉS
                r'(manual|outdated|legacy) (processes|systems|tools)',
                r'competitors (more efficient|using automation|ahead technologically)',
                r'need (to )?(modernize|automate|digitalize)'
            ],
            'normalized': 'Tus procesos son manuales mientras la competencia automatiza',
            'intent': 'problema',
            'pattern_type': 'estoy atrasado en X'
        },
        
        'metodo_equipo': {
            'patterns': [
                # ESPAÑOL
                r'(mi )?equipo (sin|no tiene) prioridades claras',
                r'todo es urgente (y )?nada avanza',
                r'equipo (desorganizado|sin método)',
                # INGLÉS
                r'team (no priorities|disorganized|everything urgent)',
                r'(lack of|no) (methodology|clear priorities)',
                r'everything (is )?urgent (but )?nothing (gets done|moves forward)'
            ],
            'normalized': 'Tu equipo no tiene prioridades claras y todo es urgente',
            'intent': 'problema',
            'pattern_type': 'equipo sin X'
        },
        
        'servicios_premium': {
            'patterns': [
                # ESPAÑOL
                r'(compito|competir) por precio (y )?no (por )?valor',
                r'(cómo|como) (vender|cobrar) (más caro|servicios premium)',
                r'propuesta (de )?valor (poco clara|no clara)',
                # INGLÉS
                r'competing on price (not|instead of) value',
                r'how to (charge more|price premium|sell expensive)',
                r'(price too low|underpricing|value proposition unclear)'
            ],
            'normalized': 'Compites por precio en lugar de por valor premium',
            'intent': 'deseo',
            'pattern_type': 'quiero cambiar de X a Y'
        },
        
        'estetica_visual': {
            'patterns': [
                # ESPAÑOL
                r'(invertí|gasté) en diseño (pero|y) (no|sin) (tráfico|visitas|resultados)',
                r'(web|sitio) (bonit[oa]|lind[oa]) (pero|y) (sin|no) (visitas|tráfico)',
                r'diseño no convierte',
                # INGLÉS
                r'(beautiful|pretty|great) (site|design) (but|with) no (traffic|visitors|results)',
                r'design (not converting|over function)',
                r'spent on design (but|with) no (traffic|results)'
            ],
            'normalized': 'Diseño bonito pero sin arquitectura de visibilidad',
            'intent': 'frustración',
            'pattern_type': 'invertí en X pero no funciona'
        },
        
        'automatizacion': {
            'patterns': [
                # ESPAÑOL
                r'(procesos|tareas|trabajo) (manuales|repetitiv[oa]s)',
                r'(falta|sin) integración (entre )?herramientas',
                r'(necesito|quiero) automatizar',
                # INGLÉS
                r'(manual|repetitive) (processes|tasks|work)',
                r'(need|want) (to )?(automate|automation)',
                r'tools not integrated',
                r'workflow automation'
            ],
            'normalized': 'Procesos manuales repetitivos sin integración',
            'intent': 'deseo',
            'pattern_type': 'quiero eliminar X'
        }
    }
    
    def normalize(self, signal: Dict) -> Dict:
        """
        Normaliza una señal cruda a estructura semántica unificada
        
        Args:
            signal: Señal cruda con raw_text, source, tactic_id
        
        Returns:
            Señal normalizada con insight en ESPAÑOL, confidence, weights
        """
        raw_text = signal.get('raw_text', '').lower()
        tactic_id = signal.get('tactic_id', '')
        source = signal.get('source', 'unknown')
        
        # Buscar patrón semántico
        pattern_data = self._match_pattern(raw_text, tactic_id)
        
        # Calcular confidence
        confidence = self._calculate_confidence(pattern_data, source, raw_text)
        
        # Estructura normalizada (100% español)
        normalized = {
            'input_raw': signal.get('raw_text', ''),
            'normalized_insight': pattern_data['normalized'],  # ← SIEMPRE ESPAÑOL
            'intent': pattern_data['intent'],
            'pattern_type': pattern_data['pattern_type'],
            'tactic_id': tactic_id,
            'confidence': round(confidence, 2),
            'source': source,
            'source_weight': self.SOURCE_WEIGHTS.get(source, 0.5),
            'timestamp': signal.get('timestamp', datetime.utcnow().isoformat()),
            'source_url': signal.get('source_url', ''),
            'matched_pattern': pattern_data.get('matched_pattern', None)
        }
        
        return normalized
    
    def _match_pattern(self, text: str, tactic_id: str) -> Dict:
        """
        Encuentra el patrón semántico que coincide con el texto
        Captura ES + EN → Output ES
        """
        if tactic_id not in self.SEMANTIC_PATTERNS:
            return {
                'normalized': text[:100],
                'intent': 'unknown',
                'pattern_type': 'generic',
                'matched_pattern': None
            }
        
        tactic_patterns = self.SEMANTIC_PATTERNS[tactic_id]
        
        # Buscar coincidencia en patterns (ES o EN)
        for pattern in tactic_patterns['patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'normalized': tactic_patterns['normalized'],  # ← SIEMPRE ESPAÑOL
                    'intent': tactic_patterns['intent'],
                    'pattern_type': tactic_patterns['pattern_type'],
                    'matched_pattern': pattern
                }
        
        # No match - usar normalizado por defecto (español)
        return {
            'normalized': tactic_patterns['normalized'],
            'intent': tactic_patterns['intent'],
            'pattern_type': tactic_patterns['pattern_type'],
            'matched_pattern': None
        }
    
    def _calculate_confidence(self, pattern_data: Dict, source: str, text: str) -> float:
        """
        Calcula confidence score basado en:
        - Source weight (Reddit=1.0, YouTube=0.7, Trends=0.5)
        - Pattern match (bonus +0.2 si hay match exacto)
        - Text length (penalty si muy corto <30 o muy largo >400)
        """
        confidence = self.SOURCE_WEIGHTS.get(source, 0.5)
        
        # Bonus si hubo pattern match exacto
        if pattern_data.get('matched_pattern'):
            confidence += 0.2
        
        # Penalty por texto muy corto o muy largo
        text_len = len(text)
        if text_len < 30:
            confidence -= 0.15
        elif text_len > 400:
            confidence -= 0.1
        
        # Clamp entre 0 y 1
        return max(0.0, min(1.0, confidence))
    
    def deduplicate_by_normalized(self, normalized_signals: List[Dict]) -> List[Dict]:
        """
        Elimina duplicados basándose en normalized_insight (español)
        Mantiene la señal con mayor confidence
        """
        seen = {}
        
        for signal in normalized_signals:
            key = signal['normalized_insight']
            
            if key not in seen:
                seen[key] = signal
            else:
                # Mantener la de mayor confidence
                if signal['confidence'] > seen[key]['confidence']:
                    seen[key] = signal
        
        return list(seen.values())
    
    def calculate_weighted_prevalence(self, normalized_signals: List[Dict]) -> float:
        """
        Calcula prevalence ponderado por source_weight
        Reddit (1.0) > YouTube (0.7) > Trends (0.5)
        
        Returns:
            Float: Prevalence ponderado (puede ser decimal)
        """
        return sum([s['source_weight'] for s in normalized_signals])
