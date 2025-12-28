"""
Debug: Show all LLM input for a specific verse
Shows exactly what gets sent to OpenAI before generation
"""

import sys
import os
import json
import io
import contextlib
from pathlib import Path

# Add paths for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "tools"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "loaders"))
sys.path.insert(0, str(SCRIPT_DIR))

# Import get_verse_info_v2 functions
from get_verse_info_v2 import load_comprehensive_quran, extract_verse_info_compact

# Import config
from config.settings import load_prompt, get_balaghah_guide_path


def main():
    surah = 68
    verse = 4

    print("DEBUG: LLM Input for Surah %d:%d" % (surah, verse))
    print()

    # Load comprehensive data
    comprehensive_path = PROJECT_ROOT / "data" / "quran_comprehensive.json"
    print("[1] Loading Quran data...")

    with contextlib.redirect_stdout(io.StringIO()):
        comprehensive_data = load_comprehensive_quran(str(comprehensive_path))

    print("    Done.")

    # Get verse info using get_verse_info_v2
    print("[2] Extracting verse data using get_verse_info_v2...")

    with contextlib.redirect_stdout(io.StringIO()):
        verse_info = extract_verse_info_compact(surah, verse, verse, comprehensive_data)

    print("    Done.")

    # Get chapter context (metadata)
    chapter_context = verse_info.get('metadata', {})
    verse_data = verse_info['verses'][0] if verse_info['verses'] else {}

    # Load balaghah guide
    print("[3] Loading balaghah guide...")
    guide_path = get_balaghah_guide_path()
    with open(guide_path, 'r', encoding='utf-8') as f:
        balaghah_guide = f.read()
    print("    Guide length: %d characters" % len(balaghah_guide))

    # Load system prompt
    print("[4] Loading system prompt...")
    system_prompt_template = load_prompt("verse_analysis_initial.txt")
    system_prompt = system_prompt_template.replace("{BALAGHAH_GUIDE}", balaghah_guide)
    print("    Prompt length: %d characters" % len(system_prompt))

    # Prepare user message
    user_message = {
        "surah": surah,
        "verse": verse,
        "chapter_context": chapter_context,
        "verse_data": verse_data,
        "instruction": "Jelaskan ayat ini dalam Bahasa Indonesia untuk pembaca umum."
    }

    user_message_json = json.dumps(user_message, ensure_ascii=False, indent=2)

    # Save all to files
    print()
    print("[5] Saving to files...")

    # Save system prompt (template only, without balaghah guide)
    with open(SCRIPT_DIR / "debug_68_4_system_prompt.txt", 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("SYSTEM PROMPT TEMPLATE (verse_analysis_initial.txt)\n")
        f.write("=" * 80 + "\n\n")
        f.write(system_prompt_template)

    # Save chapter context
    with open(SCRIPT_DIR / "debug_68_4_chapter_context.json", 'w', encoding='utf-8') as f:
        json.dump(chapter_context, f, ensure_ascii=False, indent=2)

    # Save verse data
    with open(SCRIPT_DIR / "debug_68_4_verse_data.json", 'w', encoding='utf-8') as f:
        json.dump(verse_data, f, ensure_ascii=False, indent=2)

    # Save complete user message
    with open(SCRIPT_DIR / "debug_68_4_user_message.json", 'w', encoding='utf-8') as f:
        json.dump(user_message, f, ensure_ascii=False, indent=2)

    # Save full messages array (what goes to OpenAI)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message_json}
    ]

    with open(SCRIPT_DIR / "debug_68_4_full_messages.json", 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print()
    print("Files saved:")
    print("  - debug_68_4_system_prompt.txt    (template before guide injection)")
    print("  - debug_68_4_chapter_context.json (chapter metadata)")
    print("  - debug_68_4_verse_data.json      (verse info from get_verse_info_v2)")
    print("  - debug_68_4_user_message.json    (complete user message)")
    print("  - debug_68_4_full_messages.json   (full messages array for OpenAI)")
    print()
    print("Summary:")
    print("  System prompt:  %d chars" % len(system_prompt))
    print("  User message:   %d chars" % len(user_message_json))
    print("  Total:          %d chars" % (len(system_prompt) + len(user_message_json)))


if __name__ == "__main__":
    main()
