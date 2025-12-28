#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Clear Quran section heading coverage.
Show which surahs have headings and which don't, with verse counts.
"""

import json
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Load data
    sections_file = project_root / 'data' / 'metadata' / 'clear_quran_sections.json'
    metadata_file = project_root / 'data' / 'metadata' / 'chapter_metadata.json'
    surah_info_file = project_root / 'data' / 'metadata' / 'surah_info.json'

    with open(sections_file, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    with open(surah_info_file, 'r', encoding='utf-8') as f:
        surah_info = json.load(f)

    # Prepare lists
    with_headings = []
    without_headings = []

    for ch in range(1, 115):
        ch_str = str(ch)
        verse_count = metadata[ch_str]['verses_count']
        name = surah_info[ch_str].get('name_simple', surah_info[ch_str].get('name_translation', f'Chapter {ch}'))
        revelation = metadata[ch_str]['revelation_place']

        if ch_str in sections:
            section_count = len(sections[ch_str]['sections'])
            with_headings.append({
                'chapter': ch,
                'name': name,
                'verses': verse_count,
                'sections': section_count,
                'revelation': revelation
            })
        else:
            without_headings.append({
                'chapter': ch,
                'name': name,
                'verses': verse_count,
                'revelation': revelation
            })

    # Write output
    output_file = project_root / 'section_coverage_analysis.txt'

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("="*80 + "\n")
        out.write("CLEAR QURAN SECTION HEADING COVERAGE ANALYSIS\n")
        out.write("="*80 + "\n\n")

        # Summary
        out.write(f"Total Chapters: 114\n")
        out.write(f"Chapters WITH section headings: {len(with_headings)}\n")
        out.write(f"Chapters WITHOUT section headings: {len(without_headings)}\n")
        out.write(f"Total section headings: {sum(ch['sections'] for ch in with_headings)}\n")
        out.write("\n")

        # Chapters WITH headings
        out.write("="*80 + "\n")
        out.write(f"CHAPTERS WITH SECTION HEADINGS ({len(with_headings)} chapters)\n")
        out.write("="*80 + "\n\n")
        out.write(f"{'Ch':<4} {'Name':<30} {'Verses':<8} {'Sections':<10} {'Type':<8}\n")
        out.write("-"*80 + "\n")

        for ch in with_headings:
            out.write(f"{ch['chapter']:<4} {ch['name']:<30} {ch['verses']:<8} "
                     f"{ch['sections']:<10} {ch['revelation']:<8}\n")

        out.write("\n")

        # Statistics for chapters WITH headings
        total_verses_with = sum(ch['verses'] for ch in with_headings)
        total_sections = sum(ch['sections'] for ch in with_headings)
        avg_verses = total_verses_with / len(with_headings)
        avg_sections = total_sections / len(with_headings)

        out.write("STATISTICS (Chapters WITH headings):\n")
        out.write(f"  Total verses covered: {total_verses_with}\n")
        out.write(f"  Average verses per chapter: {avg_verses:.1f}\n")
        out.write(f"  Average sections per chapter: {avg_sections:.1f}\n")
        out.write(f"  Average verses per section: {total_verses_with/total_sections:.1f}\n")
        out.write("\n")

        # Chapters WITHOUT headings
        out.write("="*80 + "\n")
        out.write(f"CHAPTERS WITHOUT SECTION HEADINGS ({len(without_headings)} chapters)\n")
        out.write("="*80 + "\n\n")
        out.write(f"{'Ch':<4} {'Name':<30} {'Verses':<8} {'Type':<8}\n")
        out.write("-"*80 + "\n")

        for ch in without_headings:
            out.write(f"{ch['chapter']:<4} {ch['name']:<30} {ch['verses']:<8} "
                     f"{ch['revelation']:<8}\n")

        out.write("\n")

        # Statistics for chapters WITHOUT headings
        total_verses_without = sum(ch['verses'] for ch in without_headings)
        avg_verses_without = total_verses_without / len(without_headings)

        out.write("STATISTICS (Chapters WITHOUT headings):\n")
        out.write(f"  Total verses: {total_verses_without}\n")
        out.write(f"  Average verses per chapter: {avg_verses_without:.1f}\n")
        out.write(f"  Shortest: {min(ch['verses'] for ch in without_headings)} verses\n")
        out.write(f"  Longest: {max(ch['verses'] for ch in without_headings)} verses\n")
        out.write("\n")

        # Overall coverage
        out.write("="*80 + "\n")
        out.write("OVERALL COVERAGE\n")
        out.write("="*80 + "\n\n")

        total_verses_all = total_verses_with + total_verses_without
        coverage_percent = (total_verses_with / total_verses_all) * 100

        out.write(f"Total verses in Quran: {total_verses_all}\n")
        out.write(f"Verses with section headings: {total_verses_with} ({coverage_percent:.1f}%)\n")
        out.write(f"Verses without section headings: {total_verses_without} "
                 f"({100-coverage_percent:.1f}%)\n")
        out.write("\n")

        # Analysis
        out.write("="*80 + "\n")
        out.write("ANALYSIS\n")
        out.write("="*80 + "\n\n")

        out.write("WHY are 50 chapters without section headings?\n")
        out.write("-"*80 + "\n")
        out.write(f"  • Average verses (WITH headings): {avg_verses:.1f}\n")
        out.write(f"  • Average verses (WITHOUT headings): {avg_verses_without:.1f}\n")
        out.write(f"  • Chapters WITHOUT headings are {avg_verses/avg_verses_without:.1f}x shorter\n")
        out.write("\n")
        out.write("Conclusion: The Clear Quran provides section headings for longer surahs\n")
        out.write("that benefit from thematic subdivisions. Shorter surahs (averaging\n")
        out.write(f"{avg_verses_without:.0f} verses) are treated as single thematic units.\n")
        out.write("\n")

        # Breakdown by verse count
        out.write("BREAKDOWN BY VERSE COUNT:\n")
        out.write("-"*80 + "\n")

        # Categorize
        categories = {
            'Very Short (1-10 verses)': [],
            'Short (11-50 verses)': [],
            'Medium (51-100 verses)': [],
            'Long (101-200 verses)': [],
            'Very Long (200+ verses)': []
        }

        for ch in without_headings:
            v = ch['verses']
            if v <= 10:
                categories['Very Short (1-10 verses)'].append(ch)
            elif v <= 50:
                categories['Short (11-50 verses)'].append(ch)
            elif v <= 100:
                categories['Medium (51-100 verses)'].append(ch)
            elif v <= 200:
                categories['Long (101-200 verses)'].append(ch)
            else:
                categories['Very Long (200+ verses)'].append(ch)

        for cat_name, cat_chapters in categories.items():
            if cat_chapters:
                out.write(f"\n{cat_name}: {len(cat_chapters)} chapters\n")
                for ch in cat_chapters[:5]:  # Show first 5
                    out.write(f"  • Ch {ch['chapter']}: {ch['name']} ({ch['verses']} verses)\n")
                if len(cat_chapters) > 5:
                    out.write(f"  ... and {len(cat_chapters)-5} more\n")

    print(f"[OK] Analysis complete!")
    print(f"[OK] Output saved to: {output_file}")
    print()
    print("Summary:")
    print(f"  • {len(with_headings)} chapters WITH section headings")
    print(f"  • {len(without_headings)} chapters WITHOUT section headings")
    print(f"  • {sum(ch['sections'] for ch in with_headings)} total section headings")
    print()

if __name__ == '__main__':
    main()
