#!/usr/bin/env python3
"""
NOMO Intelligence Engine v4.4
Generates intelligence JSON with:
- Semantic normalization (ES + EN → ES)
- Source weighting (Reddit 1.0, YouTube 0.7, Trends 0.5)
- Weighted prevalence
- Confidence scoring
- Multi-source detection
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter

# Import normalizer
from collectors.normalizer import SignalNormalizer

# ============================================
# CONFIGURATION
# ============================================
SIGNALS_FILE = "data/raw_signals.json"
OUTPUT_FILE = "nomos_home_intelligence.json"

# ============================================
# DIAGNÓSTICOS COGNITIVOS (Pre-escritos)
# ============================================
COGNITIVE_DIAGNOSES = {
    # POSICIONAMIENTO DE MARCA
    "web_no_convierte": "Tienes engagement, pero no un sistema de conversión claro. Por eso cada like, cada comentario, termina sin ingresos. La pregunta no es si funciona... es cuánto dinero estás dejando pasar cada día.",
    
    "autoridad_sector": "Tu marca no aparece ni cuando la buscan directamente. Eso significa que tu autoridad digital es prácticamente inexistente. Cada búsqueda de tu nombre hoy es una oportunidad que captura otro.",
    
    "dominio_local": "No estás visible en búsquedas locales cuando el cliente está listo para comprar. Tu Google Business está sin optimizar, sin reseñas, sin señales de autoridad. Cada \"cerca de mí\" que no respondes es un cliente que va a tu competencia.",
    
    "superar_competencia": "Tu competencia invierte en visibilidad estratégica mientras tú esperas que el tráfico orgánico llegue solo. Ellos están comprando el mercado que tú intentas ganar gratis. El problema no es su presupuesto... es tu falta de sistema SEO.",
    
    # DIRECCIÓN & PROYECTOS
    "ideas_sin_plan": "Tienes ideas, pero no un sistema que las convierta en ejecución. Por eso empiezas muchas cosas pero terminas pocas. El problema no es la creatividad... es la falta de método para priorizar y ejecutar.",
    
    "proyectos_estancados": "Arrancas proyectos con energía, pero a las 3 semanas se estancan. Sin un sistema claro de accountability y ejecución, el ciclo se repite. No necesitas más motivación... necesitas estructura.",
    
    "mensaje_confuso": "Tu comunicación no genera acción inmediata. El cliente entiende lo que haces, pero no siente urgencia de comprarte ahora. Sin escasez ni urgencia clara, tu propuesta siempre queda \"para después\".",
    
    "embudo_desordenado": "Tu embudo no está roto... está perdiendo dinero en cada etapa. Leads entran, pero no hay un sistema que los convierta en clientes de forma predecible. El problema no es el tráfico... es lo que pasa después.",
    
    # TRANSFORMA TU MARCA
    "marca_no_escala": "Creciste sin sistemas y ahora todo depende de ti. Cada cliente nuevo significa más carga operativa, más horas tuyas. Tu marca no puede crecer sin que tú trabajes más... y ese no es un modelo escalable.",
    
    "modernizacion_rapida": "Tu competencia adoptó automatización y sistemas modernos mientras tú sigues con procesos manuales. La brecha de eficiencia crece cada mes. No necesitas más esfuerzo... necesitas herramientas que multipliquen tu capacidad.",
    
    "metodo_equipo": "Tu equipo ejecuta, pero sin una prioridad clara compartida. Y cuando todo es urgente, nada realmente avanza. No necesitas más esfuerzo de tu gente... necesitas un sistema de decisión que alinee energía con resultados.",
    
    "servicios_premium": "Tu propuesta de valor no comunica la transformación real que entregas. Por eso compites por precio en lugar de por resultados. Servicios mal empaquetados atraen clientes que pagan poco y exigen mucho.",
    
    # FÁBRICA DE CONTENIDOS
    "escalar_contenido": "Estás produciendo contenido, pero sin intención de conversión estratégica. Por eso el esfuerzo no se traduce en leads ni ventas consistentes. Más contenido no es la solución... es dirección comercial en cada pieza.",
    
    "estetica_visual": "Invertiste en diseño web, pero priorizaste estética sobre estructura SEO y velocidad de carga. Resultado: una web bonita que nadie encuentra. El problema no es el diseño... es la arquitectura de visibilidad detrás.",
    
    "ads_convertir": "Estás comprando tráfico, pero no tienes un sistema que lo convierta de forma predecible. Por eso el ROI es inconsistente mes a mes. El problema no es la inversión en ads... es la arquitectura de conversión detrás.",
    
    "automatizacion": "Tus procesos son manuales y desconectados. Tu equipo está ocupado moviendo información entre herramientas en lugar de crear valor. Sin automatización, estás pagando por trabajo repetitivo que una integración resolvería."
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def load_signals() -> List[Dict]:
    """Load signals from JSON file"""
    if not Path(SIGNALS_FILE).exists():
        print(f"⚠️  Signals file not found: {SIGNALS_FILE}")
        return []
    
    try:
        with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        print(f"📂 Loaded {len(signals)} raw signals from {SIGNALS_FILE}")
        return signals
    except Exception as e:
        print(f"❌ Error loading signals: {e}")
        return []

def normalize_signals(raw_signals: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Normalize signals using SignalNormalizer
    
    Returns:
        Tuple of (normalized_signals, stats)
    """
    print("\n🔄 Normalizing signals...")
    normalizer = SignalNormalizer()
    
    normalized = []
    for signal in raw_signals:
        try:
            norm_signal = normalizer.normalize(signal)
            normalized.append(norm_signal)
        except Exception as e:
            print(f"⚠️  Error normalizing signal: {e}")
            continue
    
    # Deduplicate by normalized_insight
    print(f"   Before deduplication: {len(normalized)} signals")
    unique_normalized = normalizer.deduplicate_by_normalized(normalized)
    print(f"   After deduplication: {len(unique_normalized)} unique signals")
    
    # Stats
    stats = {
        'raw_count': len(raw_signals),
        'normalized_count': len(normalized),
        'unique_count': len(unique_normalized),
        'deduplication_rate': round((1 - len(unique_normalized) / len(normalized)) * 100, 1) if normalized else 0
    }
    
    return unique_normalized, stats

