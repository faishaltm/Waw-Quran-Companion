#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Narrative Balaghah Analyzer - Transform chapter-level balaghah statistics into thematic narratives.

Instead of just listing where patterns occur, this module explains WHY they occur
by using contextual information (section headings, ruku divisions, surah introductions).

Usage:
    from narrative_balaghah_analyzer import create_chapter_narrative
    narrative = create_chapter_narrative(chapter_data, metadata_loader)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'loaders'))
from metadata_loader import MetadataLoader


def create_root_narrative(root, root_data, chapter_num, metadata_loader):
    """
    Create narrative explanation for root repetition pattern.

    Args:
        root: Arabic root (e.g., 'طوع')
        root_data: Dict with verses, lemmas, total_occurrences
        chapter_num: Chapter number
        metadata_loader: MetadataLoader instance for context

    Returns:
        String narrative explaining the root's thematic significance
    """
    verses = root_data.get('verses', [])
    lemmas = root_data.get('lemmas', [])
    count = root_data.get('total_occurrences', len(verses))

    if not verses:
        return None

    # Get section context for each verse
    verse_contexts = []
    for verse_num in verses:
        section = metadata_loader.get_section_for_verse(chapter_num, verse_num)
        ruku = metadata_loader.get_ruku_for_verse(chapter_num, verse_num)

        verse_contexts.append({
            'verse': verse_num,
            'section_heading': section['heading'] if section else None,
            'ruku_number': ruku['ruku_number'] if ruku else None
        })

    # Build narrative based on distribution pattern
    narrative_parts = []

    # 1. Overview
    lemma_str = ', '.join(lemmas) if lemmas else root
    narrative_parts.append(f"The root {root} ({lemma_str}) appears {count} time(s)")

    # 2. Distribution analysis
    if len(verses) == 1:
        ctx = verse_contexts[0]
        if ctx['section_heading']:
            narrative_parts.append(
                f"in the '{ctx['section_heading']}' section (verse {ctx['verse']})"
            )
        else:
            narrative_parts.append(f"in verse {ctx['verse']}")

    elif len(verses) == 2:
        v1, v2 = verse_contexts[0], verse_contexts[1]

        # Check if both in same section
        if v1.get('section_heading') and v1['section_heading'] == v2.get('section_heading'):
            narrative_parts.append(
                f"twice within the '{v1['section_heading']}' section (verses {v1['verse']}, {v2['verse']}), "
                f"creating emphasis through repetition"
            )
        else:
            # Different sections - show transition
            parts = []
            if v1.get('section_heading'):
                parts.append(f"first in '{v1['section_heading']}' (v.{v1['verse']})")
            else:
                parts.append(f"first in verse {v1['verse']}")

            if v2.get('section_heading'):
                parts.append(f"then in '{v2['section_heading']}' (v.{v2['verse']})")
            else:
                parts.append(f"then in verse {v2['verse']}")

            narrative_parts.append(', '.join(parts))

    else:  # 3+ occurrences
        # Group by section
        sections_map = {}
        for ctx in verse_contexts:
            section_key = ctx.get('section_heading') or f"Ruku {ctx.get('ruku_number', '?')}"
            if section_key not in sections_map:
                sections_map[section_key] = []
            sections_map[section_key].append(ctx['verse'])

        if len(sections_map) == 1:
            # All in same section - concentrated emphasis
            section_name = list(sections_map.keys())[0]
            verse_list = ', '.join(str(v) for v in verses)
            narrative_parts.append(
                f"{len(verses)} times within the '{section_name}' section (verses {verse_list}), "
                f"creating concentrated thematic emphasis"
            )
        else:
            # Distributed across sections - trace the narrative arc
            section_mentions = []
            for section_name, section_verses in sections_map.items():
                verse_list = ', '.join(str(v) for v in section_verses)
                section_mentions.append(f"'{section_name}' ({verse_list})")

            narrative_parts.append(
                f"across {len(sections_map)} thematic sections: {', '.join(section_mentions)}, "
                f"tracing the concept through the surah's argument"
            )

    return ' '.join(narrative_parts) + '.'


