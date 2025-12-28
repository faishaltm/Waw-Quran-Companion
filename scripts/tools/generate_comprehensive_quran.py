#!/usr/bin/env python3
"""
Comprehensive Quran Data Generator

Merges all data sources into a single comprehensive JSON file with chapter-centric structure.

Input Sources (from data/ directory):
- linguistic/morphology_flat_aligned.json (38 MB, 77,429 entries) - CORRECTED alignment, flat format
- linguistic/dependencies_full.json (14 MB, 37,420 relations)
- linguistic/named_entities_full.json (1.5 MB, 5,494 entities)
- linguistic/lemmas_dictionary.json (216 KB, 1,593 lemmas)
- linguistic/pause_marks.json (796 KB, 4,359 marks)
- linguistic/balaghah_tier1.json (9.1 MB, all verses)
- text/quran_text.json (1.7 MB, 6,236 verses)
- metadata/chapter_metadata.json (23 KB, 114 chapters)
- metadata/tafsir_index.json (61 KB, 45 verses)
- metadata/asbab_nuzul_index.json (1.7 MB, 678 verses)

Output:
- data/quran_comprehensive.json (~100 MB estimated)

Structure: Chapter-centric with nested verses containing all data
Sparse data handling: Include null/[] for missing data
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict


def load_json(filepath):
    """Load JSON file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def parse_location(location_str):
    """
    Parse location string or dict to (chapter, verse, word, segment)
    Examples: "(1:1:2:1)", "1:1:2:1", {"chapter": 1, "verse": 1, "word": 2}
    """
    if isinstance(location_str, dict):
        return (
            location_str.get('chapter'),
            location_str.get('verse'),
            location_str.get('word'),
            location_str.get('segment')
        )

    # Remove parentheses if present
    location_str = location_str.strip('()')
    parts = location_str.split(':')

    # Pad with None if not enough parts
    while len(parts) < 4:
        parts.append(None)

    return tuple(int(p) if p and p != 'null' else None for p in parts[:4])


