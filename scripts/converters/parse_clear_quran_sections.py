#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract section headings from The Clear Quran text file.

The Clear Quran includes thematic section headings before verse groups.
This script parses the text file to extract:
- Section headings
- Which verses belong to each section
- Mapping to chapter and verse numbers
"""

import re
import json
from pathlib import Path

def parse_clear_quran_sections(text_file_path):
    """
    Parse The Clear Quran text file to extract section headings.

    Returns:
        dict: Nested structure with chapters, sections, and verse ranges
    """

    with open(text_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Dictionary to store all sections
    all_sections = {}
    section_list = []  # Flat list for easier iteration

    # Split content into lines
    lines = content.split('\n')

    current_chapter = None
    current_chapter_name = None
    current_section = None
    current_section_start_line = None

    # Pattern to match chapter headers like "1. The Opening" or "68. The Pen"
    chapter_pattern = re.compile(r'^(\d+)\.\s+(.+)$')

    # Pattern to match verse numbers at start of text
    # Verses typically start with a number followed by a period
    verse_pattern = re.compile(r'^(\d+)\.\s+')

    # Track if we're in a chapter (after chapter header, before next chapter)
    in_chapter = False
    section_counter = 0

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check if this is a chapter header
        chapter_match = chapter_pattern.match(line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            chapter_name = chapter_match.group(2)

            # Check if next non-empty line is Arabic transliteration (in parentheses)
            # This confirms it's a chapter header
            next_line_idx = i + 1
            while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                next_line_idx += 1

            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                if next_line.startswith('(') and next_line.endswith(')'):
                    # This is a chapter header - close previous chapter if needed
                    if in_chapter and current_chapter and all_sections.get(current_chapter):
                        # Set end verse for last section of previous chapter
                        sections = all_sections[current_chapter]['sections']
                        if sections and sections[-1]['verse_end'] is None:
                            # Will be set later in determine_section_end_verses()
                            pass

                    # Start new chapter
                    current_chapter = chapter_num
                    current_chapter_name = chapter_name
                    in_chapter = True

                    # Initialize chapter in dictionary
                    if current_chapter not in all_sections:
                        all_sections[current_chapter] = {
                            'chapter_number': current_chapter,
                            'chapter_name': current_chapter_name,
                            'sections': []
                        }

                    print(f"[OK] Found Chapter {current_chapter}: {current_chapter_name}")
                    continue

        # If we're in a chapter, look for section headings
        if in_chapter and current_chapter:
            # Section headings are typically:
            # - Not verse text (doesn't start with number.)
            # - Not too long (< 100 chars usually)
            # - Not introduction text (those are longer paragraphs)
            # - Followed eventually by verse text

            # Skip lines that are clearly not section headings
            if line.startswith('In the Name of Allah'):
                continue
            if line.startswith('(') and line.endswith(')'):
                continue  # Arabic transliteration
            if len(line) > 150:
                continue  # Too long for a heading

            # Check if this looks like a section heading
            # Section headings are:
            # - Short (< 80 chars typically)
            # - Title cased or all caps
            # - Not part of a paragraph (standalone)
            # - Followed by verses within a few lines
            if not verse_pattern.match(line) and len(line) > 0 and len(line) < 100:
                # Check if this line looks like a title
                # Title detection: starts with capital, doesn't end with period/comma
                is_title_like = (
                    line[0].isupper() and
                    not line.endswith(',') and
                    not line.endswith(';') and
                    not line.startswith('�') and  # Don't start with special chars
                    not line.startswith('[') and
                    not line.endswith('...')  # Truncated paragraphs
                )

                if not is_title_like:
                    continue

                # Skip very common introduction/paragraph starters
                skip_phrases = [
                    'This Meccan', 'This Medinan', 'In this',
                    'The following', 'As mentioned', 'Unlike',
                    'See also', 'For more', 'According to',
                    'It is', 'There is', 'There are', 'Like the',
                    'To', 'Both this', 'The beginning', 'Some chapters'
                ]

                if any(line.startswith(phrase) for phrase in skip_phrases):
                    continue

                # Check if there are verses following this heading
                # Look ahead to see if we find verse numbers
                found_verse_after = False
                first_verse_num = None
                lines_to_verse = 0

                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue

                    verse_match = verse_pattern.match(next_line)
                    if verse_match:
                        first_verse_num = int(verse_match.group(1))
                        found_verse_after = True
                        lines_to_verse = j - i
                        break

                # Section headings should be immediately before verses (within 2-3 lines)
                if found_verse_after and first_verse_num and lines_to_verse <= 3:
                    # Additional validation: section headings typically have certain patterns
                    # Common patterns: "Qualities of...", "The Story of...", "Warning to..."
                    # Or just capitalized noun phrases

                    # Skip if it looks like a sentence (has many words and ends mid-sentence)
                    word_count = len(line.split())
                    if word_count > 12:  # Section headings are usually concise
                        continue

                    # Likely a section heading
                    current_section = line
                    current_section_start_line = i
                    section_counter += 1

                    # Create section entry
                    section_entry = {
                        'section_id': section_counter,
                        'chapter': current_chapter,
                        'heading': current_section,
                        'verse_start': first_verse_num,
                        'verse_end': None,  # Will be determined later
                        'line_number': i
                    }

                    # If there was a previous section, set its end verse
                    if all_sections[current_chapter]['sections']:
                        prev_section = all_sections[current_chapter]['sections'][-1]
                        if prev_section['verse_end'] is None:
                            prev_section['verse_end'] = first_verse_num - 1

                    all_sections[current_chapter]['sections'].append(section_entry)
                    section_list.append(section_entry)

                    # Use ASCII-safe output to avoid encoding errors
                    heading_preview = current_section[:50] if len(current_section) <= 50 else current_section[:47] + '...'
                    # Replace non-ASCII chars with ?
                    heading_preview = heading_preview.encode('ascii', 'replace').decode('ascii')
                    print(f"  [{section_counter}] {heading_preview} (v.{first_verse_num})")

    return all_sections, section_list


def determine_section_end_verses(all_sections, chapter_metadata):
    """
    Determine the ending verse for sections that don't have one yet.
    Uses chapter metadata to know the last verse of each chapter.
    """
    for chapter_num, chapter_data in all_sections.items():
        sections = chapter_data['sections']

        if not sections:
            continue

        # Set end verse for last section in chapter
        last_section = sections[-1]
        if last_section['verse_end'] is None:
            # Get chapter's total verses from metadata
            if str(chapter_num) in chapter_metadata:
                total_verses = chapter_metadata[str(chapter_num)]['verses_count']
                last_section['verse_end'] = total_verses

    return all_sections


def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    text_file = project_root / 'sources' / 'clear_quran_full_text.txt'
    chapter_metadata_file = project_root / 'data' / 'metadata' / 'chapter_metadata.json'
    output_file = project_root / 'data' / 'metadata' / 'clear_quran_sections.json'

    print("="*70)
    print("PARSING THE CLEAR QURAN SECTION HEADINGS")
    print("="*70)
    print()

    # Parse sections
    print("Parsing text file...")
    all_sections, section_list = parse_clear_quran_sections(text_file)

    print()
    print(f"[OK] Found {len(all_sections)} chapters")
    print(f"[OK] Found {len(section_list)} total sections")
    print()

    # Load chapter metadata to determine end verses
    print("Loading chapter metadata to determine section end verses...")
    with open(chapter_metadata_file, 'r', encoding='utf-8') as f:
        chapter_metadata = json.load(f)

    all_sections = determine_section_end_verses(all_sections, chapter_metadata)

    # Save to JSON
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sections, f, ensure_ascii=False, indent=2)

    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)

    # Show statistics
    for chapter_num in sorted(all_sections.keys())[:10]:  # Show first 10 chapters
        chapter_data = all_sections[chapter_num]
        num_sections = len(chapter_data['sections'])
        print(f"Chapter {chapter_num:3d} ({chapter_data['chapter_name'][:30]:30s}): {num_sections:3d} sections")

    print()
    print(f"Total sections across all chapters: {len(section_list)}")
    print(f"Output saved to: {output_file}")
    print()


if __name__ == '__main__':
    main()
