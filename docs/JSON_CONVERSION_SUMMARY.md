# JSON Data Format Summary

This document describes the JSON data formats used in this project after conversion from original source files.

## 1. Quranic Text

**File**: `data/text/quran_text.json`
**Size**: 3.8 MB
**Source**: `jqurantree/src/src/main/resources/tanzil/quran-uthmani.xml`

### Structure
```json
{
  "1": {
    "chapter_number": 1,
    "verses": {
      "1": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
      "2": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ",
      "3": "ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    }
  }
}
```

### Fields
- **Keys**: Chapter numbers (1-114)
- **chapter_number**: Integer
- **verses**: Object with verse number keys (1-n) and Arabic text values

---

## 2. Morphology (Segment-Level)

**File**: `data/linguistic/morphology_segments.json`
**Size**: 39.4 MB
**Entries**: 130,030 morphological segments
**Documentation**: See `docs/MORPHOLOGY_SEGMENTS_FORMAT.md` for complete details

### Structure
```json
{
  "1": {
    "1": {
      "1": [
        {
          "segment_id": 1,
          "form": "بِ",
          "tag": "P",
          "features": "PREFIX|bi+",
          "arabic": "بِ",
          "location": "(1:1:1:1)"
        },
        {
          "segment_id": 2,
          "form": "سْمِ",
          "tag": "N",
          "features": "STEM|POS:N|LEM:{som|ROOT:smw|M|GEN",
          "arabic": "سْمِ",
          "location": "(1:1:1:2)"
        }
      ]
    }
  }
}
```

### Fields
- **form**: Arabic text in Buckwalter transliteration
- **tag**: Part-of-speech tag (N, V, P, PRON, ADJ, etc.)
- **features**: Pipe-delimited morphological features
  - PREFIX/STEM/SUFFIX: Morpheme type
  - POS: Part of speech
  - LEM: Lemma (dictionary form)
  - ROOT: Arabic root
  - Gender: M/F
  - Number: S/D/P (singular/dual/plural)
  - Case: NOM/GEN/ACC
- **arabic**: Native Unicode Arabic text
- **location**: Hierarchical reference (chapter:verse:word:segment)

---

## 3. Dependencies (Syntactic Treebank)

**File**: `data/linguistic/dependencies_full.json`
**Size**: 8.3 MB
**Entries**: 37,420 dependency relations

### Structure
```json
{
  "1:1:1": [
    {
      "id": 1,
      "child_location": "(1:1:1)",
      "child_part": 2,
      "parent_location": "(1:1:2)",
      "parent_part": 2,
      "relation": "genetive",
      "arabic_relation": "مضاف إليه",
      "english_relation": "Genetive"
    }
  ]
}
```

### Fields
- **Keys**: "chapter:verse:word" format
- **child_location**: Location of dependent word
- **parent_location**: Location of head word
- **child_part/parent_part**: Segment ID within word
- **relation**: Dependency relation type (47 types total)
- **arabic_relation**: Arabic grammatical term
- **english_relation**: English translation

### Common Relation Types
- subject (فاعل)
- object (مفعول به)
- adjective (نعت)
- genetive (مضاف إليه)
- prepositional phrase (جار ومجرور)
- conjunction (حرف عطف)

---

## 4. Named Entities

**File**: `data/linguistic/named_entities_full.json`
**Size**: 0.8 MB
**Entries**: 5,494 concept annotations

### Structure
```json
{
  "1:1:2": [
    {
      "id": 1,
      "location": "(1:1:2)",
      "concept_id": "allah",
      "concept_name": "Allah",
      "type": "concept",
      "category": null
    }
  ]
}
```

### Fields
- **Keys**: "chapter:verse:word" format
- **location**: Word location in corpus
- **concept_id**: Unique identifier (e.g., "allah", "earth", "musa")
- **concept_name**: Human-readable name
- **type**: instance/subclass/concept
- **category**: Parent category from ontology (if applicable)

---

## 5. Chapter Metadata

**File**: `data/metadata/chapter_metadata.json`
**Size**: 24 KB

### Structure
```json
{
  "1": {
    "chapter_number": 1,
    "name_arabic": "ٱلْفَاتِحَةِ",
    "revelation_place": "makkah",
    "revelation_order": 5,
    "verses_count": 7
  }
}
```

