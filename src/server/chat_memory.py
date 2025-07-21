import os
import json
from collections import defaultdict

CHAT_LOG_DIR = "db/chat_sessions"
os.makedirs(CHAT_LOG_DIR, exist_ok=True)

_sessions = defaultdict(list)

def get_chat_log_path(session_id):
    return os.path.join(CHAT_LOG_DIR, f"{session_id}.json")

def get_history(session_id):
    if session_id in _sessions:
        return _sessions[session_id]
    
    path = get_chat_log_path(session_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            _sessions[session_id] = json.load(f)
    return _sessions[session_id]

def add_message(session_id, role, message):
    history = get_history(session_id)
    history.append({"role": role, "message": message})
    _sessions[session_id] = history
    with open(get_chat_log_path(session_id), 'w') as f:
        json.dump(history, f, indent=2)
