# Data Sources and Attribution

This document provides comprehensive attribution for all data sources used in this Quranic analysis project.

## 1. Quranic Text

### Source: Tanzil Project
- **URL**: https://tanzil.net
- **File**: `jqurantree/src/src/main/resources/tanzil/quran-uthmani.xml`
- **Format**: XML
- **Text Type**: Uthmani script (with full diacritics)
- **License**: Creative Commons BY-ND 4.0
- **Coverage**: All 114 chapters, 6,236 verses
- **JSON Output**: `data/text/quran_text.json` (3.8 MB)

**Citation**:
```
Tanzil Quran Text
Copyright (C) 2008-2025 Tanzil Project
License: Creative Commons Attribution-NoDerivatives 4.0 International
```

---

## 2. Linguistic Annotations

### Source: Quranic Arabic Corpus
- **URL**: https://corpus.quran.com
- **Repository**: https://github.com/cpfair/quranic-corpus
- **Format**: Tab-delimited text files (converted to JSON)
- **License**: GNU GPL v3
- **Coverage**: All 6,236 verses

#### 2.1 Morphology (Segment-Level)
- **Original File**: `sources/quranic-corpus-full/quran-morphology-github.txt`
- **JSON Output**: `data/linguistic/morphology_segments.json` (39.4 MB)
- **Entries**: 130,030 morphological segments
- **Data**: POS tags, lemmas, roots, Arabic features (gender, number, case, etc.)
- **Documentation**: `docs/MORPHOLOGY_SEGMENTS_FORMAT.md`

#### 2.2 Dependencies (Syntactic Treebank)
- **Original File**: `sources/quranic-corpus-full/quranic-corpus-dependencies-full.txt`
- **JSON Output**: `data/linguistic/dependencies_full.json` (8.3 MB)
- **Entries**: 37,420 dependency relations
- **Data**: Parent/child locations, relation types, Arabic/English labels
- **Relation Types**: 47 types (subject, object, adjective, prepositional phrase, etc.)

#### 2.3 Named Entities
- **Original File**: `sources/quranic-corpus-full/quranic-corpus-named-entities-full.txt`
- **JSON Output**: `data/linguistic/named_entities_full.json` (0.8 MB)
- **Entries**: 5,494 semantic concept annotations
- **Top Concepts**: Allah (2,721), earth (409), Musa (136), heart (132)

#### 2.4 Lemmas Dictionary
- **Original File**: `sources/quranic-corpus-full/quranic-corpus-lemmas.txt`
- **JSON Output**: `data/linguistic/lemmas_dictionary.json` (0.2 MB)
- **Entries**: 1,593 unique lemmas
- **Data**: Buckwalter transliteration, Unicode Arabic, English translations

#### 2.5 Pause Marks (Tajweed)
- **Original File**: `sources/quranic-corpus-full/quranic-corpus-pause-marks.txt`
- **JSON Output**: `data/linguistic/pause_marks.json` (0.5 MB)
- **Entries**: 4,359 pause mark annotations

**Citation**:
```
Quranic Arabic Corpus
Copyright (C) 2009-2025 Kais Dukes
License: GNU General Public License v3
```

---

## 3. Chapter Metadata and Context