### Fields
- **chapter_number**: Integer (1-114)
- **name_arabic**: Arabic chapter name
- **revelation_place**: "makkah" or "madinah"
- **revelation_order**: Chronological order of revelation (1-114)
- **verses_count**: Total verses in chapter

---

## 6. Surah Information (with Ibn Kathir Introductions)

**File**: `data/metadata/surah_info.json`
**Size**: 90.9 KB

### Structure
```json
{
  "1": {
    "number": 1,
    "name_arabic": "سُورَةُ ٱلْفَاتِحَةِ",
    "name_simple": "Al-Faatiha",
    "name_translation": "The Opening",
    "revelation_place": "meccan",
    "verses_count": 7,
    "introduction": "Introduction to Fatihah\nWhich was revealed in Makkah..."
  }
}
```

### Fields
- **number**: Chapter number
- **name_arabic**: Full Arabic name
- **name_simple**: Simplified transliteration
- **name_translation**: English translation
- **revelation_place**: "meccan" or "medinan"
- **verses_count**: Total verses
- **introduction**: Full Ibn Kathir tafsir introduction (can be several KB)

---

## 7. Ruku Divisions

**File**: `data/metadata/ruku_divisions.json`
**Size**: 89.2 KB
**Entries**: 556 rukus

### Structure
```json
{
  "1": {
    "ruku_number": 1,
    "chapter": 1,
    "chapter_name": "Al-Faatiha",
    "verse_start": 1,
    "verse_end": 7,
    "verse_count": 7
  }
}
```

### Fields
- **ruku_number**: Sequential ruku ID (1-556)
- **chapter**: Chapter number
- **chapter_name**: Chapter name (transliteration)
- **verse_start**: First verse in this ruku
- **verse_end**: Last verse in this ruku
- **verse_count**: Total verses in ruku

### Coverage
- Total rukus: 556
- All 6,236 verses covered
- Average: 11.2 verses per ruku

---

## 8. Clear Quran Section Headings

**File**: `data/metadata/clear_quran_sections.json`
**Size**: ~500 KB (estimate)
**Entries**: 1,966 section headings

### Structure
```json
{
  "2": {
    "chapter_number": 2,
    "chapter_name": "The Cow",
    "sections": [
      {
        "section_id": 2,
        "chapter": 2,
        "heading": "Qualities of the Believers",
        "verse_start": 1,
        "verse_end": 5,
        "line_number": 1441
      },
      {
        "section_id": 3,
        "chapter": 2,
        "heading": "Qualities of the Disbelievers",
        "verse_start": 6,
        "verse_end": 7,
        "line_number": 1450
      }
    ]
  }
}
```

### Fields
- **Keys**: Chapter numbers (1-114, excluding Chapter 14)
- **chapter_number**: Integer
- **chapter_name**: English chapter name
- **sections**: Array of section objects
  - **section_id**: Sequential section ID (1-1966)
  - **chapter**: Chapter number (redundant for validation)
  - **heading**: Descriptive thematic heading (English)
  - **verse_start**: First verse in this section
  - **verse_end**: Last verse in this section
  - **line_number**: Line number in original text file (for reference)

### Coverage Statistics
- **Chapters with sections**: 113 (99.1%)
- **Chapters without sections**: 1 (Chapter 14: Ibrahim)
- **Total sections**: 1,966
- **Verses covered**: 6,184 (99.2%)
- **Verses without sections**: 52 (0.8%)
- **Average verses per section**: 3.1
- **Average sections per chapter**: 17.4

### Examples by Chapter Size

**Large Chapter (Ch 2 - Al-Baqarah)**:
- Verses: 286
- Sections: 148
- Average: 1.9 verses/section

**Medium Chapter (Ch 18 - Al-Kahf)**:
- Verses: 110
- Sections: 38
- Average: 2.9 verses/section

**Small Chapter (Ch 93 - Ad-Dhuhaa)**:
- Verses: 11
- Sections: 1
- Average: 11 verses/section

---

## 9. Asbab al-Nuzul (Occasions of Revelation)

**File**: `data/metadata/asbab_nuzul_index.json`
**Size**: 1.7 MB

### Structure
```json
{
  "2:6": [
    {
      "chapter": 2,
      "verse": 6,
      "surah_name": "Al-Baqarah",
      "occasion": "Brief description...",
      "full_narrative": "Complete narration text...",
      "verse_range": "6-7"
    }
  ]
}
```

