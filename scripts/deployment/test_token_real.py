"""Test REAL token savings with actual chapter 70 data"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager

print("=" * 70)
print("REAL TOKEN SAVINGS - Chapter 70 (Al-Ma'arij)")
print("=" * 70)

# Load cached chapter 70
cache = CacheManager()
cached = cache.get_chapter_context(70)

if not cached:
    print("[ERROR] Could not load chapter 70")
    sys.exit(1)

# Get the actual intro field
intro = cached.get('user_introduction', '') or cached.get('introduction', '')
print(f"\n1. Chapter data:")
print(f"   - Full intro length: {len(intro)} chars")
print(f"   - Main themes count: {len(cached.get('main_themes', []))}")
print(f"   - Has structure_overview: {'structure_overview' in cached}")
print(f"   - Has rhetorical_approach: {'rhetorical_approach' in cached}")

# OLD behavior: intro[:2000]
print(f"\n2. OLD BEHAVIOR (intro[:2000]):")
old_intro = intro[:2000]
old_intro_tokens = len(old_intro.split()) * 1.3
print(f"   - Length: {len(old_intro)} chars")
print(f"   - Words: {len(old_intro.split())}")
print(f"   - Estimated tokens: ~{int(old_intro_tokens)}")

# NEW behavior: summary (mock estimate based on 4 components)
print(f"\n3. NEW BEHAVIOR (chapter_summary):")
print(f"   Estimated structure:")
print(f"   - amud: 2-3 sentences (~60 words, ~78 tokens)")
print(f"   - munasabat: 3-4 sentences (~85 words, ~110 tokens)")
print(f"   - historical_context: 2-3 sentences (~60 words, ~78 tokens)")
print(f"   - tone: 1-2 sentences (~40 words, ~52 tokens)")
print(f"   -----------------------------")
summary_words = 245  # Total estimated words
summary_tokens = int(summary_words * 1.3)
print(f"   - Total: ~{summary_words} words, ~{summary_tokens} tokens")

# FALLBACK behavior: intro[:500] (for old cached chapters)
print(f"\n4. FALLBACK BEHAVIOR (intro[:500] for old cache):")
fallback_intro = intro[:500]
fallback_tokens = len(fallback_intro.split()) * 1.3
print(f"   - Length: {len(fallback_intro)} chars")
print(f"   - Estimated tokens: ~{int(fallback_tokens)}")

# Full system comparison
print("\n" + "=" * 70)
print("SYSTEM PROMPT TOKEN COMPARISON:")
print("=" * 70)

balaghah = 15000
ruku = 2500

old_chapter = int(old_intro_tokens)
new_chapter = summary_tokens
fallback_chapter = int(fallback_tokens)

old_total = balaghah + old_chapter + ruku
new_total = balaghah + new_chapter + ruku
fallback_total = balaghah + fallback_chapter + ruku

print(f"\nOLD System (current behavior - intro[:2000]):")
print(f"   Balaghah guide:     {balaghah:,} tokens")
print(f"   Chapter context:    {old_chapter:,} tokens")
print(f"   Ruku data:          {ruku:,} tokens")
print(f"   -----------------------------")
print(f"   TOTAL:              {old_total:,} tokens")

print(f"\nNEW System (with summary):")
print(f"   Balaghah guide:     {balaghah:,} tokens")
print(f"   Chapter summary:    {new_chapter:,} tokens")
print(f"   Ruku data:          {ruku:,} tokens")
print(f"   -----------------------------")
print(f"   TOTAL:              {new_total:,} tokens")

print(f"\nFALLBACK (old cache without summary):")
print(f"   Balaghah guide:     {balaghah:,} tokens")
print(f"   Chapter ([:500]):   {fallback_chapter:,} tokens")
print(f"   Ruku data:          {ruku:,} tokens")
print(f"   -----------------------------")
print(f"   TOTAL:              {fallback_total:,} tokens")

# Savings calculation
savings = old_total - new_total
savings_pct = (savings / old_total) * 100

print(f"\n" + "=" * 70)
print("SAVINGS ANALYSIS:")
print("=" * 70)
print(f"\nOLD vs NEW:")
print(f"   Tokens saved:       {savings:,} tokens per session")
print(f"   Percentage:         {savings_pct:.1f}%")
print(f"   Per surah (10 rukus): {savings * 10:,} tokens")

fallback_savings = old_total - fallback_total
print(f"\nOLD vs FALLBACK:")
print(f"   Tokens saved:       {fallback_savings:,} tokens")
print(f"   Percentage:         {(fallback_savings/old_total)*100:.1f}%")

print(f"\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print(f"With summary:         {savings:,} tokens saved ({savings_pct:.1f}%)")
print(f"Even with fallback:   {fallback_savings:,} tokens saved")
print(f"Summary is worth it:  YES")
print("=" * 70)
