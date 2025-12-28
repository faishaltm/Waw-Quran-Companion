# Balaghah Analysis Guide for LLM (Streamlined)

**TARGET AUDIENCE**: General readers with no Arabic or linguistic background

**CORE PRINCIPLES**:
1. Guide discovery through internal reasoning, then explain clearly
2. Focus on WHY devices work, not templates
3. Use accessible language
4. Connect rhetoric to meaning
5. Show how devices work together (synthesis, not lists)

---

## FOUNDATIONAL CONCEPT: Unity and Coherence (Munasabat)

**The Quran is a unity** - verses cannot be understood in isolation. Balaghah devices work **together** to create unified meaning.

**Five levels of relationship:**
1. Within a single verse (micro-coherence)
2. Between beginning and end of verse
3. Between verses within a chapter (meso-coherence)
4. Between similar verses in different chapters
5. Between opening and closing of a chapter (macro-coherence)

**Three branches work as one integrated system:**
- **Ilm al-Ma'ani**: Meaning/context (word order, sentence types, definiteness)
- **Ilm al-Bayan**: Figures of speech (metaphors, similes)
- **Ilm al-Badi'**: Embellishment (saj', jinas, parallelism)

---

## JSON DATA STRUCTURE

### Top-Level
```json
{
  "chapter": 68,
  "verse_start": 1,
  "verse_end": 5,
  "metadata": {
    "chapter_number": 68,
    "name_arabic": "ٱلْقَلَمِ",
    "revelation_place": "makkah",
    "revelation_order": 2,
    "section_headings": {
      "1-7": "Excellence of the Prophet",
      "8-16": "Warning About the Deniers"
    }
  },
  "verses": [...]
}
```

**Section Headings** show thematic architecture - use this first to understand:
- How verses are grouped into thematic sections
- Narrative flow from beginning to end
- Where your extraction range fits
- Rhetorical progression

### Each Verse
```json
{
  "verse_number": 2,
  "text": "مَآ أَنتَ بِنِعْمَةِ رَبِّكَ بِمَجْنُونٍۢ",
  "translation_en": "You are not, by the favor of your Lord, a madman.",
  "analysis": "This verse is discussing 'Defense of the Prophet' that is positioned verse 2 of 3...",
  "key_words": "Divine grace, negation of madness",
  "root_repetitions": {...},
  "balaghah": {...}
}
```

**Root Repetitions Format:**
- **First occurrence**: Full verse text, translation, and section heading shown
- **Subsequent occurrences**: Simple note referencing where first mentioned
- Use `other_verses` data to trace thematic threads across sections

---

## BALAGHAH DEVICES

### 1. Saj' (سجع) - Rhyme and Rhythm

Phonetic endings creating auditory patterns that reinforce meaning through sound.

**Data:**
```json
"saj": {
  "pattern": "ن",
  "sequence_length": 3,
  "position_in_sequence": 1
}
```

**Key Principle**: In Quran, sound follows meaning (not vice versa). The ending serves the message.

**Phonetic Classifications:**

| Letter | Type | Quality | Typical Themes | Effect |
|--------|------|---------|----------------|--------|
| ن، م | Nasal | Soft, resonant | Mercy, comfort, reflection | Soothing, contemplative |
| ا (alif) | Long vowel | Flowing, expansive | Eternity, cosmos, vastness | Extension, psychological distance |
| ق، د، ت، ك | Plosive | Harsh, abrupt | Punishment, warning, judgment | Shock, urgency, awe |
| س، ص، ح | Fricative | Hissing, breathy | Secrets, Satan's whispers | Insidious, lingering |
| ر | Rolled | Vibrating | Movement, active scenes | Dynamic, energetic |

**Analysis approach:**
1. Identify ending letter → Classify phonetically
2. Check sequence_length → Find other verses in sequence
3. Verify phonetic quality matches verse content
4. Note if pattern breaks signal thematic transition

**Chronological context:**
- Early Meccan: Elaborate, varied saj' (sophisticated audience)
- Medinan: Simple -ūn/-īn patterns (clarity over artistry)

---

### 2. Root Repetitions (تكرار الجذور)

Same Arabic root appearing in multiple verses, creating thematic and phonetic connections.

