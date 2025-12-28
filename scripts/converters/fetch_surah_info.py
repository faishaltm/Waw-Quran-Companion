#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Surah Information from Multiple Sources

This script fetches chapter-level contextual information:
1. Basic metadata from AlQuran Cloud API
2. Surah introductions from Ibn Kathir tafsir (spa5k/tafsir_api)
3. Ruku divisions from AlQuran Cloud API

Output: data/metadata/surah_info.json
"""

import json
import requests
import time
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'metadata'
OUTPUT_FILE = OUTPUT_DIR / 'surah_info.json'
RUKU_FILE = OUTPUT_DIR / 'ruku_divisions.json'

# API endpoints
ALQURAN_SURAH_LIST = "http://api.alquran.cloud/v1/surah"
IBN_KATHIR_BASE = "https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/en-tafisr-ibn-kathir"
ALQURAN_RUKU_BASE = "http://api.alquran.cloud/v1/ruku"


def fetch_basic_metadata():
    """Fetch basic surah metadata from AlQuran Cloud."""
    print("Fetching basic surah metadata from AlQuran Cloud...")

    response = requests.get(ALQURAN_SURAH_LIST)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch surah list: {response.status_code}")

    data = response.json()
    surahs = data['data']

    print(f"  Retrieved {len(surahs)} surahs")
    return {s['number']: s for s in surahs}


def extract_introduction_from_tafsir(tafsir_text):
    """
    Extract introduction portion from Ibn Kathir tafsir.

    The introduction usually comes before the verse-by-verse commentary.
    We'll take the first portion that discusses the surah as a whole.
    """
    # Look for common section markers that indicate verse commentary has started
    markers = [
        "Tafsir of Verse",
        "Tafsir Verse",
        "بِسْمِ",  # Bismillah often marks start of verse commentary
        "In the Name of Allah"
    ]

    # Find the earliest marker
    intro_end = len(tafsir_text)
    for marker in markers:
        pos = tafsir_text.find(marker)
        if pos > 0 and pos < intro_end:
            intro_end = pos

    # Take introduction portion (first section before verse commentary)
    intro = tafsir_text[:intro_end].strip()

    # Limit to reasonable size (first 3000 chars for theme/context)
    if len(intro) > 3000:
        # Try to break at a paragraph
        cutoff = intro[:3000].rfind('\n\n')
        if cutoff > 1000:  # Make sure we have substantial content
            intro = intro[:cutoff]
        else:
            intro = intro[:3000] + "..."

    return intro


def fetch_ibn_kathir_intro(surah_num):
    """Fetch surah introduction from Ibn Kathir tafsir first ayah."""
    url = f"{IBN_KATHIR_BASE}/{surah_num}.json"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"  Warning: Could not fetch tafsir for surah {surah_num}")
            return None

        data = response.json()
        ayahs = data.get('ayahs', [])

        if not ayahs:
            return None

        # First ayah usually contains surah introduction
        first_ayah = ayahs[0]
        full_text = first_ayah.get('text', '')

        # Extract introduction portion
        intro = extract_introduction_from_tafsir(full_text)

        return intro

    except Exception as e:
        print(f"  Error fetching tafsir for surah {surah_num}: {e}")
        return None


def fetch_ruku_divisions():
    """Fetch all 556 ruku divisions from AlQuran Cloud."""
    print("\nFetching ruku divisions from AlQuran Cloud...")

    rukus = {}

    for ruku_num in range(1, 557):  # 556 total rukus
        try:
            url = f"{ALQURAN_RUKU_BASE}/{ruku_num}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()['data']
                ayahs = data['ayahs']

                # Get first and last ayah to determine range
                if ayahs:
                    first_ayah = ayahs[0]
                    last_ayah = ayahs[-1]

                    rukus[ruku_num] = {
                        'ruku_number': data['number'],
                        'chapter': first_ayah['surah']['number'],
                        'chapter_name': first_ayah['surah']['englishName'],
                        'verse_start': first_ayah['numberInSurah'],
                        'verse_end': last_ayah['numberInSurah'],
                        'verse_count': len(ayahs)
                    }

                # Be nice to the API
                if ruku_num % 50 == 0:
                    print(f"  Fetched {ruku_num}/556 rukus...")
                    time.sleep(0.5)
                elif ruku_num % 10 == 0:
                    time.sleep(0.2)

        except Exception as e:
            print(f"  Error fetching ruku {ruku_num}: {e}")
            time.sleep(1)

    print(f"  Retrieved {len(rukus)} rukus")
    return rukus


def build_surah_info():
    """Build comprehensive surah information dataset."""
    print("\n" + "="*60)
    print("Building Comprehensive Surah Information Dataset")
    print("="*60)

    # Step 1: Get basic metadata
    basic_metadata = fetch_basic_metadata()

    # Step 2: Fetch Ibn Kathir introductions
    print("\nFetching surah introductions from Ibn Kathir tafsir...")
    surah_info = {}

    for surah_num in range(1, 115):
        basic = basic_metadata[surah_num]

        # Start with basic metadata
        info = {
            'number': surah_num,
            'name_arabic': basic['name'],
            'name_simple': basic['englishName'],
            'name_translation': basic['englishNameTranslation'],
            'revelation_place': basic['revelationType'].lower(),
            'verses_count': basic['numberOfAyahs']
        }

        # Add Ibn Kathir introduction
        intro = fetch_ibn_kathir_intro(surah_num)
        if intro:
            info['introduction'] = intro

        surah_info[str(surah_num)] = info

        status = "[OK]" if intro else "[NO INTRO]"
        print(f"  [{surah_num}/114] {basic['englishName']} {status}")

        # Be nice to the API/CDN
        if surah_num % 10 == 0:
            time.sleep(0.5)
        else:
            time.sleep(0.2)

    return surah_info


def main():
    """Main execution."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build surah info
    surah_info = build_surah_info()

    # Save surah info
    print(f"\nSaving surah information to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(surah_info, f, ensure_ascii=False, indent=2)

    print(f"  Saved {len(surah_info)} surahs")
    print(f"  File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

    # Fetch and save ruku divisions
    rukus = fetch_ruku_divisions()

    print(f"\nSaving ruku divisions to {RUKU_FILE}...")
    with open(RUKU_FILE, 'w', encoding='utf-8') as f:
        json.dump(rukus, f, ensure_ascii=False, indent=2)

    print(f"  Saved {len(rukus)} rukus")
    print(f"  File size: {RUKU_FILE.stat().st_size / 1024:.1f} KB")

    print("\n" + "="*60)
    print("[SUCCESS] Data acquisition complete!")
    print("="*60)

    # Statistics
    intro_count = sum(1 for s in surah_info.values() if 'introduction' in s)
    print(f"\nStatistics:")
    print(f"  - Surahs with introductions: {intro_count}/114")
    print(f"  - Ruku divisions: {len(rukus)}/556")


if __name__ == '__main__':
    main()
