# Balaghah Data Format Specification

**Version**: 2.0
**Last Updated**: 2025-01
**Source**: `scripts/tools/get_verse_info.py`

## Overview

This document specifies the JSON output format for Quranic verse information with comprehensive balaghah (rhetoric) analysis. The data is extracted by `get_verse_info.py` and includes morphological, syntactic, semantic, and rhetorical features.

## Design Principles

1. **Verse-Centric Structure**: All data organized at verse level for direct LLM consumption
2. **Syntactic Detection Only**: Code detects patterns; semantic interpretation left to LLM
3. **Rich Context**: Maximum linguistic data provided for analysis
4. **Graceful Degradation**: Missing data handled with null/absent fields
5. **Unified Format**: Consistent structure across all verses and chapters

---

## Top-Level Structure

```json
{
  "chapter": 68,
  "verse_start": 1,
  "verse_end": 3,
  "metadata": { ... },
  "verses": [ ... ],
  "chapter_balaghah": { ... }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chapter` | integer | Yes | Chapter number (1-114) |
| `verse_start` | integer | Yes | First verse in range |
| `verse_end` | integer | Yes | Last verse in range |
| `metadata` | object | Yes | Chapter metadata |
| `verses` | array | Yes | Array of verse objects |
| `chapter_balaghah` | object | No | Chapter-level balaghah patterns |

---

## Metadata Structure

```json
"metadata": {
  "chapter_number": 68,
  "name_arabic": "ٱلْقَلَمِ",
  "revelation_place": "makkah",
  "revelation_order": 2,
  "verses_count": 52
}
```

### Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `chapter_number` | integer | 1-114 | Chapter number |
| `name_arabic` | string | Unicode Arabic | Chapter name in Arabic |
| `revelation_place` | string | "makkah", "madinah" | Place of revelation |
| `revelation_order` | integer | 1-114 | Chronological order of revelation |
| `verses_count` | integer | 3-286 | Total verses in chapter |

---

## Verse Structure

```json
{
  "verse_number": 1,
  "text": "نٓ وَٱلْقَلَمِ وَمَا يَسْطُرُونَ",
  "translation_en": "Nun. By the pen and what they inscribe,",
  "tafsir": { ... },
  "asbab_nuzul": [ ... ],
  "balaghah": { ... },
  "morphology": [ ... ],
  "dependencies": [ ... ],
  "named_entities": [ ... ],
  "pause_marks": [ ... ]
}
```

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `verse_number` | integer | Yes | Verse number within chapter |
| `text` | string | Yes | Arabic text (Uthmani script) |
| `translation_en` | string | No | English translation |

### Optional Context Fields

| Field | Type | Description |
|-------|------|-------------|
| `tafsir` | object | Al-Qushairi Sufi commentary (if available) |
| `asbab_nuzul` | array | Occasions of revelation (if available) |

---

## Balaghah Structure

The `balaghah` object contains all rhetorical features detected in the verse.

```json
"balaghah": {
  "saj": { ... },
  "root_repetitions": { ... },
  "maani": { ... },
  "jinas": [ ... ],
  "iltifat": [ ... ],
  "muqabala": { ... },
  "hadhf": { ... },
  "qasam": { ... },
  "muqattaat": { ... },
  "interrogative": { ... },
  "restriction": { ... },
  "particles_emphasis": { ... },
  "tafsir_context": { ... }
}
```

### 1. Saj' (Rhyme Pattern)

