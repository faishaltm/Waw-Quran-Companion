#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Comprehensive Quran Data with Multiple Tafsirs

Updates data/quran_comprehensive.json to include:
- Al-Kashshaf (Arabic) - rhetorical/balaghah tafsir
- Ma'arif al-Qur'an (English) - comprehensive modern tafsir
- Tafsir Ibn Kathir (English) - classical hadith-based tafsir

The tafsir field will be restructured from a single dict to support multiple sources:
{
  "tafsir": {
    "al_qushairi": {...},  # Legacy - keep for backward compatibility
    "kashshaf_arabic": {...},
    "maarif_en": {...},
    "ibn_kathir_en": {...}
  }
}
"""

import json
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
METADATA_DIR = DATA_DIR / "metadata"

COMPREHENSIVE_FILE = DATA_DIR / "quran_comprehensive.json"
KASHSHAF_FILE = METADATA_DIR / "tafsir_kashshaf_arabic.json"
MAARIF_FILE = METADATA_DIR / "tafsir_maarif_en.json"
IBN_KATHIR_FILE = METADATA_DIR / "tafsir_ibn_kathir_en.json"
OLD_TAFSIR_FILE = METADATA_DIR / "tafsir_index.json"  # Legacy Al-Qushairi


def load_json(filepath):
    """Load JSON file with UTF-8 encoding"""
    print(f"Loading {filepath.name}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_kashshaf_lookup(kashshaf_data):
    """
    Build lookup dict for Al-Kashshaf tafsir.

    Al-Kashshaf has multi-verse commentaries, so we need to handle verses_range.
    For verse 2:40, we check if it's in any entry's verses_range.

    Returns: {chapter: {verse: tafsir_entry}}
    """
    lookup = {}
    verse_index = kashshaf_data.get('verse_index', {})

    for chapter_str, verses_dict in verse_index.items():
        chapter = int(chapter_str)
        lookup[chapter] = {}

        for verse_str, entry in verses_dict.items():
            verse = int(verse_str)
            verses_range = entry.get('verses_range', [verse])

            # Map ALL verses in range to this entry
            for v in verses_range:
                lookup[chapter][v] = {
                    'text': entry.get('text', ''),
                    'verses_range': verses_range,
                    'source': 'Al-Kashshaf (Zamakhshari)',
                    'methodology': 'Rhetorical/Linguistic - Explains eloquence, word choice, and syntax'
                }

    return lookup


def build_simple_lookup(tafsir_data):
    """
    Build lookup dict for simple verse-level tafsirs (Ma'arif, Ibn Kathir).

    Returns: {chapter: {verse: text}}
    """
    lookup = {}
    verse_index = tafsir_data.get('verse_index', {})

    for chapter_str, verses_dict in verse_index.items():
        chapter = int(chapter_str)
        lookup[chapter] = {}

        for verse_str, text in verses_dict.items():
            verse = int(verse_str)
            lookup[chapter][verse] = text

    return lookup


def build_old_tafsir_lookup(old_tafsir_data):
    """
    Build lookup for legacy Al-Qushairi tafsir (45 verses).

    Returns: {chapter: {verse: entry}}
    """
    lookup = {}

    for entry in old_tafsir_data.get('tafsirs', []):
        chapter = entry.get('chapter')
        verse = entry.get('verse')

        if chapter and verse:
            if chapter not in lookup:
                lookup[chapter] = {}

            lookup[chapter][verse] = {
                'arabic': entry.get('arabic', ''),
                'tafsir': entry.get('tafsir', ''),
                'tafsir_source': entry.get('tafsir_source', 'Al-Qushairi')
            }

    return lookup


def update_comprehensive_data():
    """Main function to update comprehensive Quran data with tafsirs"""
    print("="*60)
    print("Update Comprehensive Quran Data with Tafsirs")
    print("="*60)
    print()

    # Load all data files
    print("STEP 1: Loading data files")
    print("-"*60)
    comprehensive = load_json(COMPREHENSIVE_FILE)
    kashshaf = load_json(KASHSHAF_FILE)
    maarif = load_json(MAARIF_FILE)
    ibn_kathir = load_json(IBN_KATHIR_FILE)
    old_tafsir = load_json(OLD_TAFSIR_FILE)
    print()

    # Build lookup tables
    print("STEP 2: Building lookup tables")
    print("-"*60)
    print("  Building Al-Kashshaf lookup...")
    kashshaf_lookup = build_kashshaf_lookup(kashshaf)
    kashshaf_count = sum(len(verses) for verses in kashshaf_lookup.values())
    print(f"    {kashshaf_count} verses covered")

    print("  Building Ma'arif lookup...")
    maarif_lookup = build_simple_lookup(maarif)
    maarif_count = sum(len(verses) for verses in maarif_lookup.values())
    print(f"    {maarif_count} verses covered")

    print("  Building Ibn Kathir lookup...")
    ibn_kathir_lookup = build_simple_lookup(ibn_kathir)
    ibn_kathir_count = sum(len(verses) for verses in ibn_kathir_lookup.values())
    print(f"    {ibn_kathir_count} verses covered")

    print("  Building legacy Al-Qushairi lookup...")
    old_tafsir_lookup = build_old_tafsir_lookup(old_tafsir)
    old_count = sum(len(verses) for verses in old_tafsir_lookup.values())
    print(f"    {old_count} verses covered")
    print()

    # Update verses
    print("STEP 3: Updating verse tafsirs")
    print("-"*60)

    total_verses = 0
    verses_with_kashshaf = 0
    verses_with_maarif = 0
    verses_with_ibn_kathir = 0
    verses_with_old = 0

    for chapter in comprehensive['chapters']:
        chapter_num = chapter['chapter_number']

        for verse in chapter['verses']:
            verse_num = verse['verse_number']
            total_verses += 1

            # Initialize new tafsir structure
            new_tafsir = {}

            # Legacy Al-Qushairi (keep for backward compatibility)
            if chapter_num in old_tafsir_lookup and verse_num in old_tafsir_lookup[chapter_num]:
                new_tafsir['al_qushairi'] = old_tafsir_lookup[chapter_num][verse_num]
                verses_with_old += 1

            # Al-Kashshaf (Arabic - rhetorical)
            if chapter_num in kashshaf_lookup and verse_num in kashshaf_lookup[chapter_num]:
                new_tafsir['kashshaf_arabic'] = kashshaf_lookup[chapter_num][verse_num]
                verses_with_kashshaf += 1

            # Ma'arif al-Qur'an (English - comprehensive)
            if chapter_num in maarif_lookup and verse_num in maarif_lookup[chapter_num]:
                new_tafsir['maarif_en'] = {
                    'text': maarif_lookup[chapter_num][verse_num],
                    'source': "Ma'arif al-Qur'an (Mufti Muhammad Shafi)",
                    'methodology': 'Modern comprehensive - Balanced linguistic, legal, theological, and practical commentary'
                }
                verses_with_maarif += 1

            # Tafsir Ibn Kathir (English - classical)
            if chapter_num in ibn_kathir_lookup and verse_num in ibn_kathir_lookup[chapter_num]:
                new_tafsir['ibn_kathir_en'] = {
                    'text': ibn_kathir_lookup[chapter_num][verse_num],
                    'source': 'Tafsir Ibn Kathir (Hafiz Ibn Kathir)',
                    'methodology': 'Classical hadith-based - Quran explains Quran, then Hadith, then Companions'
                }
                verses_with_ibn_kathir += 1

            # Update verse tafsir field
            verse['tafsir'] = new_tafsir if new_tafsir else None

    print(f"  Total verses: {total_verses}")
    print(f"  Verses with Al-Kashshaf: {verses_with_kashshaf} ({verses_with_kashshaf/total_verses*100:.1f}%)")
    print(f"  Verses with Ma'arif: {verses_with_maarif} ({verses_with_maarif/total_verses*100:.1f}%)")
    print(f"  Verses with Ibn Kathir: {verses_with_ibn_kathir} ({verses_with_ibn_kathir/total_verses*100:.1f}%)")
    print(f"  Verses with Al-Qushairi (legacy): {verses_with_old} ({verses_with_old/total_verses*100:.1f}%)")
    print()

    # Update metadata
    print("STEP 4: Updating metadata")
    print("-"*60)
    comprehensive['metadata']['tafsir_sources'] = {
        'al_qushairi': {
            'name': 'Al-Qushairi Sufi Tafsir',
            'language': 'English',
            'coverage': f'{old_count} verses',
            'file': 'tafsir_index.json'
        },
        'kashshaf_arabic': {
            'name': 'Al-Kashshaf (Zamakhshari)',
            'language': 'Arabic',
            'coverage': f'{kashshaf_count} verses (partial - rhetorical focus)',
            'file': 'tafsir_kashshaf_arabic.json',
            'methodology': 'Rhetorical/Linguistic'
        },
        'maarif_en': {
            'name': "Ma'arif al-Qur'an (Mufti Muhammad Shafi)",
            'language': 'English',
            'coverage': f'{maarif_count} verses (complete)',
            'file': 'tafsir_maarif_en.json',
            'methodology': 'Modern comprehensive'
        },
        'ibn_kathir_en': {
            'name': 'Tafsir Ibn Kathir (Abridged)',
            'language': 'English',
            'coverage': f'{ibn_kathir_count} verses (complete)',
            'file': 'tafsir_ibn_kathir_en.json',
            'methodology': 'Classical hadith-based'
        }
    }
    print("  Added tafsir_sources to metadata")
    print()

    # Save updated comprehensive file
    print("STEP 5: Saving updated comprehensive file")
    print("-"*60)
    output_file = COMPREHENSIVE_FILE
    print(f"  Writing to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive, f, ensure_ascii=False, indent=2)

    file_size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"  File size: {file_size_mb:.2f} MB")
    print()

    print("="*60)
    print("DONE - Comprehensive data updated with tafsirs")
    print("="*60)
    print()
    print("Summary:")
    print(f"  - Al-Kashshaf (Arabic): {verses_with_kashshaf} verses")
    print(f"  - Ma'arif (English): {verses_with_maarif} verses")
    print(f"  - Ibn Kathir (English): {verses_with_ibn_kathir} verses")
    print(f"  - Al-Qushairi (legacy): {verses_with_old} verses")
    print()


if __name__ == '__main__':
    update_comprehensive_data()
