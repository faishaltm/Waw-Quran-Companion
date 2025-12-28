"""
Ruku Session Manager
Manages session boundaries based on traditional ruku divisions (556 total)
Each ruku = 1 session with full context + accumulated summary from previous sessions
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


class RukuSessionManager:
    """
    Manages session boundaries based on ruku divisions.

    Key responsibilities:
    - Track which ruku user is on
    - Load full data for current ruku
    - Provide preview of next ruku
    - Manage accumulated summaries across sessions
    """

    def __init__(self, cache_manager: CacheManager, data_loader: QuranDataLoader):
        """
        Initialize RukuSessionManager

        Args:
            cache_manager: CacheManager instance
            data_loader: QuranDataLoader instance
        """
        self.cache = cache_manager
        self.loader = data_loader

        # Load ruku divisions
        self.ruku_divisions = self.loader.ruku_divisions

        # Build chapter -> ruku mapping for fast lookup
        self._build_chapter_ruku_map()

    def _build_chapter_ruku_map(self):
        """Build mapping from chapter number to list of rukus in that chapter"""
        self.chapter_rukus: Dict[int, List[Dict]] = {}

        for ruku_num, ruku_data in self.ruku_divisions.items():
            chapter = ruku_data.get('chapter')
            if chapter not in self.chapter_rukus:
                self.chapter_rukus[chapter] = []
            self.chapter_rukus[chapter].append(ruku_data)

        # Sort by verse_start
        for chapter in self.chapter_rukus:
            self.chapter_rukus[chapter].sort(key=lambda x: x.get('verse_start', 0))

    def get_rukus_for_chapter(self, surah: int) -> List[Dict]:
        """
        Get all rukus for a chapter

        Args:
            surah: Surah number (1-114)

        Returns:
            List of ruku dicts sorted by verse_start
        """
        return self.chapter_rukus.get(surah, [])

    def get_ruku_count_for_chapter(self, surah: int) -> int:
        """Get total number of rukus in a chapter"""
        return len(self.chapter_rukus.get(surah, []))

    def get_ruku_by_index(self, surah: int, ruku_index: int) -> Optional[Dict]:
        """
        Get ruku by chapter-relative index (0-based)

        Args:
            surah: Surah number
            ruku_index: 0-based index within chapter

        Returns:
            Ruku dict or None
        """
        rukus = self.chapter_rukus.get(surah, [])
        if 0 <= ruku_index < len(rukus):
            return rukus[ruku_index]
        return None

    def get_current_ruku_index(self, surah: int, verse: int) -> int:
        """
        Get chapter-relative ruku index for a verse

        Args:
            surah: Surah number
            verse: Verse number

        Returns:
            0-based ruku index within chapter
        """
        rukus = self.chapter_rukus.get(surah, [])
        for i, ruku in enumerate(rukus):
            if ruku['verse_start'] <= verse <= ruku['verse_end']:
                return i
        return 0

    def get_ruku_full_data(self, surah: int, ruku_index: int) -> Dict[str, Any]:
        """
        Get full verse data for all verses in a ruku

        Args:
            surah: Surah number
            ruku_index: 0-based ruku index within chapter

        Returns:
            Dict with ruku info and full verse data
        """
        ruku = self.get_ruku_by_index(surah, ruku_index)
        if not ruku:
            return {}

        verse_start = ruku['verse_start']
        verse_end = ruku['verse_end']

        # Collect full data for all verses in ruku
        verses_data = []
        for verse_num in range(verse_start, verse_end + 1):
            verse_data = self.loader.get_verse_full_data(surah, verse_num)
            if verse_data:
                verses_data.append(verse_data)

        return {
            "ruku_info": {
                "chapter": surah,
                "ruku_index": ruku_index,
                "ruku_number": ruku.get('ruku_number'),
                "verse_start": verse_start,
                "verse_end": verse_end,
                "verse_count": ruku.get('verse_count', verse_end - verse_start + 1)
            },
            "verses": verses_data
        }

    def get_next_ruku_preview(self, surah: int, current_ruku_index: int) -> Optional[Dict]:
        """
        Get preview of next ruku (for lookahead)

        Args:
            surah: Surah number
            current_ruku_index: Current ruku index (0-based)

        Returns:
            Dict with next ruku info (verse range, section heading if available)
        """
        next_index = current_ruku_index + 1
        rukus = self.chapter_rukus.get(surah, [])

        if next_index >= len(rukus):
            # End of chapter
            return {
                "is_last": True,
                "message": "Ini adalah ruku terakhir dalam surah ini"
            }

        next_ruku = rukus[next_index]

        # Try to get section heading from Clear Quran sections
        section_heading = None
        try:
            section = self.loader.metadata.get_section_for_verse(
                surah, next_ruku['verse_start']
            )
            if section:
                section_heading = section.get('heading')
        except Exception:
            pass

        return {
            "is_last": False,
            "ruku_index": next_index,
            "verse_start": next_ruku['verse_start'],
            "verse_end": next_ruku['verse_end'],
            "verse_count": next_ruku.get('verse_count'),
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
        ruku_index: int,
        extraction: Dict
    ) -> Dict:
        """
        Merge newly extracted info into accumulated summary

        Args:
            surah: Surah number
            ruku_index: Completed ruku index
            extraction: Extracted info from LLM

        Returns:
            Updated accumulated summary
        """
        # Load existing summary or create new
        existing = self.get_accumulated_summary(surah) or {
            "surah": surah,
            "last_ruku_completed": -1,
            "last_verse_completed": 0,
            "accumulated_summary": {
                "themes": [],
                "balaghah_correlations": [],
                "unresolved_patterns": [],
                "key_terms": []
            }
        }

        # Get ruku info for verse tracking
        ruku = self.get_ruku_by_index(surah, ruku_index)

        # Update progress
        existing["last_ruku_completed"] = ruku_index
        existing["last_verse_completed"] = ruku.get('verse_end', 0) if ruku else 0
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
        total_rukus = self.get_ruku_count_for_chapter(surah)
        accumulated = self.get_accumulated_summary(surah)

        last_completed = -1
        if accumulated:
            last_completed = accumulated.get("last_ruku_completed", -1)

        return {
            "surah": surah,
            "total_rukus": total_rukus,
            "completed_rukus": last_completed + 1,
            "current_ruku": last_completed + 1,  # Next to analyze (0-based)
            "is_complete": last_completed >= total_rukus - 1,
            "progress_percent": round((last_completed + 1) / total_rukus * 100, 1) if total_rukus > 0 else 0
        }

    # ===== Ruku Overview Generation =====

    def generate_ruku_overview_prompt(
        self,
        surah_num: int,
        ruku_index: int,
        accumulated_summary: Optional[Dict] = None
    ) -> tuple:
        """
        Generate comprehensive ruku overview prompt using tafsir methodology.
        Based on: Farahi-Islahi Nazm theory, Ilm al-Munasabat, al-Tafsir al-Mawdu'i

        Args:
            surah_num: Surah number
            ruku_index: 0-based ruku index
            accumulated_summary: Accumulated context from previous rukus

        Returns:
            Tuple of (prompt_text, verses_data_for_json)
        """
        # Get full ruku data
        ruku_full = self.get_ruku_full_data(surah_num, ruku_index)
        if not ruku_full:
            return "", None

        ruku_info = ruku_full.get('ruku_info', {})
        verses = ruku_full.get('verses', [])

        # Get chapter metadata
        chapter_meta = self.loader.get_chapter_metadata(surah_num)
        surah_name = chapter_meta.get('name_arabic', '')
        surah_name_en = chapter_meta.get('name_english', '')

        # Try to get section heading from Clear Quran
        section_heading = ""
        try:
            section = self.loader.metadata.get_section_for_verse(
                surah_num, ruku_info.get('verse_start', 1)
            )
            if section:
                section_heading = section.get('heading', '')
        except Exception:
            pass

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
        accumulated_context = "Ini adalah ruku pertama, belum ada konteks sebelumnya."
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
        prompt = f"""Anda akan memberikan OVERVIEW NARATIF untuk Ruku {ruku_index + 1} (Ayat {ruku_info.get('verse_start')}-{ruku_info.get('verse_end')}) dari Surah {surah_name} ({surah_name_en}).

