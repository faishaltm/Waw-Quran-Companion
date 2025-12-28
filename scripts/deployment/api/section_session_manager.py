"""
Section Session Manager
Manages session boundaries based on thematic section headings (1966 total from Clear Quran)
Each section = 1 session with full context + accumulated summary from previous sessions
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "loaders"))

from api.cache_manager import CacheManager
from api.data_loader import QuranDataLoader
from config.settings import MAX_ACCUMULATED_SUMMARY_TOKENS


class SectionSessionManager:
    """
    Manages session boundaries based on section headings.

    Key responsibilities:
    - Track which section user is on
    - Load full data for current section
    - Provide preview of next section
    - Manage accumulated summaries across sessions
    """

    def __init__(self, cache_manager: CacheManager, data_loader: QuranDataLoader):
        """
        Initialize SectionSessionManager

        Args:
            cache_manager: CacheManager instance
            data_loader: QuranDataLoader instance
        """
        self.cache = cache_manager
        self.loader = data_loader

        # Load section headings from Clear Quran
        # Note: We'll load sections on-demand from metadata.get_all_section_headings()

        # Build chapter -> section mapping for fast lookup
        self._build_chapter_section_map()

    def _build_chapter_section_map(self):
        """Build mapping from chapter number to list of sections in that chapter"""
        self.chapter_sections: Dict[int, List[Dict]] = {}

        # Load all sections from clear_quran_sections.json via metadata
        # This is done once at initialization
        for surah_num in range(1, 115):  # 1-114
            sections = self.loader.get_all_section_headings(surah_num)
            if sections:
                self.chapter_sections[surah_num] = sections
                # Already sorted by verse_start in the data file

    def get_sections_for_chapter(self, surah: int) -> List[Dict]:
        """
        Get all sections for a chapter

        Args:
            surah: Surah number (1-114)

        Returns:
            List of section dicts sorted by verse_start
        """
        return self.chapter_sections.get(surah, [])

    def get_section_count_for_chapter(self, surah: int) -> int:
        """Get total number of sections in a chapter"""
        return len(self.chapter_sections.get(surah, []))

    def get_section_by_index(self, surah: int, section_index: int) -> Optional[Dict]:
        """
        Get ruku by chapter-relative index (0-based)

        Args:
            surah: Surah number
            section_index: 0-based index within chapter

        Returns:
            Section dict or None
        """
        sections = self.chapter_sections.get(surah, [])
        if 0 <= section_index < len(sections):
            return sections[section_index]
        return None

    def get_current_section_index(self, surah: int, verse: int) -> int:
        """
        Get chapter-relative section index for a verse

        Args:
            surah: Surah number
            verse: Verse number

        Returns:
            0-based section index within chapter
        """
        sections = self.chapter_sections.get(surah, [])
        for i, section in enumerate(sections):
            if section['verse_start'] <= verse <= section['verse_end']:
                return i
        return 0

    def get_section_full_data(self, surah: int, section_index: int) -> Dict[str, Any]:
        """
        Get full verse data for all verses in a section

        Args:
            surah: Surah number
            section_index: 0-based section index within chapter

        Returns:
            Dict with section info (including heading) and full verse data
        """
        section = self.get_section_by_index(surah, section_index)
        if not section:
            return {}

        verse_start = section['verse_start']
        verse_end = section['verse_end']

        # Collect full data for all verses in section
        verses_data = []
        for verse_num in range(verse_start, verse_end + 1):
            verse_data = self.loader.get_verse_full_data(surah, verse_num)
            if verse_data:
                verses_data.append(verse_data)

        return {
            "section_info": {
                "chapter": surah,
                "section_index": section_index,
                "section_id": section.get('section_id'),
                "heading": section.get('heading', ''),  # KEY: Section heading from Clear Quran
                "verse_start": verse_start,
                "verse_end": verse_end,
                "verse_count": verse_end - verse_start + 1
            },
            "verses": verses_data
        }

    def get_next_section_preview(self, surah: int, current_section_index: int) -> Optional[Dict]:
        """
        Get preview of next section (for lookahead)

        Args:
            surah: Surah number
            current_section_index: Current section index (0-based)

        Returns:
            Dict with next section info (verse range, section heading if available)
        """
        next_index = current_section_index + 1
        sections = self.chapter_sections.get(surah, [])

        if next_index >= len(sections):
            # End of chapter
            return {
                "is_last": True,
                "message": "Ini adalah section terakhir dalam surah ini"
            }

        next_section = sections[next_index]

        # Section already has heading from Clear Quran
        section_heading = next_section.get('heading', 'No heading')

        return {
            "is_last": False,
            "section_index": next_index,
            "verse_start": next_section['verse_start'],
            "verse_end": next_section['verse_end'],
            "verse_count": next_section['verse_end'] - next_section['verse_start'] + 1,
            "section_heading": section_heading
        }

    # ===== Accumulated Summary Management =====

    def get_accumulated_summary(self, surah: int) -> Optional[Dict]:
        """
        Get accumulated summary for a surah

        Args:
            surah: Surah number

        Returns:
            Accumulated summary dict or None
        """
        return self.cache.get_accumulated_summary(surah)

    def save_accumulated_summary(self, surah: int, summary: Dict) -> bool:
        """
        Save accumulated summary for a surah

        Args:
            surah: Surah number
            summary: Summary dict

        Returns:
            True if saved successfully
        """
        return self.cache.save_accumulated_summary(surah, summary)

    def merge_extraction_into_summary(
        self,
        surah: int,
        section_index: int,
        extraction: Dict
    ) -> Dict:
        """
        Merge newly extracted info into accumulated summary

        Args:
            surah: Surah number
            section_index: Completed section index
            extraction: Extracted info from LLM

        Returns:
            Updated accumulated summary
        """
        # Load existing summary or create new
        existing = self.get_accumulated_summary(surah) or {
            "surah": surah,
            "last_section_completed": -1,
            "last_verse_completed": 0,
            "accumulated_summary": {
                "themes": [],
                "balaghah_correlations": [],
                "unresolved_patterns": [],
                "key_terms": []
            }
        }

        # Get ruku info for verse tracking
        section = self.get_section_by_index(surah, section_index)

        # Update progress
        existing["last_section_completed"] = section_index
        existing["last_verse_completed"] = section.get('verse_end', 0) if section else 0
        existing["updated_at"] = datetime.now().isoformat()

        # Merge themes (deduplicate)
        new_themes = extraction.get("themes_developed", [])
        existing_themes = existing["accumulated_summary"]["themes"]
        for theme in new_themes:
            if theme not in existing_themes:
                existing_themes.append(theme)

        # Merge balaghah correlations
        new_correlations = extraction.get("balaghah_correlations", [])
        existing["accumulated_summary"]["balaghah_correlations"].extend(new_correlations)

        # Merge unresolved patterns (may resolve some)
        new_unresolved = extraction.get("unresolved_patterns", [])
        existing["accumulated_summary"]["unresolved_patterns"].extend(new_unresolved)

        # Merge key terms
        new_terms = extraction.get("key_arabic_terms", [])
        existing["accumulated_summary"]["key_terms"].extend(new_terms)

        # Trim if too large (keep most recent/important)
        self._trim_summary_if_needed(existing)

        # Save
        self.save_accumulated_summary(surah, existing)

        return existing

    def _trim_summary_if_needed(self, summary: Dict):
        """Trim accumulated summary if it exceeds token limit"""
        # Rough estimate: 4 chars = 1 token
        json_str = json.dumps(summary, ensure_ascii=False)
        estimated_tokens = len(json_str) // 4

        if estimated_tokens > MAX_ACCUMULATED_SUMMARY_TOKENS:
            acc = summary["accumulated_summary"]

            # Keep only last N items for each category
            acc["themes"] = acc["themes"][-10:]  # Last 10 themes
            acc["balaghah_correlations"] = acc["balaghah_correlations"][-15:]
            acc["unresolved_patterns"] = acc["unresolved_patterns"][-10:]
            acc["key_terms"] = acc["key_terms"][-20:]

    def clear_accumulated_summary(self, surah: int) -> bool:
        """
        Clear accumulated summary for fresh start

        Args:
            surah: Surah number

        Returns:
            True if cleared
        """
        return self.cache.delete_accumulated_summary(surah)

    # ===== Session State =====

    def get_session_progress(self, surah: int) -> Dict:
        """
        Get progress info for a surah

        Args:
            surah: Surah number

        Returns:
            Progress dict with ruku info
        """
        total_sections = self.get_section_count_for_chapter(surah)
        accumulated = self.get_accumulated_summary(surah)

        last_completed = -1
        if accumulated:
            last_completed = accumulated.get("last_section_completed", -1)

        return {
            "surah": surah,
            "total_sections": total_sections,
            "completed_sections": last_completed + 1,
            "current_section": last_completed + 1,  # Next to analyze (0-based)
            "is_complete": last_completed >= total_sections - 1,
            "progress_percent": round((last_completed + 1) / total_sections * 100, 1) if total_sections > 0 else 0
        }

    # ===== Section Overview Generation =====

    def generate_section_overview_prompt(
        self,
        surah_num: int,
        section_index: int,
        accumulated_summary: Optional[Dict] = None
    ) -> tuple:
        """
        Generate comprehensive section overview prompt using tafsir methodology.
        Based on: Farahi-Islahi Nazm theory, Ilm al-Munasabat, al-Tafsir al-Mawdu'i

        Args:
            surah_num: Surah number
            section_index: 0-based section index
            accumulated_summary: Accumulated context from previous sections

        Returns:
            Tuple of (prompt_text, verses_data_for_json)
        """
        # Get full section data
        section_full = self.get_section_full_data(surah_num, section_index)
        if not section_full:
            return "", None

        section_info = section_full.get('section_info', {})
        verses = section_full.get('verses', [])

        # Get chapter metadata
        chapter_meta = self.loader.get_chapter_metadata(surah_num)
        surah_name = chapter_meta.get('name_arabic', '')
        surah_name_en = chapter_meta.get('name_english', '')

        # Get section heading (already in section_info)
        section_heading = section_info.get('heading', 'No heading')

        # Build verses data string (all verses, not truncated)
        verses_data_lines = []
        balaghah_preview = []
        for v in verses:
            verse_num = v.get('verse', 0)
            arabic = v.get('arabic', '')
            english = v.get('english', '')
            verses_data_lines.append(f"Ayat {verse_num}:")
            verses_data_lines.append(f"  Arab: {arabic}")
            verses_data_lines.append(f"  Terjemah: {english}")

            # Collect balaghah from verse data
            if v.get('balaghah'):
                for device_name, device_data in v['balaghah'].items():
                    if isinstance(device_data, list) and device_data:
                        for item in device_data:
                            balaghah_preview.append(f"{device_name}: ayat {verse_num}")
                    elif isinstance(device_data, dict) and device_data:
                        balaghah_preview.append(f"{device_name}: ayat {verse_num}")

        verses_data_str = "\n".join(verses_data_lines)

        # Build accumulated context string
        accumulated_context = "Ini adalah section pertama, belum ada konteks sebelumnya."
        if accumulated_summary and accumulated_summary.get('accumulated_summary'):
            acc = accumulated_summary['accumulated_summary']
            context_parts = []

            if acc.get('themes'):
                context_parts.append(f"Tema yang sudah berkembang: {', '.join(acc['themes'][-5:])}")

            if acc.get('amud_progression'):
                context_parts.append(f"Progresi 'amud: {' -> '.join(acc['amud_progression'][-5:])}")

            if acc.get('balaghah_correlations'):
                recent_correlations = acc['balaghah_correlations'][-3:]
                corr_str = "; ".join([f"{c.get('device')} (ayat {c.get('verses', [])})" for c in recent_correlations])
                context_parts.append(f"Balaghah berkorelasi: {corr_str}")

            if acc.get('unresolved_patterns'):
                patterns = acc['unresolved_patterns'][-3:]
                pattern_str = "; ".join([f"{p.get('type')} dari ayat {p.get('setup_verse')}" for p in patterns])
                context_parts.append(f"Pola belum selesai: {pattern_str}")

            if acc.get('key_terms'):
                terms = [t.get('term', '') for t in acc['key_terms'][-5:]]
                context_parts.append(f"Istilah kunci: {', '.join(terms)}")

            if context_parts:
                accumulated_context = "\n".join(context_parts)

        # Build balaghah preview string
        balaghah_preview_str = "Tidak ada data balaghah terdeteksi sebelumnya."
        if balaghah_preview:
            balaghah_preview_str = "Data balaghah terdeteksi:\n" + "\n".join(balaghah_preview[:10])

        # Build the prompt
        prompt = f"""Anda akan memberikan OVERVIEW NARATIF untuk Section {section_index + 1} (Ayat {section_info.get('verse_start')}-{section_info.get('verse_end')}) dari Surah {surah_name} ({surah_name_en}).

