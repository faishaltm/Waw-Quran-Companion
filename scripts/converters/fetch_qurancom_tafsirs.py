#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Tafsir Fetcher - spa5k/tafsir_api Repository

Fetches tafsir commentaries from spa5k/tafsir_api GitHub repository:
- Ma'arif al-Qur'an (Mufti Muhammad Shafi)
- Tafsir Ibn Kathir (Abridged English)

Source: https://github.com/spa5k/tafsir_api
License: MIT

Outputs:
- data/metadata/tafsir_maarif_en.json
- data/metadata/tafsir_ibn_kathir_en.json
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"

# GitHub Raw URL Base
GITHUB_BASE = "https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir"
TAFSIR_SLUGS = {
    'maarif': 'en-tafsir-maarif-ul-quran',
    'ibn_kathir': 'en-tafisr-ibn-kathir'
}

# Rate limiting (be respectful)
REQUEST_DELAY = 1.0  # seconds between requests

# Quran structure
TOTAL_CHAPTERS = 114
VERSES_PER_CHAPTER = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}


def fetch_chapter_tafsir(chapter_number, tafsir_slug):
    """
    Fetch tafsir for a specific chapter from GitHub repository.

    Args:
        chapter_number: Chapter number (1-114)
        tafsir_slug: Tafsir slug (e.g., 'en-tafisr-ibn-kathir')

    Returns:
        dict: Chapter data with ayahs and tafsir texts
    """
    url = f"{GITHUB_BASE}/{tafsir_slug}/{chapter_number}.json"

    print(f"  Fetching chapter {chapter_number}...", end=' ')

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        ayahs = data.get('ayahs', [])
        print(f"Got {len(ayahs)} verses")

        return data

    except requests.exceptions.RequestException as e:
        print(f"\nERROR fetching chapter {chapter_number}: {e}")
        return None


def extract_tafsir_from_chapter(chapter_data, chapter_number):
    """
    Extract tafsir texts from chapter JSON data.

    Args:
        chapter_data: Chapter JSON from repository
        chapter_number: Chapter number

    Returns:
        dict: {verse_number: tafsir_text}
    """
    verse_tafsirs = {}

    if not chapter_data:
        return verse_tafsirs

    ayahs = chapter_data.get('ayahs', [])

    for ayah in ayahs:
        verse_num = ayah.get('ayah', ayah.get('number'))
        tafsir_text = ayah.get('text', '')

        if verse_num and tafsir_text:
            verse_tafsirs[verse_num] = tafsir_text

    return verse_tafsirs


def fetch_all_tafsirs():
    """
    Fetch all tafsirs for all chapters from GitHub repository.

    Returns:
        dict: {tafsir_name: verse_index}
    """
    print("="*60)
    print("Fetching Tafsirs from spa5k/tafsir_api")
    print("="*60)
    print(f"GitHub Base: {GITHUB_BASE}")
    print(f"Tafsirs: {list(TAFSIR_SLUGS.keys())}")
    print(f"Chapters: 1-{TOTAL_CHAPTERS}")
    print(f"Request delay: {REQUEST_DELAY}s")
    print()

    all_tafsirs = {}

    # Fetch each tafsir separately
    for tafsir_name, tafsir_slug in TAFSIR_SLUGS.items():
        print(f"\n[{tafsir_name.upper()}] Fetching...")
        print("-" * 60)

        tafsir_verses = {}

        failed_chapters = []

        for chapter in range(1, TOTAL_CHAPTERS + 1):
            print(f"Chapter {chapter}/{TOTAL_CHAPTERS}", end=' ')

            chapter_data = fetch_chapter_tafsir(chapter, tafsir_slug)

            if chapter_data is None:
                print(f"  FAILED - will retry")
                failed_chapters.append(chapter)
                continue

            # Extract verse tafsirs
            verse_tafsirs = extract_tafsir_from_chapter(chapter_data, chapter)

            if chapter not in tafsir_verses:
                tafsir_verses[chapter] = {}

            tafsir_verses[chapter] = verse_tafsirs

            # Small delay
            time.sleep(REQUEST_DELAY * 0.3)

        # Retry failed chapters
        if failed_chapters:
            print(f"\n\nRetrying {len(failed_chapters)} failed chapters...")
            for chapter in failed_chapters:
                print(f"Retry chapter {chapter}...", end=' ')
                time.sleep(2)  # Longer delay before retry

                chapter_data = fetch_chapter_tafsir(chapter, tafsir_slug)
                if chapter_data:
                    verse_tafsirs = extract_tafsir_from_chapter(chapter_data, chapter)
                    tafsir_verses[chapter] = verse_tafsirs
                else:
                    print(f"  STILL FAILED")

        all_tafsirs[tafsir_name] = tafsir_verses
        print(f"\n[OK] {tafsir_name} complete")

    return all_tafsirs


