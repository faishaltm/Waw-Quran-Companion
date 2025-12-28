#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse Lane's Lexicon Root Words from Internet Archive text file.
Extracts root words and their English meanings.

Input: lanes-lexicon-roots.txt
Output: lanes_lexicon_roots.json
"""

import re
import json
from pathlib import Path

def parse_lanes_lexicon(input_file):
    """
    Parse Lane's Lexicon text file to extract roots and meanings.

    Format example:
    Alif-Ba-Dal = to last/continue, remain, evermore, endure, perpetual,
    lasting/everlasting, unsocial/unfamiliar, never (when used in negative construction).

    abad n.m. 2:95, 4:57...

    Lane's Lexicon, Volume 1, pages: 41, 42
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match root entries
    # Captures: "Alif-Ba-Dal = meaning text"
    root_pattern = re.compile(
        r'^([A-Z][a-z]+-[A-Z][a-z]+-[A-Z][a-z]+(?:-[A-Z][a-z]+)?)\s*=\s*(.+?)(?=\n\n|\nLane\'s Lexicon|\n[a-z]+\s+(?:n\.|vb\.|pcple\.))',
        re.MULTILINE | re.DOTALL
    )

    roots = []
    matches = root_pattern.finditer(content)

    for match in matches:
        root_trans = match.group(1).strip()  # e.g., "Alif-Ba-Dal"
        meaning = match.group(2).strip()

        # Clean up meaning - remove excessive whitespace and newlines
        meaning = re.sub(r'\s+', ' ', meaning)
        meaning = meaning.replace('\n', ' ').strip()

        # Remove trailing commas/periods
        meaning = meaning.rstrip('.,')

        roots.append({
            'transliteration': root_trans,
            'meaning': meaning,
            'arabic_root': None  # Will be mapped later
        })

    return roots

def save_to_json(roots, output_file):
    """Save parsed roots to JSON file."""
    data = {
        'metadata': {
            'source': 'Lane\'s Lexicon via Internet Archive',
            'source_url': 'https://archive.org/details/quranic-words-with-reference-to-verses',
            'description': 'Quranic root words with meanings from Lane\'s Lexicon',
            'total_roots': len(roots),
            'format': 'English transliteration with meanings',
            'note': 'Arabic roots need to be mapped from transliterations'
        },
        'roots': roots
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(roots)} roots to {output_file}")

def main():
    # File paths
    base_dir = Path(__file__).parent.parent.parent
    input_file = base_dir / 'sources' / 'lanes-lexicon-roots.txt'
    output_file = base_dir / 'data' / 'linguistic' / 'lanes_lexicon_roots.json'

    print("Parsing Lane's Lexicon...")
    print(f"   Input: {input_file}")

    # Parse the file
    roots = parse_lanes_lexicon(input_file)

    print(f"Extracted {len(roots)} root entries")

    # Show sample
    print("\nSample entries:")
    for root in roots[:5]:
        print(f"\n{root['transliteration']}")
        print(f"  -> {root['meaning'][:100]}...")

    # Save to JSON
    print(f"\nSaving to: {output_file}")
    save_to_json(roots, output_file)

    print("\nDone!")

if __name__ == '__main__':
    main()
