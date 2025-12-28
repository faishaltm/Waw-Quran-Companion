#!/usr/bin/env python3
"""
Morphology Alignment Engine - Using GitHub Ground Truth

PROPER SOLUTION:
- Uses mustafa0x/quran-morphology from GitHub
- File format: CHAPTER:VERSE:WORD:SEGMENT with explicit location markers
- Strategy: Group segments by word, align with Tanzil canonically

DATA SOURCE:
- GitHub: https://github.com/mustafa0x/quran-morphology
- File: quran-morphology.txt (130,030 lines with segments)
- Format: CHAPTER:VERSE:WORD:SEGMENT\tARBIC\tPOS\tFEATURES

APPROACH:
1. Parse GitHub morphology file (segment-level)
2. Group segments by (chapter, verse, word)
3. Extract word-level features (ROOT, POS, LEM from stem segment)
4. Align with Tanzil tokens using explicit word indices
5. Validate against known patterns (Qul in Surah Mulk)

Author: Claude Code
Date: 2025-11-10
Status: Long-term proper solution
"""

import json
import os
import re
from typing import Dict, List, Tuple
from collections import defaultdict


# ============================================================================
# Parse GitHub morphology file
# ============================================================================

def parse_github_morphology_line(line: str) -> Dict:
    """
    Parse one line from GitHub morphology file

    Format: CHAPTER:VERSE:WORD:SEGMENT\tARBIC\tPOS\tFEATURES
    Example: 67:23:1:1\tقُلْ\tV\tIMPV|VF:1|ROOT:قول|LEM:قالَ|2MS

    Returns:
        {
            'chapter': int,
            'verse': int,
            'word': int,
            'segment': int,
            'surface': str,
            'pos_tag': str,
            'features_raw': str,
            'features': {...}  # Parsed features dict
        }
    """
    parts = line.strip().split('\t')
    if len(parts) != 4:
        return None

    location, surface, pos_tag, features_raw = parts

    # Parse location
    loc_parts = location.split(':')
    if len(loc_parts) != 4:
        return None

    chapter, verse, word, segment = map(int, loc_parts)

    # Parse features
    features = parse_features(features_raw)

    return {
        'chapter': chapter,
        'verse': verse,
        'word': word,
        'segment': segment,
        'surface': surface,
        'pos_tag': pos_tag,
        'features_raw': features_raw,
        'features': features
    }


def parse_features(features_raw: str) -> Dict:
    """
    Parse feature string into structured dict

    Example: "IMPV|VF:1|ROOT:قول|LEM:قالَ|2MS"

    Returns:
        {
            'root': 'قول',
            'lemma': 'قالَ',
            'pos': 'V',
            'tense': 'IMPV',
            'person': '2',
            'gender': 'M',
            'number': 'S',
            ...
        }
    """
    features = {}
    tokens = features_raw.split('|')

    for token in tokens:
        if ':' in token:
            key, value = token.split(':', 1)
            key_lower = key.lower()

            if key_lower == 'root':
                features['root'] = value
            elif key_lower == 'lem':
                features['lemma'] = value
            elif key_lower == 'vf':
                features['verb_form'] = value
            elif key_lower == 'fam':
                features['family'] = value
        else:
            # Standalone tags
            if token in ['IMPV', 'PERF', 'IMPF']:
                features['tense'] = token
            elif token in ['ACT_PCPL', 'PASS_PCPL']:
                features['participle'] = token
            elif token in ['NOM', 'ACC', 'GEN']:
                features['case'] = token
            elif token in ['INDEF', 'DEF']:
                features['definiteness'] = token
            elif token in ['M', 'F']:
                features['gender'] = token
            elif token in ['S', 'D', 'P']:
                features['number'] = token
            elif re.match(r'^[123](M|F)(S|D|P)$', token):
                # Person-Gender-Number (e.g., 2MS, 3FP)
                features['person'] = token[0]
                features['gender'] = token[1]
                features['number'] = token[2]
            elif token in ['PRON', 'DET', 'REL', 'PN', 'CONJ', 'P']:
                features['category'] = token

    return features