def create_saj_narrative(saj_patterns, chapter_num, metadata_loader):
    """
    Create narrative for saj' (rhyme) patterns across the chapter.

    Args:
        saj_patterns: List of saj' pattern occurrences
        chapter_num: Chapter number
        metadata_loader: MetadataLoader instance

    Returns:
        String narrative explaining saj' distribution and purpose
    """
    if not saj_patterns:
        return None

    # Group by rhyme pattern
    pattern_groups = {}
    for saj in saj_patterns:
        pattern = saj.get('pattern', '')
        if pattern not in pattern_groups:
            pattern_groups[pattern] = []
        pattern_groups[pattern].append(saj)

    narratives = []

    for pattern, occurrences in pattern_groups.items():
        # Get verse ranges
        verses = [s['verse'] for s in occurrences]
        verse_range = f"{min(verses)}-{max(verses)}" if len(verses) > 1 else str(verses[0])

        # Get section context for first and last occurrence
        first_section = metadata_loader.get_section_for_verse(chapter_num, verses[0])
        last_section = metadata_loader.get_section_for_verse(chapter_num, verses[-1])

        # Build narrative
        if len(verses) <= 3:
            narratives.append(
                f"Saj' pattern '{pattern}' appears {len(verses)} time(s) in verses {', '.join(str(v) for v in verses)}"
            )
        else:
            # Long sequence - describe the arc
            first_heading = first_section['heading'] if first_section else f"verse {verses[0]}"
            last_heading = last_section['heading'] if last_section else f"verse {verses[-1]}"

            if first_section and last_section and first_section['heading'] == last_section['heading']:
                narratives.append(
                    f"Saj' pattern '{pattern}' unifies the '{first_heading}' section "
                    f"through {len(verses)} consecutive verses ({verse_range}), "
                    f"creating sustained rhythmic emphasis"
                )
            else:
                narratives.append(
                    f"Saj' pattern '{pattern}' spans {len(verses)} verses ({verse_range}), "
                    f"from '{first_heading}' to '{last_heading}', "
                    f"linking thematic sections through rhythmic cohesion"
                )

    return ' '.join(narratives) + '.' if narratives else None


def create_chapter_narrative(chapter_data, metadata_loader):
    """
    Transform chapter-level balaghah statistics into thematic narratives.

    Args:
        chapter_data: Dict with chapter info including 'chapter_balaghah' section
        metadata_loader: MetadataLoader instance for context

    Returns:
        Dict with narrative explanations for each balaghah feature
    """
    chapter_num = chapter_data.get('chapter')
    balaghah_data = chapter_data.get('chapter_balaghah', {})

    if not balaghah_data:
        return None

    narratives = {
        'chapter': chapter_num,
        'chapter_name': chapter_data.get('metadata', {}).get('name_translation', ''),
        'thematic_analysis': {}
    }

    # 1. Root Repetitions
    root_reps = balaghah_data.get('root_repetitions', {})
    if root_reps:
        narratives['thematic_analysis']['root_patterns'] = {}
        for root, root_data in root_reps.items():
            narrative = create_root_narrative(root, root_data, chapter_num, metadata_loader)
            if narrative:
                narratives['thematic_analysis']['root_patterns'][root] = narrative

    # 2. Saj' Patterns
    saj_patterns = balaghah_data.get('saj_patterns', [])
    if saj_patterns:
        narrative = create_saj_narrative(saj_patterns, chapter_num, metadata_loader)
        if narrative:
            narratives['thematic_analysis']['saj_distribution'] = narrative

    # 3. Summary synthesis
    # Combine insights into overall thematic summary
    if narratives['thematic_analysis']:
        surah_info = metadata_loader.get_surah_info(chapter_num)
        revelation_place = surah_info.get('revelation_place', 'unknown') if surah_info else 'unknown'

        narratives['summary'] = (
            f"This {revelation_place} surah employs balaghah devices to structure its message. "
            f"The distribution of rhetorical patterns aligns with the surah's thematic divisions, "
            f"supporting the overall argument through strategic repetition and rhythmic emphasis."
        )

    return narratives