**Data:**
```json
"root_repetitions": {
  "خلق": {
    "first_occurrence_in_extraction": true,
    "lemmas": ["خُلُق"],
    "total_occurrences_in_chapter": 2,
    "translations": ["character, nature"],
    "other_verses": [
      {
        "verse": 4,
        "text": "وَإِنَّكَ لَعَلَىٰ خُلُقٍ عَظِيمٍۢ",
        "translation": "And indeed, you are of a great moral character.",
        "section_heading": "Excellence of Character"
      }
    ]
  }
}
```

**Why it matters:**
- Thematic cohesion across verses
- Phonetic echo beyond rhyme
- Section headings reveal how roots develop through themes

**Analysis approach:**
1. Read FULL verse text and translation in `other_verses`
2. Compare section headings to see thematic progression
3. Analyze lemma variations for different facets
4. Trace arc: how does concept develop across verses?

---

### 3. Verb Forms (الأوزان)

Arabic's 10 (or 15) verb forms where morphological pattern carries semantic meaning.

**Common Forms:**
- Form I (فَعَلَ): Basic action
- Form II (فَعَّلَ): Intensive/causative
- Form III (فَاعَلَ): Reciprocal/attempt
- Form IV (أَفْعَلَ): Causative
- Form V (تَفَعَّلَ): Reflexive of II
- Form VIII (اِفْتَعَلَ): Reflexive
- Form X (اِسْتَفْعَلَ): Seeking/requesting

**Analysis approach:**
- Why THIS form? (causative/intensive/reflexive meaning)
- What does it reveal about agency and theological implications?
- Does English translation capture the form's nuance?

---

### 4. Definiteness (التعريف والتنكير)

Choice between definite (ال) and indefinite carries semantic weight.

**Definite (معرفة)**: Specific, known, unique entity
**Indefinite (نكرة)**: General, new information, emphasis on quality

**Patterns:**
- DEF → DEF: Narrative tracking
- INDEF → DEF: Classic introduction
- INDEF → INDEF: Emphasizing generality
- All INDEF: Highlighting quality over identity

---

### 5. Sentence Types (الخبر والإنشاء)

**Khabar (خبر)** - Declarative: Provides information
- **Verbal** (VSO): Action-focused
- **Nominal** (SVO): Entity/state-focused

**Insha' (إنشاء)** - Performative: Creates reality, moves to action
- **Command**, **question**, **wish**, **oath**

---

### 6. Jinas (جناس) - Phonetic Wordplay

Words with phonetic similarity but semantic distinction.

**Types:**
1. **Jinas tam**: Identical sound, different meaning (rare)
2. **Jinas ishtiqaq**: Same root, different forms (most common)
3. **Jinas muharraf**: Minor phonetic shift

**Purpose**: Mnemonic aid, semantic linking, intellectual engagement

---

### 7. Iltifat (التفات) - Grammatical Shifts

Deliberate shifts in person, tense, or number.

**Types:**
- Person shift (3rd ↔ 2nd ↔ 1st)
- Tense shift (perfect ↔ imperfect ↔ imperative)
- Number shift (singular ↔ plural)

**Purpose**: Renews attention, creates intimacy, emphasizes transitions

---

### 8. Wasl/Fasl (الوصل والفصل) - Conjunction/Disjunction

**Wasl**: Sentences connected with و، ف، ثُمَّ
- Indicates continuation, sequence, causality

**Fasl**: Sentences separated without connectors
- Indicates contrast, emphasis, rhetorical break

---

### 9. Muqabala (المقابلة) - Parallel Contrasts

Complex parallel structures with multiple contrasting elements.

**Critical analysis questions:**
1. **Semantic opposition check**: Do translations show TRUE opposition (not mere difference)?
2. **Parallel element analysis**: Does each POS pair show meaningful contrast?
3. **False positive detection**: Would this be noteworthy in classical balagha?

**Rhetorical purposes:**
- Highlighting contrast
- Demonstrating completeness
- Showing balanced rewards/punishments

---

### 10. Isti'anaf (الاستئناف) - Rhetorical Resumption

Independent sentence resuming/re-emphasizing previous statement.

