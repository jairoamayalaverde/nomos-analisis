import praw
from config import Config
from datetime import datetime

class RedditCollector:
    def __init__(self):
        if not Config.REDDIT_CLIENT_ID or not Config.REDDIT_CLIENT_SECRET:
            print("⚠️  Reddit not configured, skipping...")
            self.reddit = None
            return
            
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        self.source_name = 'reddit'
    
    def collect(self, limit_per_sub: int = 20) -> list:
        """Collect from Reddit"""
        if not self.reddit:
            return []
            
        signals = []
        subreddits = Config.REDDIT_SUBREDDITS
        
        print(f"\n🔍 Reddit - Collecting from {len(subreddits)} subreddits...")
        
        for sub_name in subreddits:
            try:
                print(f"  → r/{sub_name}...", end=" ")
                subreddit = self.reddit.subreddit(sub_name)
                
                count = 0
                for post in subreddit.hot(limit=limit_per_sub):
                    signals.append({
                        'raw_text': post.title,
                        'source': self.source_name,
                        'source_url': f"https://reddit.com{post.permalink}",
                        'source_metadata': {
                            'type': 'post_title',
                            'subreddit': sub_name,
                            'score': post.score,
                            'num_comments': post.num_comments
                        },
                        'timestamp': datetime.utcnow().isoformat(),
                        'language': 'es'
                    })
                    count += 1
                    
                    if post.selftext and len(post.selftext) > 30:
                        signals.append({
                            'raw_text': post.selftext[:300],
                            'source': self.source_name,
                            'source_url': f"https://reddit.com{post.permalink}",
                            'source_metadata': {
                                'type': 'post_body',
                                'subreddit': sub_name,
                                'score': post.score
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'language': 'es'
                        })
                        count += 1
                
                print(f"✓ {count} signals")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        print(f"\n✅ Total: {len(signals)} signals from Reddit")
        return signals
