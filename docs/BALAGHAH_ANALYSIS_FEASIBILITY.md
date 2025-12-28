# Balaghah Analysis Feasibility Assessment

**Date:** 2025-11-10
**Status:** Data Inventory Complete

## Current Data Available

### 1. Morphology Data (`morphology_aligned.json`)
**77,429 words** with following fields:

#### Per-word structure:
```json
{
  "location": {"chapter": 67, "verse": 23, "word": 1},
  "surface_tanzil": "قُلْ",
  "surface_corpus": "قُلْ",
  "morphology": {
    "root": "قول",
    "lemma": "قالَ",
    "pos": "V",
    "features": {...}
  }
}
```

#### POS Tags Available:
- **V** - Verb
- **N** - Noun
- **P** - Particle

#### Features by POS Type:

**Verbs (V):**
- `tense`: IMPV (imperative), PERF (perfect), IMPF (imperfect)
- `verb_form`: 1-10 (Arabic verb forms/measures)
- `person`: 1, 2, 3
- `gender`: M, F
- `number`: S (singular), D (dual), P (plural)
- `root`: Arabic root (3-4 letters)
- `lemma`: Dictionary form
- `category`: Verb subcategory

**Nouns (N):**
- `case`: NOM, ACC, GEN
- `definiteness`: DEF (definite), INDEF (indefinite)
- `person`: 1, 2, 3 (for pronouns)
- `gender`: M, F
- `number`: S, D, P
- `root`: Arabic root
- `lemma`: Dictionary form
- `category`: PRON, PN (proper noun), REL (relative), etc.

**Particles (P):**
- `category`: CONJ (conjunction), P (preposition), DET (determiner)
- `person`: (for attached pronouns)
- `gender`: (for attached pronouns)
- `number`: (for attached pronouns)
- `lemma`: Base form

### 2. Dependency Data (`dependencies_full.json`)
**37,420 relations** with structure:
```json
{
  "child": {"chapter": 1, "verse": 1, "word": 1, "segment": null},
  "parent": {"chapter": 1, "verse": 1, "word": 2, "segment": null},
  "relation": {
    "code": "OBJ",
    "arabic": "مفعول به",
    "english": "object"
  }
}
```

#### Relation Types (47 total):
- Subject, Object, Predicate
- Adjective, Possessive, Apposition
- Prepositional phrase, Adverbial
- Conjunction, Coordinating
- And 37+ more...

### 3. Named Entities (`named_entities_full.json`)
**5,494 entities** - Semantic concepts (Allah, prophets, places, etc.)

### 4. Pause Marks (`pause_marks.json`)
**4,359 marks** - Tajweed pause annotations

---

## ✅ FEASIBLE ANALYSES (With Current Data)

### **Tier 1: Already Implemented**
1. ✅ **Saj' (Rhymed Prose)** - Phonetic ending patterns
2. ✅ **Takrar - Word Repetition** - Exact word matches
3. ✅ **Takrar - Root Repetition** - Same root across verse
4. ✅ **Takrar - Lemma Repetition** - Same lemma across verse
5. ✅ **Takrar - Structural Patterns** - POS sequence repetition
6. ✅ **Takrar - Positional Root Patterns** - Root at specific position
7. ✅ **Jinas (Paronomasia)** - Sound similarity detection

### **Tier 2: Easy to Implement (POS + Features)**

#### A. **Iltifat Detection (Grammatical Shift)**
**Feasibility:** ✅ **HIGH**
- Data needed: `person`, `number`, `tense` from features
- Implementation:
  ```python
  def detect_iltifat(verse_sequence):
      """
      Detect sudden shifts in:
      - Person: 3rd → 2nd (talking about → to)
      - Number: Singular → Plural
      - Tense: Past → Present
      """
      shifts = []
      for i in range(len(verse_sequence) - 1):
          prev_person = get_dominant_person(verse_sequence[i])
          curr_person = get_dominant_person(verse_sequence[i+1])

          if prev_person != curr_person:
              shifts.append({
                  'type': 'person_shift',
                  'from': prev_person,
                  'to': curr_person,
                  'verses': [i, i+1]
              })
      return shifts
  ```
- **Example:** Surah Yusuf shifts between 1st, 2nd, 3rd person narration

