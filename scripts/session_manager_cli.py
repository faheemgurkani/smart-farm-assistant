#!/usr/bin/env python3
"""
Session Manager CLI Tool
Provides command-line interface for managing chat sessions, viewing analytics, and cleanup operations.
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.multimodal_service.session_manager import session_manager
from src.services.multimodal_service.chat_memory import get_all_session_stats, get_session_stats, cleanup_old_sessions

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    if not timestamp_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def display_session_stats(stats: Dict):
    """Display session statistics in a formatted way"""
    print(f"\n📊 Session Statistics")
    print(f"{'='*50}")
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Avg Messages/Session: {stats['avg_messages_per_session']}")
    print(f"Oldest Session: {format_timestamp(stats['oldest_session'])}")
    print(f"Newest Session: {format_timestamp(stats['newest_session'])}")
    
    if stats['sessions_by_date']:
        print(f"\n📅 Sessions by Date:")
        for date, count in sorted(stats['sessions_by_date'].items()):
            print(f"  {date}: {count} sessions")

def display_session_list(sessions: List[Dict], limit: int = 10):
    """Display a list of sessions"""
    print(f"\n📋 Recent Sessions (showing {min(limit, len(sessions))} of {len(sessions)})")
    print(f"{'='*80}")
    print(f"{'Session ID':<20} {'Created':<20} {'Last Activity':<20} {'Messages':<10} {'User':<8} {'Assistant':<10}")
    print(f"{'-'*80}")
    
    for session in sessions[:limit]:
        session_id = session['session_id'][:18] + "..." if len(session['session_id']) > 18 else session['session_id']
        created = format_timestamp(session['created_at'])
        last_activity = format_timestamp(session['last_activity'])
        messages = session['message_count']
        user_msgs = session['user_messages']
        assistant_msgs = session['assistant_messages']
        
        print(f"{session_id:<20} {created:<20} {last_activity:<20} {messages:<10} {user_msgs:<8} {assistant_msgs:<10}")

def display_session_detail(session_id: str):
    """Display detailed information about a specific session"""
    summary = session_manager.get_session_summary(session_id)
    if not summary:
        print(f"❌ Session {session_id} not found")
        return
    
    print(f"\n📄 Session Details: {session_id}")
    print(f"{'='*60}")
    print(f"Created: {format_timestamp(summary['created_at'])}")
    print(f"Last Activity: {format_timestamp(summary['last_activity'])}")
    print(f"Duration: {summary['duration_seconds']:.1f} seconds" if summary['duration_seconds'] else "Duration: N/A")
    print(f"Total Messages: {summary['message_count']}")
    print(f"User Messages: {summary['user_messages']}")
    print(f"Assistant Messages: {summary['assistant_messages']}")
    
    if summary['messages']:
        print(f"\n💬 Chat History:")
        print(f"{'='*60}")
        for i, msg in enumerate(summary['messages'], 1):
            timestamp = format_timestamp(msg.get('timestamp', ''))
            role = msg['role']
            message = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
            print(f"{i:2d}. [{timestamp}] {role}: {message}")

def export_session(session_id: str, output_dir: str = "downloads"):
    """Export a session to a file"""
    filepath = session_manager.export_session_data(session_id, output_dir)
    if filepath:
        print(f"✅ Session exported to: {filepath}")
    else:
        print(f"❌ Failed to export session {session_id}")

def cleanup_sessions(max_age_days: int, max_sessions: int, dry_run: bool = False):
    """Clean up old sessions"""
    if dry_run:
        print(f"🔍 Dry run: Would clean up sessions older than {max_age_days} days or keep max {max_sessions} sessions")
        # For dry run, we'll just show what would be cleaned up
        sessions = get_all_session_stats()
        old_sessions = [s for s in sessions if s['last_activity']]
        print(f"Found {len(old_sessions)} sessions total")
        return
    
    removed_count = cleanup_old_sessions(max_age_days, max_sessions)
    print(f"✅ Cleanup completed: {removed_count} sessions removed")

def main():
    parser = argparse.ArgumentParser(description="Session Manager CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show session analytics')
    
    # List sessions command
    list_parser = subparsers.add_parser('list', help='List sessions')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of sessions to show')
    
    # Show session detail command
    detail_parser = subparsers.add_parser('detail', help='Show session details')
    detail_parser.add_argument('session_id', help='Session ID to show details for')
    
    # Export session command
    export_parser = subparsers.add_parser('export', help='Export session data')
    export_parser.add_argument('session_id', help='Session ID to export')
    export_parser.add_argument('--output-dir', default='downloads', help='Output directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old sessions')
    cleanup_parser.add_argument('--max-age-days', type=int, default=30, help='Maximum age in days')
    cleanup_parser.add_argument('--max-sessions', type=int, default=100, help='Maximum number of sessions to keep')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Show what would be cleaned up without doing it')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'analytics':
            stats = session_manager.get_session_analytics()
            display_session_stats(stats)
            
        elif args.command == 'list':
            sessions = get_all_session_stats()
            display_session_list(sessions, args.limit)
            
        elif args.command == 'detail':
            display_session_detail(args.session_id)
            
        elif args.command == 'export':
            export_session(args.session_id, args.output_dir)
            
        elif args.command == 'cleanup':
            cleanup_sessions(args.max_age_days, args.max_sessions, args.dry_run)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 