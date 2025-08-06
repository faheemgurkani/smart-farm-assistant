import os
import json
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """Manages chat sessions with automatic cleanup and monitoring"""
    
    def __init__(self, chat_log_dir: str = "db/chat_sessions"):
        self.chat_log_dir = chat_log_dir
        self.cleanup_config = {
            "max_age_days": 30,
            "max_sessions": 100,
            "cleanup_interval_hours": 24
        }
        self._cleanup_thread = None
        self._stop_cleanup = False
    
    def start_automatic_cleanup(self):
        """Start automatic cleanup in a background thread"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            logger.warning("Cleanup thread already running")
            return
        
        self._stop_cleanup = False
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.info("Automatic session cleanup started")
    
    def stop_automatic_cleanup(self):
        """Stop automatic cleanup"""
        self._stop_cleanup = True
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("Automatic session cleanup stopped")
    
    def _cleanup_worker(self):
        """Background worker for automatic cleanup"""
        schedule.every(self.cleanup_config["cleanup_interval_hours"]).hours.do(self.cleanup_old_sessions)
        
        while not self._stop_cleanup:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    def cleanup_old_sessions(self, max_age_days: Optional[int] = None, max_sessions: Optional[int] = None):
        """Clean up old sessions"""
        from .chat_memory import cleanup_old_sessions
        
        age_days = max_age_days or self.cleanup_config["max_age_days"]
        max_sess = max_sessions or self.cleanup_config["max_sessions"]
        
        removed_count = cleanup_old_sessions(age_days, max_sess)
        logger.info(f"Session cleanup completed: {removed_count} sessions removed")
        return removed_count
    
    def get_session_analytics(self) -> Dict:
        """Get analytics about all sessions"""
        from .chat_memory import get_all_session_stats
        
        stats = get_all_session_stats()
        
        if not stats:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "avg_messages_per_session": 0,
                "oldest_session": None,
                "newest_session": None
            }
        
        total_messages = sum(s["message_count"] for s in stats)
        avg_messages = total_messages / len(stats) if stats else 0
        
        # Parse dates for analysis
        dates = []
        for session in stats:
            if session["created_at"]:
                try:
                    dates.append(datetime.fromisoformat(session["created_at"]))
                except:
                    pass
        
        return {
            "total_sessions": len(stats),
            "total_messages": total_messages,
            "avg_messages_per_session": round(avg_messages, 2),
            "oldest_session": min(dates).isoformat() if dates else None,
            "newest_session": max(dates).isoformat() if dates else None,
            "sessions_by_date": self._group_sessions_by_date(stats)
        }
    
    def _group_sessions_by_date(self, stats: List[Dict]) -> Dict:
        """Group sessions by creation date"""
        grouped = {}
        for session in stats:
            if session["created_at"]:
                try:
                    date = datetime.fromisoformat(session["created_at"]).date().isoformat()
                    if date not in grouped:
                        grouped[date] = 0
                    grouped[date] += 1
                except:
                    pass
        return grouped
    
    def export_session_data(self, session_id: str, export_dir: str = "downloads") -> Optional[str]:
        """Export session data to a file"""
        from .chat_memory import get_history, get_session_stats
        
        os.makedirs(export_dir, exist_ok=True)
        
        # Get session data
        history = get_history(session_id)
        stats = get_session_stats(session_id)
        
        if not history and not stats:
            logger.warning(f"No data found for session {session_id}")
            return None
        
        # Create export data
        export_data = {
            "session_id": session_id,
            "exported_at": datetime.now().isoformat(),
            "session_stats": stats,
            "chat_history": history
        }
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_export_{session_id}_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)
        
        # Save export
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Session {session_id} exported to {filepath}")
        return filepath
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get a summary of a specific session"""
        from .chat_memory import get_session_stats, get_history
        
        stats = get_session_stats(session_id)
        history = get_history(session_id)
        
        if not stats:
            return None
        
        # Calculate session duration
        duration = None
        if stats["created_at"] and stats["last_activity"]:
            try:
                created = datetime.fromisoformat(stats["created_at"])
                last_activity = datetime.fromisoformat(stats["last_activity"])
                duration = (last_activity - created).total_seconds()
            except:
                pass
        
        return {
            "session_id": session_id,
            "created_at": stats["created_at"],
            "last_activity": stats["last_activity"],
            "duration_seconds": duration,
            "message_count": stats["message_count"],
            "user_messages": stats["user_messages"],
            "assistant_messages": stats["assistant_messages"],
            "messages": history
        }
    
    def update_cleanup_config(self, **kwargs):
        """Update cleanup configuration"""
        self.cleanup_config.update(kwargs)
        logger.info(f"Cleanup config updated: {self.cleanup_config}")

# Global session manager instance
session_manager = SessionManager() 