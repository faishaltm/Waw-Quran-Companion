#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert quran-morphology-github.txt (TSV format with Unicode Arabic)
to structured JSON format for integration with main database.

Input Format:  LOCATION | ARABIC | POS | FEATURES
Example:       1:1:1:2	سْمِ	N	ROOT:سمو|LEM:اسْم|M|GEN

Output Format: Hierarchical JSON with chapter → verse → word → segments
"""

import json
import re
from pathlib import Path


def parse_location(location_str):
    """Parse location string 'chapter:verse:word:segment' into dict."""
    parts = location_str.strip().split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid location format: {location_str}")

    return {
        'chapter': int(parts[0]),
        'verse': int(parts[1]),
        'word': int(parts[2]),
        'segment': int(parts[3])
    }


def parse_features(features_str):
    """Parse pipe-delimited feature string into structured dict."""
    if not features_str or features_str.strip() == '':
        return {}

    features = {}
    parts = features_str.strip().split('|')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Handle key:value pairs (ROOT:, LEM:, VF:, MOOD:, FAM:)
        if ':' in part:
            key, value = part.split(':', 1)
            features[key.lower()] = value
        else:
            # Handle standalone flags (PREF, SUFF, DET, CONJ, NEG, etc.)
            features[part.lower()] = True

    return features


def arabic_to_buckwalter_simple(arabic_text):
    """
    Simple Arabic to Buckwalter transliteration.
    For compatibility with existing codebase.

    Note: This is a simplified version. For full accuracy,
    use the existing buckwalter conversion utilities.
    """
    # Mapping of common Arabic characters to Buckwalter
    mapping = {
        'ا': 'A', 'أ': '>', 'إ': '<', 'آ': '|', 'ؤ': '&', 'ئ': '}',
        'ب': 'b', 'ت': 't', 'ث': 'v', 'ج': 'j', 'ح': 'H', 'خ': 'x',
        'د': 'd', 'ذ': '*', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': '$',
        'ص': 'S', 'ض': 'D', 'ط': 'T', 'ظ': 'Z', 'ع': 'E', 'غ': 'g',
        'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
        'ه': 'h', 'و': 'w', 'ي': 'y', 'ة': 'p', 'ى': 'Y',
        'َ': 'a', 'ُ': 'u', 'ِ': 'i', 'ً': 'F', 'ٌ': 'N', 'ٍ': 'K',
        'ْ': 'o', 'ّ': '~', 'ٰ': '`', 'ٓ': 'M', 'ٔ': '#',
        'ل': 'l', 'ال': 'Al', ' ': ' '
    }

    result = []
    for char in arabic_text:
        result.append(mapping.get(char, char))

    return ''.join(result)


def convert_github_morphology(input_file, output_file):
    """
    Convert github morphology TSV to hierarchical JSON.

    Structure:
    {
        "morphology": {
            "1": {  // chapter number
                "1": {  // verse number
                    "1": [  // word number
                        {
                            "segment": 1,
                            "arabic": "بِ",
                            "buckwalter": "bi",
                            "pos": "P",
                            "features": {
                                "p": true,
                                "pref": true,
                                "lem": "ب"
                            }
                        },
                        ...
                    ]
                }
            }
        },
        "metadata": {
            "source": "quran-morphology-github.txt",
            "total_segments": 77429,
            "format": "segment-level"
        }
    }
    """
    print(f"Reading from: {input_file}")

    morphology_data = {}
    total_segments = 0
    errors = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Parse tab-separated columns
            parts = line.split('\t')
            if len(parts) != 4:
                errors.append(f"Line {line_num}: Expected 4 columns, got {len(parts)}")
                continue

            location_str, arabic_text, pos, features_str = parts

            try:
                # Parse location
                loc = parse_location(location_str)
                chapter = str(loc['chapter'])
                verse = str(loc['verse'])
                word = str(loc['word'])
                segment = loc['segment']

                # Parse features
                features = parse_features(features_str)

                # Convert Arabic to Buckwalter (simplified)
                buckwalter = arabic_to_buckwalter_simple(arabic_text)

                # Build hierarchical structure
                if chapter not in morphology_data:
                    morphology_data[chapter] = {}
                if verse not in morphology_data[chapter]:
                    morphology_data[chapter][verse] = {}
                if word not in morphology_data[chapter][verse]:
                    morphology_data[chapter][verse][word] = []

                # Add segment
                segment_data = {
                    'segment': segment,
                    'arabic': arabic_text,
                    'buckwalter': buckwalter,
                    'pos': pos,
                    'features': features
                }

                morphology_data[chapter][verse][word].append(segment_data)
                total_segments += 1

                # Progress indicator
                if total_segments % 10000 == 0:
                    print(f"Processed {total_segments} segments...")

            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
                continue

    print(f"\nTotal segments processed: {total_segments}")

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    # Build final output structure
    output_data = {
        'morphology': morphology_data,
        'metadata': {
            'source': 'quran-morphology-github.txt',
            'total_segments': total_segments,
            'format': 'segment-level',
            'chapters': len(morphology_data),
            'note': 'Hierarchical structure: chapter → verse → word → segments array'
        }
    }

    # Write to JSON
    print(f"\nWriting to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Get file size
    file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)
    print(f"Output file size: {file_size_mb:.2f} MB")

    return total_segments, len(errors)


def main():
    """Main execution."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / 'sources' / 'quranic-corpus-full' / 'quran-morphology-github.txt'
    output_file = project_root / 'data' / 'linguistic' / 'morphology_segments.json'

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        return 1

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert
    total, errors = convert_github_morphology(input_file, output_file)

    print(f"\n{'='*60}")
    print(f"Conversion complete!")
    print(f"Total segments: {total}")
    print(f"Errors: {errors}")
    print(f"Output: {output_file}")
    print(f"{'='*60}")

    return 0


if __name__ == '__main__':
    exit(main())
