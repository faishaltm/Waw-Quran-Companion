#!/usr/bin/env python3
"""
Convert morphology_aligned.json (nested structure) to flat format
compatible with generate_comprehensive_quran.py

Input: data/linguistic/morphology_aligned.json (nested: chapters → verses → words)
Output: data/linguistic/morphology_flat_aligned.json (flat array with location keys)
"""

import json
import os

def main():
    print("=" * 70)
    print("Morphology Aligned Flattener")
    print("Converting nested structure to flat format")
    print("=" * 70)
    print()

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    input_file = os.path.join(base_dir, 'data', 'linguistic', 'morphology_aligned.json')
    output_file = os.path.join(base_dir, 'data', 'linguistic', 'morphology_flat_aligned.json')

    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()

    # Load nested morphology
    print("Loading morphology_aligned.json...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten structure
    print("Flattening structure...")
    flat_entries = []

    for chapter in data.get('morphology', []):
        chapter_num = chapter.get('number')

        for verse in chapter.get('verses', []):
            verse_num = verse.get('number')

            for word in verse.get('words', []):
                loc = word.get('location', {})
                morph = word.get('morphology', {})

                # Create flat entry compatible with generate_comprehensive_quran.py
                flat_entry = {
                    'location': {
                        'chapter': loc.get('chapter'),
                        'verse': loc.get('verse'),
                        'word': loc.get('word'),
                        'segment': None  # morphology_aligned doesn't have segments
                    },
                    'morphology': {
                        'root': morph.get('root'),
                        'lemma': morph.get('lemma'),
                        'pos': morph.get('pos'),
                        'features_raw': '',  # Not in aligned file
                        'features': morph.get('features', {})
                    },
                    'surface': word.get('surface_tanzil', ''),
                    'transliteration': ''  # Not in aligned file
                }

                flat_entries.append(flat_entry)

    print(f"  Created {len(flat_entries)} flat entries")

    # Create output structure
    output = {
        'morphology': flat_entries,
        'metadata': {
            'source': 'morphology_aligned.json (flattened)',
            'total_entries': len(flat_entries),
            'description': 'Morphology data with correct Tanzil alignment, converted to flat format'
        }
    }

    # Write output
    print(f"Writing {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Get file size
    size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print()
    print("=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print(f"File size: {size_mb:.1f} MB")
    print(f"Total entries: {len(flat_entries)}")
    print()

if __name__ == '__main__':
    main()
