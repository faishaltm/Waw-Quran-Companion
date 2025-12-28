#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Al-Kashshaf Tafsir Parser - Extract from OpenITI Format

Parses Al-Kashshaf (الكشاف) by Al-Zamakhshari from OpenITI mARkdown format
and converts to structured JSON matching the project's tafsir schema.

Source: OpenITI Corpus (Shamela version)
File: 0538JarAllahZamakhshari.Kashshaf.Shamela0023627-ara1
Author: Jar Allah al-Zamakhshari (d. 538 AH / 1144 CE)
License: Public domain (classical work)

Output: data/metadata/tafsir_kashshaf_arabic.json

Format:
{
    "source": "Al-Kashshaf (الكشاف)",
    "author": "Al-Zamakhshari",
    ...
    "tafsir": [
        {
            "chapter": 1,
            "verse": 1,
            "text": "Commentary in Arabic...",
            "verses_range": [1] or [2, 3] for multi-verse commentaries
        },
        ...
    ]
}
"""

import re
import json
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "sources" / "tafsir" / "kashshaf_openiti_raw.txt"
OUTPUT_FILE = PROJECT_ROOT / "data" / "metadata" / "tafsir_kashshaf_arabic.json"

def parse_kashshaf(input_path):
    """
    Parse Al-Kashshaf from OpenITI mARkdown format.

    Returns:
        list: List of tafsir entries
    """
    print(f"Reading Al-Kashshaf from: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"File size: {len(content):,} characters")

    # Split into lines for processing
    lines = content.split('\n')

    # Regex patterns for verse markers
    # Pattern 1: ### | [سورة النام (Chapter#) : آية Verse#]
    verse_pattern_single = re.compile(r'###\s*\|\s*\[سورة\s+[^\(]+\((\d+)\)\s*:\s*آية\s+(\d+)\]')
    # Pattern 2: ### | [سورة النام (Chapter#) : الآيات Verse1 الى Verse2]
    verse_pattern_range = re.compile(r'###\s*\|\s*\[سورة\s+[^\(]+\((\d+)\)\s*:\s*الآيات\s+(\d+)\s+الى\s+(\d+)\]')
    # Pattern 3: Incomplete markers (need to read next line)
    verse_pattern_incomplete = re.compile(r'###\s*\|\s*\[سورة\s+[^\(]+\((\d+)\)\s*:\s*آية\s*$')

    tafsir_entries = []
    current_chapter = None
    current_verses = []
    current_commentary = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for single verse marker
        match_single = verse_pattern_single.search(line)
        if match_single:
            # Save previous commentary if exists
            if current_chapter and current_verses and current_commentary:
                save_entry(tafsir_entries, current_chapter, current_verses, current_commentary)

            # Start new entry
            current_chapter = int(match_single.group(1))
            current_verses = [int(match_single.group(2))]
            current_commentary = []
            i += 1
            continue

        # Check for verse range marker
        match_range = verse_pattern_range.search(line)
        if match_range:
            # Save previous commentary if exists
            if current_chapter and current_verses and current_commentary:
                save_entry(tafsir_entries, current_chapter, current_verses, current_commentary)

            # Start new entry with range
            current_chapter = int(match_range.group(1))
            verse_start = int(match_range.group(2))
            verse_end = int(match_range.group(3))
            current_verses = list(range(verse_start, verse_end + 1))
            current_commentary = []
            i += 1
            continue

        # Check for incomplete marker (verse number on next line)
        match_incomplete = verse_pattern_incomplete.search(line)
        if match_incomplete:
            # Save previous commentary if exists
            if current_chapter and current_verses and current_commentary:
                save_entry(tafsir_entries, current_chapter, current_verses, current_commentary)

            # Read next line for verse number
            current_chapter = int(match_incomplete.group(1))
            i += 1
            if i < len(lines):
                next_line = lines[i].strip()
                # Extract verse number from next line (e.g., "4]" or "الآيات X الى Y]")
                verse_num_match = re.search(r'^(\d+)\]', next_line)
                if verse_num_match:
                    current_verses = [int(verse_num_match.group(1))]
                    current_commentary = []
                else:
                    # Might be a range, try to parse
                    range_match = re.search(r'^الآيات\s+(\d+)\s+الى\s+(\d+)\]', next_line)
                    if range_match:
                        verse_start = int(range_match.group(1))
                        verse_end = int(range_match.group(2))
                        current_verses = list(range(verse_start, verse_end + 1))
                        current_commentary = []
            i += 1
            continue

        # Check if line is a new section marker (different surah starting)
        if line.startswith('### |') and 'سورة' in line:
            # This is a verse marker we haven't matched - skip unusual formats
            i += 1
            continue

        # Skip metadata and header lines
        if line.startswith('#META#') or line.startswith('######OpenITI#'):
            i += 1
            continue

        # Skip page markers
        if line.startswith('PageV') or line.startswith('# PageV'):
            i += 1
            continue

        # Skip ms references (manuscript references)
        if 'ms' in line and re.search(r'ms\d{4}', line):
            # Clean but keep
            line = re.sub(r'\s*ms\d{4,}\s*', ' ', line)

        # Collect commentary text
        if current_chapter and current_verses:
            # Remove OpenITI formatting markers
            # Remove '# ' at start of lines (paragraph markers)
            if line.startswith('# '):
                line = line[2:]
            # Remove '~~' (continuation markers)
            line = line.replace('~~', '')

            # Skip empty lines at start of commentary
            if not current_commentary and not line:
                i += 1
                continue

            # Add line to commentary
            if line:
                current_commentary.append(line)

        i += 1

    # Save last entry
    if current_chapter and current_verses and current_commentary:
        save_entry(tafsir_entries, current_chapter, current_verses, current_commentary)

    print(f"Extracted {len(tafsir_entries)} tafsir entries")

    return tafsir_entries


def save_entry(tafsir_entries, chapter, verses, commentary):
    """
    Save a tafsir entry to the list.

    Args:
        tafsir_entries: List to append to
        chapter: Chapter number
        verses: List of verse numbers
        commentary: List of commentary text lines
    """
    # Join commentary lines into single text
    text = ' '.join(commentary).strip()

    # Skip entries with no substantial commentary
    if len(text) < 10:
        return

    # Create entry for first verse in range
    # (for multi-verse commentaries, we store under the first verse)
    entry = {
        'chapter': chapter,
        'verse': verses[0],
        'text': text,
        'verses_range': verses if len(verses) > 1 else [verses[0]]
    }

    tafsir_entries.append(entry)


def create_verse_index(tafsir_entries):
    """
    Create a verse-indexed structure for easy lookup.

    Returns:
        dict: {chapter: {verse: {text, verses_range}}}
    """
    verse_index = {}

    for entry in tafsir_entries:
        chapter = entry['chapter']
        verse = entry['verse']

        if chapter not in verse_index:
            verse_index[chapter] = {}

        verse_index[chapter][verse] = {
            'text': entry['text'],
            'verses_range': entry['verses_range']
        }

    return verse_index


def generate_statistics(tafsir_entries):
    """
    Generate coverage statistics.

    Returns:
        dict: Statistics about coverage
    """
    chapters = set(entry['chapter'] for entry in tafsir_entries)

    # Count verses per chapter
    chapter_coverage = {}
    for entry in tafsir_entries:
        chapter = entry['chapter']
        if chapter not in chapter_coverage:
            chapter_coverage[chapter] = set()
        for verse in entry['verses_range']:
            chapter_coverage[chapter].add(verse)

    # Convert to counts
    chapter_verse_counts = {ch: len(verses) for ch, verses in chapter_coverage.items()}

    # Multi-verse commentaries
    multi_verse = [e for e in tafsir_entries if len(e['verses_range']) > 1]

    stats = {
        'total_entries': len(tafsir_entries),
        'chapters_covered': len(chapters),
        'multi_verse_commentaries': len(multi_verse),
        'chapter_coverage': chapter_verse_counts
    }

    return stats


def main():
    """Main execution"""
    print("="*60)
    print("Al-Kashshaf Tafsir Parser")
    print("="*60)
    print()

    # Check input file exists
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Please run download script first.")
        sys.exit(1)

    # Parse tafsir
    tafsir_entries = parse_kashshaf(INPUT_FILE)

    # Create verse index
    print("\nCreating verse index...")
    verse_index = create_verse_index(tafsir_entries)

    # Generate statistics
    print("Generating statistics...")
    stats = generate_statistics(tafsir_entries)

    # Print statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Total tafsir entries: {stats['total_entries']}")
    print(f"Chapters covered: {stats['chapters_covered']}/114")
    print(f"Multi-verse commentaries: {stats['multi_verse_commentaries']}")
    print(f"\nTop 10 chapters by verse coverage:")
    sorted_chapters = sorted(stats['chapter_coverage'].items(), key=lambda x: x[1], reverse=True)
    for chapter, count in sorted_chapters[:10]:
        print(f"  Chapter {chapter}: {count} verses")

    # Create output structure
    output = {
        'source': 'Al-Kashshaf (الكشاف)',
        'author': 'Jar Allah al-Zamakhshari (جار الله الزمخشري)',
        'author_death': '538 AH / 1144 CE',
        'methodology': 'Rhetorical and linguistic tafsir - Premier work on Quranic eloquence and word choice analysis',
        'language': 'Arabic',
        'openiti_source': '0538JarAllahZamakhshari.Kashshaf.Shamela0023627-ara1',
        'license': 'Public domain (classical work)',
        'attribution': 'OpenITI Corpus - https://github.com/OpenITI',
        'statistics': stats,
        'verse_index': verse_index
    }

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save to JSON
    print(f"\nSaving to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Output file size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
    print("\n" + "="*60)
    print("DONE")
    print("="*60)


if __name__ == '__main__':
    main()
