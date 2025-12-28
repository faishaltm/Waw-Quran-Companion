#!/usr/bin/env python3
"""
Download English Translation from Tanzil.net

Downloads Sahih International English translation and converts to JSON format.

Source: http://tanzil.net/trans/
Translation: Sahih International (en.sahih)

Output: data/text/translation_en.json
"""

import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET


def download_translation():
    """Download Sahih International translation from Tanzil.net"""

    # Tanzil.net translation URL
    url = "http://tanzil.net/trans/en.sahih"

    print("Downloading Sahih International translation from Tanzil.net...")
    print(f"URL: {url}")
    print()

    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')

        print(f"Downloaded {len(content)} bytes")
        print()

        return content

    except Exception as e:
        print(f"ERROR downloading translation: {e}")
        sys.exit(1)


def parse_tanzil_text_format(content):
    """
    Parse Tanzil text format to JSON

    Format:
    1|1|In the name of Allah, the Entirely Merciful, the Especially Merciful.
    1|2|[All] praise is [due] to Allah, Lord of the worlds -
    ...
    chapter|verse|translation_text
    """

    print("Parsing translation data...")

    translations = {}
    lines = content.strip().split('\n')

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Parse format: chapter|verse|text
        parts = line.split('|', 2)

        if len(parts) != 3:
            print(f"WARNING: Skipping malformed line {line_num}: {line[:50]}...")
            continue

        try:
            chapter = int(parts[0])
            verse = int(parts[1])
            text = parts[2].strip()

            key = f"{chapter}:{verse}"
            translations[key] = text

        except ValueError:
            print(f"WARNING: Skipping invalid line {line_num}: {line[:50]}...")
            continue

    print(f"  Parsed {len(translations)} verse translations")
    print(f"  Chapters: 1-{max(int(k.split(':')[0]) for k in translations.keys())}")
    print()

    return translations


def save_translation_json(translations, output_path):
    """Save translations to JSON file"""

    # Build structured format
    data = {
        'metadata': {
            'source': 'Tanzil.net',
            'translation': 'Sahih International',
            'language': 'en',
            'url': 'http://tanzil.net/trans/en.sahih',
            'total_verses': len(translations),
            'license': 'Public Domain'
        },
        'translations': translations
    }

    print(f"Saving to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)

    print(f"  [OK] Saved {file_size_mb:.2f} MB")
    print()


def main():
    """Main workflow"""
    print("=" * 70)
    print("DOWNLOAD ENGLISH TRANSLATION")
    print("Source: Tanzil.net (Sahih International)")
    print("=" * 70)
    print()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    output_path = os.path.join(project_root, 'data', 'text', 'translation_en.json')

    # Download
    content = download_translation()

    # Parse
    translations = parse_tanzil_text_format(content)

    # Save
    save_translation_json(translations, output_path)

    print("=" * 70)
    print("DOWNLOAD COMPLETE")
    print("=" * 70)
    print()
    print(f"Translation saved to: {output_path}")
    print(f"Total verses: {len(translations)}")
    print()
    print("Next: Update generate_comprehensive_quran.py to merge translation")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
