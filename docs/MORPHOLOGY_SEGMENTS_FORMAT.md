# Morphology Segments Format Documentation

## Overview

The `morphology_segments.json` file contains detailed segment-level morphological analysis of the entire Quran, with **130,030 segments** covering all 114 chapters and 6,236 verses.

This is the **most granular morphological data** available in the project, sourced from `quran-morphology-github.txt` which provides segment-level decomposition (prefix, stem, suffix) with native Unicode Arabic text.

## Key Features

- **Native Unicode Arabic**: All Arabic text stored in Unicode (no Buckwalter conversion needed)
- **Segment-level granularity**: Each morpheme (prefix/stem/suffix) is a separate entry
- **Explicit feature encoding**: Verb forms (`VF:4`), mood (`MOOD:IND`), etc. clearly marked
- **Complete feature set**: All morphological features preserved from Quranic Arabic Corpus
- **52,601 more segments** than the previous `morphology_full.json` (77,429 segments)

## File Structure

```json
{
  "morphology": {
    "1": {                    // Chapter number (string key)
      "1": {                  // Verse number (string key)
        "1": [                // Word number (string key)
          {
            "segment": 1,                    // Segment number within word
            "arabic": "بِ",                  // Native Unicode Arabic text
            "buckwalter": "bi",              // Buckwalter transliteration
            "pos": "P",                      // Part of speech
            "features": {                    // Pipe-delimited features parsed
              "p": true,                     // Preposition flag
              "pref": true,                  // Prefix flag
              "lem": "ب"                     // Lemma (Unicode Arabic)
            }
          },
          {
            "segment": 2,
            "arabic": "سْمِ",
            "buckwalter": "somi",
            "pos": "N",
            "features": {
              "root": "سمو",                 // Root (Unicode Arabic)
              "lem": "اسْم",                 // Lemma (Unicode Arabic)
              "m": true,                     // Masculine
              "gen": true                    // Genitive case
            }
          }
        ],
        "2": [                // Next word...
          ...
        ]
      },
      "2": {                  // Next verse...
        ...
      }
    },
    "2": {                    // Next chapter...
      ...
    }
  },
  "metadata": {
    "source": "quran-morphology-github.txt",
    "total_segments": 130030,
    "format": "segment-level",
    "chapters": 114,
    "note": "Hierarchical structure: chapter → verse → word → segments array"
  }
}
```

## Data Fields

### Segment Structure

Each segment in the `segments` array contains:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `segment` | Integer | Segment number within word (1-based) | `1`, `2`, `3` |
| `arabic` | String | Native Unicode Arabic text with diacritics | `"بِ"`, `"سْمِ"`, `"ٱللَّهِ"` |
| `buckwalter` | String | Buckwalter transliteration (simplified conversion) | `"bi"`, `"somi"`, `"All~ah"` |
| `pos` | String | Part of speech tag | `"N"`, `"V"`, `"P"`, `"ADJ"` |
| `features` | Object | Dictionary of morphological features (parsed from pipe-delimited string) | See below |

### Part of Speech (POS) Tags

| Tag | Meaning | Description |
|-----|---------|-------------|
| `N` | Noun | Noun or noun-like structure |
| `V` | Verb | Verb (perfect, imperfect, imperative) |
| `P` | Particle | Preposition, conjunction, negation, etc. |
| `PN` | Proper Noun | Proper name (Allah, prophets, places) |
| `ADJ` | Adjective | Adjective or adjectival phrase |
| `PRON` | Pronoun | Pronoun (attached or independent) |

### Feature Keys

The `features` object contains parsed morphological features. Common keys:

#### Morpheme Type
- `pref`: Prefix (true/false)
- `suff`: Suffix (true/false)
- `det`: Determiner (true/false)
- `conj`: Conjunction (true/false)
- `neg`: Negation (true/false)

#### Grammatical Features
- `root`: Arabic root (Unicode) - e.g., `"قول"`, `"كتب"`
- `lem`: Lemma/dictionary form (Unicode) - e.g., `"قالَ"`, `"كِتاب"`
- `vf`: Verb form number - e.g., `"1"`, `"4"`, `"10"` (maps to VF:I, VF:IV, VF:X)

#### Gender & Number
- `m`: Masculine
- `f`: Feminine
- `s`: Singular
- `d`: Dual
- `p`: Plural
- `ms`: Masculine singular
- `fs`: Feminine singular
- `mp`: Masculine plural
- `fp`: Feminine plural

#### Case
- `nom`: Nominative case
- `acc`: Accusative case
- `gen`: Genitive case

#### Verb Tense/Mood
- `perf`: Perfect tense
- `impf`: Imperfect tense
- `impv`: Imperative
- `mood`: Mood value (`"IND"` = indicative, `"JUS"` = jussive, `"SUBJ"` = subjunctive)

#### Definiteness
- `det`: Definite (has Al- prefix)
- `indef`: Indefinite (explicitly marked)

#### Pronoun Reference
- `1p`: First person plural
- `2ms`: Second person masculine singular
- `3mp`: Third person masculine plural
- etc.

## Usage Examples

### Python: Load and Access Morphology