**Indicators:**
- No conjunction (related to fasl)
- Shares thematic roots with previous sentence
- Provides elaboration or emphasis

---

### 11. Hadhf (الحذف) - Ellipsis

Deliberate omission of grammatical elements.

**Types:**
- Omitted object (transitive verb without expressed object)
- Omitted predicate (nominal sentence missing predicate)
- Omitted subject (less common)

**Purposes:**
- Brevity, emphasis, generalization, known context, dramatic effect

---

### 12. Qasam (القسم) - Oath

Allah swears by creations to emphasize truths.

**Recognition:**
- Particle و or ب followed by definite noun/natural phenomenon
- Often at surah opening
- Translation shows "By the..."

**Purposes:**
- Magnifying what's sworn by
- Drawing attention to signs
- Emphasizing truth
- Thematic connection

---

### 13. Muqatta'at (الحروف المقطعة) - Disjointed Letters

Mysterious letter combinations opening 29 surahs.

**Recognition:**
- Always verse 1, word 1
- Single letter or combination standing alone
- Translation shows letter names

**Functions:**
- Mystery and transcendence
- Attention-grabbing device
- Challenge to Arabs (using same letters, can't produce similar)

**Critical**: Don't invent meanings - acknowledge scholarly disagreement. Focus on rhetorical function.

---

### 14. Interrogative Particles (أدوات الاستفهام)

Common particles: هل، أ، ما، من، متى، أين، كيف، كم، أي

**Functions:**
- Rhetorical questions (making statements)
- Engagement
- Challenge
- Emphasis
- Prompting reflection

---

### 15. Restriction Particles (أدوات الحصر)

**إنما (innama)**: "Only" - exclusive restriction
**ما...إلا (mā...illā)**: "Not...except" - exception pattern

**Functions**: Exclusivity, emphasis, negation, clarification

---

### 16. Emphasis Particles (أدوات التأكيد)

**إن / أن (inna/anna)**: "Indeed, verily"
**لَ (lam)**: Emphatic prefix
**قد (qad)**: "Indeed, already, certainly"
**لقد (laqad)**: Maximum emphasis

**Purpose**: Assertion, counter-argument, highlighting critical messages

---

### 17. Named Entities (المفاهيم المسماة)

Identified concepts marking semantic significance: allah, prophet names, cosmic entities, theological concepts, locations

**Use**: Track thematic emphasis, identify main subjects

---

### 18. Pause Marks (علامات الوقف)

Markers for recitation: مـ، لا، ج، ز، صلى، قلى

**Significance**: Guide phrasing, affect meaning disambiguation, create rhythmic units

---

## ADVANCED DEVICES (Require LLM Semantic Analysis)

### Taqdim/Ta'khir (التقديم والتأخير) - Word Order Variation

Deviation from expected Arabic orders (VSO for verbal, SVO for nominal).

**Rhetorical purposes:**
- **Qasr (القصر)**: Restriction to specific entity
- **Ta'zim (التعظيم)**: Glorification of advanced element
- **Tawkid (التوكيد)**: Emphasis
- **Tashwiq (التشويق)**: Anticipation by delaying key info
- **Tamkin (التمكين)**: Preparation for important information

---

### Tibaq (الطباق) - Antithesis

Use of antonyms creating contrast.

**Types:**
- **Tibaq al-Ijab**: Both affirmative
- **Tibaq al-Salb**: One affirmed, one negated

**Opposition categories**: Sensory, Temporal, Existential, Evaluative, Spatial, Quantitative

**Functions:**
- Paradox/conflict
- Universality (merism)
- Complementarity
- Demonstrating divine power
- Clarification by contrast

---

### Tashbih (التشبيه) - Simile

Explicit comparison using particles.

**Four elements:**
1. **Tenor (المشبه)**: Thing being compared
2. **Vehicle (المشبه به)**: Thing compared to
3. **Ground (وجه الشبه)**: Shared quality
4. **Particle (أداة التشبيه)**: Marker (كَ، كَأَنَّ، مِثْلُ، شَبَهَ)

**Classifications by completeness:**
- **Mursal**: All 4 elements present
- **Mu'akkad**: Particle omitted
- **Mujmal**: Ground not stated
- **Mufassal**: Ground explicit
- **Baligh**: Particle AND ground omitted (most powerful)

**False positives**: كَذَٰلِكَ (demonstrative), كَيْفَ (interrogative) - NOT similes

---

### Isti'arah (الاستعارة) - Metaphor

Compressed simile where one element deleted, creating metaphorical identification. Literal meaning prevented by **qarīnah** (contextual clue).

**Types:**
1. **Tasrihiyyah (تصريحية)**: Vehicle stated, tenor deleted
2. **Makniyyah (مكنية)**: Vehicle deleted, only its characteristic mentioned

**Common Quranic metaphors:**
- Light/Darkness = Guidance/Misguidance
- Vegetation = Life/faith, Withering = Death/disbelief
- Path = Religion, Going astray = Disbelief
- Bonds = Covenants, Cutting = Violation
- Sight/Blindness = Understanding/Ignorance

---

### Majaz (المجاز) - Trope

Words used in non-literal senses based on relationships.

**Two categories:**

**1. Majaz Lughawi (مجاز لغوي)**: Single word figurative
- If based on resemblance → It's Isti'arah
- If based on other relationships → Majaz Mursal (causality, part/whole, container/contained, instrument/action, temporal, consideration of past/future state)

**2. Majaz 'Aqli (مجاز عقلي)**: Attributing action to non-agent (time, place, instrument instead of real agent)

---

### Kinayah (الكناية) - Metonymy

Indirect expression where literal meaning is **possible** but intended meaning is different. Both meanings coexist.

**Types:**
1. **Kinayah 'an sifah**: Indirectly expressing attribute
2. **Kinayah 'an mawsuf**: Indirectly referring to entity
3. **Kinayah 'an nisbah**: Indirectly attributing quality

**Common patterns:**
- Physical actions for psychological states ("turning away" = rejection)
- Body parts for qualities ("clean hands" = innocent)
- Spatial relations for status ("high place" = high status)
- Possessions for character ("closed hand" = stingy)

---

## ANALYSIS STRUCTURE: TWO SECTIONS ONLY

### SECTION 1: CHAPTER OPENING AND INTRODUCTION

**Four parts as flowing narrative prose (NO bullet points except basic facts):**

**Part 1: Surah Identity and Context** (1-2 paragraphs)
- Name, chapter number, verses
- Revelation place/order
- Historical period and audience
- Occasions if available

**Part 2-3: Surah's Message and Architecture** (2-4 paragraphs UNIFIED)
- Central theme or argument
- Rhetorical purpose
- Journey from beginning → end
- How section headings reveal thematic architecture
- Narrative arc through sections
- Major transitions

**Part 4: How Rhetoric Serves Message** (2-4 paragraphs)
- Overall tone and audience appropriateness
- Structural strategy
- General rhetorical approach (direct/indirect, logic/emotion)
- Integration of form and content

**❌ DO NOT include in Section 1:**
- Saj' patterns or phonetic classifications
- Root lists or occurrence counts
- Grammatical analysis or word order
- Device inventories
- Verse-specific examples
- Lists or bullet points

**Part 5: Divine Inimitability** (2-3 paragraphs)

Address these questions in narrative form:
1. **What is most astonishing about this surah's design?**
2. **What reveals this cannot be human composition?**

**CRITICAL: Every claim MUST be backed by specific verse references and concrete examples.**

Examine:
- **Impossible multidimensional integration**: Perfect phonetic + semantic + grammatical + theological alignment simultaneously
- **Prophetic impossibility**: Beyond 7th-century Arabian capacity
- **Impossible planning**: Coherence across piecemeal revelation timeline
- **Multi-dimensional precision**: Sound matches meaning, all alternatives fail, grammatical forms encode multiple truths
- **Sustained excellence**: No weak verses, consistent quality despite adverse circumstances

**Required Evidence Standards:**

Every statement must include:
1. **Specific verse numbers** - cite exactly which verses demonstrate the feature
2. **Concrete examples** - quote actual Arabic words or patterns
3. **Measurable impossibility** - show HOW it's beyond human capacity (not just assert it)
4. **Multiple dimensions** - demonstrate AT LEAST 2-3 dimensions working together

**CRITICAL: Do NOT force phonetic analysis**
- ❌ Do NOT analyze "phonetic progressions" or "internal rhymes" across multiple verses unless OBVIOUS and UNDENIABLE
- ❌ Do NOT claim "impossible convergence" based on similar-sounding word endings (e.g., kafur/zanjabil are NOT phonetically related)
- ❌ Do NOT force phonetic patterns where none exist
- ✓ Focus on CLEAR evidence: grammatical structures, semantic coherence, theological integration, structural design
- ✓ Exception: SAJ' patterns (verse-ending rhymes) are legitimate because they're systematic and obvious
- ✓ When in doubt about phonetic patterns, SKIP IT and focus on other dimensions

**Example of BAD analysis (no evidence):**
> "The surah accomplishes several goals that would normally conflict: terrify without despairing, promise without diminishing urgency, argue logically without becoming dry."

**Problems:**
- No verse references
- No concrete examples
- Generic statement (could apply to any surah)
- No demonstration of WHY these conflict or HOW they're resolved

**Example of GOOD analysis (with evidence):**
> "Verses 7-14 describe three groups using IDENTICAL grammatical structure (وَأَصْحَابُ...) but phonetically DIVERGENT saj' patterns: verse 8 ends with مَشْأَمَة (mīm), verse 9 with مَيْمَنَة (mīm), verse 11 breaks to مُقَرَّبُونَ (nūn). Acoustic hierarchy emerges—the muqarrabun literally SOUND different. The impossibility: verses 11-26 (muqarrabun description) maintain entirely different phonetic endings from verses 41-56 (companions of the left) while keeping thematic coherence. Planning this requires: (1) knowing all 56 verses in advance, (2) distributing phonetic patterns across non-adjacent sections, (3) ensuring semantic precision isn't sacrificed for sound. No piecemeal composition could achieve this—the architect must see the entire structure before placing the first word."

**What makes evidence strong:**
- ✓ Specific verses cited (7-14, 11-26, 41-56)
- ✓ Concrete Arabic examples (وَأَصْحَابُ, مَشْأَمَة, مُقَرَّبُونَ)
- ✓ Measurable impossibility (phonetic distribution across distant sections)
- ✓ Multiple dimensions (structure + phonetics + semantics)
- ✓ Shows WHY human can't do this (piecemeal revelation problem)

**Avoid:**
- ❌ Vague claims without verse numbers
- ❌ Generic statements applicable to any surah
- ❌ Assertions without demonstration
- ❌ Single-dimension observations

---

### SECTION 2: VERSE-BY-VERSE ANALYSIS

Analyze **EVERY VERSE SEQUENTIALLY** with the following structure:

**For each verse:**

#### VERSE [NUMBER]: [Arabic text]
**Translation:** [English]

**Core Analysis: 5 continuous narrative paragraphs**
**+ Word-Level Precision: 1-2 paragraphs** (when words show exceptional precision)
**+ Reflection: 1 paragraph** (Nouman Ali Khan-style life connection)

**Paragraph 1: Sonic Experience**

This is the ONLY paragraph where phonetic/sound analysis belongs. Do NOT repeat phonetic analysis in other paragraphs.

Analyze:
- Saj' ending letter(s) and phonetic character (harsh/soft/flowing/abrupt)
- Position in sequence pattern (verse X of Y in sequence)
- How the ending sound matches verse content
- What the listener experiences physically/emotionally when hearing this sound

**Phonetic analysis rules:**
- Keep it focused on the SAJ' ENDING only
- Explain how ending sound reinforces verse meaning
- Note if sound creates physical sensation (e.g., guttural constriction for punishment, flowing nasals for mercy)
- If part of sequence, note cumulative sonic effect
- If pattern breaks, note what thematic shift occurs

**What NOT to do:**
- ❌ Do NOT analyze consonant clusters within words (unless they're the saj' ending)
- ❌ Do NOT repeat phonetic observations in other paragraphs
- ❌ Do NOT give excessive phonetic detail beyond what serves rhetorical understanding
- ❌ Do NOT analyze every sound in the verse - ONLY the saj' pattern
- ❌ Do NOT force phonetic analysis on every word
- ❌ Do NOT analyze internal root consonants for "sound symbolism" unless OBVIOUS (like دُكَّتْ دَكًّا)

**Exception for obvious sound-meaning matches:**
Only analyze internal word phonetics if there's CLEAR onomatopoeia or sound mimicry:
- ✓ GOOD: دُكَّتْ دَكًّا (dukkat dakkan) - doubled kāf mimics percussive pounding of mountains to dust
- ✓ GOOD: صَرْصَر (sarsar - howling wind) - repeated sīn/rā' mimics wind sound
- ✗ BAD: "double repetition of و-ق-ع root with central emphatic qaf creates..." - this is forcing analysis

**Paragraph 2: Conceptual Threads Through Roots**

**SKIP these common roots** (too frequent, no thematic value):
- ك-و-ن (kāna - to be, was, is, become)
- ش-ي-ء (shay' - thing, something)

For EACH remaining root in this verse, you must:
1. **Read the complete context in `other_verses`**: Read the FULL Arabic text, English translation, and section heading
2. **Compare the two contexts**: How does the root function HERE vs. THERE?
   - Same lemma/form or different?
   - Same meaning or semantic shift?
   - What's the thematic context difference? (compare section headings)
3. **Explore the theological connection**: Why does Allah place this root in THESE specific locations?
   - What thread connects verse X (section A) to verse Y (section B)?
   - Is it contrast (showing opposites)?
   - Is it progression (developing a theme)?
   - Is it echo (reinforcing same point in different context)?
   - Is it irony (same root, opposite implications)?
4. **Avoid generic statements**: NEVER say things like "This demonstrates Arabic's rich homonymic potential" or "Arabic roots generate divergent meanings." These are filler. Instead, explain the SPECIFIC theological/rhetorical purpose of THIS root appearing in THESE exact verses.

**Example of BAD analysis:**
"The root م-ل-ك appears here as 'angels' and later as 'possess.' This demonstrates Arabic's rich homonymic potential where same trilateral root generates divergent meanings."

**Example of GOOD analysis:**
"The root م-ل-ك appears first in verse 4 as ٱلْمَلَٰٓئِكَةُ (angels ascending to Allah) within the section 'A Mocker Asks for Judgment Day,' then returns in verse 30 as مَلَكَتْ أَيْمَٰنُهُمْ (what their right hands possess) within 'Excellence of the Faithful.' This creates a divine-human parallel: angels possess no autonomy—they ascend only to Allah in pure servitude; the faithful possess (مَلَكَتْ) only what Allah has made lawful for them. Both uses encode proper relationship to authority: angels to divine command, believers to divine law. The root's journey from celestial messengers to earthly possession maps the surah's movement from cosmic judgment to human ethics, showing that true faith mirrors angelic submission—possessing only what's permitted, ascending through obedience."

**Required elements in your root analysis:**
- Full verse text comparison (read what's in `other_verses`)
- Section heading comparison (what themes are being connected?)
- Theological/rhetorical exploration (WHY these verses? What's the connection?)
- NO generic statements about Arabic language

**Paragraph 3: Grammatical Architecture**
- Verb forms and why chosen
- Definiteness patterns
- Sentence type and purpose
- Why these choices matter

**Paragraph 4: Advanced Rhetorical Layers** (when present)
- Iltifat, hadhf, muqabala, wasl/fasl, qasam, etc.
- Woven into narrative (not labeled)
- Semantic opposition verification for muqabala

**Paragraph 5: Unified Effect**

Synthesize how all elements work together to create the verse's rhetorical impact:
- How do roots + grammar + advanced features converge?
- What unified effect emerges from their integration?
- What would be lost if any element were changed?

**Important**:
- Do NOT repeat phonetic analysis here (that was in Paragraph 1)
- Do NOT repeat root analysis here (that was in Paragraph 2)
- Focus on SYNTHESIS showing how everything works as orchestrated system
- Show the convergence, not individual elements again

**Word-Level Precision** (when words demonstrate exceptional exactitude):

After 5-paragraph analysis, add **"Word-Level Precision:"** section with 1-2 paragraphs examining 2-4 specific words.

**CRITICAL: When `asbab_nuzul` data exists, you MUST analyze how word choices connect to the historical occasion.** This is often where the most astonishing precision appears.

**For each selected word, analyze:**

**1. Historical Context Connection (REQUIRED if asbab_nuzul exists)**
- Read the `asbab_nuzul` narrative carefully
- Identify specific details from the historical occasion (e.g., "rain down stones", "bring painful doom")
- Check if the word's **root meaning** directly echoes/responds to those details
- Example: Mocker asks for **stones to fall down** → Allah chooses وَاقِع from root و-ق-ع meaning "to **fall down**"
- Explain the irony, precision, or prophetic response encoded in the word choice
- Show how this connection is beyond human planning (mocker's specific words → Quranic word choice)

**2. Root Meaning and Etymology**
- What is the root (ثلاثي/رباعي)?
- What are core meanings from root data in `key_words` or `root_repetitions`?
- What semantic range does the root cover?
- How does etymology connect to verse function and historical occasion?

**3. Grammatical Form Precision**
- What grammatical form used (noun, verb, participle, infinitive)?
- Why THIS form rather than alternatives?
- What does the form encode theologically or rhetorically?
- Example: Active participle وَاقِع vs. future verb سَيَقَع vs. past verb وَقَعَ - why the participle?

**4. Phonetic-Semantic Matching** (ONLY for OBVIOUS onomatopoeia - RARE)
- **Default: SKIP THIS** - Most words don't need phonetic analysis
- Only analyze if there's CLEAR, UNDENIABLE sound-meaning mimicry
- Examples that qualify:
  - ✓ دُكَّتْ دَكًّا (dukkat dakkan) - doubled kāf mimics percussive pounding
  - ✓ صَرْصَر (sarsar) - repeated sīn/rā' mimics howling wind
  - ✓ قَصْقَصَ (qasqasa) - mimics cutting/clipping sound
- Examples that DON'T qualify (do NOT analyze):
  - ✗ "emphatic qaf in وَقَعَ creates sense of impact" - this is forcing
  - ✗ "flowing nasals in Rahman create softness" - speculative
  - ✗ "plosive sounds in باطل create harshness" - not obvious mimicry
- **When in doubt, SKIP phonetic analysis** - it's better to omit than to force

**5. Visual and Physical Imagery**
- Does the root evoke specific visual imagery?
- What physical sensations or actions does the word convey?
- How does concrete imagery make abstract concepts tangible?
- Does it create multi-sensory experience?

**6. Temporal/Theological Precision**
- Does the word collapse or transcend normal time categories?
- Does it encode divine perspective vs. human perspective?
- How does it capture theological truths that tenses cannot?
- Example: وَاقِع captures "already decreed (past) + currently inevitable (present) + definitely coming (future)" simultaneously

**7. Synonym Analysis - Why Alternatives Fail**
**First**, generate 2-4 possible Arabic synonyms using your knowledge:
- Common synonyms from the same semantic field
- Words with overlapping meanings but different connotations
- Alternative grammatical forms (different verb forms, noun types, etc.)

**Then**, analyze why EACH alternative fails:
- What aspect of meaning does it capture?
- What critical dimension does it LACK?
- How would it change/diminish the meaning?
- What theological, phonetic, grammatical, historical-contextual, or imagery features would be lost?

**8. Antonym Analysis** (if antonyms/parallelism present)
- What pairs of opposing words appear?
- How do roots of antonyms create semantic symmetry/asymmetry?
- Do grammatical forms mirror or contrast?
- How do phonetic qualities reinforce opposition?
- Why these specific antonym pairs chosen?

**Integration Format:**
Write as 1-2 flowing narrative paragraphs (NOT numbered lists). Start with historical context if `asbab_nuzul` exists, then weave in root meaning, grammatical form, phonetics, imagery, temporal precision, and synonym/antonym analysis.

---

## PRACTICAL LIFE CONNECTION (Nouman Ali Khan Approach)

After completing verse analysis (5 paragraphs + Word-Level Precision), add **"Reflection: Relevance to Our Lives"** section with 1 paragraph connecting linguistic/rhetorical features to practical modern life.

**Approach inspired by Nouman Ali Khan:**

### **Guiding Principles:**

**1. Grammatical Choices → Character Lessons**
- NOUN vs VERB → permanence vs temporariness (what attitude?)
- Passive vs Active → agency and reliance
- Definite vs Indefinite → mindset implications

**2. Word Choice → Human Psychology**
- Why THIS word not synonyms? What human tendency does it address?
- Root meaning revealing human nature?
- How does precision guide behavior/mindset?

**3. Rhetorical Features → Emotional Intelligence**
- Iltifat (shift) → what does intimacy/distance teach about relationships?
- Emphasis particles → what conviction needed?
- Hadhf (omission) → what self-awareness required?

### **Reflection Questions (NAK Style):**

**On Word Choices:**
- "Why did Allah choose THIS word vs [synonym]? What does that teach us about how we should think/act?"
- "What everyday situation does this word choice apply to in MY life?"

**On Grammar:**
- "Why noun/verb/participle? What attitude does this grammatical form cultivate?"
- "What would change if this were different grammatical form?"

**On Practical Application:**
- "When in my daily life do I encounter this situation?"
- "What specific behavior should change after understanding this precision?"
- "Can I give concrete modern example paralleling this verse's wisdom?"

### **Examples of Good Connection:**

**Ex 1: Alhamdulillah (Noun)**
> "Noun 'alhamd' over verb teaches permanent gratitude vs conditional thanking. You praise a beautiful car—don't thank it. You thank someone for a favor. But 'alhamdulillah' is both: recognizing Allah's perfection (praise) AND gifts (thanks). Noun form means it's not mood-dependent—it's a state of being. When your train is late but you catch it, 'alhamdulillah' emerges emotionally. This grammatical choice cultivates optimism and humility as permanent traits, not temporary reactions."

**Ex 2: Misran (settlement) - 2:61**
> "When Israelites complained, Allah used 'misran' echoing 'Misr' (Egypt), not 'baladan' (city): 'Go back to slavery if you want those foods!' Devastating irony confronting our amnesia about past pain. How often do we romanticize what we prayed to escape? The hated job seems appealing facing new challenges. Before complaining about current blessings, remember what you begged to leave. This single word mirrors ungrateful human psychology."

**Ex 3: Rahman/Rahim (Root ر-ح-م)**
> "Both from 'raham' (womb)—mother's unconditional love BEFORE mercy. In conflicts, we lead with justice ('they deserve consequences'). But Allah prioritizes love (Rahman) before specific mercy (Rahim). What if we started with intense care (like mother) BEFORE deciding who 'deserves' kindness? The word choice rewires our emotional priorities toward people."

### **Format:** 1 paragraph with:
1. Start with linguistic feature
2. Connect to universal human experience
3. Give concrete modern example
4. End with practical application

**Avoid:**
- ❌ Generic advice without connecting HOW linguistic feature teaches it
- ❌ Historical examples only - must connect to MODERN life
- ❌ Preaching - be reflective and psychological

---

## CRITICAL INSTRUCTIONS

**Sequential order**: Analyze verse 1, then 2, then 3... Never group or skip

**Synthesis over separation**: Show how devices work together

**Flow and progression**: Explain how each verse builds on previous

**Trace thematic arcs**: Follow roots through `other_verses` data

**Completeness**: Provide full, detailed analysis - do NOT truncate

**Continue across responses**: If reaching limit, stop at verse boundary, write "[ANALYSIS CONTINUES - Response limit reached. Please reply 'continue' to proceed with verse X]"

**Anti-redundancy**:
- Explain general patterns ONCE in Section 1
- In Section 2, only reference Section 1 patterns briefly

**No lists**: Write flowing narrative paragraphs

---

## CHRONOLOGICAL CONTEXT

**Meccan (86 surahs)**: Shorter verses, rich vocabulary, elaborate saj', dramatic tone, addresses "O mankind!"
**Medinan (28 surahs)**: Longer verses, simpler vocabulary, lower saj' frequency, explanatory tone, addresses "O believers!"

---

## INTEGRATION REMINDER

When analyzing verses, devices often overlap. Check for:
1. Taqdim/ta'khir (word order)
2. Tibaq (antonyms)
3. Tashbih (comparison particles)
4. Isti'arah (metaphorical impossibilities)
5. Majaz (figurative transfers)
6. Kinayah (indirect allusions)

Show how devices work together - don't list separately.
