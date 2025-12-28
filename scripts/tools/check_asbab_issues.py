#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for issues in asbab nuzul source file
"""

import re
import json

# Read source file
with open('D:/Script/Project/quran/sources/asbabun_nuzul/asbabun_nuzul.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Standard surah names (first 10)
STANDARD_NAMES = {
    '1': 'Al-Fatihah',
    '2': 'Al-Baqarah',
    '3': "Ali 'Imran",
    '4': 'An-Nisa',
    '5': 'Al-Ma\'idah',
    '6': 'Al-An\'am',
    '7': 'Al-A\'raf',
    '8': 'Al-Anfal',
    '9': 'At-Tawbah',
    '10': 'Yunus'
}

# Find all surah headers and their positions
pattern = r'###\s+\(([^)]+)\)\s*\n\s*\[(\d+):(\d+)(?:-(\d+))?\]'
matches = list(re.finditer(pattern, content))

print('='*70)
print('Asbab Nuzul Source File Analysis')
print('='*70)
print()
print('First 15 entries (surah name vs chapter number):')
print()

issues_found = []

for i, match in enumerate(matches[:15], 1):
    surah_name = match.group(1)
    chapter = match.group(2)
    verse_start = match.group(3)
    verse_end = match.group(4) or verse_start

    print(f'{i}. Header: "{surah_name}"')
    print(f'   Verse ref: [{chapter}:{verse_start}-{verse_end}]')

    # Check encoding issues
    if '\ufffd' in surah_name or '\xe2' in surah_name or '�' in surah_name or ord(surah_name[4]) > 127:
        print(f'   [!] ENCODING ISSUE detected!')
        issues_found.append(('encoding', chapter, surah_name))

    # Check if name matches expected standard
    if chapter in STANDARD_NAMES:
        expected = STANDARD_NAMES[chapter]
        # Normalize for comparison (remove diacritics like â, ā)
        normalized = surah_name.replace('â', 'a').replace('ā', 'a').replace('ī', 'i').replace('ū', 'u')
        normalized = normalized.replace('�', 'a')  # Replace corrupted char

        if normalized != expected:
            print(f'   [!] NAME MISMATCH!')
            print(f'      Found: {normalized}')
            print(f'      Expected: {expected}')
            issues_found.append(('name_mismatch', chapter, surah_name, expected))

    print()

print('='*70)
print(f'Total issues found: {len(issues_found)}')
print('='*70)