def save_tafsir(tafsir_id, verse_index, metadata, output_path):
    """
    Save tafsir to JSON file.

    Args:
        tafsir_id: Tafsir resource ID
        verse_index: Dict of {chapter: {verse: text}}
        metadata: Dict of metadata
        output_path: Path to output file
    """
    # Generate statistics
    total_chapters = len(verse_index)
    total_verses = sum(len(verses) for verses in verse_index.values())

    stats = {
        'total_chapters': total_chapters,
        'total_verses': total_verses,
        'chapters_covered': list(verse_index.keys())
    }

    # Create output structure
    output = {
        **metadata,
        'statistics': stats,
        'verse_index': verse_index
    }

    # Save to JSON
    print(f"\nSaving to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    file_size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Chapters: {total_chapters}/114")
    print(f"Verses: {total_verses}")


def main():
    """Main execution"""
    print("="*60)
    print("English Tafsir Fetcher")
    print("="*60)
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch all tafsirs
    all_tafsirs = fetch_all_tafsirs()

    if not all_tafsirs:
        print("\nERROR: No tafsirs fetched!")
        sys.exit(1)

    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)

    # Save Ma'arif al-Qur'an
    if 'maarif' in all_tafsirs:
        print("\n[1/2] Ma'arif al-Qur'an")
        print("-" * 60)
        metadata_maarif = {
            'source': "Ma'arif al-Qur'an",
            'author': 'Mufti Muhammad Shafi',
            'translator': 'Mufti Taqi Usmani',
            'methodology': 'Modern comprehensive tafsir - Balanced approach with linguistic, legal, theological, and practical commentary',
            'language': 'English',
            'github_source': 'spa5k/tafsir_api',
            'github_slug': 'en-tafsir-maarif-ul-quran',
            'license': 'MIT',
            'attribution': 'Original: quran.com | Repository: https://github.com/spa5k/tafsir_api'
        }
        output_path = OUTPUT_DIR / "tafsir_maarif_en.json"
        save_tafsir('maarif', all_tafsirs['maarif'], metadata_maarif, output_path)

    # Save Ibn Kathir
    if 'ibn_kathir' in all_tafsirs:
        print("\n[2/2] Tafsir Ibn Kathir")
        print("-" * 60)
        metadata_ibn_kathir = {
            'source': 'Tafsir Ibn Kathir (Abridged)',
            'author': 'Hafiz Ibn Kathir (d. 1373 CE)',
            'methodology': 'Classical hadith-based tafsir - Quran explains Quran → Hadith → Companions → reasoning',
            'language': 'English',
            'github_source': 'spa5k/tafsir_api',
            'github_slug': 'en-tafisr-ibn-kathir',
            'license': 'MIT',
            'attribution': 'Original: quran.com | Repository: https://github.com/spa5k/tafsir_api'
        }
        output_path = OUTPUT_DIR / "tafsir_ibn_kathir_en.json"
        save_tafsir('ibn_kathir', all_tafsirs['ibn_kathir'], metadata_ibn_kathir, output_path)

    print("\n" + "="*60)
    print("DONE")
    print("="*60)


if __name__ == '__main__':
    main()
