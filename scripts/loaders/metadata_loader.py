#!/usr/bin/env python3
"""
Unified metadata loader for Quran linguistic analysis
Loads: chapter metadata, tafsir, asbab al-nuzul
"""

import json
import os

class MetadataLoader:
    """Unified interface to load all Quranic metadata"""

    def __init__(self, base_dir=None, load_morphology=True):
        """Initialize and load all metadata files

        Args:
            base_dir: Base directory for data files (default: auto-detect)
            load_morphology: Whether to load morphology segments (default: True)
        """
        # Default to ../../data/ relative to this script's location
        if base_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(script_dir, '..', '..', 'data')

        self.base_dir = base_dir
        metadata_dir = os.path.join(base_dir, 'metadata')
        linguistic_dir = os.path.join(base_dir, 'linguistic')

        # Load chapter metadata
        chapter_metadata_path = os.path.join(metadata_dir, 'chapter_metadata.json')
        with open(chapter_metadata_path, 'r', encoding='utf-8') as f:
            self.chapter_metadata = json.load(f)

        # Load tafsir index
        tafsir_path = os.path.join(metadata_dir, 'tafsir_index.json')
        with open(tafsir_path, 'r', encoding='utf-8') as f:
            self.tafsir_index = json.load(f)

        # Load asbab nuzul index
        asbab_path = os.path.join(metadata_dir, 'asbab_nuzul_index.json')
        with open(asbab_path, 'r', encoding='utf-8') as f:
            self.asbab_nuzul_index = json.load(f)

        # Load surah info (with introductions from Ibn Kathir)
        surah_info_path = os.path.join(metadata_dir, 'surah_info.json')
        if os.path.exists(surah_info_path):
            with open(surah_info_path, 'r', encoding='utf-8') as f:
                self.surah_info = json.load(f)
        else:
            print(f"Warning: Surah info file not found: {surah_info_path}")
            self.surah_info = {}

        # Load ruku divisions (traditional thematic sections)
        ruku_path = os.path.join(metadata_dir, 'ruku_divisions.json')
        if os.path.exists(ruku_path):
            with open(ruku_path, 'r', encoding='utf-8') as f:
                self.ruku_divisions = json.load(f)
                # Also create verse-to-ruku lookup for fast access
                self._build_verse_to_ruku_map()
        else:
            print(f"Warning: Ruku divisions file not found: {ruku_path}")
            self.ruku_divisions = {}
            self.verse_to_ruku = {}

        # Load Clear Quran sections (more detailed thematic sections with headings)
        clear_quran_sections_path = os.path.join(metadata_dir, 'clear_quran_sections.json')
        if os.path.exists(clear_quran_sections_path):
            with open(clear_quran_sections_path, 'r', encoding='utf-8') as f:
                self.clear_quran_sections = json.load(f)
                # Build verse-to-section lookup for fast access
                self._build_verse_to_section_map()
        else:
            print(f"Warning: Clear Quran sections file not found: {clear_quran_sections_path}")
            self.clear_quran_sections = {}
            self.verse_to_section = {}

        # Load Quran.com surah context (Maududi's Tafhim al-Quran)
        qurancom_context_path = os.path.join(metadata_dir, 'surah_context_qurancom.json')
        if os.path.exists(qurancom_context_path):
            with open(qurancom_context_path, 'r', encoding='utf-8') as f:
                self.qurancom_context = json.load(f)
        else:
            print(f"Warning: Quran.com context file not found: {qurancom_context_path}")
            self.qurancom_context = {}

        # Load revelation order (Tanzil.net chronological data)
        revelation_order_path = os.path.join(metadata_dir, 'revelation_order.json')
        if os.path.exists(revelation_order_path):
            with open(revelation_order_path, 'r', encoding='utf-8') as f:
                revelation_order_data = json.load(f)
                self.revelation_order = revelation_order_data.get('chapters', {})
        else:
            print(f"Warning: Revelation order file not found: {revelation_order_path}")
            self.revelation_order = {}

        # Load Al-Kashshaf tafsir (Arabic - rhetorical)
        kashshaf_path = os.path.join(metadata_dir, 'tafsir_kashshaf_arabic.json')
        if os.path.exists(kashshaf_path):
            with open(kashshaf_path, 'r', encoding='utf-8') as f:
                kashshaf_data = json.load(f)
                self.tafsir_kashshaf = self._build_kashshaf_lookup(kashshaf_data)
        else:
            print(f"Warning: Al-Kashshaf tafsir file not found: {kashshaf_path}")
            self.tafsir_kashshaf = {}

        # Load Ma'arif al-Qur'an (English - comprehensive)
        maarif_path = os.path.join(metadata_dir, 'tafsir_maarif_en.json')
        if os.path.exists(maarif_path):
            with open(maarif_path, 'r', encoding='utf-8') as f:
                maarif_data = json.load(f)
                self.tafsir_maarif = self._build_simple_tafsir_lookup(maarif_data)
        else:
            print(f"Warning: Ma'arif tafsir file not found: {maarif_path}")
            self.tafsir_maarif = {}

        # Load Ibn Kathir (English - classical)
        ibn_kathir_path = os.path.join(metadata_dir, 'tafsir_ibn_kathir_en.json')
        if os.path.exists(ibn_kathir_path):
            with open(ibn_kathir_path, 'r', encoding='utf-8') as f:
                ibn_kathir_data = json.load(f)
                self.tafsir_ibn_kathir = self._build_simple_tafsir_lookup(ibn_kathir_data)
        else:
            print(f"Warning: Ibn Kathir tafsir file not found: {ibn_kathir_path}")
            self.tafsir_ibn_kathir = {}

        # Load morphology segments if requested
        self.morphology_segments = None
        if load_morphology:
            morphology_path = os.path.join(linguistic_dir, 'morphology_segments.json')
            if os.path.exists(morphology_path):
                print(f"Loading morphology segments...")
                with open(morphology_path, 'r', encoding='utf-8') as f:
                    morph_data = json.load(f)
                    self.morphology_segments = morph_data['morphology']
                    print(f"  Total segments: {morph_data['metadata']['total_segments']}")
            else:
                print(f"Warning: Morphology segments file not found: {morphology_path}")

        print(f"Metadata loaded:")
        print(f"  Chapters: {len(self.chapter_metadata)}")
        print(f"  Tafsir entries (Al-Qushairi): {len(self.tafsir_index)}")
        print(f"  Tafsir (Al-Kashshaf Arabic): {sum(len(verses) for verses in self.tafsir_kashshaf.values())} verses")
        print(f"  Tafsir (Ma'arif English): {sum(len(verses) for verses in self.tafsir_maarif.values())} verses")
        print(f"  Tafsir (Ibn Kathir English): {sum(len(verses) for verses in self.tafsir_ibn_kathir.values())} verses")
        print(f"  Asbab nuzul verses: {len(self.asbab_nuzul_index)}")
        print(f"  Surah info (Ibn Kathir): {len(self.surah_info)}")
        print(f"  Quran.com context (Maududi): {len(self.qurancom_context)}")
        print(f"  Revelation order: {len(self.revelation_order)}")
        print(f"  Ruku divisions: {len(self.ruku_divisions)}")
        if self.clear_quran_sections:
            total_sections = sum(len(chapter_data['sections']) for chapter_data in self.clear_quran_sections.values())
            print(f"  Clear Quran sections: {total_sections} sections across {len(self.clear_quran_sections)} chapters")
        if self.morphology_segments:
            print(f"  Morphology: Enabled")

    def _build_verse_to_ruku_map(self):
        """Build a lookup map from (chapter, verse) to ruku number"""
        self.verse_to_ruku = {}

        for ruku_num_str, ruku_data in self.ruku_divisions.items():
            chapter = ruku_data['chapter']
            verse_start = ruku_data['verse_start']
            verse_end = ruku_data['verse_end']

            # Map all verses in this ruku to the ruku number
            for verse in range(verse_start, verse_end + 1):
                key = f"{chapter}:{verse}"
                self.verse_to_ruku[key] = int(ruku_num_str)

    def _build_verse_to_section_map(self):
        """Build a lookup map from (chapter, verse) to Clear Quran section"""
        self.verse_to_section = {}

        for chapter_str, chapter_data in self.clear_quran_sections.items():
            chapter = int(chapter_str)
            for section in chapter_data['sections']:
                verse_start = section['verse_start']
                verse_end = section['verse_end']

                # Map all verses in this section to the section data
                for verse in range(verse_start, verse_end + 1):
                    key = f"{chapter}:{verse}"
                    self.verse_to_section[key] = section

    def _build_kashshaf_lookup(self, kashshaf_data):
        """
        Build lookup dict for Al-Kashshaf tafsir.

        Al-Kashshaf has multi-verse commentaries, so we need to handle verses_range.
        For verse 2:40, we check if it's in any entry's verses_range.

        Returns: {chapter: {verse: tafsir_entry}}
        """
        lookup = {}
        verse_index = kashshaf_data.get('verse_index', {})

        for chapter_str, verses_dict in verse_index.items():
            chapter = int(chapter_str)
            lookup[chapter] = {}

            for verse_str, entry in verses_dict.items():
                verse = int(verse_str)
                verses_range = entry.get('verses_range', [verse])

                # Map ALL verses in range to this entry
                for v in verses_range:
                    lookup[chapter][v] = {
                        'text': entry.get('text', ''),
                        'verses_range': verses_range,
                        'source': 'Al-Kashshaf (Zamakhshari)',
                        'methodology': 'Rhetorical/Linguistic - Explains eloquence, word choice, and syntax'
                    }

        return lookup

    def _build_simple_tafsir_lookup(self, tafsir_data):
        """
        Build lookup dict for simple verse-level tafsirs (Ma'arif, Ibn Kathir).

        Returns: {chapter: {verse: text}}
        """
        lookup = {}
        verse_index = tafsir_data.get('verse_index', {})

        for chapter_str, verses_dict in verse_index.items():
            chapter = int(chapter_str)
            lookup[chapter] = {}

            for verse_str, text in verses_dict.items():
                verse = int(verse_str)
                lookup[chapter][verse] = text

        return lookup

    def get_chapter_metadata(self, chapter):
        """Get metadata for a chapter"""
        key = str(chapter)
        return self.chapter_metadata.get(key)

    def get_tafsir(self, chapter, verse):
        """Get Al-Qushairi tafsir for a verse if available (LEGACY)"""
        key = f"{chapter}:{verse}"
        return self.tafsir_index.get(key)

    def get_tafsir_kashshaf(self, chapter, verse):
        """Get Al-Kashshaf tafsir for a verse if available

        Returns:
            Dict with text, verses_range, source, and methodology
            or None if not available
        """
        if chapter in self.tafsir_kashshaf:
            return self.tafsir_kashshaf[chapter].get(verse)
        return None

    def get_tafsir_maarif(self, chapter, verse):
        """Get Ma'arif al-Qur'an tafsir for a verse

        Returns:
            String with tafsir text or None if not available
        """
        if chapter in self.tafsir_maarif:
            return self.tafsir_maarif[chapter].get(verse)
        return None

    def get_tafsir_ibn_kathir(self, chapter, verse):
        """Get Tafsir Ibn Kathir for a verse

        Returns:
            String with tafsir text or None if not available
        """
        if chapter in self.tafsir_ibn_kathir:
            return self.tafsir_ibn_kathir[chapter].get(verse)
        return None

    def get_all_tafsirs(self, chapter, verse):
        """Get all available tafsirs for a verse

        Returns:
            Dict with keys: al_qushairi, kashshaf_arabic, maarif_en, ibn_kathir_en
            Only includes tafsirs that are available for this verse
        """
        result = {}

        # Legacy Al-Qushairi
        al_qushairi = self.get_tafsir(chapter, verse)
        if al_qushairi:
            result['al_qushairi'] = al_qushairi

        # Al-Kashshaf (Arabic)
        kashshaf = self.get_tafsir_kashshaf(chapter, verse)
        if kashshaf:
            result['kashshaf_arabic'] = kashshaf

        # Ma'arif (English)
        maarif = self.get_tafsir_maarif(chapter, verse)
        if maarif:
            result['maarif_en'] = {
                'text': maarif,
                'source': "Ma'arif al-Qur'an (Mufti Muhammad Shafi)",
                'methodology': 'Modern comprehensive - Balanced linguistic, legal, theological, and practical commentary'
            }

        # Ibn Kathir (English)
        ibn_kathir = self.get_tafsir_ibn_kathir(chapter, verse)
        if ibn_kathir:
            result['ibn_kathir_en'] = {
                'text': ibn_kathir,
                'source': 'Tafsir Ibn Kathir (Hafiz Ibn Kathir)',
                'methodology': 'Classical hadith-based - Quran explains Quran, then Hadith, then Companions'
            }

        return result if result else None

    def get_asbab_nuzul(self, chapter, verse):
        """Get occasions of revelation for a verse if available"""
        key = f"{chapter}:{verse}"
        return self.asbab_nuzul_index.get(key, [])

    def get_verse_metadata(self, chapter, verse):
        """Get all metadata for a specific verse"""
        return {
            'chapter_metadata': self.get_chapter_metadata(chapter),
            'tafsir': self.get_tafsir(chapter, verse),
            'asbab_nuzul': self.get_asbab_nuzul(chapter, verse)
        }

    def has_tafsir(self, chapter, verse):
        """Check if tafsir exists for this verse"""
        key = f"{chapter}:{verse}"
        return key in self.tafsir_index

    def has_asbab_nuzul(self, chapter, verse):
        """Check if asbab nuzul exists for this verse"""
        key = f"{chapter}:{verse}"
        return key in self.asbab_nuzul_index

    def get_surah_info(self, chapter):
        """Get comprehensive surah information including introduction

        Returns:
            Dict with name, translation, revelation_place, verses_count,
            and introduction (from Ibn Kathir tafsir)
        """
        key = str(chapter)
        return self.surah_info.get(key)

    def get_qurancom_context(self, chapter):
        """Get comprehensive surah context from Quran.com API

        Source: Sayyid Abul Ala Maududi - Tafhim al-Qur'an

        Returns:
            Dict with source, short_text, and full text introduction
            covering themes, historical context, and verse structure
        """
        key = str(chapter)
        return self.qurancom_context.get(key)

    def get_revelation_order(self, chapter):
        """Get revelation order and mixed revelation info from Tanzil.net

        Returns:
            Dict with revelation_order (1-114 chronologically) and
            mixed_revelation notes if applicable
        """
        key = str(chapter)
        return self.revelation_order.get(key)

    def get_ruku_for_verse(self, chapter, verse):
        """Get ruku (thematic section) information for a verse

        Returns:
            Dict with ruku_number, chapter, chapter_name, verse_start,
            verse_end, verse_count, or None if not found
        """
        key = f"{chapter}:{verse}"
        ruku_num = self.verse_to_ruku.get(key)

        if ruku_num is not None:
            return self.ruku_divisions.get(str(ruku_num))

        return None

    def get_ruku_by_number(self, ruku_num):
        """Get ruku information by ruku number (1-556)"""
        return self.ruku_divisions.get(str(ruku_num))

    def get_section_for_verse(self, chapter, verse):
        """Get Clear Quran section (with thematic heading) for a verse

        Returns:
            Dict with section_id, chapter, heading, verse_start, verse_end,
            or None if not found

        Note: Clear Quran sections are more detailed than traditional rukus,
        providing specific thematic headings for verse groups.
        """
        key = f"{chapter}:{verse}"
        return self.verse_to_section.get(key)

    def get_chapter_sections(self, chapter):
        """Get all Clear Quran sections for a chapter

        Args:
            chapter: Chapter number (1-114)

        Returns:
            List of section dicts with section_id, heading, verse_start, verse_end
            or empty list if chapter not found
        """
        chapter_key = str(chapter)
        chapter_data = self.clear_quran_sections.get(chapter_key, {})
        return chapter_data.get('sections', [])

    def get_word_morphology(self, chapter, verse, word):
        """Get segment-level morphology for a specific word

        Args:
            chapter: Chapter number (1-114)
            verse: Verse number
            word: Word number (1-based)

        Returns:
            List of segment dictionaries, or None if not available
            Each segment contains: segment, arabic, buckwalter, pos, features
        """
        if not self.morphology_segments:
            return None

        chapter_key = str(chapter)
        verse_key = str(verse)
        word_key = str(word)

        chapter_data = self.morphology_segments.get(chapter_key)
        if not chapter_data:
            return None

        verse_data = chapter_data.get(verse_key)
        if not verse_data:
            return None

        return verse_data.get(word_key)

    def get_verse_morphology(self, chapter, verse):
        """Get all morphology for a verse

        Args:
            chapter: Chapter number (1-114)
            verse: Verse number

        Returns:
            Dictionary mapping word numbers to segment lists
        """
        if not self.morphology_segments:
            return None

        chapter_key = str(chapter)
        verse_key = str(verse)

        chapter_data = self.morphology_segments.get(chapter_key)
        if not chapter_data:
            return None

        return chapter_data.get(verse_key)

    def get_statistics(self):
        """Get statistics about available metadata"""
        stats = {
            'total_chapters': len(self.chapter_metadata),
            'chapters_with_metadata': len(self.chapter_metadata),
            'verses_with_tafsir_qushairi': len(self.tafsir_index),
            'verses_with_tafsir_kashshaf': sum(len(verses) for verses in self.tafsir_kashshaf.values()),
            'verses_with_tafsir_maarif': sum(len(verses) for verses in self.tafsir_maarif.values()),
            'verses_with_tafsir_ibn_kathir': sum(len(verses) for verses in self.tafsir_ibn_kathir.values()),
            'verses_with_asbab': len(self.asbab_nuzul_index),
            'surahs_with_info': len(self.surah_info),
            'surahs_with_introductions': sum(1 for s in self.surah_info.values()
                                             if 'introduction' in s),
            'total_rukus': len(self.ruku_divisions),
            'total_clear_quran_sections': sum(len(chapter_data['sections'])
                                              for chapter_data in self.clear_quran_sections.values())
                                           if self.clear_quran_sections else 0,
            'chapters_with_sections': len(self.clear_quran_sections),
            'meccan_chapters': sum(1 for m in self.chapter_metadata.values()
                                   if m['revelation_place'] == 'makkah'),
            'medinan_chapters': sum(1 for m in self.chapter_metadata.values()
                                    if m['revelation_place'] == 'madinah'),
        }

        if self.morphology_segments:
            stats['morphology_enabled'] = True
        else:
            stats['morphology_enabled'] = False

        return stats

