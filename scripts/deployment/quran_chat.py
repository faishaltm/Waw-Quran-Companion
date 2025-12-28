"""
Quran Analysis Chat Session
============================

Interactive session-based Quran verse analysis with REAL conversation history.
Works like chatting with an LLM - with persistent memory and context.

Commands:
    68          - Start session with Surah 68
    68:1        - Analyze specific verse
    68:1-5      - Analyze verse range
    next/n      - Continue to next verse
    prev/p      - Go back to previous verse
    regen       - Regenerate current verse (force fresh)
    status      - Show current session status
    (free text) - Chat freely about the verses

Cache Commands:
    clear all      - Clear ALL cache
    clear chapter  - Clear chapter context for current surah
    clear verse N  - Clear cache for verse N
    clear surah    - Clear all cache for current surah
    clear conv     - Clear current conversation
    clear sessions - Clear all sessions

Usage:
    python quran_chat.py           # Normal start
    python quran_chat.py --fresh   # Start with empty cache
"""

import sys
import os
import json
import io
import contextlib
from pathlib import Path
from openai import OpenAI

# Add paths for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "tools"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "loaders"))
sys.path.insert(0, str(SCRIPT_DIR))

# Import deployment components
from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.chapter_context_generator import ChapterContextGenerator
from api.conversation_manager import ConversationManager
from api.data_loader import QuranDataLoader
from config.settings import OPENAI_API_KEY