def load_github_morphology(file_path: str) -> Dict[Tuple[int, int, int], List[Dict]]:
    """
    Load GitHub morphology and group by (chapter, verse, word)

    Args:
        file_path: Path to quran-morphology.txt

    Returns:
        {
            (chapter, verse, word): [
                {segment: 1, surface: '...', features: {...}},
                {segment: 2, surface: '...', features: {...}},
                ...
            ]
        }
    """
    print("=" * 80)
    print("LOADING GITHUB MORPHOLOGY")
    print("=" * 80)
    print()

    by_word = defaultdict(list)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            entry = parse_github_morphology_line(line)
            if entry:
                key = (entry['chapter'], entry['verse'], entry['word'])
                by_word[key].append(entry)

            if line_num % 10000 == 0:
                print(f"  Processed {line_num:,} lines...")

    print(f"  Total lines: {line_num:,}")
    print(f"  Total words: {len(by_word):,}")
    print()

    return dict(by_word)


# ============================================================================
# Collapse segments to word-level
# ============================================================================

def collapse_segments_to_word(segments: List[Dict]) -> Dict:
    """
    Collapse multiple segments into a single word entry

    Strategy:
    - Concatenate surfaces
    - Extract ROOT, LEM, POS from stem (typically segment with ROOT)
    - Preserve all features from all segments

    Args:
        segments: List of segment dicts for one word

    Returns:
        {
            'surface': str,  # Concatenated surface
            'root': str,
            'lemma': str,
            'pos': str,
            'features': {...},
            'segments': [...]  # Original segments
        }
    """
    # Concatenate surfaces
    surface = ''.join(seg['surface'] for seg in segments)

    # Find stem segment (usually has ROOT)
    stem_segment = None
    for seg in segments:
        if 'root' in seg['features']:
            stem_segment = seg
            break

    # If no stem found, use first segment
    if stem_segment is None:
        stem_segment = segments[0]

    # Extract features
    root = stem_segment['features'].get('root', None)
    lemma = stem_segment['features'].get('lemma', None)
    pos = stem_segment['pos_tag']

    # Merge all features from all segments
    merged_features = {}
    for seg in segments:
        merged_features.update(seg['features'])

    return {
        'surface': surface,
        'root': root,
        'lemma': lemma,
        'pos': pos,
        'features': merged_features,
        'segments': segments
    }


# ============================================================================
# Build Tanzil index
# ============================================================================

def build_tanzil_index(quran_data: dict) -> Dict:
    """
    Build Tanzil index with locations

    Returns:
        {
            'by_verse': {(chapter, verse): [tokens...]},
            'by_location': {(chapter, verse, word): token},
            'total_words': int
        }
    """
    print("=" * 80)
    print("BUILDING TANZIL INDEX")
    print("=" * 80)
    print()

    by_verse = {}
    by_location = {}
    total_words = 0

    for chapter in quran_data['chapters']:
        chapter_num = chapter['number']
        for verse in chapter['verses']:
            verse_num = verse['number']
            tokens = verse['text'].strip().split()

            by_verse[(chapter_num, verse_num)] = tokens

            for word_idx, token in enumerate(tokens, start=1):
                by_location[(chapter_num, verse_num, word_idx)] = token
                total_words += 1

    print(f"  Total words: {total_words:,}")
    print(f"  Total verses: {len(by_verse):,}")
    print()

    return {
        'by_verse': by_verse,
        'by_location': by_location,
        'total_words': total_words
    }


# ============================================================================
# Align morphology with Tanzil
# ============================================================================

