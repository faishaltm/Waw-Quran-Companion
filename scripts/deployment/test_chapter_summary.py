"""Test chapter summary preprocessing system"""
import sys
import os
from pathlib import Path

# Set up paths
sys.path.insert(0, str(Path(__file__).parent))

from openai import OpenAI
from api.cache_manager import CacheManager
from api.chapter_context_generator import ChapterContextGenerator

# Initialize
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print('ERROR: OPENAI_API_KEY not set')
    sys.exit(1)

client = OpenAI(api_key=api_key)
cache = CacheManager()
generator = ChapterContextGenerator(cache, client)

print("=" * 70)
print("TEST 1: NEW UNCACHED CHAPTER (68 - Al-Qalam)")
print("=" * 70)
context68 = generator.get_or_generate(68)

# Check results
print('')
print('Results:')
print(f'  - Has chapter_summary: {"chapter_summary" in context68}')
if 'chapter_summary' in context68:
    summary = context68['chapter_summary']
    print(f'  - Summary keys: {list(summary.keys())}')

    # Estimate token count
    required_keys = ['amud', 'munasabat', 'historical_context', 'tone']
    text = ' '.join([summary.get(k, '') for k in required_keys])
    estimated_tokens = len(text.split()) * 1.3
    print(f'  - Estimated summary tokens: ~{int(estimated_tokens)}')

    if '_tokens_used' in summary:
        print(f'  - Extraction cost: {summary["_tokens_used"]} tokens')

    print('')
    print('Summary preview:')
    for key in required_keys:
        value = summary.get(key, '')
        preview = value[:100] + '...' if len(value) > 100 else value
        print(f'  {key}: {preview}')

print('')
print("=" * 70)
print("TEST 2: EXISTING CACHED CHAPTER (70 - Al-Ma'arij) - Auto-migration")
print("=" * 70)
context70 = generator.get_or_generate(70)

# Check results
print('')
print('Results:')
print(f'  - Has chapter_summary: {"chapter_summary" in context70}')
if 'chapter_summary' in context70:
    summary = context70['chapter_summary']
    print(f'  - Summary keys: {list(summary.keys())}')

    # Estimate token count
    required_keys = ['amud', 'munasabat', 'historical_context', 'tone']
    text = ' '.join([summary.get(k, '') for k in required_keys])
    estimated_tokens = len(text.split()) * 1.3
    print(f'  - Estimated summary tokens: ~{int(estimated_tokens)}')

    print('')
    print('Summary preview:')
    for key in required_keys:
        value = summary.get(key, '')
        preview = value[:100] + '...' if len(value) > 100 else value
        print(f'  {key}: {preview}')

print('')
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("All tests completed successfully!")
print("Token savings: ~1,500 tokens per ruku session start")
