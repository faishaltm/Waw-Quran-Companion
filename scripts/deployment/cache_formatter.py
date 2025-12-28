#!/usr/bin/env python3
"""
Cache Formatter - Convert user input to valid JSON cache files

Supports two input formats:
1. JSON-like format (with real newlines in string):
   {
     "surah_number": 110,
     "user_introduction": "Text with
     actual newlines..."
   }

2. Plain text format (filename contains surah number):
   Filename: 110.txt or surah_110.txt
   Content: Just the introduction text

Usage:
    # Single file
    python3 cache_formatter.py input.json
    python3 cache_formatter.py 110.txt

    # Bulk folder
    python3 cache_formatter.py --bulk /path/to/folder

    # Specify output directory
    python3 cache_formatter.py --bulk /path/to/folder --output cache/chapters
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path


def extract_surah_number_from_filename(filename: str) -> int:
    """Extract surah number from filename like '110.txt', 'surah_110.txt', 'chapter_110.json'"""
    # Try to find number in filename
    match = re.search(r'(\d+)', filename)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 114:
            return num
    return None


def extract_surah_number_from_content(content: str) -> int:
    """Extract surah_number from JSON-like content"""
    # Try to find "surah_number": X pattern
    match = re.search(r'"surah_number"\s*:\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return None


def extract_user_introduction_from_content(content: str) -> str:
    """Extract user_introduction from JSON-like content with real newlines"""
    # Remove the opening brace and surah_number line
    # Find the start of user_introduction value
    match = re.search(r'"user_introduction"\s*:\s*"', content)
    if not match:
        return None

    start_idx = match.end()

    # Find the closing quote and brace
    # We need to handle escaped quotes vs real end
    text = content[start_idx:]

    # Find the last closing pattern: "\n} or just "}
    # Work backwards from end
    end_patterns = ['"\n}', '"\r\n}', '"}']

    end_idx = -1
    for pattern in end_patterns:
        idx = text.rfind(pattern)
        if idx != -1:
            end_idx = idx
            break

    if end_idx == -1:
        # Try just finding last "
        end_idx = text.rfind('"')

    if end_idx == -1:
        return None

    return text[:end_idx]


def normalize_text(text: str) -> str:
    """Normalize text for JSON storage"""
    # Replace smart quotes with straight quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def process_file(input_path: str, output_dir: str = None) -> dict:
    """
    Process a single input file and create valid JSON cache

    Returns dict with status info
    """
    input_path = Path(input_path)

    if not input_path.exists():
        return {"success": False, "error": f"File not found: {input_path}"}

    # Read content
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

    # Determine format and extract data
    surah_num = None
    user_introduction = None

    # Check if it's JSON-like format
    if '"surah_number"' in content and '"user_introduction"' in content:
        surah_num = extract_surah_number_from_content(content)
        user_introduction = extract_user_introduction_from_content(content)
    else:
        # Plain text format - get surah number from filename
        surah_num = extract_surah_number_from_filename(input_path.name)
        user_introduction = content

    # Validate
    if surah_num is None:
        return {"success": False, "error": f"Could not determine surah number from {input_path.name}"}

    if user_introduction is None or len(user_introduction.strip()) == 0:
        return {"success": False, "error": f"Could not extract user_introduction from {input_path.name}"}

    # Normalize text
    user_introduction = normalize_text(user_introduction)

    # Create valid JSON structure
    data = {
        "surah_number": surah_num,
        "user_introduction": user_introduction
    }

    # Determine output path
    if output_dir:
        output_path = Path(output_dir) / f"chapter_{surah_num}_context.json"
    else:
        output_path = input_path.parent / f"chapter_{surah_num}_context.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write valid JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Verify by reading back
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            verify = json.load(f)
        verified = True
    except json.JSONDecodeError as e:
        verified = False

    return {
        "success": True,
        "surah_num": surah_num,
        "input_file": str(input_path),
        "output_file": str(output_path),
        "text_length": len(user_introduction),
        "verified": verified
    }


def process_bulk(input_dir: str, output_dir: str = None) -> list:
    """
    Process all files in a directory

    Looks for:
    - *.json files
    - *.txt files
    - Files with surah numbers in name
    """
    input_dir = Path(input_dir)

    if not input_dir.exists():
        print(f"Error: Directory not found: {input_dir}")
        return []

    # Find all potential input files
    patterns = ['*.json', '*.txt']
    files = []
    for pattern in patterns:
        files.extend(input_dir.glob(pattern))

    # Filter out already-formatted cache files
    files = [f for f in files if not f.name.startswith('chapter_') or not f.name.endswith('_context.json')]

    if not files:
        print(f"No input files found in {input_dir}")
        return []

    print(f"Found {len(files)} files to process")
    print("-" * 60)

    results = []
    for filepath in sorted(files):
        result = process_file(str(filepath), output_dir)
        results.append(result)

        if result["success"]:
            print(f"[OK] Surah {result['surah_num']:3d}: {result['text_length']:,} chars -> {Path(result['output_file']).name}")
        else:
            print(f"[FAIL] {filepath.name}: {result['error']}")

    # Summary
    success_count = sum(1 for r in results if r["success"])
    print("-" * 60)
    print(f"Processed: {success_count}/{len(results)} files successfully")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert user input files to valid JSON cache format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file (JSON-like with real newlines)
  python3 cache_formatter.py my_surah_110.json

  # Single file (plain text, surah number from filename)
  python3 cache_formatter.py 110.txt

  # Bulk process folder
  python3 cache_formatter.py --bulk ./my_introductions/

  # Bulk with custom output directory
  python3 cache_formatter.py --bulk ./my_introductions/ --output cache/chapters/

Input formats supported:
  1. JSON-like (with actual newlines in string):
     {
       "surah_number": 110,
       "user_introduction": "Text here...
       Can have real newlines..."
     }

  2. Plain text (filename must contain surah number):
     Filename: 110.txt or surah_110.txt
     Content: Just the introduction text
        """
    )

    parser.add_argument('input', nargs='?', help="Input file path")
    parser.add_argument('--bulk', '-b', metavar='DIR', help="Process all files in directory")
    parser.add_argument('--output', '-o', metavar='DIR', help="Output directory (default: same as input or cache/chapters)")

    args = parser.parse_args()

    if args.bulk:
        # Bulk mode
        output_dir = args.output or "cache/chapters"
        results = process_bulk(args.bulk, output_dir)

    elif args.input:
        # Single file mode
        result = process_file(args.input, args.output)

        if result["success"]:
            print(f"[OK] Created: {result['output_file']}")
            print(f"     Surah: {result['surah_num']}")
            print(f"     Text length: {result['text_length']:,} chars")
            print(f"     JSON valid: {result['verified']}")
        else:
            print(f"[FAIL] {result['error']}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