DATA AYAT DALAM RUKU INI:
{verses_data_str}

KONTEKS DARI RUKU SEBELUMNYA:
{accumulated_context}

SECTION HEADING (dari The Clear Quran):
{section_heading if section_heading else "Tidak tersedia"}

BALAGHAH TERDETEKSI (dari JSON):
{balaghah_preview_str}

---

<internal_reasoning>
Sebelum menulis, jawab pertanyaan-pertanyaan ini dalam pikiran Anda (JANGAN tampilkan ke user):
- Apa tema sentral ('amud) yang menyatukan semua ayat ini?
- Bagaimana ruku ini berhubungan dengan ruku sebelumnya? (tanasub/melanjutkan, tadadd/kontras, atau intiqal/transisi)
- Apa struktur internal (nazm): pembuka, isi, klimaks, penutup?
- Device balaghah apa yang paling menonjol dan akan muncul?
- Pertanyaan apa yang akan terjawab setelah analisis ayat per ayat nanti?

Gunakan jawaban ini untuk MEMANDU penulisan Anda, tapi JANGAN tampilkan sebagai numbered list.
</internal_reasoning>

## FORMAT OUTPUT - PROSA NARATIF MENGALIR:

Tulis overview dalam 3-4 paragraf NARATIF yang mengalir tanpa numbered points:

**Paragraf 1: Tema Sentral dan Posisi**
Jelaskan 'amud (tema sentral) ruku ini dan posisinya dalam alur surah. Apa pesan utama? Kenapa ayat-ayat ini dikelompokkan bersama? Hubungan dengan ruku sebelumnya (jika ada).

**Paragraf 2: Struktur dan Alur Internal**
Jelaskan bagaimana ayat-ayat tersusun secara internal (nazm). Di mana pembuka, isi, klimaks? Apakah ada titik balik atau transisi penting? Tulis mengalir, bukan bullet points.

**Paragraf 3: Preview Balaghah**
Sebutkan device balaghah yang akan ditemui dalam prosa mengalir. Integrasikan dengan konteks makna, bukan daftar terpisah.

**Paragraf 4 (opsional): Koneksi dan Antisipasi**
Jika relevan, sambungkan dengan pola dari ruku sebelumnya yang akan dilanjutkan, atau antisipasi ke ruku berikutnya.

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
        return prompt, ruku_full


# ===== Extraction Prompt =====

EXTRACTION_PROMPT = """
Ruku {ruku_index} (ayat {verse_start}-{verse_end}) telah selesai dianalisis.
Ekstrak informasi PENTING yang harus dibawa ke ruku berikutnya.

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
    {{"term": "istilah Arab", "meaning": "arti", "significance": "kenapa penting untuk ruku berikutnya"}}
  ],
  "connections_to_track": [
    {{"from_verse": 3, "note": "perlu diingat karena..."}}
  ]
}}

PENTING:
- Hanya ekstrak yang RELEVAN untuk ruku berikutnya
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
    manager = RukuSessionManager(cache, loader)

    # Test chapter 68
    print("=== Surah 68 (Al-Qalam) ===")
    rukus = manager.get_rukus_for_chapter(68)
    print(f"Total rukus: {len(rukus)}")

    for i, ruku in enumerate(rukus):
        print(f"  Ruku {i}: verses {ruku['verse_start']}-{ruku['verse_end']}")

    # Test ruku full data
    print("\n=== Ruku 0 Full Data ===")
    ruku_data = manager.get_ruku_full_data(68, 0)
    print(f"Ruku info: {ruku_data.get('ruku_info')}")
    print(f"Verses count: {len(ruku_data.get('verses', []))}")

    # Test next ruku preview
    print("\n=== Next Ruku Preview ===")
    preview = manager.get_next_ruku_preview(68, 0)
    print(f"Preview: {preview}")

    # Test progress
    print("\n=== Progress ===")
    progress = manager.get_session_progress(68)
    print(f"Progress: {progress}")