### Fields
- **Keys**: "chapter:verse" format
- **chapter**: Chapter number
- **verse**: Verse number
- **surah_name**: Chapter name
- **occasion**: Brief description
- **full_narrative**: Complete historical narration
- **verse_range**: Applicable verse range (some occasions cover multiple verses)

---

## 10. Integrated Verse Output

**Generated by**: `scripts/tools/get_verse_info_v2.py`
**Format**: JSON per request

### Structure
```json
{
  "chapter": 2,
  "verse_start": 1,
  "verse_end": 5,
  "metadata": {
    "chapter_number": 2,
    "name_arabic": "ٱلْبَقَرَةِ",
    "revelation_place": "madinah",
    "revelation_order": 87,
    "verses_count": 286,
    "introduction": "Full Ibn Kathir introduction...",
    "name_translation": "The Cow"
  },
  "verses": [
    {
      "verse_number": 1,
      "text": "الٓمٓ",
      "translation": "Alif, Lam, Meem.",
      "ruku_context": {
        "ruku_number": 2,
        "verse_start": 1,
        "verse_end": 7,
        "position_in_ruku": "verse 1 of 7"
      },
      "section_heading": {
        "heading": "Qualities of the Believers",
        "verse_start": 1,
        "verse_end": 5,
        "position": "verse 1 of 5"
      },
      "asbab_nuzul": [...],
      "analysis": "Balaghah analysis...",
      "key_words": "Root meanings..."
    }
  ],
  "chapter_balaghah": {
    "root_repetitions": {...}
  }
}
```

### Integrated Fields
- **metadata**: From surah_info.json
- **ruku_context**: From ruku_divisions.json with position calculation
- **section_heading**: From clear_quran_sections.json with position calculation
- **asbab_nuzul**: From asbab_nuzul_index.json (if available)
- **analysis**: From balaghah analysis tools
- **chapter_balaghah**: Chapter-level rhetorical patterns

---

## Location Format Standard

All linguistic data uses consistent location referencing:

### Format
```
(chapter:verse:word:segment)
```

### Examples
- `(1:1:1:1)` = Chapter 1, Verse 1, Word 1, Segment 1
- `(2:255:10:2)` = Chapter 2, Verse 255, Word 10, Segment 2

### Abbreviated Forms
- Word-level: `(1:1:2)` or `1:1:2`
- Verse-level: `2:6`

### Usage in Different Files
- **Morphology**: Full format with segments
- **Dependencies**: Full format for parent/child locations
- **Named Entities**: Word-level (3-part)
- **Asbab al-Nuzul**: Verse-level (2-part)

---

## Data Loading

### Python Loader
**Module**: `scripts/loaders/metadata_loader.py`

Provides unified interface:
```python
from metadata_loader import MetadataLoader

loader = MetadataLoader()

# Get chapter metadata
chapter = loader.get_chapter_metadata(1)

# Get ruku for a verse
ruku = loader.get_ruku_for_verse(2, 10)

# Get section heading for a verse
section = loader.get_section_for_verse(2, 1)

# Get asbab nuzul
occasions = loader.get_asbab_nuzul(2, 6)
```

### Performance
- All data loaded once at initialization
- Fast lookups via pre-built hash maps
- Verse-to-ruku map: O(1) lookup
- Verse-to-section map: O(1) lookup

---

## Conversion Scripts

All conversions from original sources were one-time operations:

1. **Quranic Text**: Extracted from XML using JQuranTree Java library
2. **Morphology**: `scripts/converters/convert_morphology_to_json.py`
3. **Dependencies**: `scripts/converters/convert_dependencies_to_json.py`
4. **Named Entities**: `scripts/converters/convert_named_entities_to_json.py`
5. **Section Headings**: `scripts/converters/parse_clear_quran_sections.py`

Scripts preserved in `scripts/converters/` for reference only. All data now maintained as JSON.

---

## Data Integrity Verification

### Validation Checks
1. All verses (1-6236) have text
2. All morphology entries have valid locations
3. All dependencies reference existing words
4. Chapter metadata matches text structure
5. Ruku divisions cover all verses without gaps
6. Section headings have valid verse ranges

### Testing
Run verification:
```bash
cd scripts/tools
python verify_data_integrity.py
```

---

## Future Additions

Potential data sources to integrate:
- Complete tafsir (e.g., Jalalayn, Maariful Quran)
- Qira'at (variant readings)
- Hadith cross-references
- Thematic index
- Word frequency analysis

See project issues for data enhancement requests.