#### B. **Verb Form Distribution Analysis**
**Feasibility:** ✅ **HIGH**
- Data needed: `verb_form` (VF:1 to VF:10)
- Implementation:
  ```python
  def analyze_verb_forms(chapter):
      """
      Analyze distribution of 10 Arabic verb forms

      VF:1 - Basic action (فَعَلَ)
      VF:2 - Intensification (فَعَّلَ)
      VF:4 - Causative (أَفْعَلَ)
      etc.
      """
      form_counts = Counter()

      for word in chapter:
          if word['pos'] == 'V':
              vf = word['features'].get('verb_form')
              if vf:
                  form_counts[f'VF:{vf}'] += 1

      return {
          'distribution': form_counts,
          'predominant': form_counts.most_common(1)[0],
          'intensity_ratio': form_counts['VF:2'] / total_verbs  # Intensification
      }
  ```
- **Rhetorical Significance:** Choice of verb form affects intensity, causation

#### C. **Sentence Type Classification (Khabar vs Insha')**
**Feasibility:** ✅ **HIGH**
- Data needed: `pos`, `tense`, first word analysis
- Implementation:
  ```python
  def classify_sentence_type(verse):
      """
      Khabar (خبر): Informative (can be true/false)
      Insha' (إنشاء): Performative (command, question, etc.)
      """
      first_word = verse[0]

      # Imperative → Command (Insha')
      if first_word['features'].get('tense') == 'IMPV':
          return {'type': 'insha', 'subtype': 'command'}

      # Starts with verb → Verbal sentence (often Khabar)
      elif first_word['pos'] == 'V':
          return {'type': 'khabar', 'form': 'verbal'}

      # Starts with noun → Nominal sentence (Khabar)
      elif first_word['pos'] == 'N':
          return {'type': 'khabar', 'form': 'nominal'}

      # Question particles → Interrogative (Insha')
      elif first_word['surface'] in ['أ', 'هل', 'ما', 'من']:
          return {'type': 'insha', 'subtype': 'interrogative'}
  ```

#### D. **Gender/Number Agreement Patterns**
**Feasibility:** ✅ **HIGH**
- Data needed: `gender`, `number` from features
- Implementation:
  ```python
  def analyze_gender_number_patterns(verse):
      """
      Detect shifts in gender/number that indicate:
      - Masculine plural for mixed groups
      - Feminine singular for abstract concepts
      - Number shifts for emphasis
      """
      gender_dist = Counter()
      number_dist = Counter()

      for word in verse:
          if 'gender' in word['features']:
              gender_dist[word['features']['gender']] += 1
          if 'number' in word['features']:
              number_dist[word['features']['number']] += 1

      return {
          'gender': gender_dist,
          'number': number_dist,
          'has_dual': 'D' in number_dist  # Dual is rhetorically marked
      }
  ```

#### E. **Definiteness Patterns**
**Feasibility:** ✅ **HIGH**
- Data needed: `definiteness` (DEF/INDEF)
- Implementation:
  ```python
  def analyze_definiteness_patterns(verse):
      """
      Definite (ال) vs Indefinite

      Rhetorical implications:
      - Definite → Known, specific
      - Indefinite → Generic, emphasis on quality
      """
      pattern = []
      for word in verse:
          if word['pos'] == 'N':
              def_status = word['features'].get('definiteness', 'UNK')
              pattern.append(def_status)

      # Detect INDEF → DEF shifts (tanwin → alif-lam)
      return {
          'pattern': pattern,
          'def_count': pattern.count('DEF'),
          'indef_count': pattern.count('INDEF')
      }
  ```

### **Tier 3: Medium Complexity (Requires Dependencies)**

#### F. **Word Order Analysis (Taqdim wa Ta'khir)**
**Feasibility:** ✅ **MEDIUM** (needs dependencies loading)
- Data needed: Dependency relations (subject, object, verb)
- Challenge: Need to load and integrate `dependencies_full.json`
- Implementation:
  ```python
  def detect_word_advancement(verse_deps):
      """
      Normal Arabic: VSO (Verb-Subject-Object)

      Deviations:
      - OVS → Object advanced (restriction/qasr)
      - SVO → Subject advanced (emphasis)
      """
      obj_relations = [r for r in verse_deps if r['relation']['code'] == 'OBJ']
      subj_relations = [r for r in verse_deps if r['relation']['code'] == 'SUB']

      for obj_rel in obj_relations:
          obj_pos = obj_rel['child']['word']
          verb_pos = obj_rel['parent']['word']

          if obj_pos < verb_pos:
              return {
                  'type': 'object_advancement',
                  'rhetorical_effect': 'restriction (qasr)',
                  'positions': [obj_pos, verb_pos]
              }
  ```
- **Example:** إِيَّاكَ نَعْبُدُ (1:5) - Object "You" advanced before verb