# Example usage
if __name__ == '__main__':
    loader = MetadataLoader()

    print("\n" + "=" * 60)
    print("Statistics:")
    stats = loader.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Example: Chapter 1 metadata")
    chapter_meta = loader.get_chapter_metadata(1)
    print(f"  Name: {chapter_meta['name_arabic']}")
    print(f"  Revelation place: {chapter_meta['revelation_place']}")
    print(f"  Revelation order: {chapter_meta['revelation_order']}")
    print(f"  Verses count: {chapter_meta['verses_count']}")

    print("\n" + "=" * 60)
    print("Example: Verse 1:5 complete metadata")
    verse_meta = loader.get_verse_metadata(1, 5)

    print(f"\nChapter: {verse_meta['chapter_metadata']['name_arabic']}")
    print(f"Revelation: {verse_meta['chapter_metadata']['revelation_place']}")

    if verse_meta['tafsir']:
        print(f"\nTafsir available: Yes")
        print(f"Preview: {verse_meta['tafsir']['tafsir'][:200]}...")
    else:
        print(f"\nTafsir available: No")

    if verse_meta['asbab_nuzul']:
        print(f"\nAsbab nuzul available: Yes ({len(verse_meta['asbab_nuzul'])} occasions)")
        for i, occasion in enumerate(verse_meta['asbab_nuzul'], 1):
            print(f"  Occasion {i}: {occasion['occasion'][:100]}...")
    else:
        print(f"\nAsbab nuzul available: No")
