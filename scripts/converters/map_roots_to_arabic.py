#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map English transliterations from Lane's Lexicon to Arabic roots.
Uses morphology data to create the mapping.

Input: lanes_lexicon_roots.json, morphology_segments.json
Output: root_meanings.json
"""

import json
from pathlib import Path
from collections import defaultdict

# Transliteration mapping (from Lane's Lexicon format to Arabic)
TRANSLITERATION_MAP = {
    'Alif': 'ا',
    'Ba': 'ب',
    'Ta': 'ت',
    'Tha': 'ث',
    'Jiim': 'ج',
    'Ha': 'ح',
    'Kha': 'خ',
    'Dal': 'د',
    'Dhal': 'ذ',
    'Ra': 'ر',
    'Zain': 'ز',
    'Siin': 'س',
    'Shiin': 'ش',
    'Sad': 'ص',
    'Dad': 'ض',
    'Tay': 'ط',
    'Zay': 'ظ',
    'Ayn': 'ع',
    'Ghayn': 'غ',
    'Fa': 'ف',
    'Qaf': 'ق',
    'Kaf': 'ك',
    'Lam': 'ل',
    'Miim': 'م',
    'Nuun': 'ن',
    'Nun': 'ن',
    'Ha-2': 'ه',
    'Waw': 'و',
    'Ya': 'ي',
    'Hamza': 'ء'
}

def transliteration_to_arabic(trans):
    """
    Convert English transliteration to Arabic root.
    Example: "Alif-Ba-Dal" -> "أبد"
    """
    parts = trans.split('-')
    arabic_letters = []

    for part in parts:
        if part in TRANSLITERATION_MAP:
            arabic_letters.append(TRANSLITERATION_MAP[part])
        else:
            # Try to handle variants
            # Some transliterations might have slight variations
            return None

    if arabic_letters:
        return ''.join(arabic_letters)
    return None

def load_quran_roots(morphology_file):
    """Extract all unique roots from Quranic morphology data."""
    with open(morphology_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    roots = set()

    # Navigate the morphology structure: chapter -> verse -> word -> segments
    morphology = data.get('morphology', {})
    for chapter_data in morphology.values():
        for verse_data in chapter_data.values():
            for word_data in verse_data.values():
                for segment in word_data:
                    features = segment.get('features', {})
                    root = features.get('root')
                    if root:
                        roots.add(root)

    print(f"Found {len(roots)} unique roots in Quran")
    return roots

def normalize_root(root):
    """Normalize Arabic root for matching."""
    # Remove diacritics and normalize hamza variants
    normalized = root.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    normalized = normalized.replace('ة', 'ه')
    return normalized

def create_root_meanings(lanes_file, morphology_file, output_file):
    """Create final root meanings dictionary."""

    # Load Lane's Lexicon data
    print("Loading Lane's Lexicon...")
    with open(lanes_file, 'r', encoding='utf-8') as f:
        lanes_data = json.load(f)

    # Load Quran roots
    print("Loading Quran roots from morphology...")
    quran_roots = load_quran_roots(morphology_file)

    # Create normalized lookup
    quran_roots_normalized = {normalize_root(r): r for r in quran_roots}

    # Map transliterations to Arabic
    print("\nMapping transliterations to Arabic roots...")
    root_meanings = {}
    mapped_count = 0
    unmapped_count = 0

    for entry in lanes_data['roots']:
        trans = entry['transliteration']
        meaning = entry['meaning']

        # Convert transliteration to Arabic
        arabic_root = transliteration_to_arabic(trans)

        if arabic_root:
            # Check if this root exists in Quran
            normalized = normalize_root(arabic_root)
            if normalized in quran_roots_normalized:
                actual_root = quran_roots_normalized[normalized]
                root_meanings[actual_root] = {
                    'root': actual_root,
                    'transliteration': trans,
                    'meaning': meaning,
                    'source': 'Lane\'s Lexicon'
                }
                mapped_count += 1
            else:
                # Still save it even if not in Quran (for completeness)
                root_meanings[arabic_root] = {
                    'root': arabic_root,
                    'transliteration': trans,
                    'meaning': meaning,
                    'source': 'Lane\'s Lexicon',
                    'in_quran': False
                }
                unmapped_count += 1
        else:
            print(f"Could not map: {trans}")

    print(f"\nMapped {mapped_count} roots to Quranic roots")
    print(f"Additional {unmapped_count} roots not in Quran")

    # Create output
    output_data = {
        'metadata': {
            'source': 'Lane\'s Lexicon via Internet Archive',
            'morphology_source': 'Quranic Arabic Corpus morphology_segments.json',
            'description': 'Arabic roots with English meanings',
            'total_roots': len(root_meanings),
            'quranic_roots': mapped_count,
            'additional_roots': unmapped_count
        },
        'roots': root_meanings
    }

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output_file}")

    # Show samples
    print("\nSample mappings:")
    for i, (root, data) in enumerate(list(root_meanings.items())[:10]):
        in_quran = "" if data.get('in_quran', True) else " [NOT IN QURAN]"
        print(f"  {root} ({data['transliteration']}): {data['meaning'][:60]}...{in_quran}")
        if i >= 9:
            break

def main():
    base_dir = Path(__file__).parent.parent.parent
    lanes_file = base_dir / 'data' / 'linguistic' / 'lanes_lexicon_roots.json'
    morphology_file = base_dir / 'data' / 'linguistic' / 'morphology_segments.json'
    output_file = base_dir / 'data' / 'linguistic' / 'root_meanings.json'

    print("=" * 60)
    print("Mapping Lane's Lexicon Roots to Arabic")
    print("=" * 60)

    create_root_meanings(lanes_file, morphology_file, output_file)

    print("\nDone!")

if __name__ == '__main__':
    main()
