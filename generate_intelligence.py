#!/usr/bin/env python3
"""
NOMO Intelligence Engine v4.2
Generates intelligence JSON with cognitive diagnoses
NO Supabase dependency - uses local signals
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from collections import Counter

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

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()

def load_signals() -> List[Dict]:
    """Load signals from JSON file"""
    if not Path(SIGNALS_FILE).exists():
        print(f"⚠️  Signals file not found: {SIGNALS_FILE}")
        return []
    
    try:
        with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        print(f"📂 Loaded {len(signals)} signals from {SIGNALS_FILE}")
        return signals
    except Exception as e:
        print(f"❌ Error loading signals: {e}")
        return []

def extract_best_insight(signals: List[Dict], max_length: int = 110) -> str:
    """
    Extract the most representative phrase with priority on pain points
    
    Prioritizes:
    1. Questions (active pain)
    2. First person (real friction)
    3. Ideal length for wizard card
    """
    candidates = []
    
    for signal in signals:
        text = clean_text(signal['raw_text'])
        
        # Skip if too short
        if len(text) < 20:
            continue
        
        # Calculate score
        score = 0
        
        # Priority 1: Questions (Active pain)
        if '?' in text:
            score += 10
        
        # Priority 2: First person (Real friction)
        first_person_words = ['mi', 'tengo', 'estoy', 'necesito', 'siento', 'no puedo', 'me falta']
        if any(word in text.lower() for word in first_person_words):
            score += 5
        
        # Priority 3: Negation (Problems)
        negation_words = ['no ', 'sin ', 'falta', 'poco', 'cero']
        if any(word in text.lower() for word in negation_words):
            score += 3
        
        # Priority 4: Ideal length
        if 30 < len(text) < max_length:
            score += 2
        
        # Priority 5: Source quality (Reddit/Google Trends)
        source = signal.get('source', '')
        if source == 'google_trends':
            score += 1  # Prefer Google Trends (Spanish, Colombia-specific)
        
        candidates.append((text, score))
    
    if not candidates:
        return None
    
    # Sort by score and return best
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def calculate_prevalence(total_signals: int) -> int:
    """
    Calculate prevalence (how many of N businesses report this)
    
    Uses ~85% as baseline
    """
    if total_signals == 0:
        return 0
    
    prevalence = int(total_signals * 0.85)
    return max(1, prevalence)  # At least 1

def generate_intelligence(signals: List[Dict]) -> Dict:
    """
    Generate intelligence JSON from signals
    
    Returns:
        Dict with insights and metadata
    """
    print("\n🧠 Generating intelligence by tactic...")
    print("="*60)
    
    # Group signals by tactic_id
    signals_by_tactic = {}
    for signal in signals:
        tactic_id = signal.get('tactic_id')
        if not tactic_id:
            continue  # Skip signals without tactic_id
        
        if tactic_id not in signals_by_tactic:
            signals_by_tactic[tactic_id] = []
        
        signals_by_tactic[tactic_id].append(signal)
    
    # Generate insights for each tactic
    insights = {}
    
    for tactic_id in COGNITIVE_DIAGNOSES.keys():
        tactic_signals = signals_by_tactic.get(tactic_id, [])
        
        # Extract best insight
        best_insight = extract_best_insight(tactic_signals)
        
        # Calculate metrics
        total_signals = len(tactic_signals)
        prevalence = calculate_prevalence(total_signals)
        
        # Get diagnosis
        diagnosis = COGNITIVE_DIAGNOSES.get(tactic_id, "")
        
        if best_insight:
            insights[tactic_id] = {
                "top_insight": best_insight,
                "total_signals": total_signals,
                "prevalence": prevalence,
                "diagnosis": diagnosis
            }
            print(f"✅ {tactic_id}: {total_signals} signals → \"{best_insight[:50]}...\"")
        else:
            # Fallback for tactics without signals
            fallback_insight = f"Necesito optimizar {tactic_id.replace('_', ' ')}"
            insights[tactic_id] = {
                "top_insight": fallback_insight,
                "total_signals": 0,
                "prevalence": 0,
                "diagnosis": diagnosis
            }
            print(f"⚠️  {tactic_id}: No signals (using fallback)")
    
    # Generate metadata
    metadata = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_signals": len(signals),
        "version": "4.2-diagnosis",
        "tactics_with_data": len([t for t in insights.values() if t['total_signals'] > 0])
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

def print_summary(intelligence: Dict):
    """Print generation summary"""
    metadata = intelligence['metadata']
    insights = intelligence['insights']
    
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    print(f"Total signals processed: {metadata['total_signals']}")
    print(f"Tactics with data: {metadata['tactics_with_data']}/16")
    print(f"Version: {metadata['version']}")
    print(f"Generated at: {metadata['generated_at']}")
    
    # Distribution
    print("\n📊 DISTRIBUTION BY TACTIC:")
    distribution = [(tid, data['total_signals']) for tid, data in insights.items()]
    distribution.sort(key=lambda x: x[1], reverse=True)
    
    for tactic_id, count in distribution[:5]:  # Top 5
        print(f"  {tactic_id}: {count} signals")
    
    print("="*60 + "\n")

# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("NOMO INTELLIGENCE ENGINE v4.2")
    print("Cognitive Diagnosis Generation")
    print("="*60)
    
    # Load signals
    signals = load_signals()
    
    if not signals:
        print("❌ No signals found. Run collection first.")
        return
    
    # Generate intelligence
    intelligence = generate_intelligence(signals)
    
    # Save to file
    save_intelligence(intelligence)
    
    # Print summary
    print_summary(intelligence)

if __name__ == "__main__":
    main()
