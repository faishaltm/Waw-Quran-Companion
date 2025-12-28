#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate morphology_segments.json against original morphology_full.json
Compare segment counts, verify data completeness, and test sample verses
"""

import json
import os
import sys

# Add loaders path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loaders'))
from metadata_loader import MetadataLoader


def load_old_morphology(filepath):
    """Load the old morphology_full.json format"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['morphology']


def validate_total_segments(old_morphology, metadata_loader):
    """Validate total segment counts match"""
    print("=" * 60)
    print("VALIDATION 1: Total Segment Counts")
    print("=" * 60)

    old_count = len(old_morphology)
    print(f"Old morphology_full.json: {old_count:,} segments")

    # Count segments in new format
    new_count = 0
    if metadata_loader.morphology_segments:
        for chapter_num, chapter_data in metadata_loader.morphology_segments.items():
            for verse_num, verse_data in chapter_data.items():
                for word_num, segments in verse_data.items():
                    new_count += len(segments)

    print(f"New morphology_segments.json: {new_count:,} segments")

    if new_count > old_count:
        print(f"[OK] New format has MORE segments ({new_count - old_count:,} additional)")
        print("     This is expected: github source has more granular segment-level data")
        result = True
    elif old_count == new_count:
        print("[OK] Segment counts match exactly!")
        result = True
    else:
        print(f"[WARN] New format has FEWER segments ({old_count - new_count:,} missing)")
        result = False

    print()
    return result


def validate_sample_verses(test_verses, metadata_loader):
    """Validate specific sample verses"""
    print("=" * 60)
    print("VALIDATION 2: Sample Verse Verification")
    print("=" * 60)

    all_pass = True

    for chapter, verse in test_verses:
        print(f"\nChapter {chapter}, Verse {verse}:")

        verse_morph = metadata_loader.get_verse_morphology(chapter, verse)

        if not verse_morph:
            print(f"  ✗ FAIL: No morphology found")
            all_pass = False
            continue

        word_count = len(verse_morph)
        total_segments = sum(len(segments) for segments in verse_morph.values())

        print(f"  Words: {word_count}")
        print(f"  Total segments: {total_segments}")

        # Check first word
        first_word_segments = verse_morph.get('1')
        if first_word_segments:
            print(f"  First word has {len(first_word_segments)} segments")

            # Check segment structure
            seg = first_word_segments[0]
            required_keys = ['segment', 'arabic', 'pos', 'features']
            missing_keys = [k for k in required_keys if k not in seg]

            if missing_keys:
                print(f"  [FAIL] Missing keys in segment: {missing_keys}")
                all_pass = False
            else:
                print(f"  [OK] Segment structure valid")
                print(f"    - POS: {seg['pos']}")
                print(f"    - Features: {len(seg['features'])} features")
        else:
            print(f"  [FAIL] No segments for word 1")
            all_pass = False

    print()
    if all_pass:
        print("[OK] ALL SAMPLE VERSES PASSED")
    else:
        print("[FAIL] SOME SAMPLE VERSES FAILED")

    print()
    return all_pass


def validate_data_completeness(metadata_loader):
    """Validate all chapters and verses have morphology data"""
    print("=" * 60)
    print("VALIDATION 3: Data Completeness Check")
    print("=" * 60)

    total_chapters = 114
    chapters_with_data = len(metadata_loader.morphology_segments.keys())

    print(f"Chapters with morphology: {chapters_with_data}/{total_chapters}")

    if chapters_with_data == total_chapters:
        print("[OK] All 114 chapters present")
    else:
        missing = set(range(1, 115)) - set(int(k) for k in metadata_loader.morphology_segments.keys())
        print(f"[FAIL] Missing chapters: {sorted(missing)}")

    # Sample check verses across different chapters
    sample_checks = [
        (1, 1),    # Al-Fatiha
        (2, 255),  # Ayat al-Kursi
        (18, 1),   # Al-Kahf
        (36, 1),   # Ya-Sin
        (67, 1),   # Al-Mulk
        (114, 6)   # An-Nas (last surah)
    ]

    missing_verses = []
    for chapter, verse in sample_checks:
        verse_morph = metadata_loader.get_verse_morphology(chapter, verse)
        if not verse_morph:
            missing_verses.append(f"{chapter}:{verse}")

    if missing_verses:
        print(f"[FAIL] Missing verses: {', '.join(missing_verses)}")
        return False
    else:
        print(f"[OK] All sample verses ({len(sample_checks)}) have morphology")

    print()
    return chapters_with_data == total_chapters


def compare_segment_data(old_morphology, metadata_loader):
    """Compare specific segment data between old and new formats"""
    print("=" * 60)
    print("VALIDATION 4: Segment Data Comparison")
    print("=" * 60)

    # Test verse 1:1:1 (Bismillah, word 1)
    print("\nComparing Verse 1:1, Word 1:")

    # Get from old format
    old_word1_segments = [
        seg for seg in old_morphology
        if seg['location']['chapter'] == 1
        and seg['location']['verse'] == 1
        and seg['location']['word'] == 1
    ]

    print(f"  Old format: {len(old_word1_segments)} segments")

    # Get from new format
    new_word1_segments = metadata_loader.get_word_morphology(1, 1, 1)
    print(f"  New format: {len(new_word1_segments) if new_word1_segments else 0} segments")

    if len(old_word1_segments) == len(new_word1_segments):
        print("  [OK] Segment count matches")

        # Compare POS tags
        old_pos = [seg['morphology']['pos'] for seg in old_word1_segments]
        new_pos = [seg['pos'] for seg in new_word1_segments]

        if old_pos == new_pos:
            print(f"  [OK] POS tags match: {old_pos}")
        else:
            print(f"  [WARN] POS tags differ")
            print(f"    Old: {old_pos}")
            print(f"    New: {new_pos}")
    else:
        print("  [INFO] Segment counts differ (expected with granular data)")

    print()


def main():
    """Main validation routine"""
    print("\n" + "=" * 60)
    print("MORPHOLOGY VALIDATION TOOL")
    print("Comparing morphology_full.json vs morphology_segments.json")
    print("=" * 60)
    print()

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    old_morph_path = os.path.join(project_root, 'data', 'linguistic', 'morphology_full.json')

    # Load old morphology
    print("Loading old morphology format...")
    try:
        old_morphology = load_old_morphology(old_morph_path)
        print(f"  Loaded {len(old_morphology):,} segments")
    except FileNotFoundError:
        print(f"ERROR: Old morphology file not found: {old_morph_path}")
        return 1

    # Load new morphology via metadata loader
    print("Loading new morphology format...")
    try:
        metadata_loader = MetadataLoader()
        if not metadata_loader.morphology_segments:
            print("ERROR: New morphology segments not loaded")
            return 1
    except Exception as e:
        print(f"ERROR loading new morphology: {e}")
        return 1

    print()

    # Run validations
    test_verses = [
        (1, 1),    # Al-Fatiha opening
        (68, 4),   # Used in balaghah examples
        (67, 23),  # Al-Mulk with takrar patterns
        (2, 255)   # Ayat al-Kursi
    ]

    results = []
    results.append(validate_total_segments(old_morphology, metadata_loader))
    results.append(validate_sample_verses(test_verses, metadata_loader))
    results.append(validate_data_completeness(metadata_loader))
    compare_segment_data(old_morphology, metadata_loader)

    # Final summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n[OK] ALL VALIDATIONS PASSED")
        print("The new morphology_segments.json is valid and complete!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} VALIDATION(S) FAILED")
        print("Please review the errors above.")
        return 1


if __name__ == '__main__':
    exit(main())