def main():
    """Demo: analyze chapters with narrative approach."""

    # Load sample data
    script_dir = Path(__file__).parent

    # Try Chapter 3 first (has section headings), then fall back to Chapter 68
    sample_files = [
        (script_dir.parent.parent / 'scripts' / 'tools' / 'verse_3_1-30_v2.json', 'ch3'),
        (script_dir.parent.parent / 'scripts' / 'tools' / 'verse_68_1-10_v2.json', 'ch68'),
    ]

    sample_file = None
    output_suffix = None
    for file_path, suffix in sample_files:
        if file_path.exists():
            sample_file = file_path
            output_suffix = suffix
            break

    if not sample_file:
        print(f"Sample files not found")
        print("Please run get_verse_info_v2.py first to generate sample data.")
        print("  Example: echo '3:1-30' | python get_verse_info_v2.py")
        return

    output_file = script_dir.parent.parent / f'temp_narrative_analysis_{output_suffix}.txt'

    with open(sample_file, 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)

    # Load metadata
    print("Loading metadata...")
    metadata_loader = MetadataLoader()

    # Create narrative
    print(f"Analyzing {sample_file.name}...")
    narratives = create_chapter_narrative(chapter_data, metadata_loader)

    # Write output to file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as out:
        chapter_num = narratives.get('chapter') if narratives else '?'
        chapter_name = narratives.get('chapter_name') if narratives else '?'
        out.write("="*70 + "\n")
        out.write(f"NARRATIVE BALAGHAH ANALYSIS - Chapter {chapter_num} ({chapter_name})\n")
        out.write("="*70 + "\n\n")

        if narratives:
            # Check if chapter has Clear Quran sections
            has_sections = False
            if 'root_patterns' in narratives.get('thematic_analysis', {}):
                # Check if any narrative mentions section headings (contains quotes)
                for narrative in narratives['thematic_analysis']['root_patterns'].values():
                    if "'" in narrative:
                        has_sections = True
                        break

            if has_sections:
                out.write("[This chapter has Clear Quran section headings - narratives show thematic context]\n\n")
            else:
                out.write("[This chapter doesn't have Clear Quran sections - using ruku context]\n\n")

            out.write(f"Chapter: {narratives['chapter']} - {narratives['chapter_name']}\n\n")

            if 'root_patterns' in narratives['thematic_analysis']:
                out.write("ROOT PATTERN NARRATIVES:\n")
                out.write("-" * 70 + "\n")
                for root, narrative in narratives['thematic_analysis']['root_patterns'].items():
                    out.write(f"\n{root}:\n")
                    out.write(f"  {narrative}\n")

            if 'saj_distribution' in narratives['thematic_analysis']:
                out.write("\nSAJ' DISTRIBUTION NARRATIVE:\n")
                out.write("-" * 70 + "\n")
                out.write(f"  {narratives['thematic_analysis']['saj_distribution']}\n")

            if 'summary' in narratives:
                out.write("\nTHEMATIC SUMMARY:\n")
                out.write("-" * 70 + "\n")
                out.write(f"  {narratives['summary']}\n")
        else:
            out.write("[No chapter-level balaghah data found]\n")

        out.write("\n" + "="*70 + "\n")
        out.write("COMPARISON: Statistics vs. Narrative\n")
        out.write("="*70 + "\n\n")
        out.write("WITHOUT NARRATIVE (current output):\n")
        out.write('  "طوع": { "verses": [8, 10], "total_occurrences": 2 }\n\n')
        out.write("WITH NARRATIVE (new output):\n")
        if narratives and 'root_patterns' in narratives['thematic_analysis']:
            for root, narrative in narratives['thematic_analysis']['root_patterns'].items():
                if root == 'طوع':
                    out.write(f'  "{root}": "{narrative}"\n')
                    break
        out.write("\n")

    print(f"[OK] Analysis complete!")
    print(f"[OK] Output saved to: {output_file}")
    print()
    print("To view the narrative analysis, read the output file:")


if __name__ == '__main__':
    main()
