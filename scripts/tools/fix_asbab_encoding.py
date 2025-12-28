#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix encoding issues in asbab nuzul source file

Replaces corrupted surah names with correct transliterations.
"""

import re

# Mapping of diacritic-heavy transliterations to plain ASCII transliterations
# These use circumflex (â, î, û) to mark long vowels, but we need plain ASCII
# The source file is valid UTF-8, but these characters cause issues in JSON parsing
CORRECTIONS = {
    # Replace â (a with circumflex) with plain 'a'
    'Al-Fâtihah': 'Al-Fatihah',  # Chapter 1
    'Al-Baqârah': 'Al-Baqarah',  # Chapter 2
    'Al-Anfâl': 'Al-Anfal',  # Chapter 8
    'Al-Ahzâb': 'Al-Ahzab',  # Chapter 33
    'Al-Hujurât': 'Al-Hujurat',  # Chapter 49
    'Al-Mujâdilah': 'Al-Mujadilah',  # Chapter 58

    # Replace û (u with circumflex) with plain 'u'
    'Ar-Rûm': 'Ar-Rum',  # Chapter 30

    # Replace full diacritic versions with plain versions
    'Tâ-Hâ': 'Ta-Ha',  # Chapter 20
}

def fix_asbab_encoding(source_path, output_path=None):
    """
    Fix encoding issues in asbab nuzul markdown file

    Args:
        source_path: Path to source markdown file
        output_path: Path to save fixed file (defaults to source_path)
    """
    if output_path is None:
        output_path = source_path

    print('='*70)
    print('Fixing Asbab Nuzul Encoding Issues')
    print('='*70)
    print()
    print(f'Reading from: {source_path}')

    # Read source file
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_applied = 0

    # Apply corrections (literal string replacements)
    for wrong, correct in CORRECTIONS.items():
        count = content.count(wrong)
        if count > 0:
            print(f'Fixing: "{wrong}" -> "{correct}" ({count} occurrences)')
            content = content.replace(wrong, correct)
            fixes_applied += count

    # Additional fix: normalize any remaining replacement characters
    if '�' in content:
        # This is a fallback - should not happen if corrections above are complete
        print('Warning: Found remaining replacement characters (�)')
        print('These may need manual review')

    print()
    print(f'Total fixes applied: {fixes_applied}')

    if fixes_applied > 0:
        print(f'\nWriting fixed content to: {output_path}')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Done!')
    else:
        print('No fixes needed - file is already correct.')

    print('='*70)

    return fixes_applied


if __name__ == '__main__':
    import sys
    import os

    # Default paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    source_path = os.path.join(project_root, 'sources', 'asbabun_nuzul', 'asbabun_nuzul.md')

    # Run fix
    fixes_applied = fix_asbab_encoding(source_path)

    sys.exit(0 if fixes_applied >= 0 else 1)
