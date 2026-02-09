import requests
from config import Config
from datetime import datetime
import time

class RedditCollector:
    def __init__(self):
        self.source_name = 'reddit'
        # User-Agent para evitar bloqueo
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def collect(self, limit_per_sub: int = 50) -> list:
        """Collect from Reddit usando endpoint .json público"""
        signals = []
        subreddits = Config.REDDIT_SUBREDDITS
        
        print(f"\n🔍 Reddit - Collecting from {len(subreddits)} subreddits...")
        
        for sub_name in subreddits:
            try:
                print(f"  → r/{sub_name}...", end=" ")
                
                # Endpoint público .json
                url = f"https://www.reddit.com/r/{sub_name}/new.json?limit={limit_per_sub}"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"✗ HTTP {response.status_code}")
                    continue
                
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                count = 0
                for post in posts:
                    post_data = post.get('data', {})
                    
                    # Post title
                    if post_data.get('title'):
                        signals.append({
                            'raw_text': post_data['title'],
                            'source': self.source_name,
                            'source_url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'source_metadata': {
                                'type': 'post_title',
                                'subreddit': sub_name,
                                'score': post_data.get('ups', 0),
                                'num_comments': post_data.get('num_comments', 0)
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'language': 'es'
                        })
                        count += 1
                    
                    # Post body (selftext)
                    if post_data.get('selftext') and len(post_data['selftext']) > 30:
                        signals.append({
                            'raw_text': post_data['selftext'][:500],  # Primeros 500 chars
                            'source': self.source_name,
                            'source_url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'source_metadata': {
                                'type': 'post_body',
                                'subreddit': sub_name,
                                'score': post_data.get('ups', 0)
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'language': 'es'
                        })
                        count += 1
                
                print(f"✓ {count} signals")
                time.sleep(2)  # Rate limiting educado
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        print(f"\n✅ Total: {len(signals)} signals from Reddit")
        return signals
