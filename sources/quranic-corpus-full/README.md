# Quranic Arabic Corpus - Complete Dataset

**Full Quran Linguistic Annotation Data**
Source: [corpus.quran.com](https://corpus.quran.com)
Version: 0.4
Coverage: Complete Quran (114 chapters, 6,236 verses, 77,429 words)

---

## 📋 Dataset Overview

This directory contains comprehensive linguistic annotations for the entire Quran, extracted from the Quranic Arabic Corpus project.

### Data Files

| File | Lines | Size | Description |
|------|-------|------|-------------|
| **quranic-corpus-dependencies-full.txt** | 37,420 | ~2.5MB | Dependency treebank (parent-child relationships) |
| **quranic-corpus-morphology-full.txt** | 77,429 | ~5.5MB | Complete morphological analysis (POS, lemmas, roots) |
| **quranic-corpus-named-entities-full.txt** | 5,494 | ~200KB | Named entity annotations (Allah, prophets, concepts) |
| **quranic-corpus-lemmas.txt** | 1,593 | ~35KB | Lemma dictionary |
| **quranic-corpus-pause-marks.txt** | 4,359 | ~90KB | Tajweed pause marks (وقف) |

---

## 📊 Data Formats

### 1. Dependency Treebank (`quranic-corpus-dependencies-full.txt`)

**37,420 dependency relationships** showing syntactic structure.

**Format:** Tab-delimited
```
CHILD	PARENT	RELATION	ARABIC_LABEL	ENGLISH_LABEL
```

**Example:**
```
(1:1:3)	(1:1:2)	adj	صفة	Adjective
(1:1:2)	(1:1:1)	poss	مضاف إليه	Possessive
(1:1:1)	(1:1:1)	gen	جار ومجرور	Prepositional phrase
```

**Relation Types:** 47 dependency relations including:
- **Nominal:** adj (صفة), poss (مضاف إليه), pred (مبتدأ وخبر), app (بدل), spec (تمييز)
- **Verbal:** subj (فاعل), obj (مفعول به), pass (نائب فاعل)
- **Phrases:** gen (جار ومجرور), link (متعلق), conj (معطوف), sub (صلة)
- **Adverbial:** circ (حال), cog (مفعول مطلق), prp (المفعول لأجله)

**Location Format:** `(chapter:verse:word:segment)`
- Example: `(1:1:3)` = Chapter 1, Verse 1, Word 3

---

### 2. Morphological Analysis (`quranic-corpus-morphology-full.txt`)

**77,429 morphological annotations** (one per word segment).

**Format:** Space-delimited features on single line per segment

**Example:**
```
bi+ POS:N LEM:{som ROOT:smw M GEN
POS:PN LEM:{ll~ah ROOT:Alh GEN
Al+ POS:ADJ LEM:r~aHoma`n ROOT:rHm MS GEN
```

**Features:**
- **Prefixes/Suffixes:** `bi+`, `Al+`, `l:P+`, `+ka`, `+hum`
- **POS:** Part-of-speech (N, V, ADJ, PRON, etc.)
- **LEM:** Lemma in Buckwalter transliteration
- **ROOT:** Triliteral/quadriliteral Arabic root
- **Gender:** M (masculine), F (feminine)
- **Number:** S (singular), D (dual), P (plural)
- **Case:** NOM (nominative), ACC (accusative), GEN (genitive)
- **Verbal features:** IMPF (imperfect), PERF (perfect), ACT (active), PASS (passive)

---

### 3. Named Entities (`quranic-corpus-named-entities-full.txt`)

**5,494 concept annotations** mapping words to semantic concepts.

**Format:** Tab-delimited
```
LOCATION	TYPE:CONCEPT_ID
```

**Example:**
```
(1:1:2:1)	CON:allah
(1:4:2:1)-(1:4:3:2)	CON:day-of-resurrection
(2:7:4:1)	CON:heart
```

**Concept Types:**
- `CON:` - Concept reference (Allah, prophets, places, abstract concepts)
- `SUBJ:` - Subject entity

**Multi-word Concepts:** Range notation for concepts spanning multiple words
- Example: `(1:4:2:1)-(1:4:3:2)` spans from word 2 to word 3

**Common Concepts:**
- `allah` (Allah)
- `day-of-resurrection` (يوم القيامة)
- `heart` (قلب)
- `heaven`, `hell`, `prophet`, `book`, etc.

---

### 4. Lemma Dictionary (`quranic-corpus-lemmas.txt`)

**1,593 unique lemmas** in the Quran.

**Format:** One lemma per line in Buckwalter transliteration

**Example:**
```
{som
{ll~ah
r~aHoma`n
r~aHiym
Hamod
```

**Encoding:** Buckwalter ASCII transliteration
- `{` = hamza (أ)
- `~` = shadda (ّ)
- `'` = hamza (ء)

---

### 5. Pause Marks (`quranic-corpus-pause-marks.txt`)

**4,359 tajweed pause marks** (علامات الوقف).

**Format:** Tab-delimited
```
LOCATION	PAUSE_TYPE
```

**Example:**
```
(1:1:4)	m
(1:2:4)	qly
(1:3:2)	j
```

**Pause Types:**
- `m` - mīm (م) - compulsory pause
- `qly` - qalīl (قلى) - preferably continue
- `j` - jāʾiz (ج) - permissible pause
- `la` - lā (لا) - no pause recommended

---

## 🔗 Location Reference System

All files use a consistent location reference format:

### Format
```
(chapter:verse:word:segment)
```

### Examples
- `(1:1:1)` - Chapter 1, Verse 1, Word 1
- `(1:1:1:1)` - Chapter 1, Verse 1, Word 1, Segment 1
- `(2:255:10:3)` - Chapter 2 (Al-Baqarah), Verse 255 (Ayat al-Kursi), Word 10, Segment 3

### Segments
Words are often split into morphological segments:
- Prefixes: `bi+` (ب), `wa+` (و), `Al+` (ال)
- Suffixes: `+ka` (ك), `+hum` (هم), `+nA` (نا)

---

## 📖 Usage Examples

### Example 1: Analyzing Verse (1:1) "Bismillah..."

**Word 1:** بِسْمِ (bis'mi - "in the name")
```
Location: (1:1:1)
Morphology: bi+ POS:N LEM:{som ROOT:smw M GEN
  - Segment 1: bi+ (preposition "in/with")
  - Segment 2: ism (noun "name", genitive case)
Dependencies:
  - (1:1:1) → (1:1:1) [gen] "prepositional phrase"
  - (1:1:2) → (1:1:1) [poss] "possessive (of Allah)"
```

**Word 2:** ٱللَّهِ (Allah)
```
Location: (1:1:2)
Morphology: POS:PN LEM:{ll~ah ROOT:Alh GEN
  - Proper noun, genitive case
Named Entity: CON:allah
Dependencies:
  - (1:1:2) → (1:1:1) [poss] "Allah modifies 'name'"
  - (1:1:3) → (1:1:2) [adj] "ar-Rahman modifies Allah"
```

### Example 2: Finding All Occurrences of a Root

To find all words from root "س م و" (smw - "name"):
```bash
grep "ROOT:smw" quranic-corpus-morphology-full.txt
```

### Example 3: Extracting Dependency Patterns

To find all subject-verb relationships:
```bash
grep "subj" quranic-corpus-dependencies-full.txt
```

---

## 🔤 Encoding & Transliteration

### Buckwalter Transliteration Table

| Arabic | Buckwalter | Name |
|--------|------------|------|
| ا | A | alif |
| ب | b | ba |
| ت | t | ta |
| ث | v | tha |
| ج | j | jim |
| ح | H | ha |
| خ | x | kha |
| د | d | dal |
| ذ | * | dhal |
| ر | r | ra |
| ز | z | zay |
| س | s | sin |
| ش | $ | shin |
| ص | S | sad |
| ض | D | dad |
| ط | T | ta |
| ظ | Z | za |
| ع | E | ayn |
| غ | g | ghayn |
| ف | f | fa |
| ق | q | qaf |
| ك | k | kaf |
| ل | l | lam |
| م | m | mim |
| ن | n | nun |
| ه | h | ha |
| و | w | waw |
| ي | y | ya |
| ء | ' | hamza |
| أ | > | hamza on alif |
| إ | < | hamza under alif |
| ئ | } | hamza on ya |
| ؤ | & | hamza on waw |

**Diacritics:**
| Arabic | Buckwalter | Name |
|--------|------------|------|
| َ | a | fatha |
| ُ | u | damma |
| ِ | i | kasra |
| ّ | ~ | shadda |
| ْ | o | sukun |
| ً | F | tanwin fatha |
| ٌ | N | tanwin damma |
| ٍ | K | tanwin kasra |

---

## 📚 Documentation & Resources

### Official Resources
- **Website:** [corpus.quran.com](https://corpus.quran.com)
- **Documentation:** [corpus.quran.com/documentation](https://corpus.quran.com/documentation)
- **Dependency Relations:** [corpus.quran.com/documentation/syntaxrelation.jsp](https://corpus.quran.com/documentation/syntaxrelation.jsp)
- **Grammar Guide:** [corpus.quran.com/documentation/grammar.jsp](https://corpus.quran.com/documentation/grammar.jsp)

### Academic Papers
- Dukes, K., & Buckwalter, T. (2010). "A Dependency Treebank of the Quran using Traditional Arabic Grammar"
- Dukes, K., Atwell, E., & Habash, N. (2013). "Supervised Collaboration for Syntactic Annotation of Quranic Arabic"

### License
- **GNU General Public License v3**
- Copyright © Kais Dukes, 2009-2017
- Maintained by [quran.com](https://quran.com) team

---

## 🛠 Data Processing Tools

### Extraction Tools (included)
- `parse_syntax_file.py` - Parse syntax.txt to extract dependencies
- `scrape_arabic_syntax.py` - Scrape Arabic grammar labels
- `scrape_corpus_concepts.py` - Scrape concept mappings

### Source Archive
- Original data source: `quranicarabiccorpus.war` (269MB)
- Downloaded from: [archive.org/details/quranicarabiccorpus](https://archive.org/details/quranicarabiccorpus)
- Extracted to: `extracted-war/`

---

## 📊 Statistics

### Coverage
- **Chapters:** 114 (complete Quran)
- **Verses:** 6,236
- **Words:** 77,429
- **Morphological segments:** ~128,000

### Annotations
- **Dependency relationships:** 37,420
- **Named entities:** 5,494
- **Unique lemmas:** 1,593
- **Pause marks:** 4,359

### Annotation Completeness
- ✅ **Morphology:** 100% (all 77,429 words)
- ⚠️ **Syntax/Dependencies:** ~14% (11,000 words manually annotated)
- ✅ **Named Entities:** 100%
- ✅ **Pause Marks:** 100%

---

## 📝 Version History

- **v0.4** (2011) - Current version
  - Complete morphological analysis
  - Partial syntactic annotation (11,000 words)
  - Full named entity annotation
  - Full pause mark annotation

---

## 🙏 Credits

**Quranic Arabic Corpus Team:**
- Dr. Kais Dukes (University of Leeds) - Project Lead
- Dr. Eric Atwell (University of Leeds)
- Tim Buckwalter - Morphological Analyzer
- Maintained by [quran.com](https://quran.com) team

**Data Extraction:**
- Extracted and formatted by Claude (Anthropic)
- Date: November 2025

---

## 📧 Contact & Support

For questions about the original corpus:
- Visit: [corpus.quran.com/feedback.jsp](https://corpus.quran.com/feedback.jsp)
- Message Board: [corpus.quran.com/messageboard.jsp](https://corpus.quran.com/messageboard.jsp)

---

**Last Updated:** November 6, 2025
**Dataset Version:** 0.4
**Format Version:** 1.0
