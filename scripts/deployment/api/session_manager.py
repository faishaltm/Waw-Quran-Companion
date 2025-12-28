"""
Session Manager for tracking reading sessions and context windows
"""
import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cache_manager import CacheManager


class SessionManager:
    """Manages reading sessions and conversation state"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def create_session(
        self,
        surah_num: int,
        verse_range: List[int],
        user_id: Optional[str] = None
    ) -> str:
        """
        Create new reading session

        Args:
            surah_num: Surah number
            verse_range: List of verse numbers to read
            user_id: Optional user identifier (e.g., Telegram user_id)

        Returns:
            session_id (UUID string)
        """
        session_id = str(uuid.uuid4())

        state = {
            "session_id": session_id,
            "user_id": user_id,
            "surah": surah_num,
            "verse_range": verse_range,
            "created_at": datetime.now().isoformat(),
            "verses_analyzed": 0,
            "verses_analyzed_list": [],
            "total_tokens": 0,
            "conversation_id": None,
            "context_resets": 0,
            "last_activity": datetime.now().isoformat()
        }

        self.cache.save_session(session_id, state)
        print(f"Created session {session_id} for surah {surah_num}, verses {verse_range[0]}-{verse_range[-1]}")

        return session_id

    def get_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session state

        Args:
            session_id: Session UUID

        Returns:
            Session state dict

        Raises:
            ValueError: If session not found
        """
        state = self.cache.get_session(session_id)

        if state is None:
            raise ValueError(f"Session {session_id} not found")

        return state

    def add_verse(
        self,
        session_id: str,
        verse_num: int,
        from_cache: bool = False,
        tokens_used: int = 0,
        one_line_summary: str = ""
    ) -> None:
        """
        Update session after verse analysis

        Args:
            session_id: Session UUID
            verse_num: Verse number that was analyzed
            from_cache: Whether result was from cache
            tokens_used: Tokens consumed (0 if from cache)
            one_line_summary: Brief summary for memory
        """
        state = self.get_state(session_id)

        # Add verse to analyzed list
        state['verses_analyzed'] += 1
        state['verses_analyzed_list'].append({
            "verse": verse_num,
            "from_cache": from_cache,
            "timestamp": datetime.now().isoformat(),
            "one_line_summary": one_line_summary
        })

        # Update token count (only for non-cached)
        if not from_cache:
            state['total_tokens'] += tokens_used

        # Update last activity
        state['last_activity'] = datetime.now().isoformat()

        self.cache.save_session(session_id, state)

    def set_conversation_id(self, session_id: str, conversation_id: str) -> None:
        """
        Set OpenAI conversation ID for session

        Args:
            session_id: Session UUID
            conversation_id: OpenAI conversation/response ID
        """
        state = self.get_state(session_id)
        state['conversation_id'] = conversation_id
        self.cache.save_session(session_id, state)

    def reset_context_window(self, session_id: str, new_conversation_id: str) -> None:
        """
        Reset context window after threshold exceeded

        Args:
            session_id: Session UUID
            new_conversation_id: New OpenAI conversation ID
        """
        state = self.get_state(session_id)

        # Reset token counter
        state['total_tokens'] = 0

        # Set new conversation ID
        state['conversation_id'] = new_conversation_id

        # Increment reset counter
        state['context_resets'] += 1

        # Log reset
        print(f"Session {session_id}: Context window reset #{state['context_resets']}")

        self.cache.save_session(session_id, state)

    def get_next_verse(self, session_id: str) -> Optional[int]:
        """
        Get next verse to analyze in session

        Args:
            session_id: Session UUID

        Returns:
            Next verse number or None if complete
        """
        state = self.get_state(session_id)

        verses_done = len(state['verses_analyzed_list'])
        verse_range = state['verse_range']

        if verses_done >= len(verse_range):
            return None  # Session complete

        return verse_range[verses_done]

    def is_complete(self, session_id: str) -> bool:
        """
        Check if session is complete

        Args:
            session_id: Session UUID

        Returns:
            True if all verses in range have been analyzed
        """
        state = self.get_state(session_id)
        return len(state['verses_analyzed_list']) >= len(state['verse_range'])

    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """
        Get session progress

        Args:
            session_id: Session UUID

        Returns:
            Progress dict with stats
        """
        state = self.get_state(session_id)

        verses_done = len(state['verses_analyzed_list'])
        total_verses = len(state['verse_range'])

        progress_pct = (verses_done / total_verses * 100) if total_verses > 0 else 0

        return {
            "session_id": session_id,
            "verses_analyzed": verses_done,
            "total_verses": total_verses,
            "progress_percentage": round(progress_pct, 1),
            "total_tokens_used": state['total_tokens'],
            "context_resets": state['context_resets'],
            "complete": verses_done >= total_verses,
            "next_verse": self.get_next_verse(session_id)
        }

    def get_previous_verses_summary(
        self,
        session_id: str,
        last_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get summary of last N verses for context

        Args:
            session_id: Session UUID
            last_n: Number of recent verses to include

        Returns:
            List of verse summaries
        """
        state = self.get_state(session_id)
        verses_list = state['verses_analyzed_list']

        # Get last N verses
        recent_verses = verses_list[-last_n:] if len(verses_list) > last_n else verses_list

        return recent_verses

    def get_all_verses_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get compact summary of ALL verses for context reset

        Args:
            session_id: Session UUID

        Returns:
            Compact summary dict
        """
        state = self.get_state(session_id)
        verses_list = state['verses_analyzed_list']

        return {
            "verses_covered": [v['verse'] for v in verses_list],
            "count": len(verses_list),
            "summaries": [
                {"verse": v['verse'], "summary": v.get('one_line_summary', '')}
                for v in verses_list
            ]
        }

    def cleanup_old_sessions(self, days_old: int = 7) -> int:
        """
        Cleanup sessions older than N days

        Args:
            days_old: Delete sessions older than this many days

        Returns:
            Number of sessions deleted
        """
        from pathlib import Path
        import time

        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0

        for session_file in self.cache.sessions_dir.glob("session_*.json"):
            if session_file.stat().st_mtime < cutoff_time:
                session_id = session_file.stem.replace("session_", "")
                if self.cache.delete_session(session_id):
                    deleted_count += 1

        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old sessions")

        return deleted_count


if __name__ == "__main__":
    # Test session manager
    from cache_manager import CacheManager

    cache = CacheManager()
    manager = SessionManager(cache)

    # Create test session
    session_id = manager.create_session(68, list(range(1, 11)))
    print(f"Session ID: {session_id}")

    # Get state
    state = manager.get_state(session_id)
    print(f"State: {state}")

    # Add verse
    manager.add_verse(session_id, 1, from_cache=False, tokens_used=1500, one_line_summary="Nun and the pen")
    manager.add_verse(session_id, 2, from_cache=True, tokens_used=0, one_line_summary="You are not insane")

    # Get progress
    progress = manager.get_progress(session_id)
    print(f"Progress: {progress}")

    # Get next verse
    next_verse = manager.get_next_verse(session_id)
    print(f"Next verse: {next_verse}")