def safe_print(text):
    """Print text safely, handling Unicode errors for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


class QuranChatSession:
    """Interactive Quran analysis session with real conversation memory"""

    def __init__(self):
        """Initialize the chat session"""
        print("Loading Quran data...")

        # Check API key
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env file")

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

        # Initialize components (suppress verbose output)
        with contextlib.redirect_stdout(io.StringIO()):
            self.cache_manager = CacheManager()
            self.session_manager = SessionManager(self.cache_manager)
            self.chapter_generator = ChapterContextGenerator(
                self.cache_manager,
                self.openai_client
            )
            self.data_loader = QuranDataLoader()

        # Initialize ConversationManager
        self.conv_manager = ConversationManager(
            self.cache_manager,
            self.session_manager,
            self.openai_client,
            self.data_loader
        )

        # Session state
        self.current_surah = None
        self.current_verse = None
        self.session_id = None
        self.chapter_info = None
        self.chapter_context = None

        print("Ready.\n")

    def start_surah(self, surah_num: int):
        """Start a new session with a surah"""
        if surah_num < 1 or surah_num > 114:
            print("Surah must be between 1-114")
            return False

        # Get chapter info
        self.chapter_info = self.data_loader.get_chapter_metadata(surah_num)
        if not self.chapter_info:
            print(f"Surah {surah_num} not found")
            return False

        self.current_surah = surah_num
        self.current_verse = 0  # Will be 1 after first "next"

        # Create new session
        verse_count = self.chapter_info.get('verses_count', 0)
        verse_list = list(range(1, verse_count + 1))
        self.session_id = self.session_manager.create_session(surah_num, verse_list)

        # Print chapter header
        print(f"\n=== Surah {surah_num}: {self.chapter_info.get('name_arabic', '')} ===")
        print(f"Verses: {verse_count} | {self.chapter_info.get('revelation_place', '')}")
        print()

        # Generate chapter context
        print("Generating chapter context...")
        with contextlib.redirect_stdout(io.StringIO()):
            self.chapter_context = self.chapter_generator.get_or_generate(surah_num)
        print("Chapter context ready.")

        # Initialize conversation with balaghah guide + chapter context
        print("Initializing conversation...")
        self.conv_manager.start_conversation(
            self.session_id,
            surah_num,
            self.chapter_context
        )
        print("Conversation ready.")
        print()

        # Show introduction preview if available
        intro = self.chapter_context.get('introduction', '')
        if intro:
            intro_preview = intro[:500] + "..." if len(intro) > 500 else intro
            print("Introduction:")
            safe_print(intro_preview)
            print()

        # Show main themes if available
        themes = self.chapter_context.get('main_themes', [])
        if themes:
            print("Main Themes:")
            for theme in themes[:5]:
                print(f"  - {theme}")
            print()

        print("Type 'next' or 'n' to start analyzing verses.")
        print("Type a verse number (e.g., '5') to jump to specific verse.")
        print("Or type any question to chat about the surah.")
        print()

        return True

    def analyze_verse(self, verse_num: int, force_regenerate: bool = False):
        """Analyze a specific verse using conversation"""
        if not self.current_surah:
            print("No surah selected. Start with a surah number (e.g., '68')")
            return

        if not self.session_id:
            print("No session active. Start with a surah number first.")
            return

        # Validate verse number
        verse_count = self.chapter_info.get('verses_count', 0)
        if verse_num < 1 or verse_num > verse_count:
            print(f"Verse must be between 1-{verse_count}")
            return

        print(f"\n--- Ayat {self.current_surah}:{verse_num} ---\n")

        try:
            # Use ConversationManager to analyze
            result = self.conv_manager.analyze_verse(
                self.session_id,
                self.current_surah,
                verse_num,
                use_cache=not force_regenerate
            )

            # Update current verse
            self.current_verse = verse_num

            # Show status
            if result.get('from_cache'):
                print("\n[FROM CACHE]")
            else:
                tokens = result.get('tokens_used', 0)
                print(f"\n[Tokens: ~{tokens:,}]")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    def handle_free_chat(self, user_message: str):
        """Handle free-form chat messages"""
        if not self.session_id:
            print("No session active. Start with a surah number first (e.g., '68')")
            return

        print()  # New line before response

        try:
            response = self.conv_manager.send_message(self.session_id, user_message)
            # Response is already printed by streaming in send_message
        except Exception as e:
            print(f"Error: {e}")

    def next_verse(self):
        """Move to next verse"""
        if not self.current_surah:
            print("No surah selected. Start with a surah number (e.g., '68')")
            return

        next_v = self.current_verse + 1
        verse_count = self.chapter_info.get('verses_count', 0)

        if next_v > verse_count:
            print(f"End of surah reached (total {verse_count} verses)")
            return

        self.analyze_verse(next_v)

    def prev_verse(self):
        """Move to previous verse"""
        if not self.current_surah:
            print("No surah selected.")
            return

        if self.current_verse <= 1:
            print("Already at first verse")
            return

        self.analyze_verse(self.current_verse - 1)

    def show_status(self):
        """Show current session status"""
        print("\n=== Session Status ===")
        if self.current_surah:
            print(f"Surah: {self.current_surah}")
            print(f"Current verse: {self.current_verse}")

            # Get conversation stats
            if self.session_id:
                conv_stats = self.conv_manager.get_conversation_stats(self.session_id)
                if 'error' not in conv_stats:
                    print(f"\nConversation:")
                    print(f"  Messages: {conv_stats['messages_count']}")
                    print(f"  Tokens: ~{conv_stats['estimated_tokens']:,} / {conv_stats['token_limit']:,} ({conv_stats['usage_percent']}%)")
                    print(f"  Summarize count: {conv_stats['summarize_count']}")
        else:
            print("No surah selected")

        # Show cache stats
        stats = self.cache_manager.get_cache_stats()
        print(f"\nCache: {stats['chapters_cached']} chapters, {stats['verses_cached']} verses, {stats['conversations']} conversations")
        print()

    def clear_cache(self, cache_type: str = "all", verse_num: int = None):
        """
        Clear cache with various options

        Args:
            cache_type: "all", "chapter", "verse", "surah", "sessions", "conv"
            verse_num: Verse number (only for cache_type="verse")
        """
        if cache_type == "all":
            self.cache_manager.clear_cache("all")
            print("Cleared ALL cache")

        elif cache_type == "chapter":
            if not self.current_surah:
                print("No surah selected")
                return
            if self.cache_manager.delete_chapter_context(self.current_surah):
                print(f"Cleared chapter context for surah {self.current_surah}")
            else:
                print(f"No chapter context cache for surah {self.current_surah}")

        elif cache_type == "verse":
            if not self.current_surah:
                print("No surah selected")
                return
            v = verse_num if verse_num else self.current_verse
            if v and self.cache_manager.delete_verse_analysis(self.current_surah, v):
                print(f"Cleared verse cache for {self.current_surah}:{v}")
            else:
                print(f"No verse cache for {self.current_surah}:{v}")

        elif cache_type == "surah":
            if not self.current_surah:
                print("No surah selected")
                return
            result = self.cache_manager.delete_surah_cache(self.current_surah)
            print(f"Cleared surah {self.current_surah}: {result['chapter']} chapter, {result['verses']} verses")

        elif cache_type == "conv":
            if not self.session_id:
                print("No active conversation")
                return
            if self.cache_manager.delete_conversation(self.session_id):
                print("Cleared current conversation")
                # Reinitialize conversation
                if self.current_surah and self.chapter_context:
                    self.conv_manager.start_conversation(
                        self.session_id,
                        self.current_surah,
                        self.chapter_context
                    )
                    print("Started fresh conversation")
            else:
                print("No conversation to clear")

        elif cache_type == "sessions":
            self.cache_manager.clear_cache("sessions")
            print("Cleared all sessions")

        elif cache_type == "conversations":
            self.cache_manager.clear_cache("conversations")
            print("Cleared all conversations")

        else:
            print(f"Unknown cache type: {cache_type}")
            print("Options: all, chapter, verse, surah, conv, sessions, conversations")

    def regen_verse(self):
        """Regenerate current verse (force fresh, ignore cache)"""
        if not self.current_surah or not self.current_verse:
            print("No verse selected. Navigate to a verse first.")
            return

        # Delete existing cache first
        self.cache_manager.delete_verse_analysis(self.current_surah, self.current_verse)
        print(f"Regenerating {self.current_surah}:{self.current_verse}...")

        # Analyze with force_regenerate
        self.analyze_verse(self.current_verse, force_regenerate=True)

    def parse_input(self, user_input: str) -> tuple:
        """
        Parse user input and return (command, args)

        Returns:
            tuple: (command_type, args)
        """
        stripped = user_input.strip()
        lower_input = stripped.lower()

        if not stripped:
            return ('empty', None)

        if lower_input in ['quit', 'exit', 'q']:
            return ('quit', None)

        if lower_input in ['next', 'n']:
            return ('next', None)

        if lower_input in ['prev', 'p', 'back']:
            return ('prev', None)

        if lower_input in ['status', 's']:
            return ('status', None)

        if lower_input in ['regen', 'refresh', 'regenerate']:
            return ('regen', None)

        # Handle clear commands
        if lower_input.startswith('clear'):
            parts = lower_input.split()
            if len(parts) == 1:
                return ('clear_help', None)
            elif parts[1] == 'all':
                return ('clear', 'all')
            elif parts[1] == 'chapter':
                return ('clear', 'chapter')
            elif parts[1] == 'surah':
                return ('clear', 'surah')
            elif parts[1] == 'sessions':
                return ('clear', 'sessions')
            elif parts[1] in ['conv', 'conversation']:
                return ('clear', 'conv')
            elif parts[1] == 'conversations':
                return ('clear', 'conversations')
            elif parts[1] == 'verse':
                if len(parts) >= 3:
                    try:
                        verse_num = int(parts[2])
                        return ('clear_verse', verse_num)
                    except ValueError:
                        return ('clear', 'verse')
                return ('clear', 'verse')
            else:
                return ('clear_help', None)

        if lower_input in ['help', 'h', '?']:
            return ('help', None)

        # Check for surah:verse format
        if ':' in lower_input:
            parts = lower_input.split(':')
            try:
                surah = int(parts[0])
                verse_part = parts[1]

                if '-' in verse_part:
                    verse_parts = verse_part.split('-')
                    start = int(verse_parts[0])
                    end = int(verse_parts[1])
                    return ('range', (surah, start, end))
                else:
                    verse = int(verse_part)
                    return ('verse', (surah, verse))
            except ValueError:
                # Not a valid surah:verse format, treat as chat
                return ('chat', stripped)

        # Check for just a number
        try:
            num = int(lower_input)
            # If current surah is set and number is small, it's probably a verse
            if self.current_surah and num <= 300:
                return ('verse_only', num)
            else:
                # Otherwise it's a surah
                return ('surah', num)
        except ValueError:
            pass

        # Default: treat as free chat
        return ('chat', stripped)

    def run(self):
        """Main interactive loop"""
        print("=" * 60)
        print("Quran Analysis Chat (with Conversation Memory)")
        print("=" * 60)
        print()
        print("Commands:")
        print("  68        - Start with Surah 68")
        print("  68:1      - Go to specific verse")
        print("  68:1-5    - Analyze range")
        print("  next/n    - Next verse")
        print("  prev/p    - Previous verse")
        print("  regen     - Regenerate current verse")
        print("  status    - Show session status")
        print("  clear     - Cache management")
        print("  help      - Show this help")
        print("  quit      - Exit")
        print()
        print("Or just type any question to chat!")
        print()

        while True:
            try:
                # Show prompt with current position
                if self.current_surah:
                    prompt = f"[{self.current_surah}:{self.current_verse}] > "
                else:
                    prompt = "> "

                user_input = input(prompt)
                cmd_type, args = self.parse_input(user_input)

                if cmd_type == 'quit':
                    print("Goodbye!")
                    break

                elif cmd_type == 'empty':
                    continue

                elif cmd_type == 'help':
                    print("\nCommands:")
                    print("  <number>  - Start surah or go to verse")
                    print("  X:Y       - Go to surah X verse Y")
                    print("  X:Y-Z     - Analyze verses Y to Z")
                    print("  next/n    - Next verse")
                    print("  prev/p    - Previous verse")
                    print("  regen     - Regenerate current verse")
                    print("  status    - Show session status")
                    print("  clear     - Cache management")
                    print("  quit      - Exit")
                    print("\nOr type any question to chat about the verses!")
                    print()

                elif cmd_type == 'chat':
                    self.handle_free_chat(args)

                elif cmd_type == 'regen':
                    self.regen_verse()

                elif cmd_type == 'clear':
                    self.clear_cache(args)

                elif cmd_type == 'clear_verse':
                    self.clear_cache('verse', args)

                elif cmd_type == 'clear_help':
                    print("\nCache Commands:")
                    print("  clear all           - Clear ALL cache")
                    print("  clear chapter       - Clear chapter context")
                    print("  clear verse         - Clear current verse cache")
                    print("  clear verse N       - Clear verse N cache")
                    print("  clear surah         - Clear all cache for surah")
                    print("  clear conv          - Clear & restart conversation")
                    print("  clear conversations - Clear all conversations")
                    print("  clear sessions      - Clear all sessions")
                    print()

                elif cmd_type == 'surah':
                    self.start_surah(args)

                elif cmd_type == 'verse':
                    surah, verse = args
                    if surah != self.current_surah:
                        self.start_surah(surah)
                    self.analyze_verse(verse)

                elif cmd_type == 'verse_only':
                    self.analyze_verse(args)

                elif cmd_type == 'range':
                    surah, start, end = args
                    if surah != self.current_surah:
                        self.start_surah(surah)
                    for v in range(start, end + 1):
                        self.analyze_verse(v)

                elif cmd_type == 'next':
                    self.next_verse()

                elif cmd_type == 'prev':
                    self.prev_verse()

                elif cmd_type == 'status':
                    self.show_status()

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type 'help' for available commands, or just type to chat")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Quran Analysis Chat")
    parser.add_argument('--fresh', action='store_true',
                        help='Start with empty cache (clear all)')
    parser.add_argument('--clear-chapters', action='store_true',
                        help='Clear chapter context cache on start')
    parser.add_argument('--clear-verses', action='store_true',
                        help='Clear verse analysis cache on start')
    parser.add_argument('--clear-conv', action='store_true',
                        help='Clear all conversations on start')
    args = parser.parse_args()

    try:
        session = QuranChatSession()

        # Handle cache clearing flags
        if args.fresh:
            print("--fresh: Clearing ALL cache...")
            session.cache_manager.clear_cache("all")
            print()
        else:
            if args.clear_chapters:
                print("--clear-chapters: Clearing chapter cache...")
                session.cache_manager.clear_cache("chapters")
            if args.clear_verses:
                print("--clear-verses: Clearing verse cache...")
                session.cache_manager.clear_cache("verses")
            if args.clear_conv:
                print("--clear-conv: Clearing conversations...")
                session.cache_manager.clear_cache("conversations")
            if args.clear_chapters or args.clear_verses or args.clear_conv:
                print()

        session.run()
    except Exception as e:
        print(f"Failed to start: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