#### G. **Syntactic Parallelism (Muqabala)**
**Feasibility:** ✅ **MEDIUM**
- Data needed: Dependency patterns across verses
- Implementation:
  ```python
  def detect_syntactic_parallelism(verse1_deps, verse2_deps):
      """
      Same syntactic structure + different content = Parallelism
      Same structure + opposite content = Muqabala (antithetical parallelism)
      """
      pattern1 = extract_dependency_pattern(verse1_deps)
      pattern2 = extract_dependency_pattern(verse2_deps)

      if pattern1 == pattern2:
          # Check if roots are antonyms
          if has_opposite_roots(verse1, verse2):
              return {'type': 'muqabala', 'structure': pattern1}
          else:
              return {'type': 'parallelism', 'structure': pattern1}
  ```

#### H. **Emphasis Marker Detection**
**Feasibility:** ✅ **MEDIUM**
- Data needed: `category` for إنّ family, `lemma` for قد
- Implementation:
  ```python
  def detect_emphasis_level(verse):
      """
      Ibtida'i (ابتدائيّ): No emphasis
      Talabi (طلبيّ): Single emphasis (إنّ, قد, ل)
      Inkari (إنكاريّ): Multiple emphasis + oath
      """
      emphasis_count = 0

      for word in verse:
          # إنّ family particles
          if word['features'].get('family') == 'إِنّ':
              emphasis_count += 1
          # قد with perfect verb
          if word['lemma'] == 'قد' and next_word_tense == 'PERF':
              emphasis_count += 1
          # Oath particles (و, ت)
          if word['surface'] in ['وَ', 'تَ'] and word['category'] == 'OATH':
              emphasis_count += 2

      if emphasis_count == 0: return 'ibtida\'i'
      elif emphasis_count == 1: return 'talabi'
      else: return 'inkari'
  ```

---

## ❌ NOT FEASIBLE (Missing Data)

### **Semantic/Pragmatic Analysis**

#### 1. **Majaz 'Aqli (Rational Trope)**
**Feasibility:** ❌ **LOW**
- **Missing:** Animacy information, semantic roles
- **Why:** Need to know if subject can logically perform action
- **Example:** "The day makes children white-haired" - Need semantic database

#### 2. **Isti'arah (Metaphor) Detection**
**Feasibility:** ❌ **LOW**
- **Missing:** Conceptual mappings, semantic fields
- **Why:** Requires understanding of which domains map to which

#### 3. **Kinayah (Metonymy) Detection**
**Feasibility:** ❌ **LOW**
- **Missing:** Cultural/pragmatic knowledge
- **Example:** "He has wide hands" = generous (needs cultural database)

#### 4. **Wasl/Fasl (Conjunction/Disjunction) Classification**
**Feasibility:** ❌ **LOW**
- **Missing:** Semantic similarity measures between verses
- **Why:** Requires understanding semantic relatedness beyond syntax

#### 5. **Ijaz (Brevity) vs Itnab (Elaboration)**
**Feasibility:** ❌ **LOW**
- **Missing:** Expected vs actual length benchmarks
- **Why:** Requires stylistic norms database

---

## 📊 Implementation Priority Recommendation

### **Phase 1: Quick Wins** (1-2 days)
1. ✅ Iltifat detection (person/number/tense shifts)
2. ✅ Verb form distribution analysis
3. ✅ Sentence type classification
4. ✅ Definiteness pattern analysis

### **Phase 2: Medium Effort** (3-5 days)
5. ⚠️ Load dependencies data
6. ⚠️ Word order analysis (taqdim/ta'khir)
7. ⚠️ Syntactic parallelism detection
8. ⚠️ Emphasis marker detection

### **Phase 3: Future Work** (requires new data)
9. ❌ Semantic analysis (majaz, isti'arah, kinayah)
10. ❌ Pragmatic analysis (wasl/fasl)
11. ❌ Stylistic analysis (ijaz/itnab)

---

## 🎯 Recommended Next Step

**Focus on Tier 2 (Easy Wins):**

Start with **Iltifat Detection** because:
1. ✅ Data already available (person, tense in features)
2. ✅ High rhetorical significance in Quran
3. ✅ Clear implementation path
4. ✅ Interesting results for users

Then add:
- Verb form distribution (shows intensity patterns)
- Sentence type classification (shows discourse structure)
- Definiteness patterns (shows specificity/generality)

**Output:** `balaghah_tier2.json` with 4 new analysis types

---

## 💾 Data Integration Needed

To enable Tier 3 analyses, we need:
```python
# Load dependencies alongside morphology
def load_dependencies():
    deps = json.load(open('data/linguistic/dependencies_full.json'))
    # Build lookup: (chapter, verse) -> [relations]
    # Integrate with morphology data
```

This would unlock:
- Word order analysis
- Syntactic parallelism
- Subject-verb agreement patterns
- Prepositional phrase analysis