### 3.1 Basic Chapter Metadata
- **Source**: AlQuran Cloud API (https://alquran.cloud/api)
- **JSON Output**: `data/metadata/chapter_metadata.json` (24 KB)
- **Entries**: 114 chapters
- **Data**: Arabic name, Meccan/Medinan classification, revelation order, verse count

**Citation**:
```
AlQuran Cloud API
https://alquran.cloud
```

### 3.2 Chapter Introductions (Ibn Kathir Tafsir)
- **Source**: spa5k/tafsir_api (GitHub)
- **URL**: https://github.com/spa5k/tafsir_api
- **API Endpoint**: https://api.spa5k.com/v1/tafsir/
- **JSON Output**: `data/metadata/surah_info.json` (90.9 KB)
- **Entries**: 114 surah introductions
- **Content**: Classical scholarly commentary on each chapter's themes, names, revelation context
- **Language**: English translation of Ibn Kathir's classical tafsir

**Citation**:
```
Tafsir Ibn Kathir (English Translation)
API provided by: spa5k/tafsir_api
Source: Classical tafsir by Imam Ibn Kathir (1301-1373 CE)
```

### 3.3 Ruku Divisions (Traditional Sections)
- **Source**: AlQuran Cloud API
- **Endpoint**: `https://api.alquran.cloud/v1/meta`
- **JSON Output**: `data/metadata/ruku_divisions.json` (89.2 KB)
- **Entries**: 556 ruku divisions
- **Coverage**: All 6,236 verses
- **Purpose**: Traditional thematic sections used in Quranic study

**Citation**:
```
Ruku Divisions
Source: AlQuran Cloud API
Based on: Traditional Islamic scholarly divisions
```

### 3.4 Section Headings (The Clear Quran)
- **Source**: The Clear Quran by Dr. Mustafa Khattab
- **URL**: https://theclearquran.org
- **Original File**: `sources/clear_quran_full_text.txt`
- **Parser Script**: `scripts/converters/parse_clear_quran_sections.py`
- **JSON Output**: `data/metadata/clear_quran_sections.json`
- **Entries**: 1,966 section headings across 113 chapters
- **Coverage**: 6,184 verses (99.2% of the Quran)
- **Missing**: Chapter 14 (Ibrahim) - 52 verses
- **Granularity**: Average 3.1 verses per section (much more detailed than rukus)

**Section Structure**:
- Descriptive thematic headings (e.g., "Qualities of the Believers")
- Verse start and end positions
- Section IDs for reference

**Citation**:
```
The Clear Quran - Section Headings
Author: Dr. Mustafa Khattab
Publisher: Furqaan Institute of Quranic Education
Copyright: © 2016-2025 Dr. Mustafa Khattab
URL: https://theclearquran.org
```

**Usage**: Section headings extracted with permission from the published text. These provide modern, English-language thematic structure that complements traditional ruku divisions.

---

## 4. Occasions of Revelation

### Source: Asbab al-Nuzul Collection
- **Original File**: `sources/asbabun_nuzul/asbabun_nuzul.md`
- **JSON Output**: `data/metadata/asbab_nuzul_index.json` (1.7 MB)
- **Entries**: 1,335 occasion narratives for 678 verses
- **Content**: Historical context and circumstances of revelation
- **Note**: Some verses have multiple narrations

---

## 5. Tafsir Commentary

### Source: Al-Qushairi Sufi Tafsir
- **Original File**: `sources/tafseer/Al_Qushairi_Tafsir_tafseer.csv`
- **JSON Output**: `data/metadata/tafsir_index.json` (64 KB)
- **Entries**: 45 verses with detailed commentary
- **Coverage**: Limited (representative selections)
- **Content**: English translation and Sufi spiritual commentary

---

## Coverage Summary

| Data Type | Source | Coverage | Entries/Size |
|-----------|--------|----------|-------------|
| **Quranic Text** | Tanzil | 100% (6,236 verses) | 3.8 MB |
| **Morphology** | Quranic Corpus | 100% | 130,030 segments (39.4 MB) |
| **Dependencies** | Quranic Corpus | 100% | 37,420 relations (8.3 MB) |
| **Named Entities** | Quranic Corpus | Selective | 5,494 entities (0.8 MB) |
| **Chapter Metadata** | AlQuran Cloud | 100% (114 chapters) | 24 KB |
| **Chapter Introductions** | Ibn Kathir | 100% (114 chapters) | 90.9 KB |
| **Ruku Divisions** | AlQuran Cloud | 100% (556 rukus) | 89.2 KB |
| **Section Headings** | The Clear Quran | 99.2% (113 chapters) | 1,966 sections |
| **Asbab al-Nuzul** | Multiple sources | 678 verses | 1.7 MB |
| **Tafsir** | Al-Qushairi | 45 verses | 64 KB |

---

## License Compliance

### Open Source Licenses
All data sources use open licenses compatible with research and educational use:

1. **Quranic Text**: CC BY-ND 4.0 (Tanzil)
2. **Linguistic Data**: GNU GPL v3 (Quranic Corpus)
3. **API Data**: Free for non-commercial use (AlQuran Cloud)
4. **Section Headings**: Used with attribution (The Clear Quran)

### Attribution Requirements
When using this dataset, please cite:
- Tanzil Project for Quranic text
- Quranic Arabic Corpus for linguistic annotations
- AlQuran Cloud for metadata and ruku divisions
- Dr. Mustafa Khattab and The Clear Quran for section headings
- Ibn Kathir for classical tafsir content
- Individual sources for asbab al-nuzul and tafsir

---

## Data Integrity

All data conversions preserve original content:
- No modifications to source text
- Lossless format conversion (text → JSON)
- Structural relationships maintained
- Original location references preserved
- Unicode encoding for Arabic text

For detailed format specifications, see `JSON_CONVERSION_SUMMARY.md`.