def build_aligned_morphology(
    tanzil_index: Dict,
    github_morphology: Dict[Tuple[int, int, int], List[Dict]]
) -> Dict:
    """
    Build aligned morphology using explicit word indices

    Strategy:
    - For each (chapter, verse, word) in GitHub morphology
    - Collapse segments to word-level
    - Map to Tanzil token at same location
    - Store with explicit location markers

    Returns:
        {
            'by_location': {(chapter, verse, word): entry},
            'chapters': [...],
            'metadata': {...}
        }
    """
    print("=" * 80)
    print("BUILDING ALIGNED MORPHOLOGY")
    print("=" * 80)
    print()

    by_location = {}
    chapters_data = defaultdict(lambda: defaultdict(list))

    aligned_count = 0
    missing_count = 0

    for (chapter, verse, word), segments in sorted(github_morphology.items()):
        # Collapse segments to word-level
        word_entry = collapse_segments_to_word(segments)

        # Get Tanzil token
        tanzil_token = tanzil_index['by_location'].get((chapter, verse, word), None)

        if tanzil_token is None:
            print(f"  WARNING: No Tanzil token for {chapter}:{verse}:{word}")
            missing_count += 1
            continue

        # Build entry
        entry = {
            'location': {
                'chapter': chapter,
                'verse': verse,
                'word': word
            },
            'surface_tanzil': tanzil_token,
            'surface_corpus': word_entry['surface'],
            'morphology': {
                'root': word_entry['root'],
                'lemma': word_entry['lemma'],
                'pos': word_entry['pos'],
                'features': word_entry['features']
            }
        }

        by_location[(chapter, verse, word)] = entry
        chapters_data[chapter][verse].append(entry)
        aligned_count += 1

        if aligned_count % 10000 == 0:
            print(f"  Aligned {aligned_count:,} words...")

    print(f"  Total aligned: {aligned_count:,}")
    print(f"  Missing: {missing_count}")
    print()

    # Build hierarchical structure
    chapters = []
    for chapter_num in sorted(chapters_data.keys()):
        verses = []
        for verse_num in sorted(chapters_data[chapter_num].keys()):
            verses.append({
                'number': verse_num,
                'words': chapters_data[chapter_num][verse_num]
            })

        chapters.append({
            'number': chapter_num,
            'verses': verses
        })

    result = {
        'by_location': by_location,
        'chapters': chapters,
        'metadata': {
            'total_aligned': aligned_count,
            'total_missing': missing_count,
            'source_text': 'tanzil-uthmani',
            'source_morphology': 'mustafa0x/quran-morphology (GitHub)',
            'morphology_version': 'v0.4 (enhanced)',
            'alignment_method': 'word-level-explicit-indices',
            'date': '2025-11-10',
            'status': 'PROPER_SOLUTION'
        }
    }

    return result


# ============================================================================
# Main
# ============================================================================

def main():
    """Main workflow"""
    print("\n")
    print("=" * 80)
    print("MORPHOLOGY ALIGNMENT - PROPER SOLUTION")
    print("Using GitHub Ground Truth (mustafa0x/quran-morphology)")
    print("=" * 80)
    print()

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')

    quran_path = os.path.join(project_root, 'data', 'text', 'quran_text.json')
    github_morph_path = os.path.join(project_root, 'sources', 'quranic-corpus-full',
                                      'quran-morphology-github.txt')
    output_path = os.path.join(project_root, 'data', 'linguistic',
                                'morphology_aligned.json')

    # Load Tanzil
    print("Loading Tanzil text...")
    with open(quran_path, 'r', encoding='utf-8') as f:
        quran_data = json.load(f)
    print()

    # Build Tanzil index
    tanzil_index = build_tanzil_index(quran_data)

    # Load GitHub morphology
    github_morphology = load_github_morphology(github_morph_path)

    # Build aligned
    aligned = build_aligned_morphology(tanzil_index, github_morphology)

    # Save
    print("Saving morphology_aligned.json...")
    output_data = {
        'morphology': aligned['chapters'],
        'metadata': aligned['metadata']
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  Saved to: {output_path}")
    print()

    print("=" * 80)
    print("ALIGNMENT COMPLETE")
    print("=" * 80)
    print()
    print(f"Total aligned: {aligned['metadata']['total_aligned']:,} words")
    print(f"Total missing: {aligned['metadata']['total_missing']} words")
    print()
    print("Next: Run test_morphology_alignment.py to validate")
    print()

    return aligned


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
