"""Check what the OLD code behavior was"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager

print("Checking OLD code behavior...")
print("=" * 70)

cache = CacheManager()
cached = cache.get_chapter_context(70)

print("\n1. Fields in cached chapter 70:")
print(f"   {list(cached.keys())}")

print("\n2. Check which field OLD code would use:")
print(f"   - 'introduction' exists: {'introduction' in cached}")
print(f"   - 'user_introduction' exists: {'user_introduction' in cached}")

# Simulate OLD code behavior
intro_old = cached.get('introduction', '')
if intro_old:
    print(f"\n3. OLD code would use 'introduction' field:")
    print(f"   - Length: {len(intro_old)} chars")
    print(f"   - Truncated[:2000]: {len(intro_old[:2000])} chars")
else:
    print(f"\n3. OLD code would use 'introduction' field:")
    print(f"   - Result: EMPTY (field does not exist)")
    print(f"   - This means OLD code was NOT including chapter intro!")

# Check themes
themes = cached.get('main_themes', [])
print(f"\n4. Main themes (OLD code did include this):")
print(f"   - Count: {len(themes)}")
if themes:
    for i, theme in enumerate(themes, 1):
        print(f"   - Theme {i}: {theme[:80]}...")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)

if not intro_old:
    print("OLD code was NOT using 'user_introduction' field!")
    print("It was looking for 'introduction' which doesn't exist in cache.")
    print("So OLD system prompt had NO chapter intro, only themes!")
    print("\nThis means:")
    print("  - OLD: Balaghah (15K) + Themes (~50 tokens) + Ruku (2.5K) = ~17.55K")
    print("  - NEW: Balaghah (15K) + Summary (318 tokens) + Ruku (2.5K) = ~17.82K")
    print("  - Result: NEW system uses MORE tokens!")
    print("\nWe need to check what field SHOULD be used for chapter context.")
else:
    print("OLD code was using 'introduction' field correctly.")
    print(f"Token estimate: {len(intro_old[:2000].split()) * 1.3:.0f} tokens")

print("=" * 70)