DATA AYAT DALAM SECTION INI:
{verses_data_str}

KONTEKS DARI SECTION SEBELUMNYA:
{accumulated_context}

SECTION HEADING (dari The Clear Quran):
{section_heading if section_heading else "Tidak tersedia"}

BALAGHAH TERDETEKSI (dari JSON):
{balaghah_preview_str}

---

<internal_reasoning>
Sebelum menulis, jawab pertanyaan-pertanyaan ini dalam pikiran Anda (JANGAN tampilkan ke user):
- Apa tema sentral ('amud) yang menyatukan semua ayat ini?
- Bagaimana section ini berhubungan dengan section sebelumnya? (tanasub/melanjutkan, tadadd/kontras, atau intiqal/transisi)
- Apa struktur internal (nazm): pembuka, isi, klimaks, penutup?
- Device balaghah apa yang paling menonjol dan akan muncul?
- Pertanyaan apa yang akan terjawab setelah analisis ayat per ayat nanti?

Gunakan jawaban ini untuk MEMANDU penulisan Anda, tapi JANGAN tampilkan sebagai numbered list.
</internal_reasoning>

## FORMAT OUTPUT - PROSA NARATIF MENGALIR:

Tulis overview dalam 3-4 paragraf NARATIF yang mengalir tanpa numbered points:

**Paragraf 1: Tema Sentral dan Posisi**
Jelaskan 'amud (tema sentral) section ini dan posisinya dalam alur surah. Apa pesan utama? Kenapa ayat-ayat ini dikelompokkan bersama? Hubungan dengan section sebelumnya (jika ada).

**Paragraf 2: Struktur dan Alur Internal**
Jelaskan bagaimana ayat-ayat tersusun secara internal (nazm). Di mana pembuka, isi, klimaks? Apakah ada titik balik atau transisi penting? Tulis mengalir, bukan bullet points.

**Paragraf 3: Preview Balaghah**
Sebutkan device balaghah yang akan ditemui dalam prosa mengalir. Integrasikan dengan konteks makna, bukan daftar terpisah.

**Paragraf 4 (opsional): Koneksi dan Antisipasi**
Jika relevan, sambungkan dengan pola dari section sebelumnya yang akan dilanjutkan, atau antisipasi ke section berikutnya.

---

ATURAN PENULISAN:
- JANGAN gunakan format numbered list (1., 2., 3.)
- JANGAN gunakan bullet points berlebihan
- Tulis paragraf mengalir seperti esai
- Gunakan **bold** untuk istilah penting saja
- Bahasa Indonesia yang mengalir
- Maksimal 400 kata
- Fokus pada INSIGHT, bukan ringkasan teks
- Format untuk Telegram (tanpa ### headers)"""

        # Return prompt and the verses data (for include_verse_data if needed)
        return prompt, section_full


# ===== Extraction Prompt =====

EXTRACTION_PROMPT = """
Section {section_index} (ayat {verse_start}-{verse_end}) telah selesai dianalisis.
Ekstrak informasi PENTING yang harus dibawa ke section berikutnya.

## FORMAT OUTPUT (JSON):
{{
  "themes_developed": ["tema 1 yang berkembang", "tema 2"],
  "balaghah_correlations": [
    {{"device": "nama device", "verses": [1, 5, 8], "note": "akan berlanjut karena..."}}
  ],
  "unresolved_patterns": [
    {{"type": "contrast/parallel/buildup", "setup_verse": 5, "expected": "kemungkinan resolution di ayat berikutnya"}}
  ],
  "key_arabic_terms": [
    {{"term": "istilah Arab", "meaning": "arti", "significance": "kenapa penting untuk section berikutnya"}}
  ],
  "connections_to_track": [
    {{"from_verse": 3, "note": "perlu diingat karena..."}}
  ]
}}

PENTING:
- Hanya ekstrak yang RELEVAN untuk section berikutnya
- Jangan ulang semua analisis
- Fokus pada pola yang belum selesai dan akan berlanjut
- Maksimal 1500 tokens
"""


if __name__ == "__main__":
    # Test
    from api.cache_manager import CacheManager
    from api.data_loader import QuranDataLoader

    cache = CacheManager()
    loader = QuranDataLoader()
    manager = SectionSessionManager(cache, loader)

    # Test chapter 68
    print("=== Surah 68 (Al-Qalam) ===")
    sections = manager.get_sections_for_chapter(68)
    print(f"Total sections: {len(sections)}")

    for i, section in enumerate(sections):
        print(f"  Section {i}: verses {ruku['verse_start']}-{ruku['verse_end']}")

    # Test ruku full data
    print("\n=== Section 0 Full Data ===")
    section_data = manager.get_section_full_data(68, 0)
    print(f"Section info: {section_data.get('section_info')}")
    print(f"Verses count: {len(section_data.get('verses', []))}")

    # Test next section preview
    print("\n=== Next Section Preview ===")
    preview = manager.get_next_section_preview(68, 0)
    print(f"Preview: {preview}")

    # Test progress
    print("\n=== Progress ===")
    progress = manager.get_session_progress(68)
    print(f"Progress: {progress}")
