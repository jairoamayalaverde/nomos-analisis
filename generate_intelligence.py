#!/usr/bin/env python3
"""
NOMO Intelligence Engine v2.0 - Tactic Specificity
Generates granular insights for each Wizard ID
"""

import json
from database import db
import re
from datetime import datetime

def clean_text(text):
    """Clean and normalize text"""
    text = re.sub(r'http\S+', '', text)
    text = ' '.join(text.split())
    return text.strip()

def extract_best_phrase(signals, max_length=110):
    """Extract the most representative phrase with priority on pain points"""
    candidates = []
    for signal in signals:
        text = clean_text(signal['raw_text'])
        score = 0
        # Prioridad 1: Preguntas (Dolor activo)
        if '?' in text: score += 10
        # Prioridad 2: Primera persona (Fricción real)
        if any(word in text.lower() for word in ['mi', 'tengo', 'estoy', 'necesito', 'siento']): score += 5
        # Longitud ideal para la tarjeta del Wizard
        if 30 < len(text) < max_length: candidates.append((text, score))
    
    if not candidates:
        return None
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def main():
    print("\n🧠 NOMO Re-engineering: Granular Tactic Mapping...")
    print("="*60)
    
    # 1. MATRIZ DE KEYWORDS POR ID DE TÁCTICA (Wizard Sync)
    tactic_keywords = {
        # Posicionamiento de Marca
        'web_no_convierte': ['vender', 'convierte', 'clientes', 'formulario', 'leads', 'no me escriben', 'web muerta'],
        'autoridad_sector': ['autoridad', 'referente', 'marca personal', 'confianza', 'experto', 'nombre', 'prestigio'],
        'dominio_local': ['local', 'maps', 'ciudad', 'negocio físico', 'zona', 'cerca de mi', 'dirección'],
        'superar_competencia': ['competencia', 'rival', 'otros', 'aparece primero', 'ranking', 'le ganan', 'comparación'],
        
        # Dirección & Proyectos
        'ideas_sin_plan': ['plan', 'ordenar', 'ideas', 'hoja de ruta', 'empezar', 'caos', 'organizar'],
        'proyectos_estancados': ['estancado', 'no avanza', 'bloqueado', 'lento', 'parado', 'ayuda', 'progreso'],
        'mensaje_confuso': ['mensaje', 'comunicación', 'no entienden', 'claro', 'explicar', 'confusión', 'valor'],
        'embudo_desordenado': ['embudo', 'funnel', 'ventas', 'pasos', 'proceso', 'fuga', 'seguimiento'],
        
        # Transforma tu marca (MOC)
        'marca_no_escala': ['escalar', 'crecer', 'techo', 'pequeño', 'estancado', 'volumen', 'masivo'],
        'modernizacion_rapida': ['moderno', 'viejo', 'actualizar', 'digital', 'tecnología', 'cambio', 'rápido'],
        'metodo_equipo': ['equipo', 'delegar', 'procesos', 'metodología', 'trabajadores', 'sistemas', 'manual'],
        'servicios_premium': ['high ticket', 'premium', 'caro', 'valor', 'élite', 'exclusivo', 'servicios'],
        
        # Fábrica de Contenidos
        'escalar_contenido': ['ia', 'artificial', 'escalar', 'rápido', 'mucho contenido', 'automatizar', 'prompts'],
        'estetica_visual': ['diseño', 'estética', 'bonito', 'impacto', 'visual', 'video', 'imagen'],
        'ads_convertir': ['ads', 'publicidad', 'pago', 'facebook', 'google', 'anuncios', 'conversión'],
        'automatizacion': ['tiempo', 'ahorrar', 'automático', 'herramientas', 'workflow', 'flujo', 'horas']
    }
    
    insights = {}
    all_signals = db.get_signals(limit=2000) # Subimos el límite por la granularidad
    
    for tactic_id, keywords in tactic_keywords.items():
        relevant = []
        for signal in all_signals:
            text_lower = signal['raw_text'].lower()
            if any(kw in text_lower for kw in keywords):
                relevant.append(signal)
        
        best_phrase = extract_best_phrase(relevant)
        
        if best_phrase:
            insights[tactic_id] = {
                "top_insight": best_phrase,
                "total_signals": len(relevant)
            }
            print(f"✅ {tactic_id}: {len(relevant)} señales -> {best_phrase[:40]}...")
        else:
            # Fallback inteligente si no hay señales para esa táctica específica
            insights[tactic_id] = {
                "top_insight": f"El mercado está buscando claridad en {tactic_id.replace('_', ' ')}",
                "total_signals": 0
            }

    output = {
        "insights": insights,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_signals": len(all_signals),
            "version": "2.1-granular"
        }
    }
    
    with open('nomos_home_intelligence.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n🚀 JSON Granular Generado Correctamente")

if __name__ == "__main__":
    main()
