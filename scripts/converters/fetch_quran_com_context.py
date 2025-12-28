#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Surah Context from Quran.com API

This script fetches comprehensive surah introductions from Quran.com API
which includes Maududi's Tafhim al-Quran commentary.

Source: https://api.quran.com/api/v4/chapters/{id}/info
Attribution: Sayyid Abul Ala Maududi - Tafhim al-Qur'an

Output: data/metadata/surah_context_qurancom.json
"""

import json
import requests
import time
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'metadata'
OUTPUT_FILE = OUTPUT_DIR / 'surah_context_qurancom.json'

# API endpoint
QURAN_COM_CHAPTER_INFO = "https://api.quran.com/api/v4/chapters/{chapter_id}/info"


def fetch_chapter_info(chapter_id):
    """
    Fetch chapter information from Quran.com API.

    Args:
        chapter_id: Chapter number (1-114)

    Returns:
        Dict with chapter info or None if failed
    """
    url = QURAN_COM_CHAPTER_INFO.format(chapter_id=chapter_id)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"  Warning: Could not fetch chapter {chapter_id} - Status {response.status_code}")
            return None

        data = response.json()
        chapter_info = data.get('chapter_info')

        if not chapter_info:
            print(f"  Warning: No chapter_info in response for chapter {chapter_id}")
            return None

        return chapter_info

    except Exception as e:
        print(f"  Error fetching chapter {chapter_id}: {e}")
        return None


def build_surah_context():
    """Fetch surah context for all 114 chapters."""
    print("\n" + "="*60)
    print("Fetching Surah Context from Quran.com API")
    print("Source: Sayyid Abul Ala Maududi - Tafhim al-Qur'an")
    print("="*60)

    surah_context = {}
    successful = 0
    failed = 0

    for chapter_id in range(1, 115):
        print(f"Fetching chapter {chapter_id}/114...", end=" ")

        chapter_info = fetch_chapter_info(chapter_id)

        if chapter_info:
            # Extract relevant fields
            context = {
                'chapter_id': chapter_info.get('id'),
                'chapter_number': chapter_info.get('chapter_id'),
                'language': chapter_info.get('language_name', 'english'),
                'source': chapter_info.get('source', 'Unknown'),
                'short_text': chapter_info.get('short_text', ''),
                'text': chapter_info.get('text', '')
            }

            surah_context[str(chapter_id)] = context
            successful += 1
            print("[OK]")
        else:
            failed += 1
            print("[FAILED]")

        # Be nice to the API - rate limiting
        if chapter_id % 10 == 0:
            print(f"  Progress: {chapter_id}/114 chapters fetched")
            time.sleep(1)  # Longer pause every 10 requests
        else:
            time.sleep(0.3)  # Short pause between requests

    print(f"\nFetch complete: {successful} successful, {failed} failed")
    return surah_context


def main():
    """Main execution."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch surah context
    surah_context = build_surah_context()

    # Save to JSON
    print(f"\nSaving surah context to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(surah_context, f, ensure_ascii=False, indent=2)

    print(f"  Saved {len(surah_context)} chapters")
    print(f"  File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

    print("\n" + "="*60)
    print("[SUCCESS] Quran.com context data fetched!")
    print("="*60)

    # Show sample
    if '68' in surah_context:
        print("\nSample - Surah 68 (Al-Qalam):")
        print(f"  Source: {surah_context['68']['source']}")
        print(f"  Short text: {surah_context['68']['short_text'][:100]}...")
        print(f"  Full text length: {len(surah_context['68']['text'])} characters")


if __name__ == '__main__':
    main()
