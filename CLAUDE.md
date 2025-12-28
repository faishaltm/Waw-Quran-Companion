# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Purpose

This repository provides comprehensive Quranic text analysis capabilities with:
- **Linguistic data**: Morphology, syntax, lemmas from Quranic Arabic Corpus
- **Textual data**: Uthmani Arabic text, English translations, chapter metadata
- **Commentary data**: Three major tafsir sources (Al-Kashshaf, Ma'arif, Ibn Kathir)
- **Contextual data**: Revelation occasions (asbab al-nuzul), thematic sections, revelation order
- **Balaghah analysis**: Rhetorical device detection and LLM-guided analysis system
- **Processing tools**: Python scripts for data extraction, conversion, and analysis

**Primary Use Case**: Generating comprehensive verse information for LLM-based balaghah (rhetorical) analysis.

---

## Architecture Overview

```
Input Data Sources -> Comprehensive JSON -> Extraction Script -> LLM Analysis
     |                      |                    |                |
- Corpus data        quran_comprehensive    get_verse_info_v3   Balaghah
- Tafsir sources          (225 MB)         (verse extractor)    analysis
- Metadata files                                                 guide v4
```

---

## Core Data Files

### Comprehensive Data (Primary)

**File**: `data/quran_comprehensive.json` (225.99 MB)
- Single source containing all integrated data
- Structure: 114 chapters -> verses -> full linguistic/contextual data
- Contents: Arabic text, English translation, morphology, balaghah features, tafsir (3 sources), asbab al-nuzul, root repetitions, chapter metadata

### Linguistic Data

| File | Size | Description |
|------|------|-------------|
| `data/linguistic/morphology_segments.json` | 39.4 MB | 130,030 segments with verb forms, POS, roots, lemmas |
| `data/linguistic/dependencies_full.json` | 8.3 MB | 37,420 syntactic relations |
| `data/linguistic/named_entities_full.json` | 0.8 MB | 5,494 concept annotations |
| `data/linguistic/lemmas_dictionary.json` | 0.2 MB | 1,593 unique lemmas |
| `data/linguistic/pause_marks.json` | 0.5 MB | 4,359 tajweed markers |

### Tafsir Data

| File | Coverage | Description |
|------|----------|-------------|
| `data/metadata/tafsir_kashshaf_arabic.json` | 51.3% | Al-Kashshaf (Arabic, rhetorical focus) |
| `data/metadata/tafsir_maarif_en.json` | 100% | Ma'arif al-Qur'an (English, comprehensive) |
| `data/metadata/tafsir_ibn_kathir_en.json` | 100% | Ibn Kathir (English, classical hadith-based) |

### Metadata Files

| File | Description |
|------|-------------|
| `data/metadata/chapter_metadata.json` | 114 chapters: names, Meccan/Medinan, revelation order |
| `data/metadata/surah_context_qurancom.json` | Maududi's Tafhim introductions (~8000 chars each) |
| `data/metadata/clear_quran_sections.json` | 1,966 thematic section headings |
| `data/metadata/ruku_divisions.json` | 556 traditional sections |
| `data/metadata/asbab_nuzul_index.json` | 678 verses with revelation occasions |
| `data/metadata/revelation_order.json` | Chronological sequence 1-114 |
| `data/text/quran_text.json` | Uthmani script, 6,236 verses |

---

## Key Scripts

### Extraction Tools

**get_verse_info_v3.py** - PRIMARY EXTRACTION TOOL
- Location: `scripts/tools/get_verse_info_v3.py`
- Input: Chapter:verse or range (e.g., "1:1" or "1:1-7")
- Output: JSON with all verse data (text, morphology, tafsir, balaghah, context)

**Usage**:
```bash
cd scripts/tools
python get_verse_info_v3.py
# Enter: 68:1-5
```

**get_verse_info_v2.py** - Previous version (still functional)

### Metadata Loader

**Location**: `scripts/loaders/metadata_loader.py`

```python
from metadata_loader import MetadataLoader
loader = MetadataLoader()

# Key methods
chapter_meta = loader.get_chapter_metadata(1)
qurancom_context = loader.get_qurancom_context(1)
tafsir = loader.get_all_tafsirs(1, 1)
occasions = loader.get_asbab_nuzul(2, 6)
section = loader.get_section_for_verse(2, 1)
ruku = loader.get_ruku_for_verse(2, 10)
```

### Balaghah Analysis Tools

Located in `scripts/tools/`:
- `analyze_balaghah_tier1.py` - Basic rhetorical analysis
- `analyze_balaghah_tier2.py` - Intermediate analysis
- `analyze_balaghah_advanced.py` - Advanced comprehensive analysis
- `narrative_balaghah_analyzer.py` - Narrative-focused analysis
- `extract_balaghah_patterns.py` - Pattern extraction

### Data Converters

Located in `scripts/converters/`:
- `parse_kashshaf_openiti.py` - Extract Al-Kashshaf from OpenITI
- `fetch_qurancom_tafsirs.py` - Fetch Ma'arif + Ibn Kathir
- `update_comprehensive_with_tafsirs.py` - Integrate tafsirs
- `parse_clear_quran_sections.py` - Extract section headings

---

## Deployment API (FastAPI)

FastAPI-based verse-by-verse Quran analysis using OpenAI GPT-4o.

**Location**: `scripts/deployment/`

### Quick Start

```bash
cd scripts/deployment
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-key-here

# Run server
cd api
python -m uvicorn main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start` | POST | Start session with `{"verse_range": "68:1-10"}` |
| `/sessions/{id}/continue` | POST | Get next verse analysis |
| `/sessions/{id}/progress` | GET | Check session progress |
| `/cache/stats` | GET | View cache statistics |

### Features

- **Intelligent Caching**: Chapter context and verse analysis cached after first generation
- **Memory Management**: Auto context reset at 100K tokens, re-injects balaghah guide
- **Cost**: ~$0.19 per 10-verse session (first time), $0 when cached

See `scripts/deployment/README.md` for full documentation.

---

## Balaghah Analysis System

### Analysis Guide

**Primary Guide**: `docs/skills/balaghah_quick_reference_v4_expanded.md`
- Optimized for Claude with XML structure
- 18+ rhetorical devices covered
- 3-step reasoning framework with verification checklists

**Device Categories**:
1. **Sound/Rhythm** (Ilm al-Badi'): Saj', Jinas, Tarsi'
2. **Meaning/Context** (Ilm al-Ma'ani): Taqdim/Takhir, Hadhf, Wasl/Fasl
3. **Figures of Speech** (Ilm al-Bayan): Tashbih, Isti'arah, Majaz, Kinayah
4. **Antithesis**: Tibaq, Muqabala
5. **Grammatical**: Iltifat, Isti'anaf, Qasam

### Typical Workflow

```
1. User requests verse analysis (e.g., "68:1-5")
2. get_verse_info_v3.py extracts from quran_comprehensive.json
3. MetadataLoader provides context data
4. LLM receives JSON + balaghah guide
5. Output: Structured rhetorical analysis
```

---

## JQuranTree Java Library (Legacy)

Java library for low-level Quranic text processing.

**Location**: `jqurantree/src/`

```bash
# Build
cd jqurantree/src
mvn clean package
mvn test
```

---

## Development Notes

### Adding New Data Sources

1. Fetch source data -> `sources/`
2. Create converter -> `scripts/converters/`
3. Generate JSON -> `data/`
4. Extend MetadataLoader if needed
5. Update get_verse_info_v3.py
6. Update this CLAUDE.md

### Data Format Standards

- **Encoding**: UTF-8 for all JSON files
- **Keys**: snake_case
- **Locations**: Format as `chapter:verse:word:segment`
- **Null handling**: Use `null`, not empty strings

### Python Environment

- Python 3.7+ required
- Standard library only for most scripts (json, os, sys, re)
- Always use `encoding='utf-8'` for file operations
- Avoid Unicode in console output (charmap errors)

### Common Operations

```bash
# Regenerate comprehensive data
cd scripts/converters
python update_comprehensive_with_tafsirs.py

# Test extraction
cd scripts/tools
python get_verse_info_v3.py
```

---

## License and Attribution

**Data Sources**:
- Quranic Arabic Corpus: http://corpus.quran.com
- Tanzil Quran Text: http://tanzil.net (CC BY-ND)
- Al-Kashshaf: OpenITI (github.com/OpenITI/0550AH)
- Ma'arif/Ibn Kathir: spa5k/tafsir_api
- Clear Quran Sections: theclearquran.org

**JQuranTree**: Kais Dukes, 2009 (GPLv3)

See `docs/DATA_SOURCES.md` for complete attribution.

---

**Last Updated**: January 2025
