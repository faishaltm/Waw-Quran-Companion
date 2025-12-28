"""
Verse Analyzer with Intelligent Memory Management
Handles verse-by-verse analysis with context window management
"""
import json
import sys
from typing import Dict, Any, Optional, List
from openai import OpenAI
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.data_loader import QuranDataLoader
from config.settings import (
    load_prompt,
    get_balaghah_guide_path,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    CONTEXT_WINDOW_THRESHOLD,
    RECENT_VERSES_MEMORY
)


class VerseAnalyzer:
    """
    Analyzes verses with intelligent memory management
    Handles: first verse, continuation, and context resets
    """

    def __init__(
        self,
        cache_manager: CacheManager,
        session_manager: SessionManager,
        openai_client: OpenAI
    ):
        """
        Initialize analyzer

        Args:
            cache_manager: Cache manager instance
            session_manager: Session manager instance
            openai_client: OpenAI client instance
        """
        self.cache = cache_manager
        self.session = session_manager
        self.client = openai_client
        self.loader = QuranDataLoader()

        # Load balaghah guide once (reused throughout)
        guide_path = get_balaghah_guide_path()
        with open(guide_path, 'r', encoding='utf-8') as f:
            self.balaghah_guide = f.read()

        # Initialized silently

    def _stream_openai_response(
        self,
        messages: List[Dict[str, str]],
        show_streaming: bool = True
    ) -> tuple[str, int]:
        """
        Stream OpenAI response with real-time display

        Args:
            messages: List of messages for OpenAI
            show_streaming: Whether to print streaming output

        Returns:
            tuple: (full_text, tokens_used)
        """
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
                stream=True,
                stream_options={"include_usage": True}
            )

            full_text = ""
            tokens_used = 0

            for chunk in response:
                # Extract content from delta (some chunks may have empty choices)
                if not chunk.choices:
                    # Handle final chunk with usage data but no choices
                    if hasattr(chunk, "usage") and chunk.usage is not None:
                        tokens_used = chunk.usage.total_tokens
                    continue

                content = chunk.choices[0].delta.content

                if content is not None:
                    if show_streaming:
                        # Safe print for Windows console (handle Arabic/Unicode text)
                        try:
                            print(content, end="", flush=True)
                        except UnicodeEncodeError:
                            # Fallback: replace unencodable chars with ?
                            safe_content = content.encode('ascii', 'replace').decode('ascii')
                            print(safe_content, end="", flush=True)
                    full_text += content

                # Extract token usage from final chunk
                if hasattr(chunk, "usage") and chunk.usage is not None:
                    tokens_used = chunk.usage.total_tokens

            if show_streaming:
                print()  # New line after streaming

            return full_text, tokens_used

        except Exception as e:
            print(f"\nError during OpenAI streaming: {e}")
            raise

    def analyze_verse(
        self,
        surah_num: int,
        verse_num: int,
        session_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze single verse with intelligent memory management

        Args:
            surah_num: Surah number
            verse_num: Verse number
            session_id: Session ID
            force_regenerate: Force regeneration even if cached

        Returns:
            Verse analysis dict
        """
        # Check cache first
        if not force_regenerate:
            cached = self.cache.get_verse_analysis(surah_num, verse_num)
            if cached:
                # Using cached analysis
                # Update session (for progress tracking)
                self.session.add_verse(
                    session_id,
                    verse_num,
                    from_cache=True,
                    tokens_used=0,
                    one_line_summary=cached.get('one_line_summary', '')
                )
                return cached

        # Generate new analysis
        # Generating analysis

        # Get session state
        state = self.session.get_state(session_id)

        # Load verse data
        verse_data = self.loader.get_verse_full_data(surah_num, verse_num)

        # Load chapter context (should be cached already)
        chapter_context = self.cache.get_chapter_context(surah_num)
        if not chapter_context:
            raise ValueError(f"Chapter context for surah {surah_num} not found. Generate it first.")

        # Determine analysis mode
        if state['verses_analyzed'] == 0:
            # FIRST VERSE: Include balaghah guide
            result = self._analyze_first_verse(
                surah_num, verse_num, verse_data, chapter_context, state
            )
        elif state['total_tokens'] > CONTEXT_WINDOW_THRESHOLD:
            # CONTEXT RESET: Re-inject guide + summary of previous verses
            result = self._analyze_with_reset(
                surah_num, verse_num, verse_data, chapter_context, state
            )
        else:
            # CONTINUATION: Reuse guide from memory
            result = self._analyze_continuation(
                surah_num, verse_num, verse_data, chapter_context, state
            )

        # Cache result
        self.cache.save_verse_analysis(surah_num, verse_num, result)

        # Update session
        self.session.add_verse(
            session_id,
            verse_num,
            from_cache=False,
            tokens_used=result['tokens_used'],
            one_line_summary=result.get('one_line_summary', '')
        )

        return result

    def _analyze_first_verse(
        self,
        surah_num: int,
        verse_num: int,
        verse_data: Dict,
        chapter_context: Dict,
        state: Dict
    ) -> Dict[str, Any]:
        """
        Analyze first verse in session: Include full balaghah guide

        Args:
            surah_num: Surah number
            verse_num: Verse number
            verse_data: Complete verse data
            chapter_context: Chapter context
            state: Session state

        Returns:
            Analysis result dict
        """
        # FIRST VERSE mode

        # Load prompt
        system_prompt = load_prompt("verse_analysis_initial.txt")

        # Inject balaghah guide into prompt
        system_prompt = system_prompt.replace("{BALAGHAH_GUIDE}", self.balaghah_guide)

        # Prepare user message
        user_message = {
            "surah": surah_num,
            "verse": verse_num,
            "chapter_context": chapter_context,
            "verse_data": verse_data,
            "instruction": "Jelaskan ayat ini dalam Bahasa Indonesia untuk pembaca umum. Sertakan analisis balaghah jika ada."
        }

        # Call OpenAI with streaming
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_message, ensure_ascii=False)}
            ]

            explanation, tokens_used = self._stream_openai_response(messages, show_streaming=True)
            print()  # New line after streaming

            # Extract one-line summary (first line or first sentence)
            one_line = explanation.split('\n')[0][:100] if explanation else ""

            result = {
                "surah": surah_num,
                "verse": verse_num,
                "explanation": explanation,
                "tokens_used": tokens_used,
                "has_balaghah_guide": True,
                "context_reset": False,
                "mode": "first_verse",
                "one_line_summary": one_line,
                "_model": OPENAI_MODEL
            }

            return result

        except Exception as e:
            print(f"Error analyzing first verse {surah_num}:{verse_num}: {e}")
            raise

    def _analyze_continuation(
        self,
        surah_num: int,
        verse_num: int,
        verse_data: Dict,
        chapter_context: Dict,
        state: Dict
    ) -> Dict[str, Any]:
        """
        Analyze continuation verse: Reuse balaghah guide from conversation memory

        Args:
            surah_num: Surah number
            verse_num: Verse number
            verse_data: Complete verse data
            chapter_context: Chapter context
            state: Session state

        Returns:
            Analysis result dict
        """
        # CONTINUATION mode

        # Get previous verses summary
        previous_summary = self._format_previous_verses_summary(
            self.session.get_previous_verses_summary(state['session_id'], RECENT_VERSES_MEMORY)
        )

        # Load prompt
        system_prompt = load_prompt("verse_analysis_continue.txt")

        # Inject balaghah guide and previous summary
        system_prompt = system_prompt.replace("{BALAGHAH_GUIDE}", self.balaghah_guide)
        system_prompt = system_prompt.replace("{previous_verses_summary}", previous_summary)

        user_data = {
            "verse": verse_num,
            "current_verse_data": verse_data,
            "instruction": f"Lanjutkan penjelasan untuk ayat {verse_num}. Hubungkan dengan ayat sebelumnya jika relevan."
        }

        # Note: In a real implementation, we would continue the conversation
        # For now, we'll send a new message (simplified)
        # In production, you'd maintain conversation history

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_data, ensure_ascii=False)}
            ]

            explanation, tokens_used = self._stream_openai_response(messages, show_streaming=True)
            print()  # New line after streaming

            one_line = explanation.split('\n')[0][:100] if explanation else ""

            result = {
                "surah": surah_num,
                "verse": verse_num,
                "explanation": explanation,
                "tokens_used": tokens_used,
                "has_balaghah_guide": True,  # Now included in all modes
                "context_reset": False,
                "mode": "continuation",
                "one_line_summary": one_line,
                "_model": OPENAI_MODEL
            }

            return result

        except Exception as e:
            print(f"Error analyzing continuation verse {surah_num}:{verse_num}: {e}")
            raise

    def _analyze_with_reset(
        self,
        surah_num: int,
        verse_num: int,
        verse_data: Dict,
        chapter_context: Dict,
        state: Dict
    ) -> Dict[str, Any]:
        """
        Analyze with context reset: Re-inject guide + summary of all previous verses

        Args:
            surah_num: Surah number
            verse_num: Verse number
            verse_data: Complete verse data
            chapter_context: Chapter context
            state: Session state

        Returns:
            Analysis result dict
        """
        # CONTEXT RESET mode

        # Get ALL previous verses summary (compact format)
        all_previous = self.session.get_all_verses_summary(state['session_id'])

        # Load prompt
        system_prompt = load_prompt("verse_analysis_reset.txt")

        # Inject balaghah guide
        system_prompt = system_prompt.replace("{BALAGHAH_GUIDE}", self.balaghah_guide)

        # Inject previous verses reference
        previous_ref = json.dumps(all_previous, ensure_ascii=False)
        system_prompt = system_prompt.replace("{previous_verses_reference}", previous_ref)

        # Prepare user message
        user_data = {
            "notice": f"Context window penuh setelah {state['verses_analyzed']} ayat. Memulai fresh conversation.",
            "current_verse": verse_num,
            "verse_data": verse_data,
            "instruction": f"Jelaskan ayat {verse_num}. Ayat sebelumnya hanya sebagai referensi."
        }

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_data, ensure_ascii=False)}
            ]

            explanation, tokens_used = self._stream_openai_response(messages, show_streaming=True)
            print()  # New line after streaming

            one_line = explanation.split('\n')[0][:100] if explanation else ""

            result = {
                "surah": surah_num,
                "verse": verse_num,
                "explanation": explanation,
                "tokens_used": tokens_used,
                "has_balaghah_guide": True,  # Re-injected
                "context_reset": True,
                "mode": "context_reset",
                "one_line_summary": one_line,
                "_model": OPENAI_MODEL,
                "_reset_number": state['context_resets'] + 1
            }

            # Reset session context window
            self.session.reset_context_window(state['session_id'], "reset")

            return result

        except Exception as e:
            print(f"Error analyzing verse with reset {surah_num}:{verse_num}: {e}")
            raise

    def _format_previous_verses_summary(self, verses_list: List[Dict]) -> str:
        """
        Format previous verses summary for continuation prompt

        Args:
            verses_list: List of previous verse dicts

        Returns:
            Formatted summary string
        """
        if not verses_list:
            return "Ini adalah ayat pertama dalam session ini."

        summaries = []
        for v in verses_list:
            verse_num = v['verse']
            summary = v.get('one_line_summary', 'N/A')
            summaries.append(f"Ayat {verse_num}: {summary}")

        return "\n".join(summaries)


if __name__ == "__main__":
    # Test verse analyzer
    import os
    from cache_manager import CacheManager
    from session_manager import SessionManager

    # Initialize
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        exit(1)

    client = OpenAI(api_key=api_key)
    cache = CacheManager()
    session_mgr = SessionManager(cache)
    analyzer = VerseAnalyzer(cache, session_mgr, client)

    # Create test session
    session_id = session_mgr.create_session(68, list(range(1, 6)))
    print(f"Created session: {session_id}")

    # Analyze first verse
    print("\n=== Analyzing verse 68:1 (first) ===")
    result1 = analyzer.analyze_verse(68, 1, session_id)
    print(f"Mode: {result1['mode']}")
    print(f"Tokens: {result1['tokens_used']}")
    print(f"Explanation (first 200 chars): {result1['explanation'][:200]}...")

    # Analyze second verse
    print("\n=== Analyzing verse 68:2 (continuation) ===")
    result2 = analyzer.analyze_verse(68, 2, session_id)
    print(f"Mode: {result2['mode']}")
    print(f"Tokens: {result2['tokens_used']}")
