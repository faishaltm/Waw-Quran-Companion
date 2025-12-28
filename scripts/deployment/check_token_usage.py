"""
Check actual token usage for chapter context
"""
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager
from api.data_loader import QuranDataLoader

def estimate_tokens(text):
    """Simple token estimation: chars / 4"""
    if not text:
        return 0
    return len(text) // 4

def check_surah_74_tokens():
    """Check token usage for Surah 74"""
    print("="*60)
    print("TOKEN USAGE ANALYSIS - SURAH 74")
    print("="*60)

    cache = CacheManager()
    loader = QuranDataLoader()

    # Get chapter context from cache
    context = cache.get_chapter_context(74)

    if not context:
        print("ERROR: Surah 74 not in cache yet")
        return

    # Get user_introduction
    user_intro = context.get('user_introduction', '')

    print(f"\n[1] USER_INTRODUCTION")
    print(f"  Characters: {len(user_intro):,}")
    print(f"  Estimated tokens: {estimate_tokens(user_intro):,}")
    print(f"  First 200 chars: {user_intro[:200]}...")

    # Get balaghah guide
    balaghah_path = Path(__file__).parent / "docs" / "skills" / "balaghah_quick_reference_v4_expanded.md"
    if balaghah_path.exists():
        with open(balaghah_path, 'r', encoding='utf-8') as f:
            balaghah_guide = f.read()

        print(f"\n[2] BALAGHAH GUIDE")
        print(f"  Characters: {len(balaghah_guide):,}")
        print(f"  Estimated tokens: {estimate_tokens(balaghah_guide):,}")
    else:
        print(f"\n[2] BALAGHAH GUIDE: Not found at {balaghah_path}")
        balaghah_guide = ""

    # Reconstruct system prompt
    chapter_meta = loader.get_chapter_metadata(74)
    system_prompt = f"""Anda adalah asisten analisis Al-Quran yang ahli dalam balaghah (retorika Arab).

PANDUAN BALAGHAH:
{balaghah_guide}

KONTEKS SURAH 74 ({chapter_meta.get('name_arabic', '')}):
Konteks surah telah diberikan di pesan pertama Anda. Gunakan informasi tersebut untuk analisis.

INSTRUKSI:
1. Ketika user meminta analisis ayat, berikan penjelasan mendalam dalam Bahasa Indonesia
2. Identifikasi dan jelaskan perangkat balaghah yang ada
3. Hubungkan dengan konteks surah (yang sudah Anda jelaskan) dan ayat sebelumnya (munasabat)
4. Gunakan bahasa yang mudah dipahami pembaca umum
5. Jika user bertanya tentang topik lain terkait ayat, jawab berdasarkan pengetahuan Anda
6. Selalu merujuk pada data yang diberikan (tafsir, morfologi, dll) jika relevan"""

    print(f"\n[3] SYSTEM PROMPT")
    print(f"  Characters: {len(system_prompt):,}")
    print(f"  Estimated tokens: {estimate_tokens(system_prompt):,}")

    # Calculate total
    total_chars = len(system_prompt) + len(user_intro)
    total_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_intro)

    print(f"\n[4] TOTAL CONVERSATION MEMORY (Initial)")
    print(f"  System prompt: {estimate_tokens(system_prompt):,} tokens")
    print(f"  User introduction: {estimate_tokens(user_intro):,} tokens")
    print(f"  ─────────────────────────")
    print(f"  TOTAL: {total_tokens:,} tokens")
    print(f"  Characters: {total_chars:,}")

    # Check what's actually in cache metadata
    if '_tokens_used' in context:
        print(f"\n[5] GENERATION COST (one-time, cached)")
        print(f"  Tokens used to generate: {context.get('_tokens_used'):,}")
        print(f"  Model: {context.get('_model', 'N/A')}")
        print(f"  Method: {context.get('_generation_method', 'N/A')}")

    print(f"\n[6] TOKEN BREAKDOWN")
    print(f"  System prompt (includes balaghah): ~{estimate_tokens(system_prompt):,} tokens")
    print(f"  User introduction: ~{estimate_tokens(user_intro):,} tokens")
    print(f"  Every message adds: ~estimated chars/4 tokens")

    print(f"\n[7] ISSUE ANALYSIS")
    if total_tokens < 20000:
        print(f"  ✓ Token usage looks reasonable ({total_tokens:,} < 20k)")
    else:
        print(f"  ✗ Token usage is high ({total_tokens:,} tokens)")
        print(f"    This means:")
        print(f"    - User_introduction is very long")
        print(f"    - Or balaghah guide is very long")
        print(f"    - Every conversation starts with {total_tokens:,} tokens!")

    # Check if user_introduction matches what system expected
    word_count = len(user_intro.split())
    print(f"\n[8] USER_INTRODUCTION QUALITY")
    print(f"  Word count: {word_count:,}")
    print(f"  Expected range: 800-1500 words")
    if 800 <= word_count <= 1500:
        print(f"  ✓ Within expected range")
    elif word_count > 1500:
        print(f"  ✗ TOO LONG - exceeds expected range by {word_count - 1500} words")
        print(f"    Recommendation: Compress or use reference-only approach")
    else:
        print(f"  ⚠ Too short - might need more detail")

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("="*60)
    print(f"The 19k tokens is mostly from:")
    if estimate_tokens(balaghah_guide) > 10000:
        print(f"  1. Balaghah guide: ~{estimate_tokens(balaghah_guide):,} tokens (MAJOR)")
    print(f"  2. User introduction: ~{estimate_tokens(user_intro):,} tokens")
    print(f"\nThis is CONVERSATION MEMORY, not generation cost.")
    print(f"Cache saves GENERATION cost (${context.get('_tokens_used', 0) * 0.000015:.3f})")
    print(f"but conversation memory is always needed for context.")
    print("="*60)

if __name__ == "__main__":
    check_surah_74_tokens()
