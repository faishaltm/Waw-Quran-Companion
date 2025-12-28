#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import Counter

def analyze_chapter(filename):
    """Extract balaghah patterns from a chapter JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chapter_num = data['chapter']
    print(f"\n{'='*60}")
    print(f"CHAPTER {chapter_num} BALAGHAH ANALYSIS")
    print(f"{'='*60}\n")

    # Extract saj' patterns
    saj_patterns = {}
    iltifat_patterns = []
    hadhf_patterns = []
    muqabala_patterns = []
    roots_mentioned = []

    for verse in data['verses']:
        verse_num = verse['verse_number']
        analysis = verse.get('analysis', '')

        # Parse saj' patterns
        if 'saj\' (rhymed prose) with the pattern' in analysis:
            pattern_start = analysis.find("pattern '") + 9
            pattern_end = analysis.find("'", pattern_start)
            if pattern_end > pattern_start:
                pattern = analysis[pattern_start:pattern_end]
                saj_patterns[pattern] = saj_patterns.get(pattern, 0) + 1

        # Parse iltifat
        if 'iltifat' in analysis.lower():
            iltifat_patterns.append(f"v{verse_num}: {analysis[analysis.find('iltifat'):analysis.find('.', analysis.find('iltifat'))]}")

        # Parse hadhf
        if 'hadhf' in analysis.lower():
            hadhf_patterns.append(verse_num)

        # Parse muqabala
        if 'muqabala' in analysis.lower():
            muqabala_patterns.append(verse_num)

        # Collect roots
        root_reps = verse.get('root_repetitions', {})
        for root in root_reps.keys():
            roots_mentioned.append(root)

    # Print results
    print("SAJ' PATTERNS:")
    print("-" * 40)
    for pattern, count in sorted(saj_patterns.items(), key=lambda x: -x[1]):
        print(f"  '{pattern}': {count} verses")

    print("\n\nTOP 20 RECURRING ROOTS:")
    print("-" * 40)
    root_counts = Counter(roots_mentioned)
    for root, count in root_counts.most_common(20):
        print(f"  {root}: {count} mentions")

    print("\n\nILTIFAT PATTERNS:")
    print("-" * 40)
    if iltifat_patterns:
        for pattern in iltifat_patterns[:10]:  # First 10
            print(f"  {pattern}")
        if len(iltifat_patterns) > 10:
            print(f"  ... and {len(iltifat_patterns) - 10} more")
    else:
        print("  None found")

    print("\n\nHADHF (ELLIPSIS) OCCURRENCES:")
    print("-" * 40)
    print(f"  Found in {len(hadhf_patterns)} verses: {hadhf_patterns[:20]}")
    if len(hadhf_patterns) > 20:
        print(f"  ... and {len(hadhf_patterns) - 20} more")

    print("\n\nMUQABALA (ANTITHESIS) OCCURRENCES:")
    print("-" * 40)
    print(f"  Found in {len(muqabala_patterns)} verses: {muqabala_patterns}")

    return {
        'saj_patterns': saj_patterns,
        'top_roots': root_counts.most_common(20),
        'iltifat_count': len(iltifat_patterns),
        'hadhf_count': len(hadhf_patterns),
        'muqabala_count': len(muqabala_patterns)
    }

if __name__ == '__main__':
    files = [
        'verse_68_1-52_v2.json',
        'verse_69_1-52_v2.json'
    ]

    for filename in files:
        analyze_chapter(filename)
