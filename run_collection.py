#!/usr/bin/env python3
"""
NOMOS ANÁLISIS™ - Collection Script v2
Runs via GitHub Actions daily
NO Supabase dependency - uses local JSON files
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import argparse

from collectors.google_trends import GoogleTrendsCollector
from collectors.reddit import RedditCollector
from collectors.youtube import YouTubeCollector

# ============================================
# CONFIGURATION
# ============================================
SIGNALS_FILE = "data/raw_signals.json"
COLLECTION_LOG_FILE = "data/collection_log.json"

def ensure_data_dir():
    """Ensure data directory exists"""
    Path("data").mkdir(exist_ok=True)

def load_existing_signals() -> List[Dict]:
    """Load existing signals from JSON file"""
    if not Path(SIGNALS_FILE).exists():
        return []
    
    try:
        with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading existing signals: {e}")
        return []

def save_signals(signals: List[Dict]):
    """Save signals to JSON file"""
    ensure_data_dir()
    
    try:
        with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(signals)} signals to {SIGNALS_FILE}")
    except Exception as e:
        print(f"❌ Error saving signals: {e}")
        raise

def log_collection(source: str, count: int, status: str, error: str = None):
    """Log collection execution"""
    ensure_data_dir()
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'source': source,
        'signals_collected': count,
        'status': status,
        'error': error
    }
    
    # Load existing log
    log = []
    if Path(COLLECTION_LOG_FILE).exists():
        try:
            with open(COLLECTION_LOG_FILE, 'r', encoding='utf-8') as f:
                log = json.load(f)
        except:
            log = []
    
    # Append new entry
    log.append(log_entry)
    
    # Keep only last 30 days
    log = log[-90:]  # 3 executions per day × 30 days
    
    # Save log
    try:
        with open(COLLECTION_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving log: {e}")

def deduplicate_signals(signals: List[Dict]) -> List[Dict]:
    """
    Remove duplicate signals based on raw_text + tactic_id
    Keeps the most recent one
    """
    seen = {}
    
    for signal in reversed(signals):  # Start from newest
        key = (signal.get('raw_text', '').lower(), signal.get('tactic_id', ''))
        
        if key not in seen:
            seen[key] = signal
    
    return list(seen.values())

def collect_from_source(source: str) -> List[Dict]:
    """
    Collect signals from specified source
    
    Args:
        source: 'google_trends', 'reddit', or 'youtube'
    
    Returns:
        List of collected signals
    """
    signals = []
    
    if source == 'google_trends':
        print("\n[GOOGLE TRENDS]")
        print("-" * 60)
        try:
            collector = GoogleTrendsCollector()
            signals = collector.collect()
            
            if signals:
                log_collection('google_trends', len(signals), 'success')
            else:
                print("\n⚠️  No signals collected")
                log_collection('google_trends', 0, 'partial', 'No data')
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            log_collection('google_trends', 0, 'failed', str(e))
    
    elif source == 'reddit':
        print("\n[REDDIT]")
        print("-" * 60)
        try:
            collector = RedditCollector()
            signals = collector.collect()
            
            if signals:
                log_collection('reddit', len(signals), 'success')
            else:
                print("\n⚠️  No signals collected")
                log_collection('reddit', 0, 'partial', 'Skipped or no data')
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            log_collection('reddit', 0, 'failed', str(e))
    
    elif source == 'youtube':
        print("\n[YOUTUBE]")
        print("-" * 60)
        try:
            collector = YouTubeCollector()
            signals = collector.collect(
                videos_per_query=5,
                comments_per_video=30
            )
            
            if signals:
                log_collection('youtube', len(signals), 'success')
            else:
                print("\n⚠️  No signals collected")
                log_collection('youtube', 0, 'partial', 'No data')
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            log_collection('youtube', 0, 'failed', str(e))
    
    else:
        print(f"❌ Unknown source: {source}")
    
    return signals

def main():
    parser = argparse.ArgumentParser(description='NOMOS Collection Script')
    parser.add_argument('--source', 
                       choices=['google_trends', 'reddit', 'youtube', 'all'],
                       default='all',
                       help='Source to collect from')
    parser.add_argument('--append', 
                       action='store_true',
                       help='Append to existing signals instead of replacing')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("NOMOS ANÁLISIS™ - Market Intelligence Collection v2")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: {args.source}")
    print(f"Mode: {'APPEND' if args.append else 'REPLACE'}")
    print("="*60)
    
    start_time = time.time()
    all_new_signals = []
    
    # Collect from sources
    if args.source in ['google_trends', 'all']:
        signals = collect_from_source('google_trends')
        all_new_signals.extend(signals)
    
    if args.source in ['reddit', 'all']:
        signals = collect_from_source('reddit')
        all_new_signals.extend(signals)
    
    if args.source in ['youtube', 'all']:
        signals = collect_from_source('youtube')
        all_new_signals.extend(signals)
    
    # Merge with existing signals if append mode
    if args.append:
        print("\n📂 Loading existing signals...")
        existing_signals = load_existing_signals()
        print(f"   Found {len(existing_signals)} existing signals")
        
        # Combine and deduplicate
        combined = existing_signals + all_new_signals
        final_signals = deduplicate_signals(combined)
        
        print(f"   After deduplication: {len(final_signals)} total signals")
    else:
        final_signals = deduplicate_signals(all_new_signals)
    
    # Save signals
    if final_signals:
        save_signals(final_signals)
    
    # Summary
    execution_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print(f"New signals collected: {len(all_new_signals)}")
    print(f"Total signals in database: {len(final_signals)}")
    print(f"Execution time: {execution_time:.2f}s")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
