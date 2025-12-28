#!/usr/bin/env python3
"""
Cache Maker - Manually inject cache entries

Usage:
    # Inject chapter context
    cache_maker.py chapter 18 --content chapter_18.json
    cache_maker.py chapter 18 --content '{"surah_number": 18, ...}'

    # Inject verse analysis
    cache_maker.py verse 18:1 --content verse_18_1.json
    cache_maker.py verse 18:1 --content '{"analysis": "...", ...}'

    # Inject accumulated summary
    cache_maker.py summary 68 --content summary_68.json
    cache_maker.py summary 68 --content '{"surah": 68, ...}'

    # View existing cache
    cache_maker.py view chapter 18
    cache_maker.py view verse 18:1
    cache_maker.py view summary 68

    # List all
    cache_maker.py list chapters
    cache_maker.py list summaries
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager

def inject_chapter(surah_num: int, content: dict):
    """Inject chapter context cache"""

    # Validate required fields
    required_fields = [
        'surah_number', 'surah_name', 'revelation_place',
        'user_introduction', 'main_themes', 'structure_overview',
        'rhetorical_approach'
    ]

    missing = [f for f in required_fields if f not in content]
    if missing:
        print(f"Error: Missing required fields: {', '.join(missing)}")
        return False

    # Add metadata if missing
    from datetime import datetime
    if '_generated_at' not in content:
        content['_generated_at'] = datetime.now().isoformat()
    if '_generation_method' not in content:
        content['_generation_method'] = 'manual_inject'
    if '_model' not in content:
        content['_model'] = 'manual'

    # Save to cache
    cache = CacheManager()
    cache.save_chapter_context(surah_num, content)

    print(f"✓ Chapter {surah_num} context injected successfully")
    return True

def inject_verse(surah_num: int, verse_num: int, content: dict):
    """Inject verse analysis cache"""

    # Validate required fields
    if 'analysis' not in content:
        print("Error: Missing required field: 'analysis'")
        return False

    # Add metadata
    from datetime import datetime
    content['surah'] = surah_num
    content['verse'] = verse_num
    if '_generated_at' not in content:
        content['_generated_at'] = datetime.now().isoformat()

    # Save to cache
    cache = CacheManager()
    cache.save_verse_analysis(surah_num, verse_num, content['analysis'])

    print(f"✓ Verse {surah_num}:{verse_num} analysis injected successfully")
    return True

def inject_summary(surah_num: int, content: dict):
    """Inject accumulated summary cache"""

    # Validate structure
    required_fields = ['surah', 'last_ruku_completed', 'accumulated_summary']
    missing = [f for f in required_fields if f not in content]
    if missing:
        print(f"Error: Missing required fields: {', '.join(missing)}")
        return False

    # Add metadata
    from datetime import datetime
    if 'updated_at' not in content:
        content['updated_at'] = datetime.now().isoformat()

    # Save to cache
    cache = CacheManager()
    cache.save_accumulated_summary(surah_num, content)

    print(f"✓ Summary for surah {surah_num} injected successfully")
    return True

def view_cache(cache_type: str, identifier: str):
    """View existing cache entry"""
    cache = CacheManager()

    if cache_type == 'chapter':
        surah_num = int(identifier)
        data = cache.get_chapter_context(surah_num)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"No cache found for chapter {surah_num}")

    elif cache_type == 'verse':
        surah_num, verse_num = map(int, identifier.split(':'))
        data = cache.get_verse_analysis(surah_num, verse_num)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"No cache found for verse {surah_num}:{verse_num}")

    elif cache_type == 'summary':
        surah_num = int(identifier)
        data = cache.get_accumulated_summary(surah_num)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"No cache found for summary {surah_num}")

def list_cache(cache_type: str):
    """List all cache of type"""
    cache = CacheManager()

    if cache_type == 'chapters':
        cache_dir = Path(__file__).parent / "cache" / "chapters"
        if not cache_dir.exists():
            print("No chapters cache directory found")
            return

        files = sorted(cache_dir.glob("chapter_*_context.json"))
        print(f"Cached chapters ({len(files)}):")
        for f in files:
            # Extract surah number
            surah = f.stem.split('_')[1]
            print(f"  - Chapter {surah}")

    elif cache_type == 'summaries':
        cache_dir = Path(__file__).parent / "cache" / "summaries"
        if not cache_dir.exists():
            print("No summaries cache directory found")
            return

        files = sorted(cache_dir.glob("surah_*_accumulated.json"))
        print(f"Cached summaries ({len(files)}):")
        for f in files:
            # Extract surah number
            surah = f.stem.split('_')[1]
            print(f"  - Surah {surah}")

def load_content(content_arg: str) -> dict:
    """Load content from file or JSON string"""

    # Check if it's a file path
    if Path(content_arg).exists():
        with open(content_arg, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Parse as JSON string
        return json.loads(content_arg)

def main():
    parser = argparse.ArgumentParser(
        description="Manually inject cache entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cache_maker.py chapter 18 --content chapter_18.json
  cache_maker.py verse 18:1 --content '{"analysis": "..."}'
  cache_maker.py summary 68 --content summary_68.json
  cache_maker.py view chapter 18
  cache_maker.py list chapters
        """
    )

    subparsers = parser.add_subparsers(dest='action', required=True)

    # Inject commands
    for cache_type in ['chapter', 'verse', 'summary']:
        p = subparsers.add_parser(cache_type, help=f"Inject {cache_type} cache")
        p.add_argument('identifier', help="Surah number or verse (e.g., 18:1)")
        p.add_argument('--content', required=True, help="JSON file path or JSON string")

    # View command
    view_parser = subparsers.add_parser('view', help="View existing cache")
    view_parser.add_argument('cache_type', choices=['chapter', 'verse', 'summary'])
    view_parser.add_argument('identifier', help="Surah number or verse")

    # List command
    list_parser = subparsers.add_parser('list', help="List all cache of type")
    list_parser.add_argument('cache_type', choices=['chapters', 'summaries'])

    args = parser.parse_args()

    try:
        if args.action == 'view':
            view_cache(args.cache_type, args.identifier)
        elif args.action == 'list':
            list_cache(args.cache_type)
        else:
            # Inject actions
            content = load_content(args.content)

            if args.action == 'chapter':
                surah_num = int(args.identifier)
                inject_chapter(surah_num, content)
            elif args.action == 'verse':
                surah_num, verse_num = map(int, args.identifier.split(':'))
                inject_verse(surah_num, verse_num, content)
            elif args.action == 'summary':
                surah_num = int(args.identifier)
                inject_summary(surah_num, content)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
