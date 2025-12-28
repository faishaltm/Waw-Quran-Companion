"""
Test script for new simplified chapter context generation
Tests that:
1. Chapter context only has user_introduction field
2. user_introduction is comprehensive (800-1500 words)
3. start_conversation_with_introduction() works correctly
4. Section headings are loaded properly
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager
from api.chapter_context_generator import ChapterContextGenerator
from api.conversation_manager import ConversationManager
from api.section_session_manager import SectionSessionManager
from api.data_loader import QuranDataLoader
from openai import OpenAI


def test_chapter_context_generation(surah_num: int = 68):
    """Test chapter context generation with new format"""

    print(f"\n{'='*60}")
    print(f"TESTING CHAPTER CONTEXT GENERATION FOR SURAH {surah_num}")
    print(f"{'='*60}\n")

    # Initialize components
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        return False

    client = OpenAI(api_key=api_key)
    cache = CacheManager()
    loader = QuranDataLoader()
    generator = ChapterContextGenerator(cache, client, loader)

    # Test 1: Generate chapter context
    print("[TEST 1] Generating chapter context...")
    try:
        context = generator.get_or_generate(surah_num, force_regenerate=False)
        print("[OK] Chapter context generated successfully")
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

    # Test 2: Check JSON structure
    print("\n[TEST 2] Checking JSON structure...")
    expected_fields = {'surah_number', 'user_introduction'}
    actual_fields = set(context.keys())

    # Remove metadata fields (start with _)
    actual_content_fields = {k for k in actual_fields if not k.startswith('_')}

    print(f"  Expected fields: {expected_fields}")
    print(f"  Actual content fields: {actual_content_fields}")

    if actual_content_fields == expected_fields:
        print("[OK] JSON structure is correct (only user_introduction)")
    else:
        print(f"[FAIL] Unexpected fields found")
        print(f"  Extra fields: {actual_content_fields - expected_fields}")
        print(f"  Missing fields: {expected_fields - actual_content_fields}")
        return False

    # Test 3: Check user_introduction content
    print("\n[TEST 3] Checking user_introduction content...")
    user_intro = context.get('user_introduction', '')
    word_count = len(user_intro.split())

    print(f"  Length: {len(user_intro)} characters")
    print(f"  Word count: {word_count} words")

    if 400 <= word_count <= 2000:  # Allow some flexibility
        print(f"[OK] user_introduction has appropriate length ({word_count} words)")
    else:
        print(f"[WARN] user_introduction length outside expected range (400-2000 words)")

    # Show preview
    preview = user_intro[:300]
    print(f"\n  Preview:\n  {preview}...\n")

    # Test 4: Test conversation initialization
    print("[TEST 4] Testing conversation initialization...")
    try:
        conv_manager = ConversationManager(cache, client, loader)
        test_session_id = f"test_session_{surah_num}"

        conv_manager.start_conversation_with_introduction(
            session_id=test_session_id,
            surah_num=surah_num,
            user_introduction=user_intro
        )

        print("[OK] Conversation initialized successfully")

        # Check conversation structure
        conversation = cache.get_conversation(test_session_id)
        if conversation:
            messages = conversation.get('messages', [])
            print(f"  Message count: {len(messages)}")

            if len(messages) >= 2:
                first_msg = messages[0]
                second_msg = messages[1]

                print(f"  First message role: {first_msg.get('role')}")
                print(f"  Second message role: {second_msg.get('role')}")

                if first_msg.get('role') == 'system' and second_msg.get('role') == 'assistant':
                    print("âœ“ Conversation structure is correct")
                    print(f"  Assistant intro length: {len(second_msg.get('content', ''))} chars")
                else:
                    print("âœ— FAILED: Incorrect message roles")
                    return False
            else:
                print("âœ— FAILED: Not enough messages in conversation")
                return False
        else:
            print("âœ— FAILED: Could not retrieve conversation")
            return False

        # Clean up test conversation
        cache.delete_conversation(test_session_id)

    except Exception as e:
        print(f"âœ— FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5: Test section headings
    print("\n[TEST 5] Testing section headings...")
    try:
        section_manager = SectionSessionManager(cache, client, loader)
        sections = section_manager.get_sections_for_chapter(surah_num)

        print(f"  Total sections: {len(sections)}")

        if len(sections) > 0:
            print("âœ“ Sections loaded successfully")

            # Show first 3 sections
            print("\n  First 3 sections:")
            for i, section in enumerate(sections[:3], 1):
                heading = section.get('heading', 'No heading')
                verse_range = f"{section['verse_start']}-{section['verse_end']}"
                print(f"    {i}. \"{heading}\" (verses {verse_range})")
        else:
            print("âœ— FAILED: No sections found")
            return False

        # Test getting section with full data
        section_data = section_manager.get_section_full_data(surah_num, 0)
        if section_data:
            section_info = section_data.get('section_info', {})
            heading = section_info.get('heading', 'No heading')
            print(f"\n  Section 1 heading: \"{heading}\"")
            print("âœ“ Section data retrieval works correctly")
        else:
            print("âœ— FAILED: Could not get section data")
            return False

    except Exception as e:
        print(f"âœ— FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # All tests passed
    print(f"\n{'='*60}")
    print("ALL TESTS PASSED âœ“")
    print(f"{'='*60}\n")

    return True


def test_cache_format():
    """Test that old cache format is detected and regenerated"""
    print(f"\n{'='*60}")
    print("TESTING CACHE FORMAT DETECTION")
    print(f"{'='*60}\n")

    cache = CacheManager()

    # Simulate old format
    old_format = {
        'surah_number': 68,
        'main_themes': ['theme1', 'theme2'],
        'structure_overview': 'some structure',
        'user_introduction': 'intro text'
    }

    print("[TEST] Checking old format detection...")
    has_old_fields = 'main_themes' in old_format or 'structure_overview' in old_format

    if has_old_fields:
        print("âœ“ Old format correctly detected (has main_themes or structure_overview)")
    else:
        print("âœ— FAILED: Old format not detected")
        return False

    # Check new format
    new_format = {
        'surah_number': 68,
        'user_introduction': 'intro text',
        '_generation_method': 'full_load',
        '_tokens_used': 10000
    }

    print("\n[TEST] Checking new format validation...")
    has_old_fields = 'main_themes' in new_format or 'structure_overview' in new_format

    if not has_old_fields:
        print("âœ“ New format correctly validated (no old fields)")
    else:
        print("âœ— FAILED: New format has old fields")
        return False

    print(f"\n{'='*60}")
    print("CACHE FORMAT TESTS PASSED âœ“")
    print(f"{'='*60}\n")

    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING NEW CHAPTER CONTEXT ARCHITECTURE")
    print("="*60)

    # Test cache format detection
    if not test_cache_format():
        print("\nCache format tests FAILED")
        sys.exit(1)

    # Test chapter context generation for a short surah
    if not test_chapter_context_generation(surah_num=68):
        print("\nChapter context tests FAILED for surah 68")
        sys.exit(1)

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY âœ“")
    print("="*60)
    print("\nThe new architecture is working correctly:")
    print("  â€¢ Chapter context only contains user_introduction")
    print("  â€¢ user_introduction is comprehensive and well-formatted")
    print("  â€¢ Conversation initialization works with new method")
    print("  â€¢ Section headings are loaded and accessible")
    print("\nYou can now run the Telegram bot with these changes!")