def count_sources_by_tactic(signals: List[Dict]) -> Dict[str, List[str]]:
    """
    Count unique sources per tactic
    
    Returns:
        Dict[tactic_id, list of sources]
    """
    sources_by_tactic = {}
    
    for signal in signals:
        tactic_id = signal.get('tactic_id')
        source = signal.get('source')
        
        if tactic_id not in sources_by_tactic:
            sources_by_tactic[tactic_id] = set()
        
        sources_by_tactic[tactic_id].add(source)
    
    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in sources_by_tactic.items()}

def calculate_avg_confidence(signals: List[Dict]) -> float:
    """Calculate average confidence for a set of signals"""
    if not signals:
        return 0.0
    
    confidences = [s.get('confidence', 0.5) for s in signals]
    return round(sum(confidences) / len(confidences), 2)

def generate_intelligence(normalized_signals: List[Dict]) -> Dict:
    """
    Generate intelligence JSON from normalized signals
    
    Returns:
        Dict with insights and metadata
    """
    print("\n🧠 Generating intelligence by tactic...")
    print("="*60)
    
    normalizer = SignalNormalizer()
    
    # Group signals by tactic_id
    signals_by_tactic = {}
    for signal in normalized_signals:
        tactic_id = signal.get('tactic_id')
        if not tactic_id:
            continue
        
        if tactic_id not in signals_by_tactic:
            signals_by_tactic[tactic_id] = []
        
        signals_by_tactic[tactic_id].append(signal)
    
    # Count sources
    sources_by_tactic = count_sources_by_tactic(normalized_signals)
    
    # Generate insights for each tactic
    insights = {}
    
    for tactic_id in COGNITIVE_DIAGNOSES.keys():
        tactic_signals = signals_by_tactic.get(tactic_id, [])
        
        # Get top insight (normalized, español)
        if tactic_signals:
            # Sort by confidence and get top
            tactic_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            top_insight = tactic_signals[0]['normalized_insight']
        else:
            top_insight = f"Necesito optimizar {tactic_id.replace('_', ' ')}"
        
        # Calculate metrics
        total_signals = len(tactic_signals)
        
        # Weighted prevalence
        prevalence = int(normalizer.calculate_weighted_prevalence(tactic_signals))
        
        # Average confidence
        avg_confidence = calculate_avg_confidence(tactic_signals)
        
        # Sources
        sources = sources_by_tactic.get(tactic_id, [])
        
        # Diagnosis
        diagnosis = COGNITIVE_DIAGNOSES.get(tactic_id, "")
        
        insights[tactic_id] = {
            "top_insight": top_insight,
            "total_signals": total_signals,
            "prevalence": prevalence,
            "diagnosis": diagnosis,
            "confidence": avg_confidence,
            "sources": sources
        }
        
        if total_signals > 0:
            sources_str = ", ".join(sources) if sources else "N/A"
            print(f"✅ {tactic_id}: {total_signals} signals | conf: {avg_confidence} | sources: {sources_str}")
            print(f"   → \"{top_insight[:70]}...\"")
        else:
            print(f"⚠️  {tactic_id}: No signals (using fallback)")
    
    # Generate metadata
    metadata = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_signals": len(normalized_signals),
        "version": "4.4-normalized",
        "tactics_with_data": len([t for t in insights.values() if t['total_signals'] > 0]),
        "avg_confidence": calculate_avg_confidence(normalized_signals),
        "sources_used": sorted(list(set([s.get('source') for s in normalized_signals])))
    }
    
    return {
        "insights": insights,
        "metadata": metadata
    }

