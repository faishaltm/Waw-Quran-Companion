"""Test token estimation with REAL cached chapter data"""
import sys
import json
from pathlib import Path

# Set up paths
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager

print("=" * 70)
print("TOKEN ESTIMATION TEST - Real Cached Chapter 70")
print("=" * 70)

# Load cached chapter
cache = CacheManager()
cached_chapter = cache.get_chapter_context(70)

if not cached_chapter:
    print("[ERROR] Could not load chapter 70")
    sys.exit(1)

# Simulate OLD system (full intro[:2000])
print("\n1. OLD SYSTEM (full intro[:2000]):")
intro_full = cached_chapter.get('user_introduction', '')
old_output = intro_full[:2000]
old_tokens = len(old_output.split()) * 1.3
print(f"   Length: {len(old_output)} chars")
print(f"   Estimated tokens: ~{int(old_tokens)}")

# Simulate NEW system with summary (mock - actual will be shorter)
print("\n2. NEW SYSTEM (with summary - MOCK estimate):")
# Assume summary will be ~300-500 words total across 4 components
# amud: 2-3 sentences (~50-80 words)
# munasabat: 3-4 sentences (~70-100 words)
# historical_context: 2-3 sentences (~50-80 words)
# tone: 1-2 sentences (~30-50 words)
# Total: ~200-310 words → ~260-400 tokens

mock_summary_words = 250  # Conservative estimate
mock_summary_tokens = mock_summary_words * 1.3
print(f"   Estimated words: ~{mock_summary_words}")
print(f"   Estimated tokens: ~{int(mock_summary_tokens)}")

# Simulate FALLBACK system (truncated intro[:500])
print("\n3. FALLBACK SYSTEM (truncated intro[:500]):")
fallback_output = intro_full[:500]
fallback_tokens = len(fallback_output.split()) * 1.3
print(f"   Length: {len(fallback_output)} chars")
print(f"   Estimated tokens: ~{int(fallback_tokens)}")

# Calculate savings
print("\n" + "=" * 70)
print("TOKEN SAVINGS CALCULATION:")
print("=" * 70)

balaghah_tokens = 15000
ruku_tokens = 2500

old_total = balaghah_tokens + int(old_tokens) + ruku_tokens
new_total = balaghah_tokens + int(mock_summary_tokens) + ruku_tokens
savings = old_total - new_total
savings_percent = (savings / old_total) * 100

print(f"\nOLD System:")
print(f"   Balaghah guide:     15,000 tokens")
print(f"   Chapter (full):     ~{int(old_tokens):,} tokens")
print(f"   Ruku data:           2,500 tokens")
print(f"   -----------------------------")
print(f"   TOTAL:              ~{old_total:,} tokens")

print(f"\nNEW System:")
print(f"   Balaghah guide:     15,000 tokens")
print(f"   Chapter (summary):  ~{int(mock_summary_tokens):,} tokens")
print(f"   Ruku data:           2,500 tokens")
print(f"   -----------------------------")
print(f"   TOTAL:              ~{new_total:,} tokens")

print(f"\nSAVINGS:")
print(f"   Per session:        ~{savings:,} tokens")
print(f"   Percentage:         ~{savings_percent:.1f}%")
print(f"   Per surah (10 rukus): ~{savings * 10:,} tokens")

print("\n" + "=" * 70)
print("COST ANALYSIS:")
print("=" * 70)

# Assuming GPT-5.1 pricing (example)
input_cost_per_1k = 0.005  # $5 per 1M tokens
output_cost_per_1k = 0.015  # $15 per 1M tokens

# Summary extraction cost (one-time per chapter)
extraction_input_tokens = 2000  # Prompt + full context
extraction_output_tokens = 500  # Summary
extraction_cost = (extraction_input_tokens / 1000 * input_cost_per_1k) + \
                  (extraction_output_tokens / 1000 * output_cost_per_1k)

print(f"\nSummary extraction (one-time per chapter):")
print(f"   Input:  {extraction_input_tokens:,} tokens × ${input_cost_per_1k:.3f}/1K = ${extraction_input_tokens/1000*input_cost_per_1k:.4f}")
print(f"   Output: {extraction_output_tokens:,} tokens × ${output_cost_per_1k:.3f}/1K = ${extraction_output_tokens/1000*output_cost_per_1k:.4f}")
print(f"   Total:  ${extraction_cost:.4f} per chapter")

# Per session savings
session_input_savings = savings
session_cost_savings = (session_input_savings / 1000) * input_cost_per_1k

print(f"\nPer ruku session savings:")
print(f"   Tokens saved:  {savings:,} tokens")
print(f"   Cost saved:    ${session_cost_savings:.4f} per session")

# Breakeven
breakeven_sessions = extraction_cost / session_cost_savings

print(f"\nBreakeven analysis:")
print(f"   Extraction cost:  ${extraction_cost:.4f}")
print(f"   Savings per session: ${session_cost_savings:.4f}")
print(f"   Breakeven at:     ~{int(breakeven_sessions)} sessions")

print("\n" + "=" * 70)
print("[OK] Token estimation complete!")
print(f"     Estimated savings: {savings:,} tokens per session ({savings_percent:.1f}%)")
print("=" * 70)
