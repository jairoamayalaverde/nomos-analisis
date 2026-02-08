from supabase import create_client, Client
from config import Config
from typing import List, Dict, Any, Optional
from datetime import datetime

class SupabaseDB:
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_KEY
        )
    
    def insert_signals(self, signals: List[Dict[str, Any]]) -> List[Dict]:
        """Insert multiple signals"""
        try:
            response = self.client.table('signals').insert(signals).execute()
            print(f"✅ Inserted {len(response.data)} signals")
            return response.data
        except Exception as e:
            print(f"❌ Error inserting signals: {e}")
            return []
    
    def get_signals(self, limit: int = 1000, source: str = None) -> List[Dict]:
        """Get recent signals"""
        query = self.client.table('signals').select('*')
        
        if source:
            query = query.eq('source', source)
        
        response = query.order('timestamp', desc=True).limit(limit).execute()
        return response.data
    
    def log_collection(self, 
                      source: str, 
                      signals_collected: int,
                      status: str = 'success',
                      error: Optional[str] = None,
                      execution_time: Optional[float] = None):
        """Log collection execution"""
        log_data = {
            'source': source,
            'signals_collected': signals_collected,
            'status': status,
            'error_message': error,
            'execution_time_seconds': execution_time,
            'completed_at': datetime.utcnow().isoformat()
        }
        self.client.table('collection_logs').insert(log_data).execute()

# Singleton
db = SupabaseDB()