def save_intelligence(intelligence: Dict):
    """Save intelligence JSON to file"""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(intelligence, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Intelligence JSON saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n❌ Error saving JSON: {e}")
        raise

def print_summary(intelligence: Dict, norm_stats: Dict):
    """Print generation summary"""
    metadata = intelligence['metadata']
    insights = intelligence['insights']
    
    print("\n" + "="*60)
    print("GENERATION SUMMARY v4.4")
    print("="*60)
    print(f"Raw signals: {norm_stats['raw_count']}")
    print(f"After normalization: {norm_stats['normalized_count']}")
    print(f"After deduplication: {norm_stats['unique_count']} ({norm_stats['deduplication_rate']}% removed)")
    print(f"Tactics with data: {metadata['tactics_with_data']}/16")
    print(f"Average confidence: {metadata['avg_confidence']}")
    print(f"Sources: {', '.join(metadata['sources_used'])}")
    print(f"Version: {metadata['version']}")
    
    # Distribution
    print("\n📊 DISTRIBUTION BY TACTIC (Top 10):")
    distribution = [(tid, data['total_signals']) for tid, data in insights.items()]
    distribution.sort(key=lambda x: x[1], reverse=True)
    
    for tactic_id, count in distribution[:10]:
        conf = insights[tactic_id]['confidence']
        sources = insights[tactic_id]['sources']
        sources_str = ", ".join(sources) if sources else "N/A"
        print(f"  {tactic_id}: {count} signals | conf: {conf} | [{sources_str}]")
    
    print("="*60 + "\n")

# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("NOMO INTELLIGENCE ENGINE v4.4")
    print("Normalization + Weighted Prevalence + Multi-Source")
    print("="*60)
    
    # Load raw signals
    raw_signals = load_signals()
    
    if not raw_signals:
        print("❌ No signals found. Run collection first.")
        return
    
    # Normalize signals
    normalized_signals, norm_stats = normalize_signals(raw_signals)
    
    if not normalized_signals:
        print("❌ No signals after normalization.")
        return
    
    # Generate intelligence
    intelligence = generate_intelligence(normalized_signals)
    
    # Save to file
    save_intelligence(intelligence)
    
    # Print summary
    print_summary(intelligence, norm_stats)

if __name__ == "__main__":
    main()