```python
import json

# Load morphology segments
with open('data/linguistic/morphology_segments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    morphology = data['morphology']

# Access verse 1:1 (Bismillah)
chapter_1 = morphology['1']
verse_1 = chapter_1['1']

# Get all words in verse
for word_num, segments in verse_1.items():
    print(f"Word {word_num}:")
    for seg in segments:
        print(f"  Segment {seg['segment']}: {seg['arabic']} ({seg['pos']})")
        if 'root' in seg['features']:
            print(f"    Root: {seg['features']['root']}")
        if 'lem' in seg['features']:
            print(f"    Lemma: {seg['features']['lem']}")
```

### Python: Using MetadataLoader

```python
from metadata_loader import MetadataLoader

# Initialize loader (automatically loads morphology)
loader = MetadataLoader()

# Get morphology for specific word
word_morphology = loader.get_word_morphology(chapter=1, verse=1, word=1)
print(f"Word has {len(word_morphology)} segments")

for segment in word_morphology:
    print(f"Segment {segment['segment']}: {segment['arabic']}")
    print(f"  POS: {segment['pos']}")
    print(f"  Features: {list(segment['features'].keys())}")

# Get all morphology for a verse
verse_morphology = loader.get_verse_morphology(chapter=1, verse=1)
print(f"Verse has {len(verse_morphology)} words")
```

### Python: Format for Display (as used in get_verse_info.py)

```python
def format_morphology_segment(segment):
    """Format segment for human-readable display"""
    formatted = {
        'segment': segment['segment'],
        'arabic': segment['arabic'],
        'pos': segment['pos']
    }

    features = segment.get('features', {})

    # Extract root and lemma
    if 'root' in features:
        formatted['root'] = features['root']
    if 'lem' in features:
        formatted['lemma'] = features['lem']

    # Extract verb form
    if 'vf' in features:
        formatted['verb_form'] = f"VF:{features['vf']}"

    # Determine morpheme type
    if 'pref' in features:
        formatted['type'] = 'PREFIX'
    elif 'suff' in features:
        formatted['type'] = 'SUFFIX'
    else:
        formatted['type'] = 'STEM'

    # Build grammar string
    grammar = []
    if 'ms' in features:
        grammar.append('Masc.Sing')
    if 'nom' in features:
        grammar.append('Nominative')
    # ... etc.

    if grammar:
        formatted['grammar'] = ' | '.join(grammar)

    return formatted
```

## Comparison with Old Format

### Old: `morphology_full.json` (77,429 segments)

- Buckwalter transliteration only (no native Arabic)
- Pre-parsed into separate fields
- Some features missing or inconsistent
- Less granular (combined morphemes in some cases)

### New: `morphology_segments.json` (130,030 segments)

- ✓ Native Unicode Arabic with diacritics
- ✓ More granular segment-level data (52,601 additional segments)
- ✓ Explicit verb forms (`VF:4` instead of `"(IV)"`)
- ✓ Consistent feature structure
- ✓ Simplified Buckwalter for backward compatibility

### Migration Notes

The new format is **backward compatible** in the sense that all data from the old format is preserved. However:

1. **Segment counts differ**: The new format has more segments because it breaks down words more granularly
2. **Arabic text available**: Use `segment['arabic']` instead of converting from Buckwalter
3. **Features are objects**: Parse `features` dict instead of regex on `features_raw` string
4. **Verb forms explicit**: Use `features.get('vf')` instead of regex matching `"(IV)"`

## Data Source

- **Original source**: [Quranic Arabic Corpus](https://corpus.quran.com) GitHub repository
- **File**: `quran-morphology-github.txt` (Tab-separated values)
- **Converted by**: `scripts/converters/convert_github_morphology.py`
- **Validation**: `scripts/tools/validate_morphology.py` (all tests passed)

## Statistics

```
Total segments:    130,030
Total chapters:    114
Total verses:      6,236
Average segs/word: 2.08 (some words have 1-4 segments)
File size:         39.42 MB (JSON with indentation)
Encoding:          UTF-8
```

## Integration Points

### 1. `metadata_loader.py`

Automatically loads morphology segments on initialization:

```python
loader = MetadataLoader()
# Access via:
loader.get_word_morphology(chapter, verse, word)
loader.get_verse_morphology(chapter, verse)
```

### 2. `get_verse_info.py`

Includes segment-level morphology in verse output:

```bash
cd scripts/tools
python get_verse_info.py
# Enter: 1:1
# Output: verse_1_1.json includes "morphology" field with segments
```

### 3. Future Integration

The detailed morphology can be used for:

- **Balaghah analysis**: Identify rhetorical devices based on morphological patterns
- **Syntactic analysis**: Dependency parsing using POS and case information
- **Semantic analysis**: Root-based semantic grouping
- **Verb form analysis**: Categorize verbs by form (causative, reciprocal, etc.)
- **Grammatical pattern detection**: Find repeated grammatical structures

## References

- [Quranic Arabic Corpus Documentation](https://corpus.quran.com/documentation/)
- [Arabic Morphology Basics](https://en.wikipedia.org/wiki/Arabic_grammar)
- [Buckwalter Transliteration](https://en.wikipedia.org/wiki/Buckwalter_transliteration)

---

**Last Updated**: November 13, 2024
**Format Version**: 1.0
**Data Version**: Quranic Arabic Corpus (Complete Morphology)