```json
"saj": {
  "pattern": "ن",
  "sequence_length": 3,
  "position_in_sequence": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | string | Ending letter/pattern (Arabic) |
| `sequence_length` | integer | Total verses in this rhyme sequence |
| `position_in_sequence` | integer | Position of this verse in sequence |

### 2. Root Repetitions

**NEW FORMAT (v2.0)**: Full details at verse level

```json
"root_repetitions": {
  "رحم": {
    "lemmas": ["رَحِيم", "رَحْمٰن"],
    "related_verses": [3, 5],
    "total_verses": 3,
    "appears_in_current_verse": true,
    "translations": ["merciful", "compassionate"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| Root key | string | Arabic root (3-4 letters) |
| `lemmas` | array[string] | Dictionary forms derived from this root |
| `related_verses` | array[integer] | Other verses containing this root (excludes current) |
| `total_verses` | integer | Total verses with this root in chapter |
| `appears_in_current_verse` | boolean | Always true at verse level |
| `translations` | array[string] | English meanings (if available) |

### 3. Ma'ani - Sentence Types

```json
"maani": {
  "sentence_type": {
    "type": "khabar",
    "subtype": "oath",
    "description": "Oath with disconnected letter (نٓ)"
  },
  "verb_forms": { ... },
  "definiteness": { ... }
}
```

#### Sentence Types

| `type` | `subtype` | Description |
|--------|-----------|-------------|
| `khabar` | `nominal` | Noun-initial declarative |
| `khabar` | `verbal` | Verb-initial declarative |
| `khabar` | `oath` | Oath sentence (qasam) |
| `khabar` | `particle-initial` | Starts with particle |
| `insha` | `command` | Imperative |
| `insha` | `question` | Interrogative |
| `insha` | `wish` | Optative |

### 4. Jinas (Wordplay)

```json
"jinas": [
  {
    "word1": "ٱلرَّحْمَٰنِ",
    "word2": "ٱلرَّحِيمِ",
    "positions": [3, 4],
    "similarity": 0.833,
    "type": "jinas_ishtiqaq",
    "roots": ["رحم", "رحم"]
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `word1`, `word2` | string | The two similar words |
| `positions` | array[integer] | Word positions in verse |
| `similarity` | float | Phonetic similarity (0.0-1.0) |
| `type` | string | Jinas category |
| `roots` | array[string] | Roots of both words |

### 5. Iltifat (Grammatical Shifts)

```json
"iltifat": [
  {
    "type": "number_shift",
    "detected_pattern": {
      "from_number": "plural",
      "to_number": "singular",
      "from_verse": 1,
      "to_verse": 2,
      "shift_description": "plural → singular",
      "evidence": {
        "from": {"verse": 1, "word": 2, "text": "وَٱلْقَلَمِ"},
        "to": {"verse": 2, "word": 2, "text": "أَنتَ"}
      }
    }
  }
]
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `type` | string | `person_shift`, `number_shift`, `tense_shift`, `addressee_shift` | Type of shift |
| `detected_pattern` | object | - | Shift details |
| `from_verse`, `to_verse` | integer | - | Verses involved in shift |
| `evidence` | object | - | Specific words showing shift |

### 6. Muqabala (Parallelism)

**ENHANCED (v2.0)**: Now includes translations

```json
"muqabala": {
  "muqabala_patterns": [
    {
      "syntactic_pattern": ["P", "N"],
      "structure1": {
        "P": {"arabic": "مَآ", "translation": "not"},
        "N": {"arabic": "أَنتَ"}
      },
      "structure2": {
        "P": {"arabic": "بِ", "translation": "with"},
        "N": {"arabic": "رَبِّ", "root": "ربب", "translation": "lord"}
      },
      "parallelism_type": "syntactic"
    }
  ],
  "count": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `syntactic_pattern` | array[string] | POS pattern: P (particle), N (noun), V (verb) |
| `structure1`, `structure2` | object | Parallel structures |
| `translation` | string | English meaning (if available) |
| `parallelism_type` | string | `syntactic`, `semantic`, or `both` |

### 7. Hadhf (Ellipsis)

```json
"hadhf": {
  "hadhf_patterns": [
    {
      "type": "omitted_object",
      "verb_word": 4,
      "verb_text": "يَسْطُرُ",
      "verb_root": "سطر"
    }
  ],
  "count": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Type of omission |
| `verb_word` | integer | Word number of verb |
| `verb_text` | string | Arabic text of verb |
| `verb_root` | string | Root of verb |

### 8. Qasam (Oath)

**NEW (v2.0)**: Syntactic detection

```json
"qasam": {
  "has_qasam": true,
  "elements": [
    {
      "particle": "و",
      "word_number": 2,
      "word_text": "وَٱلْقَلَمِ",
      "lemma": "قَلَم",
      "root": "قلم"
    }
  ],
  "count": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `has_qasam` | boolean | Oath detected |
| `particle` | string | Oath particle: "و" or "ت" |
| `word_number` | integer | Position in verse |
| `word_text` | string | Full word with particle |
| `lemma` | string | Dictionary form of sworn-by noun |
| `root` | string | Root of sworn-by noun |

### 9. Muqatta'at (Disconnected Letters)

**NEW (v2.0)**: Syntactic detection

```json
"muqattaat": {
  "has_muqattaat": true,
  "letters": "نٓ",
  "word_number": 1,
  "interpretation": "unknown",
  "note": "Disconnected letters at chapter opening"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `has_muqattaat` | boolean | Muqatta'at detected |
| `letters` | string | The mysterious letters |
| `word_number` | integer | Always 1 (first word) |
| `interpretation` | string | Always "unknown" |
| `note` | string | Descriptive note |

### 10. Interrogative Particles

**NEW (v2.0)**: Question words

```json
"interrogative": {
  "has_interrogative": true,
  "particles": [
    {
      "particle": "هل",
      "word_number": 1,
      "word_text": "هَلْ",
      "position": "initial"
    }
  ],
  "count": 1
}
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `particle` | string | هل, أ, ما, من, etc. | Interrogative particle |
| `position` | string | `initial`, `medial` | Position in verse (first 3 words = initial) |

### 11. Restriction Particles

**NEW (v2.0)**: Hasr patterns

```json
"restriction": {
  "has_restriction": true,
  "patterns": [
    {
      "pattern": "innama",
      "word_number": 1,
      "word_text": "إِنَّمَا",
      "type": "exclusive_restriction"
    },
    {
      "pattern": "ma_illa",
      "word_numbers": [2, 5],
      "words": ["مَا", "إِلَّا"],
      "type": "exception_restriction",
      "span": 3
    }
  ],
  "count": 2
}
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `pattern` | string | `innama`, `ma_illa` | Restriction pattern type |
| `type` | string | `exclusive_restriction`, `exception_restriction` | Rhetorical function |
| `span` | integer | - | Distance between ما and إلا (for ma_illa pattern) |

### 12. Emphasis Particles

**NEW (v2.0)**: Ta'kid particles

```json
"particles_emphasis": {
  "has_emphasis": true,
  "particles": [
    {
      "particle": "إن",
      "word_number": 1,
      "word_text": "إِنَّ",
      "type": "assertion"
    },
    {
      "particle": "قد",
      "word_number": 3,
      "word_text": "قَدْ",
      "type": "assertion"
    }
  ],
  "count": 2
}
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `particle` | string | إن, أن, ل, قد, لقد | Emphasis particle |
| `type` | string | `assertion` | Always "assertion" for now |

### 13. Tafsir Context

Automatically generated summary for LLM

```json
"tafsir_context": {
  "linguistic_features_summary": [
    "saj' (rhyme pattern: ن, sequence: 3 verses)",
    "sentence type: khabar - oath",
    "iltifat (shifts: number)",
    "hadhf (ellipsis: 1 omissions)",
    "qasam (oath: 1 elements)",
    "muqatta'at (disconnected letters: نٓ)"
  ]
}
```

---

## Morphology Structure

**NEW (v2.0)**: Segment-level morphology from `morphology_segments.json`

```json
"morphology": [
  {
    "word_number": 2,
    "word_text": "وَٱلْقَلَمِ",
    "segments": [
      {
        "segment": 1,
        "arabic": "وَ",
        "pos": "P",
        "lemma": "و",
        "type": "PREFIX",
        "grammar": "Plur"
      },
      {
        "segment": 2,
        "arabic": "ٱلْ",
        "pos": "P",
        "lemma": "ال",
        "type": "PREFIX",
        "grammar": "Definite"
      },
      {
        "segment": 3,
        "arabic": "قَلَمِ",
        "pos": "N",
        "root": "قلم",
        "lemma": "قَلَم",
        "type": "STEM",
        "grammar": "Masc | Genitive"
      }
    ]
  }
]
```

### Word-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `word_number` | integer | Position in verse |
| `word_text` | string | Complete word with diacritics |
| `segments` | array | Morpheme breakdown |

### Segment-Level Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `segment` | integer | 1, 2, 3... | Segment number |
| `arabic` | string | Unicode | Arabic text of segment |
| `pos` | string | N, V, P, ADJ, PRON | Part of speech |
| `lemma` | string | Unicode | Dictionary form |
| `root` | string | 3-4 letters | Arabic root |
| `type` | string | PREFIX, STEM, SUFFIX | Morpheme type |
| `grammar` | string | Pipe-separated | Grammatical features |
| `verb_form` | string | VF:1 to VF:10 | Verb form (if verb) |

### Part of Speech (POS) Values

| Code | Meaning | Arabic | Example |
|------|---------|--------|---------|
| N | Noun | اسم | قَلَم |
| V | Verb | فعل | يَسْطُرُ |
| P | Particle | حرف | وَ، بِ، إِنَّ |
| ADJ | Adjective | صفة | عَظِيم |
| PRON | Pronoun | ضمير | أَنتَ، هُوَ |

### Grammar Features

Features in `grammar` field (pipe-separated):

- **Gender**: `Masc`, `Fem`
- **Number**: `Singular`, `Dual`, `Plural`
- **Case**: `Nominative`, `Genitive`, `Accusative`
- **Definiteness**: `Definite`, `Indefinite`
- **Verb aspect**: `Perfect`, `Imperfect`
- **Verb mood**: `Indicative`, `Jussive`, `Subjunctive`

---

## Dependencies Structure

**NEW (v2.0)**: Syntactic relations from Quranic Arabic Corpus

```json
"dependencies": [
  {
    "child": {
      "chapter": 68,
      "verse": 1,
      "word": 2
    },
    "parent": {
      "chapter": 68,
      "verse": 1,
      "word": 2
    },
    "relation": {
      "code": "gen",
      "arabic": "جار ومجرور",
      "english": "Prepositional phrase"
    }
  }
]
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `child` | object | Dependent word location |
| `parent` | object | Head word location |
| `relation.code` | string | Abbreviated relation type |
| `relation.arabic` | string | Arabic grammatical term |
| `relation.english` | string | English description |

### Common Relation Types

| Code | Arabic | English |
|------|--------|---------|
| `subj` | فاعل | Subject |
| `obj` | مفعول به | Object |
| `gen` | جار ومجرور | Prepositional phrase |
| `conj` | معطوف | Coordinating conjunction |
| `adj` | نعت | Adjective/Attribute |
| `possessed` | مضاف إليه | Possessive (idafa) |

---

## Named Entities Structure

**NEW (v2.0)**: Concept annotations from Quranic Arabic Corpus

```json
"named_entities": [
  {
    "location": {
      "start": {
        "chapter": 68,
        "verse": 1,
        "word": 2,
        "segment": 3
      },
      "is_range": false
    },
    "entity_type": "CON",
    "concept": "pen"
  }
]
```

### Fields

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `location.start` | object | - | Starting location |
| `location.end` | object | - | Ending location (if range) |
| `location.is_range` | boolean | - | Whether entity spans multiple words |
| `entity_type` | string | CON, PN, LOC | Entity category |
| `concept` | string | - | Concept identifier (lowercase, English) |

### Entity Types

| Code | Meaning | Examples |
|------|---------|----------|
| CON | Concept | allah, pen, heaven, faith |
| PN | Proper Name | ibrahim, musa, makkah |
| LOC | Location | badr, uhud, egypt |

---

## Pause Marks Structure

**NEW (v2.0)**: Tajweed recitation marks

```json
"pause_marks": [
  {
    "location": {
      "chapter": 34
    },
    "mark_type": "6",
    "description": "Unknown pause type"
  }
]
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `location.chapter` | integer | Absolute verse number (1-6236) |
| `mark_type` | string | Pause type code |
| `description` | string | Pause description |

**Note**: The `chapter` field stores **absolute verse numbering** (1-6236), not chapter number. This is a legacy format from the source data.

### Pause Types (Classical Tajweed)

| Type | Symbol | Arabic | Meaning |
|------|--------|--------|---------|
| 1 | مـ | لازم | Compulsory pause |
| 2 | لا | ممنوع | Prohibition of pausing |
| 3 | ج | جائز | Permissible pause |
| 4 | ز | جائز الوصل | Permissible continuation |
| 5 | صلى | أولى بالوقف | Better to pause |
| 6 | قلى | أولى بالوصل | Better to continue |

---

## Chapter-Level Balaghah

Aggregated patterns across the requested verse range

```json
"chapter_balaghah": {
  "root_repetitions": {
    "رحم": {
      "lemmas": ["رَحِيم", "رَحْمٰن"],
      "verses": [1, 3],
      "total_occurrences": 2,
      "translations": ["merciful", "compassionate"]
    }
  }
}
```

### Root Repetitions

| Field | Type | Description |
|-------|------|-------------|
| Root key | string | Arabic root |
| `lemmas` | array[string] | All lemma forms found |
| `verses` | array[integer] | All verses containing root |
| `total_occurrences` | integer | Number of verses (same as verses.length) |
| `translations` | array[string] | English meanings (if available) |

---

## Data Sources

### Primary Sources

1. **Quranic Text**: Tanzil project (Uthmani script)
2. **Morphology**: Quranic Arabic Corpus - `morphology_segments.json` (130,030 segments)
3. **Dependencies**: Quranic Arabic Corpus - `dependencies_full.json` (37,420 relations)
4. **Named Entities**: Quranic Arabic Corpus - `named_entities_full.json` (5,494 entities)
5. **Pause Marks**: Quranic Arabic Corpus - `pause_marks.json` (4,359 marks)
6. **Lemmas Dictionary**: Quranic Arabic Corpus - `lemmas_dictionary.json` (1,593 unique lemmas)
7. **Chapter Metadata**: Extracted from Tanzil and historical sources
8. **Tafsir**: Al-Qushairi Sufi commentary (45 verses)
9. **Asbab al-Nuzul**: Occasions of revelation (678 verses, 1,335 entries)

### Balaghah Analysis

- **Saj', Jinas, Takrar**: Computed from morphology and text analysis
- **Ma'ani features**: Extracted from morphological POS and features
- **Iltifat, Hadhf, Wasl/Fasl, Muqabala, Isti'anaf**: Pre-analyzed in `quran_comprehensive.json`
- **Qasam, Muqatta'at**: **NEW** - Syntactically detected (v2.0)
- **Particles (Interrogative, Restriction, Emphasis)**: **NEW** - Syntactically detected (v2.0)

---

## Version History

### Version 2.0 (2025-01)

**Major Enhancements:**

1. **Data Integration**:
   - Added `dependencies` field (syntactic relations)
   - Added `named_entities` field (concept annotations)
   - Added `pause_marks` field (tajweed marks)

2. **Syntactic Detection**:
   - Added `qasam` detection (oath patterns)
   - Added `muqattaat` detection (disconnected letters)
   - Added `interrogative` particle detection
   - Added `restriction` particle detection (hasr)
   - Added `particles_emphasis` detection (ta'kid)

3. **Structural Improvements**:
   - Unified `root_repetitions`: Full details now at verse level (not just references)
   - Enhanced `muqabala`: Added translation fields
   - Updated `morphology`: Segment-level from `morphology_segments.json`

4. **Documentation**:
   - Enhanced `tafsir_context.linguistic_features_summary` with new features
   - Added 6 new device categories to output

### Version 1.0 (2024-12)

Initial release with core balaghah analysis:
- Saj', Root Repetitions, Jinas
- Ma'ani (verb forms, definiteness, sentence types)
- Iltifat, Wasl/Fasl, Muqabala, Hadhf, Isti'anaf
- Basic morphology and chapter metadata

---

## Usage Guidelines

### For LLMs

1. **Start with verse context**: Read `text`, `translation_en`, and `metadata`
2. **Check `tafsir_context.linguistic_features_summary`**: Quick overview of detected features
3. **Dive into specific features**: Examine detailed structures as needed
4. **Use morphology for word-level analysis**: When interpreting specific terms
5. **Consider dependencies for sentence structure**: Understanding grammatical relationships
6. **Track concepts via named_entities**: Thematic analysis
7. **Remember**: Code detects syntax; YOU interpret semantics

### For Developers

1. **All fields are optional except core verse data**
2. **Check field existence before accessing**
3. **Empty arrays/objects may be omitted**
4. **Translations may be missing** (limited lemma dictionary)
5. **Pause marks use absolute verse numbering** (not chapter:verse)
6. **Morphology is segment-level**: One word = multiple segments
7. **Dependencies may have self-loops**: When word is root of tree

---

## Example: Complete Verse

See `scripts/tools/verse_68_1-3.json` for a complete example with all features present.

---

## Contact & Contribution

**Data Issues**: Check source files in `data/linguistic/` and `data/text/`
**Code Issues**: See `scripts/tools/get_verse_info.py`
**Format Questions**: Refer to this specification

**License**: Data from Quranic Arabic Corpus (CC BY-NC-ND 3.0), Analysis code (GPLv3)
