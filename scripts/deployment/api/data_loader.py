"""
Data loader utilities for accessing Quran data
Wrapper around existing metadata_loader.py and get_verse_info_v3.py
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "loaders"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "tools"))

from metadata_loader import MetadataLoader
from get_verse_info_v3 import load_comprehensive_quran, extract_verse_info_compact


class QuranDataLoader:
    """Wrapper for loading Quran data with simplified interface"""

    def __init__(self):
        """Initialize metadata loader"""
        self.loader = MetadataLoader()

        # Load comprehensive data using get_verse_info_v3 function
        comprehensive_path = PROJECT_ROOT / "data" / "quran_comprehensive.json"
        print(f"Loading comprehensive data from: {comprehensive_path}")
        self.comprehensive_data = load_comprehensive_quran(str(comprehensive_path))

        print("QuranDataLoader initialized (using get_verse_info_v3)")

    # ===== Properties for RukuSessionManager =====

    @property
    def metadata(self) -> MetadataLoader:
        """Expose MetadataLoader for direct access"""
        return self.loader

    @property
    def ruku_divisions(self) -> Dict[str, Any]:
        """Get ruku divisions data (556 traditional divisions)"""
        return self.loader.ruku_divisions

    def get_chapter_metadata(self, surah_num: int) -> Dict[str, Any]:
        """
        Get chapter metadata

        Args:
            surah_num: Surah number (1-114)

        Returns:
            Chapter metadata dict
        """
        meta = self.loader.get_chapter_metadata(surah_num)
        if not meta:
            raise ValueError(f"Chapter {surah_num} not found")
        return meta

    def get_verse_full_data(self, surah_num: int, verse_num: int) -> Dict[str, Any]:
        """
        Get complete verse data with all available information
        Uses get_verse_info_v3 for pure JSON balaghah format

        Args:
            surah_num: Surah number
            verse_num: Verse number

        Returns:
            Complete verse data dict (v3 format with pure JSON balaghah)
        """
        # Use extract_verse_info_compact from v3 to get full data
        # Pass self.loader to avoid repeated MetadataLoader instantiation
        result = extract_verse_info_compact(surah_num, verse_num, verse_num, self.comprehensive_data, self.loader)

        # Extract single verse from result
        if result.get('verses') and len(result['verses']) > 0:
            verse_data = result['verses'][0]

            # Ensure it has the structure expected by verse_analyzer
            # Map v3 format to expected format
            return {
                "surah": surah_num,
                "verse": verse_num,
                "arabic": verse_data.get('text', ''),
                "english": verse_data.get('translation', ''),
                "tafsir": verse_data.get('tafsir'),
                "asbab_nuzul": verse_data.get('asbab_nuzul'),
                "balaghah": verse_data.get('balaghah'),  # Pure JSON format from v3
                "root_repetitions": verse_data.get('root_repetitions'),
                "words": verse_data.get('words'),  # Morphology array from v3
                "section_heading": None  # Will be added below
            }

        # Fallback if extraction failed
        return {
            "surah": surah_num,
            "verse": verse_num,
            "arabic": "",
            "english": "",
            "tafsir": None,
            "asbab_nuzul": None,
            "balaghah": None,
            "root_repetitions": None,
            "words": None,
            "section_heading": None
        }

    def get_all_verses_in_surah(self, surah_num: int) -> List[Dict[str, Any]]:
        """
        Get all verses in a surah (for short surah full load)

        Args:
            surah_num: Surah number

        Returns:
            List of verse dicts with basic data
        """
        chapter_meta = self.get_chapter_metadata(surah_num)
        verse_count = chapter_meta['verses_count']  # Fixed: was 'verses'

        verses = []
        for v in range(1, verse_count + 1):
            # Load basic data for each verse
            verse_data = self.get_verse_full_data(surah_num, v)
            verses.append(verse_data)

        return verses

    def get_surah_context(self, surah_num: int) -> Optional[str]:
        """
        Get surah introduction/context (Maududi)

        Args:
            surah_num: Surah number

        Returns:
            Surah context text or None
        """
        context = self.loader.get_qurancom_context(surah_num)
        return context

    def get_all_section_headings(self, surah_num: int) -> List[Dict[str, Any]]:
        """
        Get all section headings for a surah

        Args:
            surah_num: Surah number

        Returns:
            List of section heading dicts
        """
        # This would require iterating through all verses
        # and collecting unique sections
        # Simplified version for now

        chapter_meta = self.get_chapter_metadata(surah_num)
        verse_count = chapter_meta['verses_count']  # Fixed: was 'verses'

        sections = []
        seen_headings = set()

        for v in range(1, verse_count + 1):
            section = self.loader.get_section_for_verse(surah_num, v)
            if section:
                heading = section.get("heading")
                if heading and heading not in seen_headings:
                    sections.append({
                        "heading": heading,
                        "verse_start": section.get("verse_start"),
                        "verse_end": section.get("verse_end")
                    })
                    seen_headings.add(heading)

        return sections

    def parse_verse_range(self, verse_range_str: str) -> tuple:
        """
        Parse verse range string

        Args:
            verse_range_str: Format "68:1-10" or "2:255"

        Returns:
            (surah_num, [verse_numbers])

        Raises:
            ValueError: If format is invalid
        """
        try:
            # Split surah and verses
            parts = verse_range_str.split(':')
            if len(parts) != 2:
                raise ValueError("Format must be 'surah:verse' or 'surah:start-end'")

            surah_num = int(parts[0])

            # Check if range or single verse
            if '-' in parts[1]:
                verse_start, verse_end = parts[1].split('-')
                verse_nums = list(range(int(verse_start), int(verse_end) + 1))
            else:
                verse_nums = [int(parts[1])]

            return surah_num, verse_nums

        except Exception as e:
            raise ValueError(f"Invalid verse range format: {verse_range_str}. Error: {e}")


if __name__ == "__main__":
    # Test data loader
    loader = QuranDataLoader()

    # Test parse verse range
    surah, verses = loader.parse_verse_range("68:1-10")
    print(f"Parsed: Surah {surah}, Verses {verses}")

    # Test get chapter metadata
    meta = loader.get_chapter_metadata(68)
    print(f"Chapter metadata: {meta}")

    # Test get surah context
    context = loader.get_surah_context(68)
    if context:
        print(f"Surah context (first 200 chars): {context[:200]}...")

    # Test get verse data
    verse_data = loader.get_verse_full_data(68, 1)
    print(f"Verse data keys: {verse_data.keys()}")
