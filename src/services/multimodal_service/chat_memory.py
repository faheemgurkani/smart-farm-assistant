import os
import json
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import glob

CHAT_LOG_DIR = "db/chat_sessions"
os.makedirs(CHAT_LOG_DIR, exist_ok=True)

_sessions = defaultdict(list)
_session_metadata = {}  # Store session metadata

# Session-level context store
_contexts = dict()

def get_context(session_id):
    """Get or create the context dict for a session."""
    return _contexts.setdefault(session_id, {})

def update_context(session_id, updates):
    """Update the context dict for a session with new key-value pairs."""
    ctx = get_context(session_id)
    ctx.update(updates)

def get_chat_log_path(session_id):
    return os.path.join(CHAT_LOG_DIR, f"{session_id}.json")

def get_metadata_path(session_id):
    return os.path.join(CHAT_LOG_DIR, f"{session_id}_metadata.json")

def create_session_metadata(session_id):
    """Create initial session metadata"""
    metadata = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "message_count": 0,
        "user_messages": 0,
        "assistant_messages": 0
    }
    _session_metadata[session_id] = metadata
    save_session_metadata(session_id)
    return metadata

def save_session_metadata(session_id):
    """Save session metadata to file"""
    if session_id in _session_metadata:
        path = get_metadata_path(session_id)
        with open(path, 'w') as f:
            json.dump(_session_metadata[session_id], f, indent=2)

def load_session_metadata(session_id):
    """Load session metadata from file"""
    path = get_metadata_path(session_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            _session_metadata[session_id] = json.load(f)
    return _session_metadata.get(session_id)

def update_session_activity(session_id):
    """Update last activity timestamp and message count"""
    if session_id not in _session_metadata:
        create_session_metadata(session_id)
    
    metadata = _session_metadata[session_id]
    metadata["last_activity"] = datetime.now().isoformat()
    metadata["message_count"] += 1
    save_session_metadata(session_id)

def get_history(session_id):
    if session_id in _sessions:
        return _sessions[session_id]
    
    path = get_chat_log_path(session_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            _sessions[session_id] = json.load(f)
        # Load metadata if it exists
        load_session_metadata(session_id)
    else:
        # Create new session metadata for new sessions
        create_session_metadata(session_id)
    return _sessions[session_id]

def add_message(session_id, role, message):
    """Add a message to the session with timestamp"""
    history = get_history(session_id)
    
    # Create message with timestamp
    message_data = {
        "role": role,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "message_id": str(uuid.uuid4())
    }
    
    history.append(message_data)
    _sessions[session_id] = history
    
    # Update session metadata
    update_session_activity(session_id)
    if role == "User":
        _session_metadata[session_id]["user_messages"] += 1
    elif role == "Assistant":
        _session_metadata[session_id]["assistant_messages"] += 1
    save_session_metadata(session_id)
    
    # Save to file
    with open(get_chat_log_path(session_id), 'w') as f:
        json.dump(history, f, indent=2)

def cleanup_old_sessions(max_age_days=30, max_sessions=100):
    """Clean up old sessions based on age and count"""
    session_files = glob.glob(os.path.join(CHAT_LOG_DIR, "*.json"))
    session_files = [f for f in session_files if not f.endswith("_metadata.json")]
    
    # Get session info with timestamps
    session_info = []
    for file_path in session_files:
        session_id = os.path.basename(file_path).replace(".json", "")
        metadata_path = get_metadata_path(session_id)
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                last_activity = datetime.fromisoformat(metadata.get("last_activity", metadata.get("created_at")))
                session_info.append({
                    "session_id": session_id,
                    "file_path": file_path,
                    "metadata_path": metadata_path,
                    "last_activity": last_activity
                })
    
    # Sort by last activity (oldest first)
    session_info.sort(key=lambda x: x["last_activity"])
    
    # Remove sessions older than max_age_days
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    sessions_to_remove = []
    
    for session in session_info:
        if session["last_activity"] < cutoff_date:
            sessions_to_remove.append(session)
    
    # If we have too many sessions, remove oldest ones
    if len(session_info) > max_sessions:
        excess_count = len(session_info) - max_sessions
        sessions_to_remove.extend(session_info[:excess_count])
    
    # Remove duplicate sessions (in case of overlap)
    unique_sessions_to_remove = []
    seen_ids = set()
    for session in sessions_to_remove:
        if session["session_id"] not in seen_ids:
            unique_sessions_to_remove.append(session)
            seen_ids.add(session["session_id"])
    
    # Actually remove the files
    removed_count = 0
    for session in unique_sessions_to_remove:
        try:
            if os.path.exists(session["file_path"]):
                os.remove(session["file_path"])
            if os.path.exists(session["metadata_path"]):
                os.remove(session["metadata_path"])
            removed_count += 1
        except Exception as e:
            print(f"Error removing session {session['session_id']}: {e}")
    
    return removed_count

def get_session_stats(session_id):
    """Get statistics for a specific session"""
    metadata = load_session_metadata(session_id)
    if metadata:
        return {
            "session_id": session_id,
            "created_at": metadata.get("created_at"),
            "last_activity": metadata.get("last_activity"),
            "message_count": metadata.get("message_count", 0),
            "user_messages": metadata.get("user_messages", 0),
            "assistant_messages": metadata.get("assistant_messages", 0)
        }
    return None

def get_all_session_stats():
    """Get statistics for all sessions"""
    session_files = glob.glob(os.path.join(CHAT_LOG_DIR, "*_metadata.json"))
    stats = []
    
    for metadata_file in session_files:
        session_id = os.path.basename(metadata_file).replace("_metadata.json", "")
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            stats.append({
                "session_id": session_id,
                "created_at": metadata.get("created_at"),
                "last_activity": metadata.get("last_activity"),
                "message_count": metadata.get("message_count", 0),
                "user_messages": metadata.get("user_messages", 0),
                "assistant_messages": metadata.get("assistant_messages", 0)
            })
    
    return sorted(stats, key=lambda x: x["last_activity"], reverse=True)
