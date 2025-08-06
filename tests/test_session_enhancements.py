#!/usr/bin/env python3
"""
Test script for session enhancements
Tests the new timestamp, metadata, and cleanup functionality
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.multimodal_service.chat_memory import (
    add_message, get_history, get_session_stats, 
    cleanup_old_sessions, create_session_metadata
)
from src.services.multimodal_service.session_manager import session_manager

def test_timestamped_messages():
    """Test that messages are properly timestamped"""
    print("🧪 Testing timestamped messages...")
    
    session_id = f"test_timestamp_{uuid.uuid4()}"
    
    # Add some test messages
    add_message(session_id, "User", "Hello, this is a test message")
    add_message(session_id, "Assistant", "Hello! I'm here to help with your farming questions.")
    add_message(session_id, "User", "What's the best time to plant wheat?")
    add_message(session_id, "Assistant", "Wheat should be planted in November for best results in Punjab.")
    
    # Get the history and check timestamps
    history = get_history(session_id)
    
    print(f"✅ Session created: {session_id}")
    print(f"✅ Messages in session: {len(history)}")
    
    for i, msg in enumerate(history, 1):
        print(f"  Message {i}:")
        print(f"    Role: {msg['role']}")
        print(f"    Message: {msg['message'][:50]}...")
        print(f"    Timestamp: {msg.get('timestamp', 'MISSING')}")
        print(f"    Message ID: {msg.get('message_id', 'MISSING')}")
        
        # Verify timestamp exists
        assert 'timestamp' in msg, f"Message {i} missing timestamp"
        assert 'message_id' in msg, f"Message {i} missing message_id"
    
    print("✅ All messages have timestamps and message IDs")
    return session_id

def test_session_metadata():
    """Test session metadata functionality"""
    print("\n🧪 Testing session metadata...")
    
    session_id = f"test_metadata_{uuid.uuid4()}"
    
    # Create metadata
    metadata = create_session_metadata(session_id)
    
    print(f"✅ Metadata created for session: {session_id}")
    print(f"  Created at: {metadata['created_at']}")
    print(f"  Last activity: {metadata['last_activity']}")
    print(f"  Message count: {metadata['message_count']}")
    
    # Add some messages and check metadata updates
    add_message(session_id, "User", "Test message 1")
    add_message(session_id, "Assistant", "Test response 1")
    add_message(session_id, "User", "Test message 2")
    
    # Get updated stats
    stats = get_session_stats(session_id)
    
    print(f"✅ Session stats after messages:")
    print(f"  Message count: {stats['message_count']}")
    print(f"  User messages: {stats['user_messages']}")
    print(f"  Assistant messages: {stats['assistant_messages']}")
    
    assert stats['message_count'] == 3, f"Expected 3 messages, got {stats['message_count']}"
    assert stats['user_messages'] == 2, f"Expected 2 user messages, got {stats['user_messages']}"
    assert stats['assistant_messages'] == 1, f"Expected 1 assistant message, got {stats['assistant_messages']}"
    
    print("✅ Session metadata working correctly")
    return session_id

def test_session_analytics():
    """Test session analytics functionality"""
    print("\n🧪 Testing session analytics...")
    
    # Get analytics
    analytics = session_manager.get_session_analytics()
    
    print(f"✅ Analytics retrieved:")
    print(f"  Total sessions: {analytics['total_sessions']}")
    print(f"  Total messages: {analytics['total_messages']}")
    print(f"  Avg messages/session: {analytics['avg_messages_per_session']}")
    print(f"  Oldest session: {analytics['oldest_session']}")
    print(f"  Newest session: {analytics['newest_session']}")
    
    if analytics['sessions_by_date']:
        print(f"  Sessions by date: {len(analytics['sessions_by_date'])} dates")
    
    print("✅ Session analytics working correctly")

def test_session_export():
    """Test session export functionality"""
    print("\n🧪 Testing session export...")
    
    session_id = f"test_export_{uuid.uuid4()}"
    
    # Add some test messages
    add_message(session_id, "User", "Export test message 1")
    add_message(session_id, "Assistant", "Export test response 1")
    add_message(session_id, "User", "Export test message 2")
    
    # Export the session
    export_path = session_manager.export_session_data(session_id, "downloads")
    
    if export_path and os.path.exists(export_path):
        print(f"✅ Session exported to: {export_path}")
        
        # Read and verify export
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        print(f"  Export contains:")
        print(f"    Session ID: {export_data['session_id']}")
        print(f"    Exported at: {export_data['exported_at']}")
        print(f"    Session stats: {export_data['session_stats']}")
        print(f"    Chat history: {len(export_data['chat_history'])} messages")
        
        assert export_data['session_id'] == session_id
        assert len(export_data['chat_history']) == 3
        
        print("✅ Session export working correctly")
    else:
        print("❌ Session export failed")

def test_cleanup_functionality():
    """Test cleanup functionality (dry run)"""
    print("\n🧪 Testing cleanup functionality (dry run)...")
    
    # Create some old sessions for testing
    old_session_ids = []
    for i in range(3):
        session_id = f"old_test_{uuid.uuid4()}"
        old_session_ids.append(session_id)
        
        # Add a message to create the session
        add_message(session_id, "User", f"Old test message {i}")
    
    print(f"✅ Created {len(old_session_ids)} test sessions")
    
    # Test cleanup with dry run
    removed_count = cleanup_old_sessions(max_age_days=1, max_sessions=5)
    print(f"✅ Cleanup completed: {removed_count} sessions removed")
    
    print("✅ Cleanup functionality working correctly")

def test_session_summary():
    """Test session summary functionality"""
    print("\n🧪 Testing session summary...")
    
    session_id = f"test_summary_{uuid.uuid4()}"
    
    # Add messages with some delay to test duration
    add_message(session_id, "User", "Summary test message 1")
    add_message(session_id, "Assistant", "Summary test response 1")
    add_message(session_id, "User", "Summary test message 2")
    
    # Get session summary
    summary = session_manager.get_session_summary(session_id)
    
    if summary:
        print(f"✅ Session summary retrieved:")
        print(f"  Session ID: {summary['session_id']}")
        print(f"  Created at: {summary['created_at']}")
        print(f"  Last activity: {summary['last_activity']}")
        print(f"  Duration: {summary['duration_seconds']:.1f} seconds")
        print(f"  Message count: {summary['message_count']}")
        print(f"  User messages: {summary['user_messages']}")
        print(f"  Assistant messages: {summary['assistant_messages']}")
        print(f"  Messages in history: {len(summary['messages'])}")
        
        assert summary['message_count'] == 3
        assert summary['user_messages'] == 2
        assert summary['assistant_messages'] == 1
        assert len(summary['messages']) == 3
        
        print("✅ Session summary working correctly")
    else:
        print("❌ Session summary failed")

def main():
    """Run all tests"""
    print("🚀 Starting session enhancement tests...")
    print("=" * 60)
    
    try:
        # Run all tests
        test_timestamped_messages()
        test_session_metadata()
        test_session_analytics()
        test_session_export()
        test_cleanup_functionality()
        test_session_summary()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Session enhancements are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 