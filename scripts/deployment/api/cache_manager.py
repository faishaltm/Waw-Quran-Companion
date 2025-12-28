"""
Cache Manager for storing and retrieving JSON cache files
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class CacheManager:
    """Manages JSON cache for chapters, verses, sessions, conversations, and chats"""

    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            # Default to scripts/deployment/cache
            base_dir = Path(__file__).parent.parent
            cache_dir = base_dir / "cache"

        self.cache_dir = Path(cache_dir)
        self.chapters_dir = self.cache_dir / "chapters"
        self.verses_dir = self.cache_dir / "verses"
        self.sessions_dir = self.cache_dir / "sessions"
        self.conversations_dir = self.cache_dir / "conversations"
        self.chats_dir = self.cache_dir / "chats"
        self.summaries_dir = self.cache_dir / "summaries"  # Accumulated summaries

        # Create directories if they don't exist
        for directory in [self.chapters_dir, self.verses_dir, self.sessions_dir,
                          self.conversations_dir, self.chats_dir, self.summaries_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    # ===== Chapter Context Methods =====

    def get_chapter_context(self, surah_num: int) -> Optional[Dict[str, Any]]:
        """
        Get cached chapter context

        Args:
            surah_num: Surah number (1-114)

        Returns:
            Chapter context dict or None if not cached
        """
        path = self.chapters_dir / f"chapter_{surah_num}_context.json"

        print(f"  [DEBUG] Cache manager checking: {path}")
        print(f"  [DEBUG] Cache dir exists: {self.chapters_dir.exists()}")
        print(f"  [DEBUG] Cache file exists: {path.exists()}")

        if not path.exists():
            print(f"  [DEBUG] File not found, returning None")
            return None

        print(f"  [DEBUG] File found, size: {path.stat().st_size} bytes")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  [DEBUG] Read {len(content)} chars from file")

                # Parse JSON
                data = json.loads(content)
                print(f"  [DEBUG] JSON parsed successfully")
                print(f"  [DEBUG] Parsed JSON has {len(data)} top-level keys: {list(data.keys())}")

                # Add cache metadata
                data['_cached_at'] = path.stat().st_mtime

                return data

        except json.JSONDecodeError as e:
            print(f"  [ERROR] JSON parse failed: {e}")
            print(f"  [ERROR] First 200 chars: {content[:200] if content else 'empty'}")
            return None
        except Exception as e:
            print(f"  [ERROR] Failed to read cache: {type(e).__name__}: {e}")
            import traceback
            print(f"  [ERROR] Traceback: {traceback.format_exc()}")
            return None

    def save_chapter_context(self, surah_num: int, context: Dict[str, Any]) -> bool:
        """
        Save chapter context to cache

        Args:
            surah_num: Surah number
            context: Chapter context data

        Returns:
            True if saved successfully
        """
        path = self.chapters_dir / f"chapter_{surah_num}_context.json"

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(context, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving chapter {surah_num} cache: {e}")
            return False

    # ===== Verse Analysis Methods =====

    def get_verse_analysis(self, surah_num: int, verse_num: int) -> Optional[Dict[str, Any]]:
        """
        Get cached verse analysis

        Args:
            surah_num: Surah number
            verse_num: Verse number

        Returns:
            Verse analysis dict or None if not cached
        """
        path = self.verses_dir / f"verse_{surah_num}_{verse_num}_analysis.json"

        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_cached_at'] = path.stat().st_mtime
                data['from_cache'] = True
                return data
        except Exception as e:
            print(f"Error loading verse {surah_num}:{verse_num} cache: {e}")
            return None

    def save_verse_analysis(self, surah_num: int, verse_num: int, analysis: Dict[str, Any]) -> bool:
        """
        Save verse analysis to cache

        Args:
            surah_num: Surah number
            verse_num: Verse number
            analysis: Verse analysis data

        Returns:
            True if saved successfully
        """
        path = self.verses_dir / f"verse_{surah_num}_{verse_num}_analysis.json"

        try:
            # Add metadata
            analysis['_generated_at'] = datetime.now().isoformat()
            analysis['_verse_id'] = f"{surah_num}:{verse_num}"

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving verse {surah_num}:{verse_num} cache: {e}")
            return False

    # ===== Session Methods =====

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session state

        Args:
            session_id: Session UUID

        Returns:
            Session state dict or None if not found
        """
        path = self.sessions_dir / f"session_{session_id}.json"

        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def save_session(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save session state

        Args:
            session_id: Session UUID
            state: Session state data

        Returns:
            True if saved successfully
        """
        path = self.sessions_dir / f"session_{session_id}.json"

        try:
            # Add metadata
            state['_updated_at'] = datetime.now().isoformat()

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session (cleanup)

        Args:
            session_id: Session UUID

        Returns:
            True if deleted successfully
        """
        path = self.sessions_dir / f"session_{session_id}.json"

        try:
            if path.exists():
                path.unlink()
                print(f"Deleted session {session_id}")
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    # ===== Conversation Methods =====

    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation history for a session

        Args:
            session_id: Session UUID

        Returns:
            Conversation dict with messages array, or None if not found
        """
        path = self.conversations_dir / f"conv_{session_id}.json"

        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation {session_id}: {e}")
            return None

    def save_conversation(self, session_id: str, conversation: Dict[str, Any]) -> bool:
        """
        Save conversation to file

        Args:
            session_id: Session UUID
            conversation: Conversation dict with messages array

        Returns:
            True if saved successfully
        """
        path = self.conversations_dir / f"conv_{session_id}.json"

        try:
            conversation['_updated_at'] = datetime.now().isoformat()

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving conversation {session_id}: {e}")
            return False

    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete conversation file

        Args:
            session_id: Session UUID

        Returns:
            True if deleted successfully
        """
        path = self.conversations_dir / f"conv_{session_id}.json"

        try:
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting conversation {session_id}: {e}")
            return False

    # ===== Chat Cache Methods =====

    def save_chat(self, surah_num: int, verse_num: int, user_id: str, question: str, answer: str) -> bool:
        """
        Save a chat Q&A to cache

        Args:
            surah_num: Surah number
            verse_num: Current verse context
            user_id: Telegram user ID
            question: User's question
            answer: LLM's response

        Returns:
            True if saved successfully
        """
        import hashlib

        # Create hash from question for filename
        question_hash = hashlib.md5(question.encode()).hexdigest()[:12]
        filename = f"chat_{surah_num}_{verse_num}_{question_hash}.json"
        path = self.chats_dir / filename

        try:
            chat_data = {
                "surah": surah_num,
                "verse": verse_num,
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving chat cache: {e}")
            return False

    def get_all_chats(self, surah_num: int = None, verse_num: int = None) -> list:
        """
        Get all cached chats, optionally filtered by surah/verse

        Args:
            surah_num: Optional surah filter
            verse_num: Optional verse filter (requires surah_num)

        Returns:
            List of chat dicts
        """
        chats = []

        try:
            if surah_num and verse_num:
                pattern = f"chat_{surah_num}_{verse_num}_*.json"
            elif surah_num:
                pattern = f"chat_{surah_num}_*.json"
            else:
                pattern = "chat_*.json"

            for file in self.chats_dir.glob(pattern):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        chat = json.load(f)
                        chat['_filename'] = file.name
                        chats.append(chat)
                except Exception:
                    continue

            # Sort by timestamp
            chats.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        except Exception as e:
            print(f"Error loading chats: {e}")

        return chats

    def get_chat_count(self) -> int:
        """Get total number of cached chats"""
        return len(list(self.chats_dir.glob("chat_*.json")))

    # ===== Accumulated Summary Methods (for Ruku Sessions) =====

    def get_accumulated_summary(self, surah_num: int) -> Optional[Dict[str, Any]]:
        """
        Get accumulated summary for a surah (used for ruku-based sessions)

        Args:
            surah_num: Surah number (1-114)

        Returns:
            Accumulated summary dict or None if not found
        """
        path = self.summaries_dir / f"surah_{surah_num}_accumulated.json"

        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading accumulated summary for surah {surah_num}: {e}")
            return None

    def save_accumulated_summary(self, surah_num: int, summary: Dict[str, Any]) -> bool:
        """
        Save accumulated summary for a surah

        Args:
            surah_num: Surah number
            summary: Accumulated summary dict

        Returns:
            True if saved successfully
        """
        path = self.summaries_dir / f"surah_{surah_num}_accumulated.json"

        try:
            summary['_updated_at'] = datetime.now().isoformat()

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving accumulated summary for surah {surah_num}: {e}")
            return False

    def delete_accumulated_summary(self, surah_num: int) -> bool:
        """
        Delete accumulated summary for a surah (for fresh start)

        Args:
            surah_num: Surah number

        Returns:
            True if deleted successfully
        """
        path = self.summaries_dir / f"surah_{surah_num}_accumulated.json"

        try:
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting accumulated summary for surah {surah_num}: {e}")
            return False

    def get_all_accumulated_summaries(self) -> Dict[int, Dict]:
        """
        Get all accumulated summaries

        Returns:
            Dict mapping surah number to summary
        """
        summaries = {}

        try:
            for file in self.summaries_dir.glob("surah_*_accumulated.json"):
                try:
                    # Extract surah number from filename
                    surah_num = int(file.stem.split('_')[1])
                    with open(file, 'r', encoding='utf-8') as f:
                        summaries[surah_num] = json.load(f)
                except Exception:
                    continue
        except Exception as e:
            print(f"Error loading accumulated summaries: {e}")

        return summaries

    # ===== Delete Methods =====

    def delete_chapter_context(self, surah_num: int) -> bool:
        """
        Delete specific chapter context cache

        Args:
            surah_num: Surah number

        Returns:
            True if deleted successfully
        """
        path = self.chapters_dir / f"chapter_{surah_num}_context.json"
        try:
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting chapter {surah_num} cache: {e}")
            return False

    def delete_verse_analysis(self, surah_num: int, verse_num: int) -> bool:
        """
        Delete specific verse analysis cache

        Args:
            surah_num: Surah number
            verse_num: Verse number

        Returns:
            True if deleted successfully
        """
        path = self.verses_dir / f"verse_{surah_num}_{verse_num}_analysis.json"
        try:
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting verse {surah_num}:{verse_num} cache: {e}")
            return False

    def delete_surah_cache(self, surah_num: int) -> Dict[str, int]:
        """
        Delete all cache for a specific surah (chapter + all verses)

        Args:
            surah_num: Surah number

        Returns:
            Dict with counts of deleted items
        """
        deleted = {"chapter": 0, "verses": 0}

        # Delete chapter context
        if self.delete_chapter_context(surah_num):
            deleted["chapter"] = 1

        # Delete all verses for this surah
        for file in self.verses_dir.glob(f"verse_{surah_num}_*_analysis.json"):
            try:
                file.unlink()
                deleted["verses"] += 1
            except Exception:
                pass

        return deleted

    # ===== Utility Methods =====

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics

        Returns:
            Dict with counts of cached items
        """
        return {
            "chapters_cached": len(list(self.chapters_dir.glob("*.json"))),
            "verses_cached": len(list(self.verses_dir.glob("*.json"))),
            "active_sessions": len(list(self.sessions_dir.glob("*.json"))),
            "conversations": len(list(self.conversations_dir.glob("*.json"))),
            "chats_cached": len(list(self.chats_dir.glob("*.json"))),
            "accumulated_summaries": len(list(self.summaries_dir.glob("*.json")))
        }

    def clear_cache(self, cache_type: str = "all") -> bool:
        """
        Clear cache (use with caution)

        Args:
            cache_type: "chapters", "verses", "sessions", "conversations", "chats", "summaries", or "all"

        Returns:
            True if cleared successfully
        """
        try:
            if cache_type in ["chapters", "all"]:
                for file in self.chapters_dir.glob("*.json"):
                    file.unlink()
                print("Cleared chapters cache")

            if cache_type in ["verses", "all"]:
                for file in self.verses_dir.glob("*.json"):
                    file.unlink()
                print("Cleared verses cache")

            if cache_type in ["sessions", "all"]:
                for file in self.sessions_dir.glob("*.json"):
                    file.unlink()
                print("Cleared sessions cache")

            if cache_type in ["conversations", "all"]:
                for file in self.conversations_dir.glob("*.json"):
                    file.unlink()
                print("Cleared conversations cache")

            if cache_type in ["chats", "all"]:
                for file in self.chats_dir.glob("*.json"):
                    file.unlink()
                print("Cleared chats cache")

            if cache_type in ["summaries", "all"]:
                for file in self.summaries_dir.glob("*.json"):
                    file.unlink()
                print("Cleared accumulated summaries cache")

            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False


if __name__ == "__main__":
    # Test cache manager
    cache = CacheManager()

    print("Cache Stats:", cache.get_cache_stats())

    # Test chapter cache
    test_context = {
        "surah_name": "Al-Qalam",
        "main_themes": ["Patience", "Divine Justice"],
        "structure": {}
    }
    cache.save_chapter_context(68, test_context)

    loaded = cache.get_chapter_context(68)
    print("Loaded chapter:", loaded)

    print("\nCache Stats:", cache.get_cache_stats())
