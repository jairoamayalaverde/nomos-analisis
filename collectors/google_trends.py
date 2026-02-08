from pytrends.request import TrendReq
from config import Config
from datetime import datetime
import time

class GoogleTrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='es-CO', tz=360)
        self.source_name = 'google_trends'
    
    def collect(self) -> list:
        """Collect from Google Trends"""
        signals = []
        keywords = Config.GOOGLE_TRENDS_KEYWORDS
        
        print(f"\n🔍 Google Trends - Collecting for {len(keywords)} keywords...")
        
        for keyword in keywords:
            try:
                print(f"  → {keyword}...", end=" ")
                
                self.pytrends.build_payload(
                    [keyword], 
                    timeframe='today 7-d',
                    geo='CO'
                )
                
                related = self.pytrends.related_queries()
                
                count = 0
                if keyword in related:
                    top = related[keyword]['top']
                    if top is not None:
                        for _, row in top.iterrows():
                            signals.append({
                                'raw_text': row['query'],
                                'source': self.source_name,
                                'source_metadata': {
                                    'type': 'top_query',
                                    'value': int(row['value']),
                                    'base_keyword': keyword
                                },
                                'timestamp': datetime.utcnow().isoformat(),
                                'language': 'es'
                            })
                            count += 1
                    
                    rising = related[keyword]['rising']
                    if rising is not None:
                        for _, row in rising.iterrows():
                            signals.append({
                                'raw_text': row['query'],
                                'source': self.source_name,
                                'source_metadata': {
                                    'type': 'rising_query',
                                    'value': str(row['value']),
                                    'base_keyword': keyword
                                },
                                'timestamp': datetime.utcnow().isoformat(),
                                'language': 'es'
                            })
                            count += 1
                
                print(f"✓ {count} signals")
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        print(f"\n✅ Total: {len(signals)} signals from Google Trends")
        return signals
