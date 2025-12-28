#!/usr/bin/env python3
"""
LLM Input Viewer - Show what would be sent to LLM for /surah command

Usage:
    python llm_input_viewer.py 68                # Show chapter context generation input
    python llm_input_viewer.py 68 --section 0    # Show section overview input
    python llm_input_viewer.py 68 --verse 1      # Show verse analysis input
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager
from api.data_loader import QuranDataLoader
from api.chapter_context_generator import ChapterContextGenerator
from api.section_session_manager import SectionSessionManager
from config.settings import (
    load_prompt,
    get_balaghah_guide_path,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE
)

def show_chapter_context_input(surah_num: int):
    """Show input for chapter context generation"""

    print("=" * 80)
    print(f"CHAPTER CONTEXT GENERATION INPUT - Surah {surah_num}")
    print("=" * 80)

    loader = QuranDataLoader()

    # Load chapter metadata
    chapter_meta = loader.get_chapter_metadata(surah_num)

    print(f"\nMODEL: {OPENAI_MODEL}")
    print(f"TEMPERATURE: {OPENAI_TEMPERATURE}")
    print(f"RESPONSE_FORMAT: json_object")

    print("\n" + "-" * 80)
    print("SYSTEM PROMPT:")
    print("-" * 80)

    # Load system prompt
    system_prompt = load_prompt("chapter_context_short.txt")
    print(system_prompt)

    print("\n" + "-" * 80)
    print("USER MESSAGE (JSON):")
    print("-" * 80)

    # Load all verses
    all_verses = loader.get_all_verses_in_surah(surah_num)

    # Simplify verse data
    simplified_verses = []
    for v in all_verses:
        simplified_verses.append({
            "verse": v['verse'],
            "arabic": v.get('arabic', ''),
            "english": v.get('english', '')
        })

    # Load surah introduction
    surah_intro = loader.get_surah_context(surah_num)

    # Get section headings
    section_headings = loader.get_all_section_headings(surah_num)
    section_dict = {}
    for s in section_headings:
        key = f"{s['verse_start']}-{s['verse_end']}"
        section_dict[key] = s['heading']

    # Prepare metadata
    metadata = {
        "chapter_number": surah_num,
        "name_arabic": chapter_meta.get('name_arabic', ''),
        "revelation_place": chapter_meta.get('revelation_place', ''),
        "revelation_order": chapter_meta.get('revelation_order', 0),
        "verses_count": chapter_meta.get('verses_count', 0),
        "section_headings": section_dict
    }

    if surah_intro and isinstance(surah_intro, dict):
        metadata["introduction"] = surah_intro.get('text', '')
        metadata["introduction_source"] = surah_intro.get('source', '')
    elif surah_intro and isinstance(surah_intro, str):
        metadata["introduction"] = surah_intro

    # User data
    user_data = {
        "chapter": surah_num,
        "metadata": metadata,
        "verses": simplified_verses
    }

    print(json.dumps(user_data, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("END OF INPUT")
    print("=" * 80)

def show_section_overview_input(surah_num: int, section_index: int):
    """Show input for section overview generation"""

    print("=" * 80)
    print(f"SECTION OVERVIEW INPUT - Surah {surah_num}, Section {section_index}")
    print("=" * 80)

    cache = CacheManager()
    loader = QuranDataLoader()

    # Get chapter context
    chapter_context = cache.get_chapter_context(surah_num)
    if not chapter_context:
        print("ERROR: Chapter context not cached. Generate it first.")
        return

    # Get section data
    section_manager = SectionSessionManager(cache, None, loader)
    section_data = section_manager.get_section_full_data(surah_num, section_index)

    print(f"\nMODEL: {OPENAI_MODEL}")
    print(f"TEMPERATURE: 0.7")

    print("\n" + "-" * 80)
    print("SYSTEM PROMPT (EXCERPT - first 1000 chars):")
    print("-" * 80)

    # Load balaghah guide
    balaghah_path = get_balaghah_guide_path()
    with open(balaghah_path, 'r', encoding='utf-8') as f:
        balaghah_guide = f.read()

    print(balaghah_guide[:1000] + "...")
    print("\n[... BALAGHAH GUIDE CONTINUES ...]\n")

    # Chapter context section
    chapter_meta = loader.get_chapter_metadata(surah_num)
    user_introduction = chapter_context.get('user_introduction', '')

    print("-" * 80)
    print("CHAPTER CONTEXT (user_introduction - first assistant message):")
    print("-" * 80)
    print(f"\nSurah: {chapter_meta.get('name_arabic', '')} ({chapter_meta.get('name_english', '')})")
    print(f"\nUser Introduction (first {min(500, len(user_introduction))} chars):")
    print(user_introduction[:500] + "..." if len(user_introduction) > 500 else user_introduction)
    print(f"\n[Total length: {len(user_introduction)} chars, ~{len(user_introduction)//4} tokens]")

    print("\n" + "-" * 80)
    print("SECTION DATA:")
    print("-" * 80)
    if section_data:
        print(json.dumps(section_data, ensure_ascii=False, indent=2))
    else:
        print("ERROR: Section data not found")

    print("\n" + "-" * 80)
    print("USER MESSAGE (PROMPT):")
    print("-" * 80)
    if section_data:
        section_info = section_data.get('section_info', {})
        section_heading = section_info.get('heading', 'No heading')
        prompt = f"""Anda akan memberikan OVERVIEW NARATIF untuk Section {section_index + 1}:
"{section_heading}"

Verses {section_info.get('verse_start')}-{section_info.get('verse_end')}

[Full section overview prompt would be generated by section_manager.generate_section_overview_prompt()]"""
        print(prompt)
    else:
        print("ERROR: Cannot generate prompt without section data")

    print("\n" + "=" * 80)
    print("END OF INPUT")
    print("=" * 80)

def show_verse_analysis_input(surah_num: int, verse_num: int):
    """Show input for verse analysis"""

    print("=" * 80)
    print(f"VERSE ANALYSIS INPUT - Surah {surah_num}:{verse_num}")
    print("=" * 80)

    loader = QuranDataLoader()

    # Load verse analysis prompt
    verse_prompt_path = Path(__file__).parent / "prompts" / "verse_analysis_prompt.txt"
    with open(verse_prompt_path, 'r', encoding='utf-8') as f:
        verse_analysis_prompt = f.read()

    print(f"\nMODEL: {OPENAI_MODEL}")
    print(f"TEMPERATURE: {OPENAI_TEMPERATURE}")

    print("\n" + "-" * 80)
    print("SYSTEM PROMPT (EXCERPT - first 1000 chars):")
    print("-" * 80)

    # Balaghah guide
    balaghah_path = get_balaghah_guide_path()
    with open(balaghah_path, 'r', encoding='utf-8') as f:
        balaghah_guide = f.read()

    print(balaghah_guide[:1000] + "...")
    print("\n[... BALAGHAH GUIDE CONTINUES ...]\n")

    print("-" * 80)
    print("VERSE ANALYSIS PROMPT:")
    print("-" * 80)
    print(verse_analysis_prompt)

    print("\n" + "-" * 80)
    print("USER MESSAGE:")
    print("-" * 80)

    user_message = f"""Analisis ayat {surah_num}:{verse_num} dengan struktur 5 paragraf.

{verse_analysis_prompt}

DATA AYAT (dalam JSON):
Gunakan data berikut untuk analisis Anda."""

    print(user_message)

    print("\n" + "-" * 80)
    print("VERSE DATA (JSON):")
    print("-" * 80)

    # Get verse data
    verse_data = loader.get_verse_full_data(surah_num, verse_num)
    print(json.dumps(verse_data, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("END OF INPUT")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="View LLM inputs for /surah command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python llm_input_viewer.py 68                  # Chapter context input
  python llm_input_viewer.py 68 --section 0      # Section overview input
  python llm_input_viewer.py 68 --verse 1        # Verse analysis input
        """
    )

    parser.add_argument('surah', type=int, help="Surah number (1-114)")
    parser.add_argument('--section', type=int, help="Show section overview input")
    parser.add_argument('--verse', type=int, help="Show verse analysis input")

    args = parser.parse_args()

    try:
        if args.verse:
            show_verse_analysis_input(args.surah, args.verse)
        elif args.section is not None:
            show_section_overview_input(args.surah, args.section)
        else:
            show_chapter_context_input(args.surah)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
