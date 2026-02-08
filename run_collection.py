#!/usr/bin/env python3
"""
NOMOS ANÁLISIS™ - Collection Script
Runs via GitHub Actions daily
"""

import time
from datetime import datetime
from collectors.google_trends import GoogleTrendsCollector
from collectors.reddit import RedditCollector
from database import db

def main():
    print("\n" + "="*60)
    print("NOMOS ANÁLISIS™ - Market Intelligence Collection")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    total_signals = 0
    start_time = time.time()
    
    # Google Trends
    print("\n[1/2] GOOGLE TRENDS")
    print("-" * 60)
    try:
        gt_collector = GoogleTrendsCollector()
        gt_signals = gt_collector.collect()
        
        if gt_signals:
            inserted = db.insert_signals(gt_signals)
            total_signals += len(inserted)
            db.log_collection('google_trends', len(inserted), 'success')
        else:
            print("\n⚠️  No signals collected")
            db.log_collection('google_trends', 0, 'partial', 'No data')
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.log_collection('google_trends', 0, 'failed', str(e))
    
    # Reddit
    print("\n[2/2] REDDIT")
    print("-" * 60)
    try:
        reddit_collector = RedditCollector()
        reddit_signals = reddit_collector.collect()
        
        if reddit_signals:
            inserted = db.insert_signals(reddit_signals)
            total_signals += len(inserted)
            db.log_collection('reddit', len(inserted), 'success')
        else:
            print("\n⚠️  Reddit skipped or no data")
            db.log_collection('reddit', 0, 'partial', 'Skipped or no data')
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.log_collection('reddit', 0, 'failed', str(e))
    
    # Summary
    execution_time = time.time() - start_time
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print(f"Total signals: {total_signals}")
    print(f"Execution time: {execution_time:.2f}s")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
