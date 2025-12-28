"""
Local Testing Script for Verse Analysis System
==============================================

This script mimics the full deployment flow locally:
1. Takes verse input (e.g., "68:1-10")
2. Generates chapter context (cached)
3. Analyzes verses one by one with OpenAI
4. Shows the full flow before Telegram deployment

Usage:
    python test_verse_analysis_local.py
    Then enter: 68:1-10
"""

import sys
import os
from pathlib import Path
import json
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.chapter_context_generator import ChapterContextGenerator
from api.verse_analyzer import VerseAnalyzer
from config.settings import OPENAI_API_KEY


def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "=" * 80)
    if title:
        print(f" {title}")
        print("=" * 80)
    print()


def safe_print(text):
    """Print text safely, handling Unicode errors for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace unencodable characters with ?
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


def print_section(title, content, max_length=500):
    """Print a section with title and content"""
    print(f"\n--- {title} ---")
    if len(content) > max_length:
        safe_print(content[:max_length] + "...")
        print(f"(Total length: {len(content)} characters)")
    else:
        safe_print(content)


def parse_verse_range(verse_range_str):
    """
    Parse verse range string like '68:1-10' or '2:255'

    Returns:
        tuple: (surah_num, start_verse, end_verse)
    """
    try:
        # Split by colon
        parts = verse_range_str.split(":")
        if len(parts) != 2:
            raise ValueError("Format must be surah:verse or surah:verse1-verse2")

        surah_num = int(parts[0])

        # Check if it's a range or single verse
        if "-" in parts[1]:
            verse_parts = parts[1].split("-")
            start_verse = int(verse_parts[0])
            end_verse = int(verse_parts[1])
        else:
            start_verse = int(parts[1])
            end_verse = start_verse

        return surah_num, start_verse, end_verse

    except Exception as e:
        raise ValueError(f"Invalid verse range format: {verse_range_str}. Use format like '68:1-10' or '2:255'")


def main():
    """Main testing function"""

    # Check for command line argument
    if len(sys.argv) < 2:
        print("Usage: python test_verse_analysis_local.py <verse_range>")
        print("Example: python test_verse_analysis_local.py 68:1-10")
        return

    verse_range_input = sys.argv[1]

    print(f"\n=== Quran Verse Analysis: {verse_range_input} ===\n")

    # Check API key
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set in .env file")
        return

    # Initialize components (suppress verbose output)
    print("Loading data...")
    import io
    import contextlib

    # Suppress verbose loading messages
    with contextlib.redirect_stdout(io.StringIO()):
        cache_manager = CacheManager()
        session_manager = SessionManager(cache_manager)
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        chapter_generator = ChapterContextGenerator(cache_manager, openai_client)
        verse_analyzer = VerseAnalyzer(cache_manager, session_manager, openai_client)

    print("Data loaded.")

    try:
        surah_num, start_verse, end_verse = parse_verse_range(verse_range_input)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    # Step 1: Generate Chapter Context
    print(f"Generating chapter context for Surah {surah_num}...")

    try:
        # Suppress verbose output from chapter generator
        with contextlib.redirect_stdout(io.StringIO()):
            chapter_context = chapter_generator.get_or_generate(surah_num)
        print("Chapter context ready.")

    except Exception as e:
        print(f"ERROR: {e}")
        return

    # Step 2: Create Reading Session
    verse_list = list(range(start_verse, end_verse + 1))
    with contextlib.redirect_stdout(io.StringIO()):
        session_id = session_manager.create_session(surah_num, verse_list)

    # Step 3: Analyze Verses One by One
    for idx, verse_num in enumerate(verse_list, 1):
        print(f"\n--- Ayat {surah_num}:{verse_num} ({idx}/{len(verse_list)}) ---\n")

        try:
            # Check if cached first
            cached_result = cache_manager.get_verse_analysis(surah_num, verse_num)
            if cached_result:
                print("[FROM CACHE]")
                safe_print(cached_result.get('explanation', 'N/A'))

                # Update session
                session_manager.add_verse(
                    session_id,
                    verse_num,
                    from_cache=True,
                    tokens_used=0,
                    one_line_summary=cached_result.get('one_line_summary', '')
                )
            else:
                print("Generating analysis...")
                print()

                # Suppress verbose output, only show streaming
                with contextlib.redirect_stdout(io.StringIO()):
                    # This triggers the streaming internally
                    pass

                # Actually run with streaming visible
                analysis_result = verse_analyzer.analyze_verse(surah_num, verse_num, session_id)

        except Exception as e:
            print(f"ERROR: {e}")
            break

    # Final Summary
    final_state = session_manager.get_state(session_id)
    print(f"\n=== Done ===")
    print(f"Analyzed: {final_state['verses_analyzed']}/{len(verse_list)} verses")
    print(f"Tokens used: {final_state['total_tokens']:,}")


if __name__ == "__main__":
    main()