def main():
    print("=" * 70)
    print("Comprehensive Quran Data Generator")
    print("=" * 70)
    print()

    # Determine base directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    data_dir = os.path.join(base_dir, 'data')

    print(f"Base directory: {base_dir}")
    print(f"Data directory: {data_dir}")
    print()

    # Load all source files
    print("Loading source files...")

    print("  [1/10] Loading quran_text.json...")
    quran_text = load_json(os.path.join(data_dir, 'text', 'quran_text.json'))

    print("  [2/10] Loading chapter_metadata.json...")
    chapter_metadata = load_json(os.path.join(data_dir, 'metadata', 'chapter_metadata.json'))

    print("  [3/10] Loading morphology_flat_aligned.json...")
    morphology_data = load_json(os.path.join(data_dir, 'linguistic', 'morphology_flat_aligned.json'))

    print("  [4/10] Loading dependencies_full.json...")
    dependencies_data = load_json(os.path.join(data_dir, 'linguistic', 'dependencies_full.json'))

    print("  [5/10] Loading named_entities_full.json...")
    entities_data = load_json(os.path.join(data_dir, 'linguistic', 'named_entities_full.json'))

    print("  [6/10] Loading lemmas_dictionary.json...")
    lemmas_data = load_json(os.path.join(data_dir, 'linguistic', 'lemmas_dictionary.json'))

    print("  [7/10] Loading pause_marks.json...")
    pause_marks_data = load_json(os.path.join(data_dir, 'linguistic', 'pause_marks.json'))

    print("  [8/11] Loading balaghah_tier1.json...")
    balaghah_tier1 = load_json(os.path.join(data_dir, 'linguistic', 'balaghah_tier1.json'))

    print("  [9/11] Loading balaghah_tier2.json...")
    try:
        balaghah_tier2 = load_json(os.path.join(data_dir, 'linguistic', 'balaghah_tier2.json'))
        has_tier2 = True
        print("    (Tier 2 loaded successfully)")
    except (FileNotFoundError, SystemExit):
        balaghah_tier2 = None
        has_tier2 = False
        print("    (Tier 2 not found - using Tier 1 only)")

    print("  [10/13] Loading balaghah_advanced.json...")
    try:
        balaghah_advanced = load_json(os.path.join(data_dir, 'linguistic', 'balaghah_advanced.json'))
        has_advanced = True
        print("    (Advanced features loaded successfully)")
    except (FileNotFoundError, SystemExit):
        balaghah_advanced = None
        has_advanced = False
        print("    (Advanced features not found - using Tier 1-2 only)")

    print("  [11/13] Loading tafsir_index.json...")
    tafsir_data = load_json(os.path.join(data_dir, 'metadata', 'tafsir_index.json'))

    print("  [12/13] Loading asbab_nuzul_index.json...")
    asbab_data = load_json(os.path.join(data_dir, 'metadata', 'asbab_nuzul_index.json'))

    print("  [13/13] Loading translation_en.json...")
    try:
        translation_data = load_json(os.path.join(data_dir, 'text', 'translation_en.json'))
        has_translation = True
        print("    (English translation loaded)")
    except (FileNotFoundError, SystemExit):
        translation_data = None
        has_translation = False
        print("    (Translation not found - Arabic only)")

    print()
    print("All files loaded successfully!")
    print()

    # Index morphology by location
    print("Indexing morphology data...")
    morphology_index = defaultdict(list)
    for entry in morphology_data.get('morphology', []):
        loc = entry.get('location', {})
        chapter = loc.get('chapter')
        verse = loc.get('verse')
        word = loc.get('word')
        if chapter and verse and word:
            key = (chapter, verse, word)
            morphology_index[key].append(entry)

    # Index dependencies by child location
    print("Indexing dependencies data...")
    dependencies_index = defaultdict(list)
    for entry in dependencies_data.get('dependencies', []):
        child = entry.get('child', {})
        chapter = child.get('chapter')
        verse = child.get('verse')
        word = child.get('word')
        if chapter and verse and word:
            key = (chapter, verse, word)
            dependencies_index[key].append(entry)

    # Index entities by location
    print("Indexing named entities data...")
    entities_index = defaultdict(list)
    for entry in entities_data.get('entities', []):
        loc = entry.get('location', {}).get('start', {})
        chapter = loc.get('chapter')
        verse = loc.get('verse')
        word = loc.get('word')
        if chapter and verse and word:
            key = (chapter, verse, word)
            entities_index[key].append(entry)

    # Index pause marks by location
    print("Indexing pause marks data...")
    pause_marks_index = defaultdict(list)
    for entry in pause_marks_data.get('pause_marks', []):
        loc = entry.get('location', {})
        chapter = loc.get('chapter')
        verse = loc.get('verse')
        word = loc.get('word')
        if chapter and verse:
            # Some pause marks are chapter-level only
            if word:
                key = (chapter, verse, word)
            else:
                key = (chapter, verse)
            pause_marks_index[key].append(entry)

    # Index balaghah tier 1 by chapter
    print("Indexing balaghah tier 1 data...")
    balaghah_tier1_index = {}
    for chapter_data in balaghah_tier1.get('chapters', []):
        chapter_num = chapter_data.get('chapter')
        if chapter_num:
            balaghah_tier1_index[chapter_num] = chapter_data

    # Index balaghah tier 2 by chapter
    balaghah_tier2_index = {}
    if has_tier2:
        print("Indexing balaghah tier 2 data...")
        for chapter_data in balaghah_tier2.get('chapters', []):
            chapter_num = chapter_data.get('chapter')
            if chapter_num:
                balaghah_tier2_index[chapter_num] = chapter_data

    # Index balaghah advanced by chapter
    balaghah_advanced_index = {}
    if has_advanced:
        print("Indexing balaghah advanced data...")
        for chapter_data in balaghah_advanced.get('chapters', []):
            chapter_num = chapter_data.get('chapter')
            if chapter_num:
                balaghah_advanced_index[chapter_num] = chapter_data

    print()
    print("Building comprehensive structure...")
    print()

    # Build comprehensive structure
    comprehensive = {
        'metadata': {
            'version': '1.0',
            'generated': datetime.now().isoformat(),
            'sources': {
                'morphology': 'quranic-corpus-morphology-full.txt',
                'dependencies': 'quranic-corpus-dependencies-full.txt',
                'named_entities': 'quranic-corpus-named-entities-full.txt',
                'lemmas': 'quranic-corpus-lemmas.txt',
                'pause_marks': 'quranic-corpus-pause-marks.txt',
                'balaghah': 'Generated analysis (Tier 1: Saj\', Takrar, Jinas; Tier 2: Ma\'ani; Advanced: Iltifat, Wasl/Fasl, Muqabala, Isti\'anaf, Hadhf, Tafsir Context)',
                'quran_text': 'tanzil-quran-uthmani.xml (Tanzil project)',
                'translation_en': 'Sahih International (Tanzil.net)' if has_translation else 'Not available',
                'chapter_metadata': 'Compiled from multiple sources',
                'tafsir': 'Al-Qushairi Sufi Tafsir',
                'asbab_nuzul': 'Asbab al-Nuzul (Occasions of Revelation)'
            },
            'statistics': {
                'total_chapters': 114,
                'total_verses': 6236,
                'total_words': len(morphology_index),
                'total_morphology_segments': len(morphology_data.get('morphology', [])),
                'total_dependencies': len(dependencies_data.get('dependencies', [])),
                'total_entities': len(entities_data.get('entities', [])),
                'total_pause_marks': len(pause_marks_data.get('pause_marks', [])),
                'verses_with_tafsir': len(tafsir_data),
                'verses_with_asbab_nuzul': len(asbab_data),
                'balaghah_coverage': '100% (all verses)'
            },
            'data_completeness': {
                'morphology': '100%',
                'dependencies': '100%',
                'quran_text': '100%',
                'chapter_metadata': '100%',
                'balaghah': '100%',
                'named_entities': '~0.3% (sparse)',
                'pause_marks': '~70% (sparse)',
                'tafsir': '0.7% (45 verses only)',
                'asbab_nuzul': '10.9% (678 verses)'
            }
        },
        'chapters': []
    }

    # Process each chapter
    for chapter_info in quran_text.get('chapters', []):
        chapter_num = chapter_info.get('number')

        print(f"  Processing Chapter {chapter_num}...")

        # Get chapter metadata
        chapter_meta = chapter_metadata.get(str(chapter_num), {})

        # Get balaghah data for chapter (all tiers)
        chapter_balaghah_tier1 = balaghah_tier1_index.get(chapter_num, {})
        balaghah_tier1_verses = {v['verse_number']: v for v in chapter_balaghah_tier1.get('verses', [])}

        chapter_balaghah_tier2 = balaghah_tier2_index.get(chapter_num, {})
        balaghah_tier2_verses = {v['verse_number']: v for v in chapter_balaghah_tier2.get('verses', [])} if has_tier2 else {}

        chapter_balaghah_advanced = balaghah_advanced_index.get(chapter_num, {})
        balaghah_advanced_verses = {v['verse_number']: v for v in chapter_balaghah_advanced.get('verses', [])} if has_advanced else {}
        balaghah_advanced_iltifat = chapter_balaghah_advanced.get('iltifat', []) if has_advanced else []

        chapter = {
            'chapter_number': chapter_num,
            'name_arabic': chapter_meta.get('name_arabic', chapter_info.get('name')),
            'revelation_place': chapter_meta.get('revelation_place'),
            'revelation_order': chapter_meta.get('revelation_order'),
            'verses_count': chapter_info.get('verses_count', len(chapter_info.get('verses', []))),
            'pages_count': chapter_meta.get('pages_count'),
            'verses': []
        }

        # Process each verse in chapter
        for verse_info in chapter_info.get('verses', []):
            verse_num = verse_info.get('number')

            # Get tafsir if available
            tafsir_key = f"{chapter_num}:{verse_num}"
            tafsir = tafsir_data.get(tafsir_key, None)

            # Get asbab nuzul if available
            asbab = asbab_data.get(tafsir_key, [])

            # Get balaghah for this verse (merge all tiers)
            verse_balaghah_tier1 = balaghah_tier1_verses.get(verse_num, {})
            verse_balaghah_tier2 = balaghah_tier2_verses.get(verse_num, {})
            verse_balaghah_advanced = balaghah_advanced_verses.get(verse_num, {})

            # Merge tiers into single balaghah object
            balaghah_merged = {}

            # Add Tier 1 features: Saj', Takrar, Jinas
            # Transform saj data to flattened format
            if verse_balaghah_tier1.get('saj'):
                saj_data = verse_balaghah_tier1['saj']
                if saj_data.get('in_saj_sequence'):
                    balaghah_merged['saj'] = {
                        'pattern': saj_data.get('ending_pattern'),
                        'sequence_length': saj_data.get('saj_sequence', {}).get('sequence_length'),
                        'position_in_sequence': saj_data.get('saj_sequence', {}).get('position_in_sequence')
                    }

            if verse_balaghah_tier1.get('takrar'):
                balaghah_merged['takrar'] = verse_balaghah_tier1['takrar']

            if verse_balaghah_tier1.get('jinas'):
                balaghah_merged['jinas'] = verse_balaghah_tier1['jinas']

            # Add Tier 2 if available
            if has_tier2:
                balaghah_merged['maani'] = verse_balaghah_tier2.get('maani', {})

            # Add Advanced features if available
            if has_advanced:
                # Add verse-level advanced features
                if verse_balaghah_advanced.get('wasl_fasl'):
                    balaghah_merged['wasl_fasl'] = verse_balaghah_advanced['wasl_fasl']
                if verse_balaghah_advanced.get('muqabala'):
                    balaghah_merged['muqabala'] = verse_balaghah_advanced['muqabala']
                if verse_balaghah_advanced.get('istianaf'):
                    balaghah_merged['istianaf'] = verse_balaghah_advanced['istianaf']
                if verse_balaghah_advanced.get('hadhf'):
                    balaghah_merged['hadhf'] = verse_balaghah_advanced['hadhf']
                # NOTE: tafsir_context is created AFTER merge, not copied here

                # Add chapter-level iltifat patterns relevant to this verse
                verse_iltifat = [pattern for pattern in balaghah_advanced_iltifat
                               if pattern.get('context', {}).get('verse_range', '').startswith(f"{verse_num}-")
                               or pattern.get('detected_pattern', {}).get('from_verse') == verse_num
                               or pattern.get('detected_pattern', {}).get('to_verse') == verse_num]
                if verse_iltifat:
                    balaghah_merged['iltifat'] = verse_iltifat

            # Create comprehensive tafsir_context AFTER all features are merged
            # This ensures the summary includes ALL detected features (tier 1, 2, and 3)
            if verse_balaghah_advanced.get('tafsir_context'):
                # Get the original tafsir_context to preserve asbab_nuzul info
                original_context = verse_balaghah_advanced['tafsir_context']
                # Re-summarize features using the COMPLETE merged balaghah
                from analyze_balaghah_advanced import TafsirContextIntegrator
                integrator = TafsirContextIntegrator(asbab_data, chapter_metadata)
                updated_context = integrator.integrate_context(chapter_num, verse_num, balaghah_merged)
                balaghah_merged['tafsir_context'] = updated_context

            # Get English translation if available
            translation_key = f"{chapter_num}:{verse_num}"
            translation_text = None
            if has_translation and translation_data:
                translation_text = translation_data.get('translations', {}).get(translation_key)

            verse = {
                'verse_number': verse_num,
                'text': verse_info.get('text'),
                'translation_en': translation_text,
                'words': [],
                'tafsir': tafsir,
                'asbab_nuzul': asbab if asbab else [],
                'balaghah': balaghah_merged
            }

            # Find all words in this verse (get unique word numbers from morphology)
            word_numbers = set()
            for key in morphology_index.keys():
                if key[0] == chapter_num and key[1] == verse_num:
                    word_numbers.add(key[2])

            # Split verse text to get word texts
            verse_text = verse_info.get('text', '')
            word_texts = verse_text.strip().split() if verse_text else []

            # Process each word
            for word_num in sorted(word_numbers):
                key = (chapter_num, verse_num, word_num)

                # Get word text from split (word_num is 1-indexed)
                word_text = word_texts[word_num - 1] if word_num <= len(word_texts) else ''

                # Get morphology segments for this word
                morphology_segments = morphology_index.get(key, [])

                # Get dependencies for this word
                dependencies = dependencies_index.get(key, [])

                # Get entities for this word
                entities = entities_index.get(key, [])

                # Get pause marks for this word
                pause_marks = pause_marks_index.get(key, [])

                # Build word structure
                word = {
                    'word_number': word_num,
                    'text': word_text,  # Add word text
                    'morphology': morphology_segments,
                    'dependencies': dependencies,
                    'entities': entities if entities else [],
                    'pause_marks': pause_marks if pause_marks else []
                }

                verse['words'].append(word)

            # Add verse-level pause marks (if any)
            verse_pause_key = (chapter_num, verse_num)
            verse_pause_marks = pause_marks_index.get(verse_pause_key, [])
            if verse_pause_marks:
                verse['verse_level_pause_marks'] = verse_pause_marks

            chapter['verses'].append(verse)

        comprehensive['chapters'].append(chapter)

    print()
    print("Writing comprehensive JSON file...")

    output_path = os.path.join(data_dir, 'quran_comprehensive.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comprehensive, f, ensure_ascii=False, indent=2)

    # Get file size
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)

    print()
    print("=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"Output: {output_path}")
    print(f"Size: {file_size_mb:.1f} MB")
    print()
    print("Comprehensive Quran data file generated successfully!")
    print()


if __name__ == '__main__':
    main()
