#!/usr/bin/env python3
"""
Generate nomos_home_intelligence.json from real market signals
Auto-commits to repo via GitHub Actions
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
    """Extract the most representative phrase"""
    candidates = []
    
    for signal in signals:
        text = clean_text(signal['raw_text'])
        
        # Prefer questions
        if '?' in text and 20 < len(text) < max_length:
            candidates.append((text, 10))
        elif 20 < len(text) < max_length:
            candidates.append((text, 5))
    
    if not candidates:
        return "Necesito ayuda estratégica con marketing digital"
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def main():
    print("\n🧠 Generating Intelligence JSON...")
    print("="*60)
    
    insight_keywords = {
        'Poco Tráfico': [
            'seo', 'google', 'tráfico', 'visitas', 'posicionamiento',
            'aparecer', 'encontrar', 'búsqueda', 'ranking', 'web'
        ],
        'Técnico': [
            'proyecto', 'plan', 'organizar', 'método', 'estancado',
            'estrategia', 'dirección', 'proceso', 'sistema', 'equipo'
        ],
        'Competencia': [
            'competencia', 'superar', 'mercado', 'diferenciación',
            'rival', 'otros', 'mejor que', 'ganar', 'perder'
        ],
        'Baja Conversión': [
            'conversión', 'contenido', 'ventas', 'leads', 'resultados',
            'clientes', 'publicidad', 'anuncios', 'engagement', 'roi'
        ]
    }
    
    insights = {}
    all_signals = db.get_signals(limit=1000)
    
    for category, keywords in insight_keywords.items():
        print(f"\n📊 {category}...")
        
        relevant = []
        for signal in all_signals:
            text_lower = signal['raw_text'].lower()
            if any(kw in text_lower for kw in keywords):
                relevant.append(signal)
        
        print(f"   {len(relevant)} signals found")
        
        if relevant:
            best = extract_best_phrase(relevant)
            insights[category] = {
                "reddit_voice": best,
                "signal_count": len(relevant)
            }
            print(f"   → {best[:50]}...")
        else:
            insights[category] = {
                "reddit_voice": f"Necesito ayuda con {category.lower()}",
                "signal_count": 0
            }
    
    output = {
        "insights": insights,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_signals": len(all_signals),
            "version": "2.0-auto"
        }
    }
    
    # Save
    with open('nomos_home_intelligence.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n✅ JSON Generated")
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
