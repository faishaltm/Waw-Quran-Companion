# Balaghah Analysis Guide for LLM (Concise Version)

**TARGET AUDIENCE**: General readers with no Arabic or linguistic background

**DELIVERY PRINCIPLES**:
1. **Guide discovery** - Use internal reasoning to uncover insights, then explain them clearly
2. **Focus on understanding** - Explain WHY devices work, not templates of WHAT to say
3. **Use accessible language** - Simplify without condescending
4. **Explain significance** - Connect rhetoric to meaning, not decoration to art
5. **Provide clear analysis** - Give coherent, well-reasoned interpretations based on scholarly thinking

---

## Core Analytical Framework: Holistic Interpretation

### **The Unity Principle (Munasabat المناسبات)**

**Foundational concept from Islamic scholarship:**
> "The content of the Qur'an is **a unity that cannot be separated** between one verse/letter and another" - Mannā' al-Qaṭṭān

**What this means for analysis:**
- Balaghah devices don't exist in isolation—they work **together** to create unified meaning
- A verse cannot be fully understood without examining its **relationships** to surrounding verses
- Context determines how rhetorical devices should be interpreted

### **Al-Munasabat: The Science of Coherence**

**Definition:** Al-Munasabat means "connection," "proximity," or "likeness"—the study of how Quranic elements relate and depend on each other.

**Five levels of relationship:**
1. **Within a single verse** - How devices work together (micro-coherence)
2. **Between beginning and end of verse** - Opening/closing relationship
3. **Between verses within a chapter** - Sequential development (meso-coherence)
4. **Between similar verses in different chapters** - Thematic echoes
5. **Between opening and closing of a chapter** - Surah unity (macro-coherence)

**Why it matters:**
> When an interpreter understands the Qur'an in the perspective of coherence, **'he cannot adopt anything except one single opinion regarding its meaning'**

### **Integrated vs Atomistic Analysis**

**❌ ATOMISTIC APPROACH (Avoid):**
- Devices listed separately with no synthesis, no context, no unified meaning
- This is **not balaghah analysis**—it's just data reporting

**✅ HOLISTIC APPROACH (Required):**
- Devices working together with connection to surrounding verses
- Unified rhetorical purpose with contextual meaning
- Synthesis showing how form serves function

### **Three Branches of Balaghah as Integrated System**

**1. Ilm al-Ma'ani (علم المعاني)** - Science of Meaning/Context
- Word order, sentence types, definiteness
- Clarity according to **audience and context**

**2. Ilm al-Bayan (علم البيان)** - Science of Figures of Speech
- Metaphors, similes, examples
- Making concepts **relatable**

**3. Ilm al-Badi' (علم البديع)** - Science of Embellishment
- Saj', jinas, parallelism
- **Choice of words and tone**

**Critical principle:**
> "When these three sciences are **merged**, it is the essence of balaghah"

**Do not analyze these separately**—show how they work together as one integrated system.

### **Contextual Analysis at Three Levels**

**Micro-level (Within Verse):**
- How do saj' + root repetitions + verb forms + definiteness **reinforce each other**?
- What **unified effect** do they create?
- How does phonetic quality **match semantic content**?

**Meso-level (Between Verses):**
- How does this verse connect to **previous/next verses**?
- Do root repetitions (check `other_verses` in `root_repetitions`) show **thematic development**?
- Do section headings reveal how verses are grouped into **thematic units**?
- Does the verse **build on**, **contrast with**, or **parallel** surrounding content?

**Macro-level (Surah/Thematic):**
- How does this verse fit the **surah's main theme**?
- Does it introduce, develop, or conclude a **thematic section**?
- How does it relate to **similar verses in other surahs**?

### **Presentation Format: Always Contextual**

**Your output should follow this structure:**

**1. Verse Context (Establish foundation)**
- Position in surah (early/middle/late)
- Surrounding verses (what comes before/after)
- Surah theme and this verse's role

**2. Integrated Analysis (Show synthesis)**
- Identify all devices present
- Explain how they work **together** to create unified effect
- Connect phonetics → semantics → context

**3. Inter-Verse Connections (Follow relationships)**
- Trace root repetitions (using `other_verses` data) to show thematic development
- Compare section headings to understand thematic architecture
- Note sequential relationships (verse before/after)
- Identify thematic threads across sections

**4. Unified Interpretation (Synthesize meaning)**
- What is the verse's **rhetorical purpose**?
- How do all elements serve that purpose?
- What does the reader/listener experience?

**Never present:**
- Device-by-device lists without synthesis
- Findings without context
- Analysis without showing relationships

**Always present:**
- Context → Devices working together → Relationships → Unified meaning

---

## How to Read the JSON Output

**Context-first design**: The output presents meaning before analysis, with section headings and root repetitions integrated into natural language narratives.

### Top-Level Structure:
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
    "verses_count": 52,
    "section_headings": {
      "1-7": "Excellence of the Prophet",
      "8-16": "Warning the Prophet About the Deniers"
    }
  },
  "verses": [...]
}
```

**CRITICAL - Section Headings in Metadata**: The `section_headings` dictionary provides the complete chapter structure. **Always use this first** to understand:
- The thematic architecture of the entire chapter
- How verses are grouped into thematic sections
- The narrative flow from beginning to end
- Where your extraction range fits in the bigger picture
- The chapter's rhetorical progression

### Each Verse Contains:
```json
{
  "verse_number": 2,
  "text": "مَآ أَنتَ بِنِعْمَةِ رَبِّكَ بِمَجْنُونٍۢ",
  "translation_en": "You are not, by the favor of your Lord, a madman.",
  "analysis": "This verse is discussing 'Defense of the Prophet' that is positioned verse 2 of 3...",
  "key_words": "Divine grace, negation of madness, prophetic defense",
  "root_repetitions": {...},
  "balaghah": {...}
}
```

### Integrated Format Features:

**1. Section Headings (Rhetorical Architecture)**
- Integrated into the `analysis` narrative with positioning information
- Format: "This verse is discussing '{heading}' that is positioned verse {X} of {Y}."
- **No separate `section_heading` field** - all context is in the narrative

**2. Root Repetitions with Contextual Information**
- For **first occurrence** in extraction range: Full verse text, translation, and section heading shown
- For **subsequent occurrences**: Simple note referencing where it was first mentioned
- Integrated into `analysis` narrative with natural language
- Also available as structured data in `root_repetitions` field

**3. Thematic Architecture Analysis**
Using section headings, you can understand:
- **Verse position within theme**: "verse 2 of 3" tells you this is the middle verse developing a theme
- **Thematic boundaries**: When section heading changes, a new theme begins
- **Micro-coherence**: Verses within same section share thematic unity
- **Rhetorical development**: Track how argument/narrative progresses through sections

**4. Root Repetitions as Thematic Connectors**
The `analysis` field includes contextual root repetitions showing:
- **Semantic connection**: Same root links related concepts
- **Cross-verse coherence**: Roots create thematic threads
- **Contextual meaning**: Full verse text helps understand the connection
- **Section awareness**: Section headings show thematic relationship

---

## Balaghah Devices

### 1. Saj' (سجع) - Rhyme and Rhythm

**Essence**: Phonetic endings (fāṣilah/fawāṣil) that create auditory patterns while carrying semantic weight. Research shows these endings are "semantically-oriented"—not merely ornamental, but actively reinforcing meaning through sound.

**Data Structure:**
```json
"saj": {
  "pattern": "ن",
  "sequence_length": 3,
  "position_in_sequence": 1
}
```

#### **Core Principles**

**Phonetic vs. Semantic**: Classical scholars (al-Rummānī) distinguished Quranic **fāṣilah** from ordinary saj' by arguing that in poetry, meaning follows sound, but in the Quran, **sound follows meaning**. The rhyme serves the message, not vice versa.

**Cognitive function**: Research shows rhythmic patterns enhance verbal memory formation. Repetition of phonetic endings creates "retrieval cues"—when you hear one verse's ending, it primes recall of the next.

**Sound symbolism**: The Quran employs phonetic structure to mirror meaning. Harsh sounds accompany warnings; soft sounds accompany mercy. The ending isn't just decoration—it's **part of the message**.

#### **Phonetic Classification of Endings**

Different consonant and vowel endings create distinct rhetorical effects.

##### **1. Nasal Consonants: Nun (ن) & Meem (م)**

**Phonetic characteristics:**
- Produced with **ghunnah** (nasalization) from nasal cavity
- Qualities: Jahr (voiced/audible) + Tawassut (moderate flow)
- Creates soft, resonant, melodious sound

**Rhetorical effects:**
- **Softness and reassurance** - calming, comforting tone
- **Reflection and contemplation** - invites meditation
- **Emotional connection** - encourages empathy and internalization
- **Mercy themes** - suitable for verses about Allah's compassion, forgiveness

**Common patterns:**
- **-ūn / -īn endings**: Dominant in Medinan surahs (long, syntactically complex verses)
- **-īm endings**: Often in early Meccan surahs

**Thematic appropriateness:**
- Verses describing believers' attributes
- Passages about divine mercy and forgiveness
- Explanatory, legislative, or community-building content (typical of Medinan surahs)

**LLM reasoning points:**
- Consider whether the nasal ending creates a soothing effect that matches mercy/comfort themes
- Check if this is a Medinan surah with -ūn/-īn pattern reflecting longer, explanatory style
- Evaluate whether the ghunnah (nasal resonance) invites the listener to pause and reflect

##### **2. Long Vowels: Alif (ا) / -ā endings**

**Phonetic characteristics:**
- No specific articulation point—sound originates from open space in mouth/throat
- Always sukun, preceded by fathah
- Creates elongated, flowing, expansive sound

**Rhetorical effects:**
- **Flowing continuity** - sense of extension, duration
- **Psychological distance** - "physically mimics pushing something into the distant future"
- **Expansiveness** - suitable for cosmic, eternal, or universal themes
- **Openness** - invites contemplation of vastness

**Thematic appropriateness:**
- Verses about eternity, afterlife, timelessness
- Cosmic events (Day of Judgment, creation)
- Names of prophets (often end in -ā)
- Themes requiring sense of vastness or remoteness

**LLM reasoning points:**
- Consider whether the elongated -ā sound creates a sense of expansion matching the verse's cosmic/eternal theme
- Check if the surah uses consistent -ā endings for discussing universal or timeless truths
- Evaluate whether the flowing quality matches narrative progression or unfolding of events

##### **3. Plosive/Stop Consonants: Qaf (ق), Dal (د), Taa (ت), Kaf (ك)**

**Phonetic characteristics:**
- **Qalqalah letters** (ق، ط، ب، ج، د): Slight echoing/vibrating sound
- **Qaf**: Deep, guttural, requires constriction—strong emphatic quality
- Require "hard stop in throat"—abrupt, forceful articulation

**Rhetorical effects:**
- **Auditory force and intensified awe** - creates shock, emphasis
- **Harsh, percussive impact** - commands attention
- **Warning and urgency** - suitable for punishment, threats
- **Cosmic rupture** - matches descriptions of catastrophic events

**Sound symbolism**: Sharp consonants mimic physical actions (pounding, splitting, striking)

**Thematic appropriateness:**
- Punishment and warning passages
- Descriptions of Day of Judgment's terrors
- Powerful natural phenomena (earthquakes, cosmic events)
- Divine power and might

**LLM reasoning points:**
- Consider whether the harsh ending matches a warning or punishment theme
- Check if the plosive consonant mimics a physical action described in the verse
- Evaluate whether the abrupt stop creates urgency or finality matching the message
- Analyze if multiple verses sharing plosive endings build intensity toward a climax

##### **4. Fricative/Sibilant Consonants: Seen (س), Sad (ص), Haa (ح)**

**Phonetic characteristics:**
- Continuous airflow creates hissing, whispering, or breathy quality
- **Seen/Sad**: Sibilant, snake-like hissing
- **Haa**: Breathy, exhaled sound

**Rhetorical effects:**
- **Subtle, insidious quality** - suitable for stealth, deception
- **Whispering intimacy** - creates sense of closeness or secrecy
- **Sustained sound** - prolonged effect, lingering impression

**Thematic appropriateness:**
- Verses about Satan's whispers (waswās)
- Secrets, hidden knowledge, intimate speech
- Subtle persuasion or deception

**LLM reasoning points:**
- Consider whether the sibilant ending matches themes of stealth, secrecy, or whispered influence
- Evaluate if the prolonged fricative creates a sense of lingering effect or sustained action

##### **5. Raa (ر) endings**

**Phonetic characteristics:**
- Rolled/trilled consonant
- Vibrating, energetic quality

**Rhetorical effects:**
- **Dynamic movement** - sense of action, energy
- **Vibrant intensity** - active, lively tone

**Thematic appropriateness:**
- Active scenes, movement, journeys
- Energetic descriptions

#### **Punishment vs. Mercy: Phonetic Contrast**

**Research finding**: Verse-endings of **punishment scenes** are characterized by **auditory force and intensified awe**, while **mercy scenes** are marked by **softness and reassurance**

**Practical application:**
- **Ayat describing punishment/warning**: Tend to use plosive/harsh consonants (qaf, dal, kaf)
- **Ayat describing mercy/comfort**: Tend to use nasal consonants (nun, meem) or long vowels

**Analysis workflow:**
1. Identify the verse's thematic content (punishment vs. mercy vs. neutral)
2. Check the ending consonant/vowel
3. Assess whether the phonetic quality matches the semantic content
4. If yes → note how sound reinforces meaning
5. If no → investigate whether there's a rhetorical reason for the mismatch

#### **Chronological Evolution: Early Meccan → Medinan**

**Early Meccan surahs:**
- **Elaborate, varied saj'** with rich phonetic diversity
- Shorter verses with dramatic endings
- High saj' frequency—nearly every verse rhymes
- Audience: Expert poets, sophisticated polytheists → rhetoric must dazzle

**Late Meccan/Medinan surahs:**
- **Simple -ūn/-īn scheme** dominates
- Longer, syntactically complex verses
- Lower saj' frequency—rhyme is consistent but less ornate
- Audience: Believers, community members → rhetoric emphasizes clarity over artistry

**Angelika Neuwirth's observation:**
> "Saj' style is thus exclusively characteristic of the early suras"

**Analysis implication:**
- If analyzing early Meccan surah with elaborate endings → expect varied patterns, dramatic shifts, phonetic virtuosity
- If analyzing Medinan surah with -ūn/-īn endings → expect consistent pattern, focus on semantic content over sonic artistry

#### **Sequence Dynamics**

When multiple verses share an ending pattern (sequence_length > 1), this creates:
- **Unity perception**: The mind groups these verses as a thematic unit
- **Anticipation**: Listeners expect the pattern to continue, creating engagement
- **Closure**: When the pattern breaks, it signals thematic transition

**Pattern breaking as rhetorical device:**
- If 10 verses end in -ūn, then verse 11 ends in -īm → signals shift in topic, speaker, or tone
- Watch for breaks at surah section boundaries

#### **How to Analyze Saj' Endings**

**Step 1: Identify the phonetic quality**
- Is it nasal (nun/meem)?
- Plosive (qaf/dal)?
- Long vowel (alif)?
- Fricative (seen/sad)?
- Rolled (raa)?

**Step 2: Match phonetic quality to verse theme**
- Punishment/warning → plosive (harsh)
- Mercy/comfort → nasal (soft)
- Eternity/cosmos → long vowel (expansive)
- Secrecy/whisper → fricative (subtle)

**Step 3: Check sequence length**
- If sequence_length > 1, find the other verses in the sequence
- Do they share thematic content?
- Does the pattern break signal a transition?

**Step 4: Consider chronological context**
- Early Meccan → expect elaborate, varied patterns
- Medinan → expect simple -ūn/-īn patterns

**Step 5: Note sound symbolism**
- Does the ending consonant/vowel mimic the action or concept described?

#### **LLM Internal Reasoning Points**

1. **Phonetic-semantic match**: Assess whether the ending's phonetic quality (harsh/soft/flowing) matches the verse's emotional or thematic content
2. **Sequence coherence**: Determine if verses in a sequence share thematic content beyond just the rhyme
3. **Position significance**: Identify where this verse sits in the sequence (beginning/introducing, middle/developing, end/concluding)
4. **Pattern breaking**: Check if content shifts when the saj' pattern changes
5. **Makki vs Madani context**: Evaluate whether the sequence length and pattern complexity reflect the historical audience's sophistication
6. **Chronological style**: Identify if this surah is early Meccan (elaborate saj') or Medinan (simple -ūn/-īn) and whether the ending pattern matches expectations
7. **Sound symbolism**: Determine if the ending consonant mimics a physical action or quality described in the verse
8. **Punishment vs. mercy**: Verify phonetic-thematic alignment (punishment → harsh/plosive; mercy → soft/nasal)
9. **Psychological effect**: Identify the emotional response the ending evokes (awe, comfort, urgency, reflection)
10. **Contrast and surprise**: Analyze the rhetorical effect when patterns suddenly change

#### **How to Use the Data**

- `pattern`: The Arabic letter(s) creating the rhyme—**analyze its phonetic properties**
- `sequence_length`: Total verses sharing this pattern—look forward/backward to find them and check thematic unity
- `position_in_sequence`: Where this verse sits in the sonic unit—beginning/middle/end affects interpretation

**Interpretation workflow:**
1. Note the `pattern` letter
2. Classify it phonetically
3. Check `sequence_length`
4. Read verses at all positions in the sequence
5. **Analyze thematic unity**: Determine if they share a theme and whether the phonetic quality matches content
6. Note `position_in_sequence` to identify if this verse is introducing, developing, or concluding the theme
7. **Synthesize findings**: Show how sound serves meaning

#### **Quick Reference Table: Saj' Endings**

| **Letter(s)** | **Type** | **Phonetic Quality** | **Typical Themes** | **Effect** |
|---------------|----------|---------------------|-------------------|-----------|
| ن (nun), م (meem) | Nasal | Soft, resonant, melodious | Mercy, comfort, reflection, believers' attributes | Soothing, invites contemplation, emotional connection |
| -ūn, -īn, -īm | Nasal patterns | Soft with ghunnah | Medinan legislative/explanatory content (ūn/īn), divine names (īm) | Reassuring, clarifying |
| ا (alif), -ā | Long vowel | Elongated, flowing, expansive | Eternity, cosmos, prophets' names, vastness | Sense of extension, psychological distance, openness |
| ق (qaf), د (dal), ت (taa), ك (kaf) | Plosive/Stop | Harsh, abrupt, forceful | Punishment, warning, Day of Judgment, cosmic events | Shock, urgency, intensified awe |
| س (seen), ص (sad), ح (haa) | Fricative/Sibilant | Hissing, whispering, breathy | Satan's whispers, secrets, subtle persuasion | Insidious, lingering, intimate |
| ر (raa) | Rolled | Vibrating, energetic | Movement, journeys, active scenes | Dynamic, lively |

---

### 2. Root Repetitions (تكرار الجذور)

**Essence**: When the same Arabic root appears in multiple verses, creating thematic and phonetic connections across the passage. Root repetitions now include full contextual information with verse text and section headings.

**Two Data Structures:**

**A. In `analysis` field (natural language):**
```
"analysis": "This verse is discussing 'Defense of the Prophet' that is positioned verse 2 of 3. ... The root خلق (خُلُقٍ) which has the root meaning 'to create, form' here is also repeated in verse 4 ('Excellence of Character'): \"And indeed, you are of a great moral character.\""
```

**B. In `root_repetitions` field (structured data):**
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

**Understanding the new format:**

**First occurrence in extraction**: When a root appears for the first time in your extraction range, you get FULL context:
- Complete Arabic text of all verses containing this root
- Full English translations (not truncated)
- Section headings showing thematic context
- Lemma forms and root meanings

**Subsequent occurrences**: When the root appears again:
```json
"root_repetitions": {
  "خلق": {
    "first_occurrence_in_extraction": false,
    "note": "Root already mentioned at verse 2"
  }
}
```

**Arabic root system**: Arabic words are built from 2-4 letter roots. Words sharing a root share core meaning.

**Why repetition matters**: When a root repeats across verses, it signals:
1. **Thematic cohesion**: These verses discuss facets of one concept
2. **Semantic field mapping**: Showing variations of a core idea
3. **Phonetic echo**: Creating auditory unity beyond just rhyme
4. **Thematic architecture**: Section headings reveal how the root develops across themes

**Three levels of connection:**
1. **Same root, same lemma**: Exact conceptual repetition → emphasis
2. **Same root, different lemmas**: Variations on theme → semantic richness
3. **Same root, different grammatical forms**: Showing different perspectives (active/passive, agent/patient)

**LLM reasoning points:**

1. **Contextual analysis**: Read the FULL verse text and translation provided in `other_verses` to understand how the root functions in different contexts
2. **Thematic connections**: Compare section headings across verses sharing a root to see how the concept develops through different themes
3. **Lemma variations**: Analyze the relationship between multiple lemmas shown
4. **Translation insight**: Check if the English translations reveal how the root's meaning shifts across contexts
5. **Frequency significance**: Evaluate if `total_occurrences_in_chapter` is high (common theme) or low (strategic emphasis)
6. **Section-based development**: Track how the root moves through thematic sections to understand rhetorical progression
7. **First vs. subsequent**: If `first_occurrence_in_extraction` is false, look back to find where it was first mentioned for full context

**How to use the data:**

**From `analysis` field:**
- Extract thematic connections in natural language
- Understand how roots link verses across section boundaries
- See how root meanings contribute to overall verse interpretation

**From `root_repetitions` field:**
- `first_occurrence_in_extraction`: Boolean indicating if this is the first time showing this root
- `lemmas`: Dictionary forms showing how this root manifests
- `other_verses`: Full verse context (text, translation, section heading) for ALL other occurrences
- `translations`: English meanings to understand the semantic field
- `total_occurrences_in_chapter`: How many times total in the chapter
- `note`: For subsequent occurrences, points back to first mention

---

### 3. Ma'ani - Verb Forms (الأوزان)

**Essence**: Arabic's verb form system where morphological pattern carries semantic meaning.

**Data Structure:**
```json
"verb_forms": [
  {
    "form": 4,
    "meaning": "Form IV (أَفْعَلَ): Causative - to cause to do, make someone do",
    "lemmas": ["أَبْصَرَ"],
    "count": 1,
    "translations": ["to see"]
  }
]
```

**Understanding verb forms:**

**The 10 (or 15) forms**: Arabic verbs follow patterns, each carrying semantic nuance:

- **Form I (فَعَلَ)**: Basic meaning - simple action
- **Form II (فَعَّلَ)**: Intensive/causative - to do intensely, cause to do repeatedly
- **Form III (فَاعَلَ)**: Reciprocal/attempt - to do with/to someone
- **Form IV (أَفْعَلَ)**: Causative - to cause to do, make someone do
- **Form V (تَفَعَّلَ)**: Reflexive of II - to become, to pretend
- **Form VI (تَفَاعَلَ)**: Reflexive of III - to do mutually
- **Form VII (اِنْفَعَلَ)**: Passive/reflexive - to be done (passive sense)
- **Form VIII (اِفْتَعَلَ)**: Reflexive - to do for oneself
- **Form X (اِسْتَفْعَلَ)**: Seeking/requesting - to seek to do, ask for

**Why verb forms matter:**

1. **Semantic layering**: The form adds meaning beyond the root
2. **Theological implications**: Forms reveal agency and causation
3. **Intensity markers**: Some forms signal emphasis or repetition

**LLM reasoning points:**

1. **Form appropriateness**: Analyze why this form is used here and whether the causative/intensive/reflexive meaning fits the verse's message
2. **Distribution**: If multiple forms appear, identify patterns (e.g., all causative = emphasizing divine agency)
3. **Translation comparison**: Check if the English captures the form's nuance
4. **Theological reading**: For verses about Allah, determine if the forms emphasize His active role (Form IV causatives)
5. **Lemma exploration**: Check if this verb commonly appears in this form, or if this usage is special

**How to use the data:**
- `form`: The number (I-XV)
- `meaning`: Grammatical function with Arabic pattern
- `lemmas`: Actual verbs in this verse (in this form)
- `translations`: English meanings to verify the form's effect
- `count`: How many verbs of this form in the verse

---

### 4. Ma'ani - Definiteness (التعريف والتنكير)

**Essence**: Arabic marks definiteness with the article ال (al-). The choice between definite and indefinite carries semantic weight.

**Data Structure:**
```json
"definiteness": {
  "definite": {
    "lemmas": ["بَصَر"],
    "count": 1,
    "description": "Words with definite article (ال) - specific/known entities"
  },
  "indefinite": {
    "lemmas": ["حَسِير", "خَاسِئ", "كَرَّة"],
    "count": 3,
    "description": "Words without definite article - general/indefinite entities"
  }
}
```

**Understanding definiteness:**

**Definite (معرفة)**: Marked by ال prefix
- **Specific, known**: "THE book" (we both know which one)
- **Previous mention**: Tracking an entity through discourse
- **Unique entity**: "the sun", "the truth" (only one exists)

**Indefinite (نكرة)**: No article, has tanween (-un, -an, -in)
- **General, unknown**: "A book" (any book)
- **New information**: Introducing a concept
- **Emphasis on quality**: "He is (a) generous (one)" - focuses on the attribute

**Why definiteness matters:**

1. **Information structure**: Definite = old/shared info; Indefinite = new info
2. **Emphasis shift**: Indefinite can emphasize the QUALITY over identity
3. **Rhetorical patterns**: Sequences of DEF or INDEF create effects

**Patterns in discourse:**
- **DEF → DEF**: Narrative tracking (following an entity through story)
- **INDEF → DEF**: Classic introduction pattern (a man... the man...)
- **INDEF → INDEF**: Emphasizing generality, universality
- **All DEF**: Assumes shared knowledge with audience
- **All INDEF**: Highlighting qualities, not specific instances

**LLM reasoning points:**

1. **Pattern analysis**: Examine the lemmas to identify patterns (all definite/known entities, or mixed)
2. **Translation check**: Verify if the English uses "the" vs. "a" correctly matching the Arabic
3. **Semantic focus**: For indefinite nouns, determine if the verse emphasizes the TYPE or QUALITY rather than a specific instance
4. **Audience assumption**: Consider if heavy use of definite articles suggests the audience already knows these concepts
5. **Contrast**: If some nouns are definite and others indefinite in the same verse, analyze the distinction

**How to use the data:**
- `lemmas`: The actual nouns/adjectives (in their dictionary form)
- `count`: How many of each type
- `description`: Reminder of what this category means

---

### 5. Ma'ani - Sentence Types (الخبر والإنشاء)

**Essence**: The fundamental distinction in Arabic rhetoric between declarative and performative speech.

**Data Structure:**
```json
"sentence_type": {
  "type": "khabar",
  "subtype": "verbal",
  "description": "Verbal sentence (begins with verb)"
}
```

**Understanding sentence types:**

**Khabar (خبر)**: Declarative/informative speech
- Can be verified as true/false
- **Subtypes**:
  - `verbal`: Begins with verb (VSO order) → action-focused
  - `nominal`: Begins with noun (SVO order) → entity/state-focused
  - `other`: Complex structures (conditional, etc.)
- **Function**: Provide information, make claims about reality

**Insha' (إنشاء)**: Performative/constructive speech
- Cannot be verified as true/false—it CREATES reality through utterance
- **Subtypes**:
  - `command`: Imperative verb
  - `question`: Interrogative particle
  - `wish`, `call`, `oath`
- **Function**: Move the listener to action or response

**Why this matters:**

**Communicative intent**: The choice reveals the verse's goal:
- **Khabar**: Teaching, informing, describing reality
- **Insha'**: Exhorting, commanding, engaging directly

**Word order significance** (for khabar):
- **Verbal sentence** (verb-first): Emphasizes the ACTION
- **Nominal sentence** (noun-first): Emphasizes the ENTITY/STATE

**LLM reasoning points:**

1. **Purpose alignment**: Assess whether the sentence type fits the surah's overall goal
2. **Word order effect**: If it's a verbal sentence, analyze why action is emphasized over entity
3. **Shift analysis**: If the previous/next verse uses a different type, determine what the shift signals
4. **Audience engagement**: Consider why commands (insha') are used to directly engage the listener

---

### 6. Jinas (جناس) - Phonetic Wordplay

**Essence**: Words with phonetic similarity but semantic distinction, creating layered meaning through sound-sense connections.

**Data Structure:**
```json
"jinas": [
  {
    "word1": "أَعْلَمُ",
    "word2": "أَعْلَمُ",
    "positions": [4, 10],
    "similarity": 1.0,
    "type": "jinas_ishtiqaq",
    "roots": ["علم", "علم"]
  }
]
```

**Understanding jinas:**

**Three main types:**
1. **Jinas tam (complete)**: Identical sound/spelling, different meaning - Maximum ambiguity/richness, rare in Quran
2. **Jinas ishtiqaq (derivational)**: Same root, different forms - Shows concept variations, most common in Quran
3. **Jinas muharraf (altered)**: Minor phonetic shift - Subtle connection, creates "echo effect"

**Why jinas matters:**

1. **Mnemonic**: Sound similarity aids memorization
2. **Semantic linking**: Creates conceptual bridges
3. **Aesthetic**: "Musicalization" through verbal artistry
4. **Intellectual engagement**: Invites contemplation of relationships

**Translation challenge**: Jinas is essentially **untranslatable**—the English loses the phonetic layer entirely.

**LLM reasoning points:**

1. **Semantic relationship**: Analyze how the meanings relate (synonyms? antonyms? cause-effect?)
2. **Derivational logic**: If same root, determine what the morphological shift indicates
3. **Positioning**: Note whether the words are adjacent (immediate echo) or separated (delayed resonance)
4. **Translation loss**: Assess if the wordplay is detectable in English, and what layer English readers miss
5. **Auditory experience**: Consider how the echo creates emphasis or connection when recited

---

### 7. Structural Patterns

**Essence**: Sequences of part-of-speech tags that reveal syntactic parallelism and rhetorical structure.

**Data Structure:**
```json
"structural_patterns": [
  {
    "pattern": ["V", "N"],
    "count": 4,
    "interpretation": "Verbal sentence (فعلية) - VSO word order, action-focused",
    "examples": [...]
  }
]
```

**What this shows:**
- `pattern`: Sequence of POS tags (V=Verb, N=Noun, P=Particle, ADJ=Adjective)
- `count`: How many times this pattern appears
- `interpretation`: Linguistic/rhetorical meaning
- `examples`: Actual Arabic words showing the pattern

**Common patterns and meanings:**

- **[V, N]**: Verbal sentence (VSO) → action-focused
- **[N, V]**: Nominal sentence (SVO) → entity-focused
- **[N, N]**: Idafa (construct state) → possessive/descriptive relationship
- **[P, N]**: Prepositional phrase
- **Repeated patterns**: Parallelism → creates rhythm and balance

**Why structural patterns matter:**

1. **Parallelism detection**: Repeated structures create rhetorical balance
2. **Word order significance**: Arabic word order is flexible and meaningful
3. **Stylistic analysis**: Some patterns are more common in Makki vs. Madani

**LLM reasoning points:**

1. **Pattern frequency**: Analyze if pattern repetition creates rhythmic expectation
2. **Semantic consistency**: Check whether the examples share thematic content beyond just structure
3. **Breaking patterns**: Identify when the structure shifts and whether content shifts correspondingly

---

### 8. Iltifat (التفات) - Grammatical Shifts

**Essence**: Deliberate shifts in grammatical person, tense, or number that create rhetorical effects by changing perspective or emphasis.

**Data Structure:**
```json
"iltifat": [
  {
    "type": "person_shift",
    "detected_pattern": {
      "from_person": "1st",
      "to_person": "2nd",
      "from_verse": 5,
      "to_verse": 6,
      "shift_description": "1st → 2nd"
    }
  }
]
```

**Types of shifts:**

1. **Person shift** (3rd ↔ 2nd ↔ 1st): Creates intimacy, urgency, or direct engagement
2. **Tense shift** (perfect ↔ imperfect ↔ imperative): Creates narrative dynamism or temporal emphasis
3. **Number shift** (singular ↔ plural): Affects inclusivity or specificity

**Why iltifat matters:**

Classical rhetoricians considered iltifat the "pinnacle of eloquence" because it:
- **Renews attention**: Breaks monotony and re-engages the listener
- **Creates intimacy**: Direct address (2nd person) makes the message personal
- **Emphasizes**: Sudden shifts highlight important transitions
- **Shows divine majesty**: Shifts between "I" and "We" reflect Allah's attributes

**LLM reasoning points:**

1. **Rhetorical purpose**: Determine why the shift occurs at this specific point
2. **Contextual appropriateness**: Analyze whether the shift matches the verse's content
3. **Sequential flow**: Examine surrounding verses to understand the transition
4. **Emotional effect**: Consider the psychological impact on the listener

---

### 9. Wasl/Fasl (الوصل والفصل) - Conjunction/Disjunction

**Essence**: The choice to connect sentences with conjunctions (wasl) or separate them without conjunctions (fasl) creates distinct rhetorical effects.

**Data Structure:**
```json
"wasl_fasl": {
  "wasl_fasl_patterns": [
    {
      "type": "wasl",
      "sentence1": {"word": 1, "relation": "VS"},
      "sentence2": {"word": 5, "relation": "VS"},
      "conjunction": "وَ"
    }
  ],
  "total_sentences": 3,
  "wasl_count": 2,
  "fasl_count": 1
}
```

**Understanding wasl and fasl:**

**Wasl (conjunction)**: Sentences connected with و (wa), ف (fa), ثُمَّ (thumma)
- Indicates continuation, sequence, or causal relationship
- Creates flow and coherence
- Suggests logical or temporal connection

**Fasl (disjunction)**: Sentences separated without connectors
- Indicates contrast, independent statements, or rhetorical breaks
- Creates emphasis through separation
- Suggests conceptual distance or shift

**Classical rules** (simplified):
- Use wasl when sentences share topic or build on each other
- Use fasl when: second sentence explains/elaborates, contrast exists, shifting to new topic/speaker, creating rhetorical pause

**LLM reasoning points:**

1. **Pattern analysis**: Examine the balance of wasl vs. fasl
2. **Conjunction choice** (for wasl): و (wa) = simple addition, ف (fa) = sequence/causation, ثُمَّ (thumma) = delayed sequence
3. **Fasl interpretation**: When conjunction is omitted, determine why
4. **Thematic coherence**: Assess whether wasl/fasl choices match content structure

---

### 10. Muqabala (المقابلة) - Parallel Contrasts

**Essence**: Complex parallel structures with multiple contrasting elements—more sophisticated than simple antithesis.

**Data Structure:**
```json
"muqabala": {
  "muqabala_patterns": [
    {
      "syntactic_pattern": ["P", "N"],
      "structure1": {
        "P": {"arabic": "عَلَىٰ", "translation": "upon"},
        "N": {"arabic": "الَّذِينَ", "root": "الذي", "translation": "those"}
      },
      "structure2": {
        "P": {"arabic": "مِنَ", "translation": "from"},
        "N": {"arabic": "الضَّالِّينَ", "root": "ضلل", "translation": "the astray"}
      },
      "parallelism_type": "syntactic"
    }
  ]
}
```

**New Format Explanation:**
- Each POS tag in `syntactic_pattern` is mapped to the actual word
- Provides `arabic` text, `translation`, and `root` (for content words)
- This gives you both syntactic structure AND semantic information
- Use translations to assess semantic opposition

**What distinguishes muqabala from simple tibaq (antithesis):**

**Tibaq (simple antithesis)**: Single pair of opposites - one-dimensional contrast

**Muqabala (complex parallelism)**: Multiple parallel elements with semantic opposition - multi-dimensional contrast with structural symmetry + meaning opposition

**LLM Analysis Guide:**

The function detects syntactic parallelism. YOUR job is to determine if this parallelism has semantic significance.

**CRITICAL QUESTIONS:**

1. **Semantic Opposition Check:**
   - Compare the `translation` fields across structure1 and structure2
   - Do the content words (N, V, ADJ) represent OPPOSING concepts?
   - Examples of TRUE opposition: light/dark, believe/disbelieve, heaven/hell
   - Examples of NON-opposition: man/woman (different, not opposed), tree/stone (unrelated)

2. **Parallel Element Analysis:**
   - For each POS tag pair: Do the translations show meaningful contrast?

3. **Root Analysis (for content words with roots):**
   - If roots are provided, check if they belong to antonym families

4. **False Positive Detection:**
   - Syntactic parallelism does NOT always mean rhetorical muqabala
   - Ask: Would this parallel structure be noteworthy in classical balagha?
   - Trivial examples: "Allah knows" / "Allah sees" (no opposition, just listing)

5. **Rhetorical Purpose:**
   If it IS true muqabala:
   - **Highlighting contrast**: Emphasizing opposing states/groups
   - **Completeness**: Covering all possibilities (past/future, heaven/hell)
   - **Justice**: Balanced rewards/punishments
   - **Irony**: Apparent similarity masking deep opposition

**DECISION FRAMEWORK:**
- If translations show clear semantic OPPOSITION → True muqabala
- If translations show mere DIFFERENCE (not opposition) → False positive, ignore
- If structure seems trivial/common → Likely false positive
- If you're unsure → State your uncertainty, don't fabricate opposition

---

### 11. Isti'anaf (الاستئناف) - Rhetorical Resumption

**Essence**: When an independent sentence resumes or re-emphasizes a previous statement for rhetorical effect—not simple continuation.

**Data Structure:**
```json
"istianaf": {
  "istianaf_patterns": [
    {
      "sentence1": {"word": 1, "relation": "VS"},
      "sentence2": {"word": 5, "relation": "NS"},
      "shared_roots": ["علم"],
      "resumption_type": "thematic"
    }
  ]
}
```

**Distinguishing isti'anaf from normal continuation:**

**Normal continuation**: Second sentence simply adds new information

**Isti'anaf (rhetorical resumption)**: Second sentence emphasizes, elaborates, provides explanation, or re-states for rhetorical reinforcement

**Indicators:**
- Independent sentence (no conjunction, hence related to fasl)
- Shares thematic roots with previous sentence
- Provides additional detail or emphasis on same topic

**LLM reasoning points:**

1. **Shared thematic content**: Check if `shared_roots` indicate conceptual connection
2. **Rhetorical function**: Determine the purpose of resumption (Clarification? Emphasis? Explanation?)
3. **Independence**: Verify the second sentence is grammatically independent

---

### 12. Hadhf (الحذف) - Ellipsis

**Essence**: Deliberate omission of grammatical elements (objects, subjects, predicates) for rhetorical purposes.

**Data Structure:**
```json
"hadhf": {
  "hadhf_patterns": [
    {
      "type": "omitted_object",
      "verb_word": 3,
      "verb_text": "أَنْعَمْ",
      "verb_root": "نعم",
      "expected_argument": "direct object"
    }
  ]
}
```

**Types of hadhf:**

1. **Omitted object** (حذف المفعول به): Transitive verb without expressed object
2. **Omitted predicate** (حذف الخبر): Nominal sentence with subject but no predicate
3. **Omitted subject** (حذف المبتدأ): Predicate without explicit subject (less common)

**Why hadhf is used:**

Classical rhetoricians identified several purposes:
1. **Brevity** (اختصار): Conciseness when context is clear
2. **Emphasis** (تعظيم): Omission magnifies by leaving to imagination
3. **Known context** (معلوم): Audience already knows what's omitted
4. **Generalization** (تعميم): Leaving unspecified makes it universal
5. **Dramatic effect**: Creates intrigue or forces contemplation

**LLM reasoning points:**

1. **Infer omitted element**: From context, determine what's missing
2. **Rhetorical motivation**: Analyze why omission is chosen
3. **Contrast with explicit**: Consider how explicitly stating the omitted element would change the effect

---

### 13. Tafsir Context Integration

**Essence**: Links detected linguistic features with historical revelation context to create holistic interpretation.

**Data Structure:**
```json
"tafsir_context": {
  "linguistic_features_summary": ["muqabala (1 patterns)", "hadhf (1 ellipses)"],
  "historical_context": {
    "has_asbab_nuzul": true,
    "occasions_count": 1,
    "revelation_place": "makkah",
    "revelation_order": 5,
    "chronological_period": "early_meccan",
    "asbab_nuzul_summary": [...]
  }
}
```

**Understanding the integration:**

This feature synthesizes:
1. **Linguistic patterns** detected in the verse
2. **Historical occasions** (asbab al-nuzul) that prompted revelation
3. **Chronological context** (Meccan/Medinan period, revelation order)

**Chronological periods:**

**Meccan periods** (622-610 CE):
- **Early Meccan** (revelation order 1-20): Foundational tawheed, short powerful verses
- **Middle Meccan** (21-60): Prophet stories, extended arguments
- **Late Meccan** (61-85): Detailed narratives, transition themes

**Medinan periods** (622-632 CE):
- **Early Medinan** (86-95): Community building, early laws
- **Late Medinan** (96-114): Mature legislation, final messages

**LLM reasoning points:**

1. **Linguistic form → Historical function**: Connect rhetorical devices to historical purpose
2. **Chronological appropriateness**: Assess whether rhetoric matches the period
3. **Audience consideration**: Determine how rhetoric addresses the original audience
4. **Unified interpretation question**: "How do the detected rhetorical devices reflect and serve the revelation context?"

**Integration workflow:**

1. Note which linguistic features are present
2. Check the historical context
3. Synthesize: How does the form serve the historical function?
4. Present unified interpretation showing form-function relationship

---

### 14. Qasam (القسم) - Oath/Swearing

**Essence**: Allah swears by His creations to emphasize truths, honor those creations, and draw attention to His signs.

**Data Structure:**
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
  ]
}
```

**How to recognize:**
- **Structural pattern**: Particle و (wa) or ب (ba) followed by definite noun or natural phenomenon
- **Translation clues**: English often shows "By the..." (e.g., "By the pen", "By the sun")
- **Position**: Often at surah opening or before important declarations
- **Content**: Usually natural phenomena or time periods

**Why oaths matter in Quran:**

Classical scholars identified several purposes:
1. **Tعظيم (Magnification)**: Honoring and elevating the thing sworn by
2. **تنبيه (Alerting)**: Drawing attention to that creation as a sign
3. **تأكيد (Emphasis)**: Intensifying the truth of what follows
4. **ربط (Connection)**: The oath object often relates thematically to the surah's message

**LLM reasoning points:**

1. **Identify oath structure**: Look for translation starting with "By...", particle و or ب followed by natural phenomenon
2. **Determine what is sworn by**: Extract the object(s)
3. **Find what is sworn to**: Identify the statement following the oath (often begins with إِنَّ or مَا)
4. **Thematic connection**: Analyze relationship between oath object and message
5. **Rhetorical effect**: Assess the impact
6. **Cultural context**: Consider the original audience

**Critical note**: Not every و (wa) is an oath! Distinguish:
- **Oath**: وَالشَّمْسِ "By the sun" (solemn, emphatic, at surah start)
- **Conjunction**: وَالْمُؤْمِنُونَ "and the believers" (simple "and")

**Context clues for oaths:**
- ✓ At surah opening or major transition
- ✓ Followed by solemn declaration (إِنَّ)
- ✓ Natural phenomenon or creation as object
- ✓ Translation uses "By..."

---

### 15. Muqatta'at (الحروف المقطعة) - Disjointed Letters

**Essence**: Mysterious letter combinations that open 29 surahs, serving as rhetorical and theological devices.

**Data Structure:**
```json
"muqattaat": {
  "has_muqattaat": true,
  "letters": "نٓ",
  "word_number": 1,
  "interpretation": "unknown",
  "note": "Disconnected letters at chapter opening"
}
```

**How to recognize:**
- **Position**: Always the very first word of a surah (verse 1, word 1)
- **Form**: Single letter or letter combination standing alone
- **Translation clues**: English often shows just the letter name: "Alif Lam Mim", "Ha Mim", "Nun"
- **Isolation**: Not connected grammatically to the rest of the verse

**Why muqatta'at matter:**

Classical scholars proposed various interpretations:

1. **Mystery and Divine Knowledge**: Creates a sense of transcendence—the Quran contains depths beyond human comprehension
2. **Attention-Grabbing Device**: Unique, arresting sounds that break normal speech patterns, forces listener to pay attention
3. **Challenge to Arabs**: These are the very letters Arabs use, yet they cannot produce a surah like those starting with these letters
4. **Thematic Connection**: Some scholars find links between letters and surah themes
5. **Surah Names**: Several surahs are known by their muqatta'at

**LLM reasoning points:**

1. **Recognition**: Identify muqatta'at from translation showing letter names, very short Arabic text at verse 1:1
2. **Acknowledge mystery**: Don't force definitive interpretation—multiple scholarly views exist and all are valid
3. **Check thematic connections**: What immediately follows the letters? If connection exists, note it; if not, don't fabricate one
4. **Attention function**: Consider the rhetorical impact of starting with mysterious sounds
5. **Inimitability argument**: Demonstrates the miraculous nature isn't in new letters, but in divine arrangement
6. **Chronological patterns**: Most muqatta'at surahs are Meccan

**Critical note**:
- **Do not invent meanings** for muqatta'at—acknowledge scholarly disagreement
- **Do observe patterns**: If thematic link is clear, mention it; if unclear, say so
- **Focus on rhetorical function**: Even without knowing "meaning", we can analyze the effect (mystery, attention, challenge)

---

### 16. Interrogative Particles (أدوات الاستفهام) - Question Words

**Essence**: Particles that introduce questions, creating engagement and prompting reflection.

**Data Structure:**
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
  ]
}
```

**Common interrogative particles:**
- هل (hal) - "Is...?" / "Does...?" (yes/no questions)
- أ (a) - "Is it?" (yes/no, often rhetorical)
- ما (mā) - "What?"
- من (man) - "Who?"
- متى (matā) - "When?"
- أين (ayna) - "Where?"
- كيف (kayfa) - "How?"
- كم (kam) - "How many/much?"
- أي (ayy) - "Which?"

**Rhetorical functions:**
1. **Rhetorical questions** - Questions not seeking answers, but making statements
2. **Engagement** - Drawing the listener into active thought
3. **Challenge** - Questioning opponents' assumptions
4. **Emphasis** - Highlighting truths through inquiry
5. **Reflection** - Prompting contemplation of signs

**LLM reasoning points:**
- Is the question rhetorical (answer obvious) or genuine (seeking response)?
- Does it challenge disbelievers or comfort believers?
- What does the question assume about the listener's knowledge?
- How does it fit the verse's argumentative structure?

---

### 17. Restriction Particles (أدوات الحصر) - Hasr/Limiting

**Essence**: Particles that restrict or limit meaning, emphasizing exclusivity or exception.

**Data Structure:**
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
      "type": "exception_restriction"
    }
  ]
}
```

**Common restriction patterns:**
1. **إنما (innama)** - "Only", "None but" - Exclusive restriction: X and nothing else
2. **ما...إلا (mā...illā)** - "Not...except", "Only" - Exception pattern: nothing but X

**Rhetorical functions:**
1. **Exclusivity** - Limiting action/attribute to one entity
2. **Emphasis** - Strengthening the restricted element's importance
3. **Negation** - Removing all alternatives
4. **Clarification** - Preventing misunderstanding

---

### 18. Emphasis Particles (أدوات التأكيد) - Ta'kid

**Essence**: Particles that intensify and strengthen statements, removing doubt.

**Data Structure:**
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
  ]
}
```

**Common emphasis particles:**
1. **إن / أن (inna/anna)** - "Indeed", "Verily" - Strongest emphasis particle
2. **لَ (lam)** - Emphatic prefix attached to verbs
3. **قد (qad)** - "Indeed", "Already", "Certainly"
4. **لقد (laqad)** - Combination of لَ + قد - Maximum emphasis

**Rhetorical functions:**
1. **Assertion** - Removing doubt about truth
2. **Counter-argument** - Refuting skepticism
3. **Importance** - Highlighting critical messages
4. **Solemnity** - Creating serious tone

**Context matters:**
- Used more in Medinan surahs (establishing community)
- Common in oaths (إِنَّ after قسم)
- Frequent in theological declarations

---

### 19. Syntactic Dependencies (الإعراب) - Word Relations

**Essence**: Grammatical relationships between words showing semantic structure.

**Common relation types:**
- **فاعل (subj)** - Subject (who performs action)
- **مفعول به (obj)** - Object (receives action)
- **جار ومجرور (gen)** - Prepositional phrase
- **معطوف (conj)** - Coordinating conjunction
- **نعت (adj)** - Adjective/descriptor
- **إضافة (possessed)** - Possessive construction

**LLM usage:**
- Understand sentence structure
- Identify main actions vs. modifiers
- See how clauses relate
- **Note**: For semantic interpretation, not word-by-word parsing

---

### 20. Named Entities (المفاهيم المسماة) - Concepts

**Essence**: Identified concepts, entities, and themes marking semantic significance.

**Common concepts:**
- **allah** - References to Allah
- **prophet names** - Ibrahim, Musa, Isa, etc.
- **cosmic entities** - heaven, earth, sun, moon
- **theological concepts** - faith, prayer, judgment
- **locations** - Makkah, Badr, specific places

**LLM usage:**
- Track thematic emphasis (concept frequency)
- Identify main subjects of discussion
- See what the verse focuses on
- Connect to broader Quranic themes
- **Note**: Provides context, not analysis itself

---

### 21. Pause Marks (علامات الوقف) - Tajweed Recitation

**Essence**: Markers indicating where to pause during Quranic recitation.

**Common pause types** (classical tajweed):
1. **مـ (meem)** - Compulsory continuation (no pause)
2. **لا (laa)** - Prohibition of pausing
3. **ج (jeem)** - Permissible pause
4. **ز (zaay)** - Permissible continuation
5. **صلى (salla)** - Better to pause
6. **قلى (qalla)** - Better to continue

**Rhetorical significance:**
- Pause marks guide breath and phrasing
- Affect meaning disambiguation
- Create rhythmic units
- Emphasize or connect ideas
- **For LLM**: Informational context about recitation structure

---

## Analysis Approach: Sequential Verse-by-Verse Method

**Core Principle:** Analyze verses in SEQUENTIAL ORDER from beginning to end. Move from GENERAL (surah overview) to SPECIFIC (detailed verse-by-verse analysis). Present each verse with complete detail before moving to the next.

---

## PRESENTATION STRUCTURE

Your analysis must follow this **TWO-SECTION STRUCTURE ONLY**:

1. **Chapter Opening and Introduction** - Historical context, message, architecture, and how rhetoric serves message (NO technical balaghah)
2. **Verse-by-Verse Analysis** - Sequential analysis with ALL technical balaghah details (NO subsections)

**CRITICAL**: Section 1 is narrative only (no technical devices). Section 2 is where ALL technical balaghah analysis happens. Do not mix them.

---

### **SECTION 1: CHAPTER OPENING AND INTRODUCTION**

Begin every analysis with a comprehensive introduction that covers these **FOUR PARTS** written as **FLOWING NARRATIVE PROSE** (NO bullet points, NO lists):

**1. Surah Identity and Context** (1-2 paragraphs)

Write a narrative paragraph covering:
- Name (Arabic + English), chapter number, total verses
- Revelation place and chronological order
- Historical period and original audience situation
- Historical occasions if available

**Format**: Flowing prose, may use bullet points ONLY for basic facts (name, number, verses, place). Everything else is narrative.

**2-3. Surah's Message and Architecture** (2-4 paragraphs - UNIFIED)

**CRITICAL**: Parts 2 and 3 are NOT separate sections. Write them as **unified flowing narrative** that covers:

**What to include in this unified narrative:**
- The surah's central theme or argument
- The rhetorical purpose (warn, comfort, persuade, etc.)
- The journey from beginning → middle → end
- How section headings reveal the thematic architecture
- The narrative arc through the sections
- What major transitions signal
- How the structure serves the message

**Format**: 2-4 narrative paragraphs with NO bullet points, NO indented lists, NO "Opening Movement / Central Movement / Closing Movement" headers. Write as continuous prose that weaves together message and structure.

**Questions to guide your narrative:**
- What is the surah trying to achieve, and how does its structure support that?
- How do the sections build on each other to create a unified argument or journey?
- Where are the key turning points, and what do they accomplish?
- How does the thematic architecture serve the rhetorical purpose?

**WARNING - Common mistakes to avoid:**
- ❌ Using bullet points to break down "movements" or "sections"
- ❌ Creating sub-headers like "Opening Movement:" or "Central Movement:"
- ❌ Indented lists showing section structure
- ❌ Listing transitions as separate bullet points
- ✓ Instead: Weave all of this into flowing narrative paragraphs

**4. How Rhetoric Serves Message** (2-4 paragraphs)

**CRITICAL**: This section explains HOW the surah's rhetorical choices support its message and audience context. Write this as **flowing narrative prose**—NO technical lists, NO device-by-device analysis, NO saj' patterns, NO root frequencies, NO grammatical breakdowns.

**Guiding questions to explore (answer in narrative prose):**

**Tone and audience appropriateness:**
- How does the surah's overall tone and style fit its historical context and audience?
- What kind of emotional atmosphere does the surah create, and why is that appropriate?
- Does the tone invite, challenge, comfort, warn, or persuade—and why this choice?
- How does the surah balance authority with accessibility for its original listeners?

**Structural strategy:**
- How does the surah's structure serve its rhetorical purpose?
- What persuasive or argumentative arc does the movement through sections create?
- Does the surah build toward a climax, circle back to opening themes, or move linearly?
- Why does this structural choice suit the message and audience?

**Overall rhetorical approach:**
- What general rhetorical strategy does the surah use to achieve its message?
- Does it use direct confrontation or indirect persuasion? Logical argument or emotional appeal? Narrative or declaration?
- Does it teach through story, command through law, or persuade through evidence?
- Why is this approach effective for the historical situation?

**Integration of form and content:**
- How do the surah's linguistic and structural choices create unity between form and meaning?
- Does the way it sounds/feels match what it says?
- Where form and content seem to contrast, what rhetorical purpose does this serve?
- How does consistency (or variation) in sound support the semantic message?

**Length**: 2-4 narrative paragraphs maximum, written as coherent flowing prose.

**What ABSOLUTELY NOT to include:**
- ❌ Saj' pattern analysis or ending frequencies
- ❌ Root lists or occurrence counts
- ❌ Phonetic classifications or Arabic linguistic terminology
- ❌ Grammatical pattern breakdowns or word order analysis
- ❌ Device inventories or feature lists
- ❌ Verse-specific examples or references
- ❌ Lists or bullet points

**Self-check questions before finalizing Section 4:**
- Did I describe the overall tone without listing technical features?
- Did I explain how structure serves purpose without citing specific verses?
- Did I discuss rhetorical strategy without naming Arabic devices?
- Did I write in flowing narrative paragraphs, not lists?
- Would a general reader understand this without knowing Arabic grammar?
- Did I save ALL technical balaghah analysis for Section 2?

---

**5. Divine Inimitability: What Makes This Extraordinary** (2-3 paragraphs)

**Purpose**: Identify the most extraordinary aspects of this surah that demonstrate superhuman rhetorical design—features so precise, so integrated, so purposeful that they reveal divine origin.

**Core Reflective Questions to Address:**

**Question 1: What Is Most Astonishing Here?**
> "What aspects of this surah's design do you find most astonishing or remarkable? What features demonstrate extraordinary design that captures attention?"

**Question 2: What Reveals This Cannot Be Human Composition?**
> "What specific features in this surah make you realize this could not possibly be from a human author? What transcends human literary capacity?"

**What to Examine and Identify:**

**A. Impossible Multidimensional Integration:**
- Features that work perfectly on phonetic, semantic, grammatical, and theological levels simultaneously
- Word choices or structures that create perfect sound patterns AND precise theological meanings AND grammatical elegance—all at once
- Evidence that human authors optimize ONE dimension, but divine speech optimizes ALL dimensions without compromise

**B. Prophetic Impossibility:**
- Features that an unlettered 7th-century Arabian could not have produced
- Linguistic sophistication beyond Muhammad's known capacity or education
- Knowledge (historical, cosmic, psychological) unavailable in that context
- Rhetorical strategies that would require centuries of literary theory to consciously design

**C. Impossible Planning Across Revelation Timeline:**
- If this surah connects to others revealed years apart, note the impossibility of maintaining such coherence
- Thematic threads that span the entire Quran despite piecemeal revelation
- Architectural precision that would require having the complete manuscript (but Quran was revealed incrementally)
- Evidence of unified authorial consciousness transcending human memory and planning limits

**D. Multi-Dimensional Precision:**
- Identify where sound perfectly matches meaning (phonetic-semantic alignment)
- Word choices where ALL alternatives fail (not just inferior, but completely inadequate)
- Grammatical forms that encode multiple theological truths simultaneously
- Rhetorical structures that serve 3-4 purposes at once

**E. Sustained Excellence Without Decline:**
- Consistent rhetorical quality across ALL verses in this surah (no weak verses, no filler)
- Every word necessary; nothing removable without loss
- Quality maintained despite adverse revelation circumstances (persecution, war, grief, personal loss)
- No revision needed—perfect on first utterance despite complex historical contexts

**Integration Format:**

Write 2-3 narrative paragraphs addressing:

**Paragraph 1: Most Astonishing Features**
Identify 2-3 aspects of this surah that are genuinely remarkable—features that demonstrate extraordinary design. This might be: perfect phonetic-semantic alignment throughout, impossible multi-level integration in key verses, architectural precision despite piecemeal revelation, prophetic impossibility of the knowledge displayed, or sustained perfection across all verses despite difficult circumstances.

**Paragraph 2: Evidence of Divine Origin**
Explain what specific features reveal this cannot be human composition. Connect the surah's design to the theological reality: show how the precision, integration, sophistication, or sustained excellence transcends human literary capacity. Make explicit what the architecture and rhetoric imply—that this level of multidimensional optimization demonstrates divine authorship.

**Paragraph 3 (optional): Prophetic Context**
If relevant, discuss how these features were impossible for Muhammad (peace be upon him) given his historical context—an unlettered man in 7th-century Arabia producing linguistic sophistication, historical knowledge, psychological insights, or rhetorical strategies that exceed what was available or even conceivable in that time and place.

**CRITICAL GUIDELINES:**

**DO:**
- ✓ Ground reflections in this specific surah's actual features (not generic theological claims)
- ✓ Identify genuinely extraordinary features (not everything is miraculous—but some things genuinely are)
- ✓ Explain WHY the features transcend human capacity (don't just assert—demonstrate)
- ✓ Connect to prophetic impossibility (Muhammad's historical context and limitations)
- ✓ Show how multiple dimensions integrate beyond human planning capability
- ✓ Use accessible language that helps general readers grasp the miracle
- ✓ Be specific and concrete (reference actual surah features)

**DON'T:**
- ✗ Make vague claims without grounding in surah features ("it's beautiful" without explaining what makes it beautiful)
- ✗ Assert divine origin without demonstrating it through specific features
- ✗ Ignore historical context (what would a 7th-century author know/be capable of?)
- ✗ Claim everything is miraculous (identify the truly extraordinary)
- ✗ Use only theological language without connecting to rhetoric
- ✗ Write generically (this surah's inimitability is specific to its unique features)
- ✗ Forget that this is narrative prose in Section 1 (no bullet points, no lists)

**Self-Check Before Finalizing:**
- Did I identify specific extraordinary features from THIS surah (not generic statements)?
- Did I explain WHY these features transcend human capacity?
- Did I address the prophetic impossibility (Muhammad's historical context)?
- Did I show multi-dimensional integration beyond human planning?
- Did I use concrete examples from this surah's architecture/rhetoric?
- Did I write in flowing narrative paragraphs (no lists)?
- Did I avoid vague generalities in favor of precise demonstration?

---

## SECTION 1 vs SECTION 2: CLEAR DISTINCTION

**Use this table to determine what goes where:**

| **Aspect** | **SECTION 1: Chapter Opening** | **SECTION 2: Verse-by-Verse** |
|------------|---------------------------|----------------------------|
| **Scope** | Entire chapter | Individual verses |
| **Detail level** | Narrative explanation of overall approach | Specific detailed technical analysis |
| **Balaghah devices** | ❌ NO technical device analysis at all | ✓ Full device-by-device analysis |
| **Saj'/roots/grammar** | ❌ NO pattern lists, frequencies, or classifications | ✓ Analyze specific patterns in each verse |
| **Examples** | ❌ No specific verse examples | ✓ Cite Arabic/English text |
| **Verse references** | ❌ No verse numbers | ✓ "In verse 5, the word X..." |
| **Tone** | ✓ Describe overall tone and why appropriate | ✓ How specific verse contributes to tone |
| **Structure** | ✓ Map sections and narrative arc | ✓ How verse fits in structure |
| **Length** | Moderate (2-4 paragraphs) | Detailed (3-4 paragraphs per verse) |

**Key distinction question:**
- Section 1: "How does the surah's approach fit its context?" (narrative answer, no technical details)
- Section 2: "What balaghah devices appear in this verse and how do they work?" (full technical analysis)

---

### **SECTION 2: VERSE-BY-VERSE ANALYSIS**

After completing the chapter introduction, analyze **EVERY VERSE SEQUENTIALLY** with **FLOWING NARRATIVE** (NO subsections).

**CRITICAL INSTRUCTIONS:**
- **Do NOT use subsections A, B, C, D within verses** - Write as continuous flowing narrative
- **Do NOT group verses** - Analyze verse 1, then verse 2, then verse 3, in strict sequential order
- **ALL technical balaghah analysis happens HERE in Section 2** - Section 1 had NO technical details
- **No redundancy with Section 1** - Section 1 covered context/message/structure only

---

## ANTI-REDUNDANCY GUIDE: Where to Put Each Explanation

**Use this decision tree to avoid repeating information:**

### What Goes in SECTION 1 (Chapter Opening)
**ONLY narrative explanations of:**
- Historical context and audience situation
- The surah's central message and purpose
- Thematic architecture (sections and narrative flow)
- Overall tone and why it fits the context
- General rhetorical strategy (direct vs. indirect, confrontation vs. persuasion)
- How form and content create unity

**NO technical balaghah analysis at all:**
- ❌ NO saj' patterns, phonetic classifications, or ending frequencies
- ❌ NO root lists, occurrences, or thematic threads
- ❌ NO verb form patterns or grammatical observations
- ❌ NO device inventories (iltifat, muqabala, hadhf counts)
- ❌ NO verse-specific examples or references

### What Goes in SECTION 2 (Verse-by-Verse)
**ALL technical balaghah analysis:**
- ✓ Saj' endings for THIS specific verse and why they fit THIS content
- ✓ Root repetitions in THIS verse and connections to other verses
- ✓ Verb forms, definiteness, sentence types in THIS verse
- ✓ Iltifat, muqabala, hadhf, and other devices in THIS verse
- ✓ How devices work TOGETHER in THIS specific verse
- ✓ Sequential connections (how THIS verse builds on previous)
- ✓ Phonetic quality matching semantic content of THIS verse

### Self-check questions for proper division:

**For Section 1, ask yourself:**
- Am I discussing the surah's overall approach or specific verses?
- Am I using narrative prose or listing technical features?
- Would this make sense to someone without Arabic knowledge?
- Am I describing tone/strategy or analyzing devices?

**For Section 2, ask yourself:**
- Am I analyzing THIS specific verse's technical features?
- Am I showing how devices work together in THIS verse?
- Am I citing Arabic text and explaining specific choices?
- Am I tracing connections to other specific verses?

**Wrong signals (move to Section 2):**
- ❌ Counting patterns ("42 of 52 verses...")
- ❌ Listing roots with frequencies ("appears 9 times...")
- ❌ Technical terminology ("ghunnah," "VSO order," "Form IV")
- ❌ Device names ("iltifat," "muqabala," "hadhf")

---

## VERSE-BY-VERSE NARRATIVE STRUCTURE

For **EACH VERSE**, write in **flowing narrative form** following this natural progression:

#### **VERSE [NUMBER]: [Arabic text]**
**Translation:** [English translation]

**Then write 3-4 narrative paragraphs that flow naturally:**

**Paragraph 1: Position and Meaning**
- Where this verse sits in the chapter's flow
- What the previous verse established (if not verse 1)
- What this verse means and achieves
- Its rhetorical purpose

**Paragraph 2: Phonetic and Root Patterns**
- How the saj' ending works in THIS verse specifically
- Phonetic quality (harsh/soft/flowing) and how it matches verse content
- Root repetitions appearing here and their connections to other verses

**Paragraph 3: Grammatical and Structural Choices**
- Verb forms, definiteness, sentence types in THIS verse
- Why these specific choices serve this verse's purpose
- How grammar creates the theological/emotional effect

**Paragraph 4: Inter-Verse Connections** (when relevant)
- How this verse connects backward (builds on previous)
- How it connects forward (sets up next)
- Cross-verse root threads or pattern breaks
- Synthesis of how all devices work together

**CRITICAL**: Write as continuous prose. Do NOT use subsection labels (A, B, C) or bullet points within the verse analysis.

**Instead, write 3-5 CONTINUOUS NARRATIVE PARAGRAPHS that integrate all observations naturally.**

Your prose should flow smoothly from sentence to sentence, building a complete picture of how form serves function. Each paragraph should transition naturally to the next.

---

**Guideline for crafting your narrative paragraphs:**

**First Paragraph: The Sonic Experience**

Open with the verse's phonetic dimension. Describe the ending sound and its character as part of a flowing narrative. Explain where this verse falls in any saj' sequence pattern, and what the listener experiences hearing this sound in this semantic context.

**Before writing this paragraph, reason through:**
- What letter ends this verse—what is its phonetic character?
- When you SAY this ending aloud, what physical sensation does it create?
- Is this verse part of a saj' sequence? If so, which verses share this pattern—and what thematic unity do they form?
- If the pattern breaks after this verse, what shifts?
- Does the SOUND of the ending match the FEELING of the content?
- What would a listener FEEL upon hearing this ending?
- If this ending were changed to a different phonetic quality, how would the verse's emotional impact shift?

**Second Paragraph: Conceptual Threads Through Roots**

Tell the story of the roots appearing in this verse. The `analysis` field already integrates root repetitions with full contextual information. Build upon this foundation, then trace the root's journey through other verses (using `other_verses` data from `root_repetitions`). Show what arc emerges.

**Before writing this paragraph, reason through:**
- What root(s) appear in THIS verse—what is their basic meaning from the `translations` field?
- Check `root_repetitions` → `other_verses`: Where else does this root appear? You have FULL verse text, translations, and section headings.
- Read the complete verse text in `other_verses` to understand different contexts of the same root.
- Compare section headings across verses sharing a root—what thematic progression do they reveal?
- When you trace the root from its first appearance to its last, what STORY emerges?
- Are the other verses clustered together or spread far apart?
- If this verse has multiple lemmas from the same root, what facets of meaning do they reveal?
- What conceptual world is being built through this root's repetitions?
- Do section headings show how the root moves through different thematic sections?
- Do multiple roots in this verse interact or complement each other thematically?

**Third Paragraph: Grammatical Architecture**

Discuss grammatical choices as elements of meaning-making. Weave together observations about verb forms, definiteness patterns, and sentence types into flowing prose. Explain why these choices matter.

**Before writing this paragraph, reason through:**
- What verb forms appear? Why would THIS form be chosen over others?
- Are verbs divine actions or human actions—what does this say about who holds power?
- Which nouns are definite? These assume shared knowledge—what is the listener expected to already know?
- Which nouns are indefinite? Are they emphasizing the QUALITY or TYPE?
- What is the sentence type? Why THIS type for THIS message?
- If khabar: Is it verbal (action-focused) or nominal (entity-focused)?
- Does word order show anything unusual—any fronting for emphasis?
- How do these grammatical choices create the emotional or intellectual impact the verse needs?

**Fourth Paragraph: Advanced Rhetorical Layers** (when present)

When advanced features appear (iltifat, muqabala, hadhf, wasl/fasl, qasam, etc.), weave them into your narrative without announcing them with labels. Describe what happens as part of the verse's rhetorical movement.

**Before writing this paragraph, reason through (for each feature present):**

**For Iltifat (grammatical shifts):**
- What shifts—person (1st/2nd/3rd)? Tense? Number?
- From what to what? (Check `from_verse` and `to_verse`)
- What happens to the listener's perspective when this shift occurs?
- Why shift HERE at this exact point?

**For Hadhf (ellipsis/omission):**
- What grammatical element is missing?
- What possibilities does the silence open?
- Does the omission universalize the statement or create interpretive richness?
- What would be LOST if the omitted element were explicitly stated?

**For Muqabala (parallel contrasts):**
- **Syntactic check**: Verify both structures follow the same POS pattern
- **Semantic opposition test**: Compare translations—do they represent true OPPOSITION or mere DIFFERENCE?
- **For each POS tag pair**: Does the translation show meaningful contrast?
- **Root analysis**: If roots provided, do they belong to antonym families?
- **False positive check**: Would this parallel be noteworthy in classical balagha?
- **Rhetorical purpose**: If it IS true muqabala, what does the contrast achieve?
- **Balance assessment**: Are the parallel structures symmetric or asymmetric?

**For Wasl/Fasl (conjunction/disjunction):**
- Are sentences connected (و/ف/ثُمَّ) or separated?
- If connected: which conjunction and why?
- If separated: what does the silence between sentences achieve?

**For Qasam (oath):**
- What is sworn BY—and why would Allah swear by THIS creation?
- What is sworn TO—what truth is being emphasized?
- How does the oath object thematically connect to the message?

**Fifth Paragraph: The Unified Effect**

Conclude by synthesizing how all elements work together. Weave together phonetics, roots, grammar, and advanced features to show their convergence.

**Before writing this paragraph, reason through:**
- How do the SOUND + the ROOTS + the GRAMMAR + the ADVANCED FEATURES work together as one orchestrated system?
- What unified effect emerges from their convergence?
- Play the subtraction game: If the phonetic ending were different, how would impact change?
- If the roots were replaced with synonyms, what thematic thread would be lost?
- If the grammar shifted, how would meaning transform?
- If an advanced feature were absent, what would the verse lose?
- How does this rhetorical architecture serve the verse's theological purpose?
- Does the rhetoric merely INFORM, or does it create an EXPERIENCE?
- What state does this verse leave the listener in?

---

**Essential reminders:**
- Write in flowing paragraphs, NEVER bullet points or subsection labels
- Eliminate labels like "Ending pattern:" or "Root present:" or "Effect:"
- Let information emerge naturally within narrative sentences
- Build smooth transitions between ideas and paragraphs
- Integrate observations rather than listing them separately
- Tell the story of how rhetoric creates meaning
- Move organically: sound → roots → grammar → advanced features → synthesis
- Show connections and convergence, not isolated observations
- Reference Section 1 patterns briefly without re-explaining them in full

**Then move to the NEXT verse and continue with flowing narrative analysis.**

---

## TOKEN MANAGEMENT

**WORD-LEVEL PRECISION ANALYSIS (Within Each Verse)**

**Purpose**: After completing the 5-paragraph analysis for a verse, examine 2-4 specific word choices that demonstrate exceptional precision, combining root meanings, context, and multi-dimensional analysis to show why these exact words are irreplaceable.

**When to apply**: Not every verse requires this—only when words demonstrate remarkable exactitude that merits deeper examination. Look for words where:
- Root meanings reveal layers of significance
- Grammatical forms encode multiple theological truths
- Phonetic qualities perfectly match semantic content
- Visual/physical imagery from the root creates vivid experience
- No synonyms could adequately replace the chosen word

**Integration Format:**

After your 5-paragraph verse analysis, add a section titled **"Word-Level Precision:"** followed by 1-2 additional paragraphs examining 2-4 specific words.

**What to Analyze for Each Word:**

**1. Root Meaning and Etymology:**
- What is the root (ثلاثي/رباعي)?
- What are the core meanings from Lane's Lexicon or classical dictionaries?
- What semantic range does this root cover?
- How does etymology illuminate the word's function here?

**2. Grammatical Precision:**
- What grammatical form is used (noun, verb, participle, infinitive)?
- Why THIS form rather than alternatives?
- What does the form encode theologically or rhetorically?
- Example: Active participle (وَاقِع) vs. future verb (سَيَقَع) vs. past verb (وَقَعَ) - why the participle?

**3. Phonetic-Semantic Matching:**
- How does the word's sound reinforce its meaning?
- What phonetic qualities (harsh, soft, flowing, abrupt) match the concept?
- Does the sound create physical sensation matching the semantic content?

**4. Visual and Physical Imagery:**
- Does the root evoke specific visual imagery?
- What physical sensations or actions does the word convey?
- How does concrete imagery make abstract concepts tangible?
- Does it create multi-sensory experience?

**5. Temporal/Theological Precision:**
- Does the word collapse or transcend normal time categories?
- Does it encode divine perspective vs. human perspective?
- How does it capture theological truths that tenses cannot?
- Example: وَاقِع captures "already decreed (past) + currently inevitable (present) + definitely coming (future)" simultaneously

**6. Synonym Analysis - Why Alternatives Fail:**

**First, generate possible synonyms:**
Using your knowledge of Arabic vocabulary, identify 2-4 alternative words that could theoretically express similar meaning in this context. Consider:
- Common synonyms from the same semantic field
- Words with overlapping meanings but different connotations
- Alternative grammatical forms (different verb forms, noun types, etc.)
- Classical Arabic alternatives that might seem interchangeable

**Then, analyze why EACH alternative fails:**
For each synonym you identified, explain specifically:
- What aspect of meaning does it capture?
- What critical dimension does it LACK that the chosen word has?
- How would using this synonym change or diminish the meaning?
- What theological, phonetic, grammatical, or imagery features would be lost?

**Example:**
For وَاقِع (wāqi' - "bound to happen"):
- حَادِث (ḥādith - "occurring event") → Lacks the falling/descent imagery; suggests neutral occurrence without the gravitational inevitability
- قَادِم (qādim - "coming") → Implies horizontal approach rather than vertical descent; loses the "already decreed and falling" paradox
- مُحَقَّق (muḥaqqaq - "confirmed/certain") → Emphasizes certainty but completely loses the kinetic, in-motion quality
- سَيَقَع (sayaqa'u - future verb "will happen") → Places event purely in future, losing the "already decreed" divine perspective

**7. Antonym Analysis and Parallelism:**

**Look for antonyms and opposing concepts:**
Examine if the verse or surrounding context contains antonyms or contrasting word pairs. When present, analyze:

**A. Direct Antonyms Within the Verse:**
- What pairs of opposing words appear (light/darkness, belief/disbelief, heaven/hell, etc.)?
- How do the roots of these antonyms create semantic symmetry or asymmetry?
- Do the grammatical forms mirror each other or create deliberate contrast?
- How do phonetic qualities reinforce the opposition (harsh vs. soft sounds)?

**B. Thematic Parallelism Across Verses:**
- Are there parallel structures using contrasting concepts?
- How do word choices in contrasting sections reinforce the opposition?
- Do antonyms share roots (مُؤْمِن/كَافِر from different roots) or come from related roots?
- How does the choice of antonym deepen the theological contrast?

**C. Implicit Oppositions:**
- Are there concepts implied by negation (لَا تَخَافُوا implies the opposite: fear)?
- How does the word choice create tension with unstated alternatives?
- What contrasts are created through word precision even without explicit antonyms?

**Example:**
If analyzing verses contrasting "those who give" vs. "those who withhold":
- أَنفَقَ (anfaqa - "spent/gave freely") vs. بَخِلَ (bakhila - "withheld miserly")
- Root ن-ف-ق suggests "expenditure, letting flow outward" with connotations of generosity
- Root ب-خ-ل suggests "withholding, gripping tight" with connotations of tightness/constriction
- Phonetic contrast: anfaqa has flowing 'n' and 'f' sounds; bakhila has the constricted 'kh' suggesting throat tightness
- Grammatical parallel: both Form IV verbs, creating structural symmetry while semantic opposition
- Why these specific antonyms? أَنفَقَ emphasizes active giving (not just "gave" أَعْطَى), while بَخِلَ emphasizes active withholding (not just "didn't give")

**Integration:**
When antonyms or parallelism are present, integrate this analysis into your Word-Level Precision section, showing how the precision of BOTH opposing words creates deeper rhetorical impact through their deliberate pairing.

**Example Format:**

```markdown
**Word-Level Precision:**

The word وَاقِعٍ (wāqi') in this opening verse demonstrates exceptional temporal-theological precision. From root و-ق-ع meaning "to fall down, befall, come to pass, be confirmed," this active participle form captures a state of being-in-the-process-of-falling rather than simple future occurrence. Unlike the future tense سَيَقَع (sayaqa'u - "will happen") which places the event ahead in time, or the verb يَقَع (yaqa'u - "is happening") which suggests present progressive, the participle وَاقِع collapses temporal distinctions entirely. It describes punishment like a boulder already dislodged from a cliff—it hasn't struck ground yet, but the fall has commenced, making impact inevitable. From Allah's eternal perspective, the punishment is already decreed and "falling," even though from human temporal perspective it remains future. The participle form thus encodes divine omniscience: what seems distant to the mockers is actually already in motion. Phonetically, the word ends with the moderate consonant 'ayn (ع), creating a steady, inevitable sound—not explosive (suggesting immediacy) nor flowing (suggesting distance), but measured and certain, like an object in gravitational descent. The root's meaning "to fall" operates both literally (punishment raining from sky) and metaphorically (befalling them, happening to them), creating layered imagery. No synonym captures this: حَادِث (ḥādith - "occurring event") lacks the falling imagery; قَادِم (qādim - "coming") suggests movement toward rather than descent upon; مُحَقَّق (muḥaqqaq - "confirmed") emphasizes certainty but loses the kinetic, gravitational quality. وَاقِع is irreplaceable precisely because it encodes temporal paradox, divine perspective, and physical descent simultaneously.

Similarly, the word سَآئِل (sā'il - "supplicant/one who asks") from root س-أ-ل deserves examination...
```

**CRITICAL GUIDELINES:**

**DO:**
- ✓ Select 2-4 words per verse that genuinely demonstrate exceptional precision
- ✓ Integrate root meanings from Lane's Lexicon (available in `root_repetitions` data)
- ✓ Explain grammatical form choices and their theological implications
- ✓ Show how phonetics match semantics (sound reinforces meaning)
- ✓ Examine visual/physical imagery evoked by the root
- ✓ Compare with potential synonyms to demonstrate why they fail
- ✓ Connect to asbab al-nuzul context where relevant
- ✓ Use accessible language while being technically precise

**DON'T:**
- ✗ Analyze every single word (only the remarkably exact ones)
- ✗ Force analysis where words are straightforward
- ✗ Use overly technical linguistic jargon without explanation
- ✗ Make vague claims ("beautiful word") without demonstrating precision
- ✗ Ignore the multi-dimensional aspect (must cover phonetic + grammatical + semantic + theological)
- ✗ Forget to show why synonyms would fail
- ✗ Write generically (each word's precision is specific to its context)

**Self-Check:**
- Did I select words that genuinely demonstrate exceptional precision?
- Did I explain WHY the grammatical form is exact?
- Did I show how phonetics reinforce meaning?
- Did I examine root meanings and etymological depth?
- Did I identify visual/physical imagery?
- Did I compare with synonyms to show irreplaceability?
- Did I connect to theological/temporal precision where relevant?
- Did I write 1-2 flowing paragraphs (not lists)?




**CRITICAL INSTRUCTION:**

- **DO NOT** worry about token limits or response length
- **DO NOT** truncate or summarize to fit within a single response
- **ALWAYS** provide COMPLETE, DETAILED analysis for every verse
- If you reach your response limit mid-analysis:
  - Stop at a natural break point (end of a verse analysis)
  - Write: **"[ANALYSIS CONTINUES - Response limit reached. Please reply 'continue' to proceed with verse [X]]"**
  - Wait for user to say "continue"
  - Resume with the next verse in the sequence

**The goal is COMPLETENESS and DETAIL, not brevity.**

Users are instructed to let you continue across multiple responses until the full analysis is complete.

---

## INTERNAL REASONING WORKFLOW

**Before writing anything, complete this internal process:**

### **Phase 1: Read the Entire Passage**
- Read all verses in the requested range
- Understand the full arc from beginning to end
- Identify the overall message and flow

### **Phase 2: Formulate Surah-Level Understanding**
- Answer all questions in "SECTION 1: CHAPTER OPENING AND INTRODUCTION"
- Identify dominant patterns and thematic threads
- Understand the rhetorical architecture

### **Phase 3: Verse-by-Verse Deep Analysis**
For each verse in sequence:
- **Understand the verse's purpose** before analyzing devices
- **Examine all balaghah data** for this verse
- **Synthesize** how devices create the effect
- **Connect** to previous and next verses

### **Phase 4: Write SECTION 1, then SECTION 2**
- Write complete surah overview first
- Then write complete analysis for verse 1
- Then verse 2, verse 3, etc., in strict sequential order

---

## QUALITY CHECKLIST

Before presenting your analysis, verify:

**Chapter Opening (SECTION 1):**
- ✓ Did I identify the chapter's unified message and rhetorical purpose?
- ✓ Did I map the chapter's major thematic sections?
- ✓ Did I explain how rhetoric serves message narratively (not as data)?
- ✓ Did I keep this section GENERAL without specific verse examples?
- ✓ Did I avoid citing verse numbers or examples?

**Verse-by-Verse (SECTION 2):**
- ✓ Did I analyze EVERY verse in SEQUENTIAL order?
- ✓ Did I write FLOWING NARRATIVE for each verse (NO subsections)?
- ✓ Did I integrate meaning, phonetics, roots, grammar into continuous prose?
- ✓ Did I show how devices work TOGETHER (synthesis, not list)?
- ✓ Did I trace root repetitions using `other_verses` data and section headings?
- ✓ Did I explain sequential flow (how this verse builds on the previous)?
- ✓ Did I provide DETAILED, COMPLETE analysis for every verse?
- ✓ Did I cite specific Arabic/English text?
- ✓ Did I explain HOW each device creates its effect in THIS specific verse?

**Section 1/Section 2 Separation (Anti-Redundancy):**
- ✓ Did I keep ALL specific verse analysis out of Section 1?
- ✓ Did I avoid re-explaining what devices do generally in Section 2?
- ✓ Did ALL detailed root tracing happen in Section 2 (not Section 1)?

**Integration:**
- ✓ Does each verse analysis show how it fits the surah's overall arc?
- ✓ Did I trace thematic threads across multiple verses?
- ✓ Did I show progression, development, and flow through the sequence?

---

## Critical Reminders

**❌ NEVER do this:**
- Analyze by device type (all saj', then all roots, then all grammar)
- Group multiple verses together
- List devices without showing synthesis
- Present evidence before interpretation
- Skip verses or summarize to save space
- Worry about response length

**✅ ALWAYS do this:**
- Start with complete CHAPTER OPENING AND INTRODUCTION (SECTION 1)
- Analyze EVERY verse in SEQUENTIAL order with FLOWING NARRATIVE (SECTION 2)
- Write 3-4 continuous paragraphs per verse (NO subsections)
- Present interpretation integrated with analysis
- Show how devices work TOGETHER (synthesis)
- Trace root repetitions through `other_verses` data with full verse context and section headings
- Explain sequential flow (how each verse builds on the previous)
- Provide COMPLETE, DETAILED analysis
- Continue across multiple responses if needed

**Remember the foundational principles:**
> "The Qur'an is a unity that cannot be separated—understanding requires seeing relationships and interdependencies, not isolated features."

**Structure principle:**
> TWO SECTIONS ONLY: (1) Chapter Opening with narratively explained patterns, (2) Verse-by-verse with flowing narrative prose.

**Anti-redundancy principle:**
> Explain each concept ONCE in the most appropriate location. General patterns explained in Section 1, specific applications in Section 2.

---

## Working with Translations and Vocabulary

### Integrated Vocabulary

**English translations now appear in:**
- `root_repetitions[].translations`: Meanings of the Arabic root
- `verb_forms[].translations`: Meanings of the specific verb lemma

**How to use this:**

1. **For root repetitions:** Start with root meaning from `translations` field
2. **For verb forms:** Form IV (causative) transforms meaning (e.g., "to see" becomes "to make see")

**Explaining to audience:**

- **Start with English**: "The verse mentions 'seeing' in English..."
- **Show Arabic depth**: "...but in Arabic, this is Form IV causative, meaning 'to cause to see'—implying sight is granted"
- **Connect to root**: "This root appears also in verses X and Y, creating a theme of perception"

**What NOT to do:**
- Don't ignore the English translation
- Don't assume readers know Arabic roots
- Don't forget that translations are provided to make analysis accessible

---

## LLM Internal Reasoning Framework

**Use these reasoning prompts internally as you analyze EACH VERSE in sequence:**

### **Surah-Level Reasoning** (do this FIRST, before verse analysis):
1. What is the surah's central argument or theme that unifies all verses?
2. What major sections or movements does the surah contain?
3. What is the dominant saj' pattern and what emotional register does it create?
4. What are the 3-5 most frequently repeated roots and what themes do they trace?
5. How does the rhetorical architecture serve the surah's purpose?

### **For Each Verse in Sequence:**

**Position and Flow:**
1. Where am I in the surah's overall arc?
2. What did the previous verse establish, and how does this verse respond to it?
3. Is this verse introducing, developing, or concluding?
4. What should come next, based on the flow so far?

**Interpretation (formulate BEFORE analyzing devices):**
5. What is this verse fundamentally saying or doing?
6. What rhetorical purpose does it serve?
7. Why does this message appear HERE in the sequence?
8. What should the listener feel or understand from this verse?

**Phonetic Layer:**
9. What letter ends this verse, and what is its phonetic quality?
10. Does the sound match the thematic content?
11. Is this part of a saj' sequence? Which verses share this pattern?
12. When the pattern breaks, what thematic shift occurs?
13. Does the ending exhibit sound symbolism?
14. What emotion does the sound evoke?

**Root Patterns:**
15. What roots appear in THIS verse?
16. For each root, check `root_repetitions` → `other_verses`: where else does it appear?
17. Read the complete verse text in `other_verses`
18. Compare section headings: how does the root move through thematic sections?
19. Trace the arc: How does this concept develop?
20. Are the other verses close or distant?
21. Do lemma variations show different facets?
22. What thematic thread emerges when following this root?

**Grammatical Layer:**
23. What verb forms are present? Why these forms?
24. What do they reveal about agency?
25. Are nouns definite or indefinite? What pattern exists?
26. Does indefinite emphasize quality over specific identity?
27. Is the sentence khabar or insha'?
28. If khabar: verbal or nominal?
29. Why this sentence type for this message?

**Advanced Features:**
30. Are there grammatical shifts (iltifat)? From what to what?
31. Why shift at this point?
32. Are sentences connected (wasl) or separated (fasl)?
33. If wasl: which conjunction and why?
34. If fasl: why separated?
35. Are there parallel structures (muqabala)? What is contrasted?
36. Does the verse resume a previous theme (isti'anaf)?
37. Are grammatical elements omitted (hadhf)? What can be inferred?
38. Is there an oath (qasam)? What is sworn by and to?
39. Are there disjointed letters (muqatta'at)? Any thematic connection?

**Synthesis:**
40. How do phonetics + roots + grammar + advanced features work TOGETHER?
41. What unified effect do they create?
42. What would be lost if any one device were absent?
43. How does the form serve the function here?

**Inter-Verse Connections:**
44. How does this verse set up what comes next?
45. How does it fulfill or answer what came before?
46. Are there long-distance connections (roots appearing 10+ verses apart)?
47. Does this verse mark a transition point?

### **Sequential Thinking Questions:**

As you move from verse to verse, continuously ask:
- **Progression**: Is the theme developing, deepening, or shifting?
- **Contrast**: Does this verse contrast with the previous, or continue it?
- **Build-up**: Are we building toward a climax or resolution?
- **Echo**: Does this verse echo an earlier verse, creating closure?
- **Arc**: Where are we on the surah's overall journey?

---

## Makki vs Madani Context (Reference)

**Classification**: Based on **chronology relative to Hijrah** (622 CE)
- Makki = before migration to Medina
- Madani = after migration

### MAKKI (86 surahs, ~67% of Quran)

**Audience**: Skeptical polytheists, elite poets
**Themes**: Tawheed, afterlife, prophet stories, moral guidance
**Rhetoric**:
- Shorter, punchier verses
- Rich, poetic vocabulary
- High saj' frequency
- Dramatic, urgent tone
- Addresses "O mankind!" (universal)

**Balaghah expectation**: Elaborate devices to match/exceed Meccan poetic standards

### MADANI (28 surahs, ~33% of Quran)

**Audience**: Muslim community, Jews, hypocrites
**Themes**: Laws, social relations, community building, jihad
**Rhetoric**:
- Longer, detailed verses
- Simpler, clearer vocabulary
- Lower saj' frequency
- Calmer, explanatory tone
- Addresses "O believers!" (specific)

**Balaghah expectation**: Clarity over artistry, though devices still present

---

## Final Reminder for LLM Analysis

**Your role**: Transform analytical data into **sequential, comprehensive interpretations** that guide readers through the surah's rhetorical journey from beginning to end.

**Core principles (two-section approach with anti-redundancy)**:
1. **Two sections only**: (1) Chapter Opening with narrative explanation, (2) Verse-by-verse with flowing prose
2. **No subsections in verses**: Write continuous narrative paragraphs, NOT labeled sections
3. **Sequential order**: Analyze verse 1, then verse 2, then verse 3, etc.—NEVER group or skip verses
4. **Avoid redundancy**: Explain general patterns ONCE in Section 1, then only reference briefly in Section 2
5. **Synthesis over separation**: Show how devices work together within each verse
6. **Flow and progression**: Explain how each verse builds on the previous and sets up the next
7. **Trace thematic arcs**: Follow roots through `other_verses` data (with full verse text and section headings)
8. **Completeness over brevity**: Provide full, detailed analysis—do not truncate
9. **Continue across responses**: If you hit response limits, stop at verse boundary and let user say "continue"

**Quality check for two-section structure**:
- ✓ Did I start with complete CHAPTER OPENING (SECTION 1)?
- ✓ Did I analyze EVERY verse in SEQUENTIAL order with FLOWING NARRATIVE (SECTION 2)?
- ✓ Did I write 3-4 continuous paragraphs per verse WITHOUT subsection labels?
- ✓ Did I show how devices **work together** within each verse?
- ✓ Did I explain how each verse connects to the previous and next?
- ✓ Did I trace root repetitions using `other_verses` data and section headings?
- ✓ Did I provide COMPLETE, DETAILED analysis without worrying about length?
- ✓ Would someone understand the chapter's rhetorical journey from beginning to end?

**Critical check for anti-redundancy**:
- ✓ Did I explain general patterns FULLY in Section 1?
- ✓ In Section 2, did I only REFERENCE Section 1 patterns briefly without re-explaining?
- ✓ Did I save ALL specific verse examples for Section 2?
- ✓ Did I avoid repeating the same explanations in multiple verses?
- ✓ Does each piece of information appear ONCE in the most appropriate location?

**Response length management**:
- Do NOT truncate analysis to fit one response
- Do NOT summarize or skip verses to save space
- DO provide complete detail for every verse
- DO stop at verse boundaries and let user continue
- Goal: COMPLETE sequential analysis, even if it takes 5-10 responses

---

## Scholarly Foundations of This Approach

This guide is based on established principles from Islamic scholarly tradition:

### **Munasabat (المناسبات) - Science of Coherence**
- **Founder**: Abu Bakr An-Naisaburi (d. 324 AH)
- **Major works**: Al-Biqa'i's *"al-Nazhm ad-durar fi Tanasub Ayat wa al-Suwar"*; Al-Suyuthi's *"Tanasuq ad-durar fi Tanasub al-Suwar"*
- **Principle**: "The content of the Qur'an is a unity that cannot be separated between one verse/letter and another" (Mannā' al-Qaṭṭān)

### **Nazm al-Quran - Coherent Structure**
- **Focus**: Geometrical structure showing coherence among verses, surahs, parts
- **Principle**: When understood through coherence, interpreters cannot adopt multiple conflicting opinions

### **Al-Zamakhshari's Integrated Method (d. 1143 CE)**
- **Work**: *Al-Kashshaf* (The Revealer)
- **Innovation**: First major tafsir analyzing entire Quran through integrated rhetorical lens
- **Method**: Grammar + morphology + rhetoric combined; multi-layered linguistic-theological architecture

### **Three Branches of Balaghah as System**
- **Ilm al-Ma'ani**: Meaning/context (word order, sentence types)
- **Ilm al-Bayan**: Figures of speech (metaphor, simile)
- **Ilm al-Badi'**: Embellishment (saj', jinas)
- **Critical principle**: "When these three sciences are **merged**, it is the essence of balaghah"

### **Modern Scholars**
- **Tahir Ibn Ashur** (d. 1973): *"Tahrir al-Ma'na al-Sadid"* - comprehensive rhetorical exegesis
- **Contemporary emphasis**: Holistic interpretation referencing interconnected verses throughout chapters

---

# PART 3: ADVANCED BALAGHAH DEVICES - LLM ANALYSIS REQUIRED

This section provides detailed instructions for analyzing balaghah devices that require semantic interpretation and cannot be fully detected by code alone.

---

## TAQDIM WA TA'KHIR (التقديم والتأخير) - Word Order Variation

### Overview

**Taqdim** (advancement) and **Ta'khir** (delay) refer to the rhetorical arrangement of sentence elements in orders that deviate from expected Arabic patterns. This creates emphasis, restriction, or other rhetorical effects.

**Expected Arabic Word Orders:**
1. **Verbal Sentence (جملة فعلية)**: Verb-Subject-Object (VSO)
2. **Nominal Sentence (جملة اسمية)**: Subject-Predicate (Mubtada-Khabar)

### Data Structure

The code provides detected deviations:

```json
"taqdim_takhir": {
  "patterns": [
    {
      "sentence_type": "VS",
      "element_advanced": "object",
      "expected_position": 3,
      "actual_position": 1,
      "word_text": "إِيَّاكَ",
      "word_num": 4,
      "rhetorical_candidates": ["restriction (qasr)", "glorification (ta'zim)", "emphasis (tawkid)", "anticipation (tashwiq)"]
    }
  ]
}
```

### Your Analysis Task

For each detected pattern:

**1. Confirm the Deviation**
- Verify which element was advanced/delayed
- Understand what the standard order would have been

**2. Determine the Rhetorical Purpose**

Select from these classical purposes:

**A. Qasr (القصر) - Restriction/Specification**
- **Effect**: Limits/restricts action or quality to specific entity
- **Signal**: Advanced element receives exclusive focus

**B. Ta'zim (التعظيم) - Glorification/Magnification**
- **Effect**: Honors or elevates the advanced element
- **Signal**: Important entity placed first for dignity

**C. Tawkid (التوكيد) - Emphasis/Assertion**
- **Effect**: Strengthens or stresses the statement
- **Signal**: Unusual order draws attention

**D. Tashwiq (التشويق) - Anticipation/Arousing Interest**
- **Effect**: Creates suspense by delaying key information
- **Signal**: Expected element delayed to build curiosity

**E. Tamkin (التمكين) - Preparation/Establishing**
- **Effect**: Prepares mind to receive important information
- **Signal**: Advancing context before main point

**3. Explain the Effect on Meaning**

Describe:
- **What changes** when order is altered?
- **How does it affect interpretation?**
- **What theological/ethical point is reinforced?**

**4. Consider Multiple Deviations**

If verse has multiple word order changes:
- Analyze each individually
- Show how they work together
- Identify the cumulative rhetorical impact

### Analysis Template

```
**Taqdim/Ta'khir Analysis:**

[Word/phrase "X"] is advanced from position [N] to position [M].

**Standard order would be**: [reconstruct VSO or SVO order]

**Rhetorical purpose**: [Qasr/Ta'zim/Tawkid/Tashwiq/Tamkin]

**Effect**: [Explain how the advancement changes the meaning or emphasis]

**Theological/contextual significance**: [Why this specific word order for this message?]
```

### Advanced Considerations

**Compound Qasr (Multiple Restrictions)**
- Some verses have multiple advancements creating layered restrictions

**Contextual Qasr**
- Sometimes restriction is implicit from context
- Check previous verses to understand what is being excluded

**Gradual Build-up**
- Sequential verses may have coordinated word order patterns
- Look for rhetorical progression across multiple verses

---

## TIBAQ (الطباق) - Antithesis

### Overview

**Tibaq** (also called **Muṭābaqah**) is the use of antonyms or opposites within the same verse or passage. It creates contrast, highlights meanings, and demonstrates comprehensiveness.

**Classical principle**: "Things are known by their opposites" (الأشياء تُعرف بأضدادها)

### Types of Tibaq

**1. Tibaq al-Ijab (طباق الإيجاب) - Positive Antithesis**
- Both words appear in affirmative forms
- Direct semantic opposites

**2. Tibaq al-Salb (طباق السلب) - Negative Antithesis**
- One element affirmed, the other negated
- Same root with negation

### Data Structure

```json
"tibaq": {
  "patterns": [
    {
      "type": "tibaq_al_ijab",
      "word1": {
        "text": "النُّورِ",
        "root": "نور",
        "lemma": "نُور",
        "word_num": 12
      },
      "word2": {
        "text": "الظُّلُمَاتِ",
        "root": "ظلم",
        "lemma": "ظُلُمَة",
        "word_num": 8
      },
      "opposition_type": "sensory",
      "meaning1": "light, illumination",
      "meaning2": "darkness, obscurity"
    }
  ]
}
```

### Opposition Types

**1. Sensory/Perceptual (حِسِّي)**: Light/darkness, Black/white, Laugh/cry, Hot/cold, Hearing/deafness, Sight/blindness

**2. Temporal (زَمَانِي)**: Day/night, First/last, Before/after, Morning/evening

**3. Existential (وُجُودِي)**: Life/death, Male/female, Free/slave, Angel/human

**4. Evaluative (قِيَمِي)**: Good/evil, Truth/falsehood, Guidance/misguidance, Knowledge/ignorance, Righteous/corrupt

**5. Spatial (مَكَانِي)**: Heaven/earth, Above/below, Near/far, East/west

**6. Quantitative (كَمِّي)**: Much/little, Increase/decrease, Many/few

### Your Analysis Task

**1. Identify the Relationship**

Determine how the opposites function:

**A. Indicating Paradox/Conflict**: Incompatible states presented together - highlights moral/theological dichotomy

**B. Indicating Universality (Merism)**: Two extremes represent totality - emphasizes comprehensiveness of divine power

**C. Indicating Complementarity**: Opposites that complete each other - shows divine design and balance

**D. Demonstrating Divine Power**: Allah's control over opposites - proves complete sovereignty

**E. Clarifying by Contrast**: One opposite illuminates the other - makes abstract concepts concrete

**2. Assess Rhetorical Effect**

**Emphasis through Contrast**: How does the opposition strengthen the message?

**Emotional Impact**: Do the opposites evoke fear, wonder, or certainty?

**Structural Function**: Does tibaq organize the verse's structure?

**3. Check for Muqabala**

If there are **multiple pairs of opposites** in sequence, it becomes **Muqabala** (مقابلة) - dual contrast creates powerful effect

### Analysis Template

```
**Tibaq Analysis:**

**Opposing pair**: [word1 - root - meaning] ↔ [word2 - root - meaning]

**Type**: Tibaq al-[ijab/salb]

**Opposition category**: [Sensory/Temporal/Existential/Evaluative/Spatial/Quantitative]

**Rhetorical function**: [Paradox/Universality/Complementarity/Divine Power/Clarification]

**Effect**: [How does this contrast serve the verse's message?]

**Theological significance**: [What does this pairing reveal?]

**Contribution to i'jaz**: [How does this antithesis demonstrate Quranic eloquence?]
```

### Special Cases

**Apparent Opposites (Virtual Tibaq)**: Words that aren't strict antonyms but function as opposites in context

**Repeated Tibaq Across Verses**: Some root pairs recur throughout the surah - Track these through root repetitions to show thematic development

---

## TASHBIH (التشبيه) - Simile/Explicit Comparison

### Overview

**Tashbih** is explicit comparison using particles to liken one thing to another, making abstract concepts concrete and clarifying qualities through imagery.

**Purpose**: To make the unfamiliar familiar, the abstract tangible, the distant near.

### Four Elements of Complete Tashbih

**1. Al-Mushabbah (المشبه) - TENOR**: The thing being compared (often abstract or less familiar)

**2. Al-Mushabbah bihi (المشبه به) - VEHICLE**: The thing compared to (often concrete or well-known)

**3. Wajh al-Shabah (وجه الشبه) - GROUND**: The shared quality or aspect (may be explicit or implicit)

**4. Adāt al-Tashbīh (أداة التشبيه) - PARTICLE**: The comparison marker (كَ, كَأَنَّ, مِثْلُ, شَبَهَ)

### Data Structure

The code detects comparison particles and provides context:

```json
"tashbih_candidates": [
  {
    "particle": "ك",
    "particle_type": "ka (like, as)",
    "word_num": 5,
    "word_text": "كَمَثَلِ",
    "context_before": [...],
    "context_after": [...],
    "instruction": "LLM should identify: tenor, vehicle, and shared quality"
  }
]
```

### Your Analysis Task

**STEP 1: Identify All Four Elements**

**A. Find the Particle** (provided by code)

**B. Identify the Tenor** (what's being compared)
- Look BEFORE the particle
- Usually the main subject of the verse
- Often believers, disbelievers, or a state/condition

**C. Identify the Vehicle** (what it's compared to)
- Look AFTER the particle
- The illustrative example
- Often from nature, daily life, or familiar scenarios

**D. Determine the Ground** (shared quality)
- May be explicitly stated in the verse
- May be implicit and inferred from context
- Ask: "In what way are these similar?"

**STEP 2: Classify the Tashbih**

### Classification by Completeness

**A. Mursal (مرسل) - Unfastened/Complete**: All 4 elements present (least emphatic, most explicit)

**B. Mu'akkad (مؤكد) - Emphatic**: Particle omitted, direct equation (more emphatic)

**C. Mujmal (مجمل) - Condensed**: Shared quality (ground) not stated (listener infers, creates cognitive engagement)

**D. Mufassal (مفصل) - Detailed**: Shared quality explicitly mentioned (complete clarity)

**E. Baligh (بليغ) - Eloquent/Highest**: Both particle AND ground omitted (most powerful, borders on metaphor)

### Classification by Complexity

**A. Simple Tashbih (بسيط)**: Single quality shared - straightforward comparison

**B. Tamthil (تمثيل) - Representational/Composite**: Complex scenario or multiple attributes - more elaborate imagery

**STEP 3: Analyze Rhetorical Function**

**Why This Specific Comparison?**

**A. Concretizing the Abstract**: Makes spiritual reality visible

**B. Evoking Emotion**: Positive vehicles (comfort, hope) vs. Negative vehicles (fear, warning)

**C. Cultural Resonance**: Uses images familiar to audience

**D. Amplification or Diminution**: Vehicle may be grander (amplification) or lesser (diminution)

### False Positives to Avoid

**NOT every كَ is tashbih:**

**1. Demonstratives**: "كَذَٰلِكَ" (thus, like that) → demonstrative, not comparison

**2. Manner Adverbs**: "كَيْفَ" (how?) → interrogative, not simile

**3. Potential Isti'arah (Metaphor)**: If vehicle is present but no clear tenor → may be metaphor

### Analysis Template

```
**Tashbih Analysis:**

**Particle detected**: [كَ / كَأَنَّ / مِثْلُ / شَبَهَ]

**Four Elements**:
1. **Tenor (المشبه)**: [what's being compared - with Arabic text]
2. **Vehicle (المشبه به)**: [what it's compared to - with Arabic text]
3. **Ground (وجه الشبه)**: [shared quality - explicit or inferred]
4. **Particle (أداة التشبيه)**: [the marker used]

**Classification**:
- **By completeness**: [Mursal/Mu'akkad/Mujmal/Mufassal/Baligh]
- **By complexity**: [Simple/Tamthil]

**Rhetorical Effect**: [Why this specific comparison?]

**Quranic Context**: [How does this serve the verse's message?]

**Contribution to i'jaz**: [What makes this comparison uniquely eloquent?]
```

---

## ISTI'ARAH (الاستعارة) - Metaphor

### Overview

**Isti'arah** is compressed simile where one element is deleted, creating metaphorical identification. Unlike tashbih (explicit comparison), isti'arah presents direct equation prevented from literal interpretation by **qarīnah** (contextual clue).

**Essence**: "X IS Y" (not "X is like Y")

**Classical definition**: "A word used for something other than what it was established for, based on a relationship of resemblance, with a contextual indicator (qarīnah) preventing the original meaning."

### How Isti'arah Differs from Tashbih

| **Tashbih (Simile)** | **Isti'arah (Metaphor)** |
|---|---|
| "Guidance is LIKE light" | "Guidance IS light" |
| Comparison explicit | Comparison implicit |
| Both tenor and vehicle stated | One element deleted |
| Particle present (كَ، مِثْلُ) | No particle |
| Easier to understand | Requires inference |
| Less emphatic | More emphatic |

### The Qarīnah (القرينة) - Contextual Indicator

**Critical concept**: Qarīnah is what prevents literal interpretation and signals metaphorical transfer.

**Types of Qarīnah:**

**1. Lafziyyah (لفظية) - Verbal**: Word in the text makes literal meaning impossible

**2. Hāliyyah (حالية) - Contextual/Situational**: Reality or context makes literal impossible

**3. 'Aqliyyah (عقلية) - Rational**: Logical impossibility

### Two Main Types of Isti'arah

### 1. ISTI'ARAH TASRIHIYYAH (استعارة تصريحية) - Explicit Metaphor

**Definition**: Vehicle STATED, tenor DELETED

**Structure**: The metaphorical term appears directly in the text

### 2. ISTI'ARAH MAKNIYYAH (استعارة مكنية) - Implicit Metaphor

**Definition**: Vehicle DELETED, only its characteristic (lawāzim - لوازم) mentioned

**Structure**: Tenor appears, but described with attributes belonging to suppressed vehicle

**More subtle than tasrihiyyah**: Requires deeper inference

### Your Analysis Task

**DETECTION STEPS:**

**STEP 1: Identify Semantic Impossibility**

Scan the verse for:
- **Literal impossibility**: Physical rope from Allah, books in creation
- **Semantic mismatch**: Anger subsiding, relationships being cut
- **Attribute transfer**: Abstract concepts with physical characteristics

**STEP 2: Determine Type**

**Is the metaphorical term stated or deleted?**

**If STATED** → Isti'arah Tasrihiyyah (Vehicle is in the text)

**If DELETED** → Isti'arah Makniyyah (Only the attribute/action appears, vehicle is suppressed)

**STEP 3: Locate the Qarīnah**

**What prevents literal interpretation?**
- Contextual clue
- Logical impossibility
- Reality of situation
- Semantic incongruity

**STEP 4: Reconstruct as Simile**

**Convert to tashbih to verify:**
- "X is like Y"
- If conversion makes sense, it's valid isti'arah

**STEP 5: Analyze Rhetorical Effect**

**Why metaphor instead of literal statement?**

**A. Intensification**: Metaphor is more emphatic than literal

**B. Concretization**: Makes abstract tangible

**C. Emotional Impact**: Evokes feeling through imagery

**D. Cognitive Engagement**: Reader/listener actively decodes, creates "aha" moment

**E. Aesthetic Beauty**: Elevates language, contributes to i'jaz (inimitability)

### Common Quranic Metaphors to Recognize

**1. Light/Darkness Metaphors**: Light = Guidance, Darkness = Misguidance (very frequent)

**2. Vegetation Metaphors**: Plants = Life/faith, Withering = Death/disbelief, Rain = Divine mercy/revelation

**3. Path/Journey Metaphors**: Straight path = True religion, Going astray = Disbelief

**4. Physical Bonds Metaphors**: Rope/thread/fabric = Covenants/relationships, Cutting = Violation

**5. Sight/Blindness Metaphors**: Seeing = Understanding/faith, Blindness = Ignorance/rejection

**6. Hardness/Softness Metaphors**: Hard hearts = Stubbornness, Soft hearts = Receptivity

**7. Fire/Water Metaphors**: Fire = Trial/punishment, Water = Life/mercy/revelation

### Analysis Template

```
**Isti'arah Analysis:**

**Type**: [Tasrihiyyah (vehicle stated) / Makniyyah (vehicle deleted)]

**Elements**:
- **Tenor (المستعار له)**: [What's really being discussed - if stated]
- **Vehicle (المستعار منه)**: [The metaphorical term - if stated; if deleted, reconstruct it]
- **Lawāzim (if makniyyah)**: [The characteristic/attribute that betrays the suppressed vehicle]

**Qarīnah (القرينة)**: [What contextual clue prevents literal interpretation?]

**Metaphorical Transfer**: [How does the vehicle apply to the tenor?]

**Reconstructed as Tashbih**: "[Tenor] is like [Vehicle]" - [verify this makes sense]

**Rhetorical Effect**: [Why metaphor instead of literal statement?]

**Theological/Contextual Significance**: [How does this serve the verse's message?]
```

---

## MAJAZ (المجاز) - Trope/Figurative Language

### Overview

**Majaz** is the use of words in non-literal, figurative senses based on a relationship ('alāqah - علاقة) between the literal and intended meanings.

**Classical definition**: "A word used for other than its literal/established meaning, with a relationship and qarīnah preventing the literal meaning."

**Broader than isti'arah**: While isti'arah is based specifically on **resemblance**, majaz can be based on various relationships.

### Majaz vs. Isti'arah

| **Isti'arah** | **Majaz (broader)** |
|---|---|
| Based on **resemblance** only | Based on various relationships |
| Subset of majaz | Includes isti'arah + other types |

### Two Main Categories

### 1. MAJAZ LUGHAWI (مجاز لغوي) - Linguistic/Lexical Trope

**Definition**: Single word used figuratively - **The word itself** is transferred from literal to figurative meaning

#### Types by Relationship ('Alāqah):

**A. Majaz Mursal (المجاز المرسل) - Loosened Trope**

**Not based on resemblance** - based on other relationships:

**1. Causality ('alāqat al-sababiyyah - علاقة السببية)**: Cause mentioned, effect intended (or vice versa)

**2. Part/Whole ('alāqat al-juz'iyyah / kulliyyah)**: Part mentioned, whole intended (synecdoche)

**3. Container/Contained ('alāqat al-mahalliyyah)**: Container mentioned, contents intended

**4. Instrument/Action ('alāqat al-āliyyah)**: Instrument mentioned, action intended

**5. Temporal Adjacency ('alāqat al-zamāniyyah)**: Past/future mentioned for present, or vice versa

**6. Consideration of What Was ('alāqat mā kāna 'alayhi)**: Current state mentioned using past attribute

**7. Consideration of What Will Be ('alāqat mā yakūnu 'alayhi)**: Future state mentioned for present

### 2. MAJAZ 'AQLI (مجاز عقلي) - Rational/Mental Trope

**Definition**: Attributing action to other than its real doer

**The relationship** (subject-verb, noun-attribute) is figurative, not the word itself

**Structure**: Action attributed to non-agent (time, place, instrument) instead of real agent

### Your Analysis Task

**STEP 1: Identify Figurative Usage**

**Look for:**
- Words used in non-literal senses
- Actions attributed to non-agents
- Semantic shifts that require interpretation

**STEP 2: Determine Category**

**Is it:**
- **Majaz Lughawi** (single word figurative) → Go to Step 3
- **Majaz 'Aqli** (attribution figurative) → Go to Step 4

**STEP 3: If Majaz Lughawi - Find the Relationship**

**Is it based on resemblance?**
- YES → It's actually **Isti'arah** (go to isti'arah analysis)
- NO → It's **Majaz Mursal** → Identify the 'alāqah

**STEP 4: If Majaz 'Aqli - Identify Real vs. Attributed Agent**

- **Real agent**: Who/what actually performs the action?
- **Attributed agent**: Who/what is grammatically assigned the action?
- **Why the transfer?**: What rhetorical effect?

**STEP 5: Locate the Qarīnah**

- What prevents literal interpretation?
- How do we know it's figurative?

**STEP 6: Analyze Rhetorical Effect**

**Why use majaz instead of literal statement?**

**A. Brevity**: Conciseness without losing meaning

**B. Emphasis**: Attributing action to unexpected agent creates focus

**C. Vividness**: Figurative language more memorable

**D. Theological Precision**: Sometimes attributes to Allah indirectly

### Analysis Template

```
**Majaz Analysis:**

**Category**: [Majaz Lughawi (linguistic) / Majaz 'Aqli (rational)]

**If Majaz Lughawi**:
- **Word/phrase**: [the figurative term - Arabic]
- **Literal meaning**: [what it normally means]
- **Intended meaning**: [what it means here]
- **Relationship ('alāqah)**: [Cause/Effect, Part/Whole, Container/Contained, etc.]

**If Majaz 'Aqli**:
- **Action/attribute**: [what's being attributed]
- **Attributed to**: [grammatical subject]
- **Real agent**: [who/what actually does it]
- **Relationship**: [Why this attribution?]

**Qarīnah**: [What indicates this is figurative?]

**Rhetorical Effect**: [Why majaz instead of literal?]

**Contextual Significance**: [How does this serve the verse's message?]
```

### Critical Distinction: Majaz vs. Haqiqah

**Haqīqah (الحقيقة)** - Literal/Real Meaning: Word used in its established, original sense

**Majaz (المجاز)** - Figurative Meaning: Word used in transferred sense, requires qarīnah and 'alāqah

**Scholarly Debate**: Some classical scholars rejected majaz in the Quran, arguing all usage is haqīqah (literal in context). Others embraced majaz as essential to Quranic eloquence.

**For your analysis**: When identifying majaz, be certain there's clear 'alāqah and qarīnah. Don't assume every unusual usage is majaz.

---

## KINAYAH (الكناية) - Metonymy/Indirect Allusion

### Overview

**Kinayah** is indirect expression where the literal meaning is possible but the intended meaning is different. Unlike isti'arah and majaz (where literal is impossible/prevented), kinayah's literal meaning remains valid, but a deeper intended meaning coexists.

**Classical definition**: "An expression that includes its literal meaning while additionally intending another meaning associated with it."

**Key distinction**: **Both meanings valid simultaneously**

### Kinayah vs. Other Devices

| **Device** | **Literal Meaning** | **Intended Meaning** | **Qarīnah** |
|---|---|---|---|
| **Haqīqah** | ✓ Only literal | - | N/A |
| **Isti'arah** | ✗ Impossible | ✓ Metaphorical only | Prevents literal |
| **Majaz** | ✗ Prevented | ✓ Figurative only | Prevents literal |
| **Kinayah** | ✓ Possible | ✓ Also intended | Suggests additional meaning |

### Three Types of Kinayah

### 1. KINAYAH 'AN SIFAH (كناية عن صفة) - Metonymy for Attribute

**Definition**: Indirectly expressing a quality/characteristic

**Structure**: Mention concrete action/thing → Imply abstract quality

### 2. KINAYAH 'AN MAWSUF (كناية عن موصوف) - Metonymy for Entity

**Definition**: Indirectly referring to a person/thing through their attributes or effects

**Structure**: Mention quality/action → Imply the person/thing possessing it

### 3. KINAYAH 'AN NISBAH (كناية عن نسبة) - Metonymy for Attribution

**Definition**: Indirectly attributing quality to entity by attributing it to something connected to that entity

**Structure**: Attribute quality to X (connected to Y) → Imply Y has the quality

### Common Quranic Kinayah Patterns

**1. Physical Actions for Psychological States**:
- **"Turning away" (أَعْرَضَ) = Rejection/arrogance**
- **"Covering/concealing" (كَفَرَ from root "cover") = Disbelief**

**2. Body Parts for Qualities**:
- **"Much tongue" / "Long tongue" = Eloquence or gossip**
- **"Clean hands" = Innocent of theft**
- **"Many ashes" (كَثِيرُ الرَّمَادِ) = Generosity**

**3. Spatial Relations for Status**:
- **"High place" = High status**
- **"Lowering the wing" = Humility**

**4. Possessions for Character**:
- **"Closed hand" = Stingy**
- **"Open hand" = Generous**

### Your Analysis Task

**STEP 1: Check if Literal Meaning is Possible**

**Critical test**: Could this be understood literally in context?

- **YES** → Possible kinayah, continue analysis
- **NO** → Not kinayah (likely isti'arah or majaz instead)

**STEP 2: Identify the Intended Meaning**

**What deeper meaning coexists with literal?**
- Abstract quality (generosity, humility, wisdom)
- Unstated person/entity
- Attributed characteristic

**STEP 3: Determine Type**

**What's being indirectly expressed?**
- **Attribute/Quality** → Kinayah 'an sifah
- **Person/Thing** → Kinayah 'an mawsuf
- **Attribution** (quality → entity) → Kinayah 'an nisbah

**STEP 4: Analyze the Indirection**

**Why indirect instead of direct?**

**A. Elegance/Politeness**: Softens criticism, creates respectful distance

**B. Concreteness**: Makes abstract tangible, shows instead of tells

**C. Vividness**: Creates memorable imagery, engages imagination

**D. Emphasis Through Evidence**: Action proves quality, more convincing than assertion

**E. Cultural Resonance**: Uses familiar idioms, taps into shared imagery

**STEP 5: Consider Dual Meaning**

**Unlike isti'arah, both literal and figurative coexist:**

**Both meanings enrich the verse** - Don't eliminate literal

### Analysis Template

```
**Kinayah Analysis:**

**Expression**: [The indirect phrase - Arabic]

**Literal meaning**: [What it says directly - is this meaning valid? ✓/✗]

**Intended meaning**: [What it implies indirectly]

**Type**: [Kinayah 'an sifah/mawsuf/nisbah]

**Mechanism**: [How does the literal expression lead to the intended meaning?]

**Why indirection?**: [What's gained by saying it indirectly?]

**Dual meaning significance**: [How do the literal and figurative meanings work together?]

**Contextual effect**: [How does this kinayah serve the verse's message?]
```

### Advanced: Compound Kinayah

Some verses have multiple layers of kinayah working together - creates devastating compound effect through indirect means.

---

## INTEGRATION: Using All Devices Together

When analyzing a verse, devices often overlap and interact:

**Example Verse Analysis Flow**:

1. **Check for taqdim/ta'khir**: Is word order unusual?
2. **Check for tibaq**: Are there antonyms?
3. **Check for tashbih**: Are there comparison particles?
4. **Check for isti'arah**: Are there metaphorical impossibilities?
5. **Check for majaz**: Are there figurative transfers?
6. **Check for kinayah**: Are there indirect allusions with valid literal meaning?

**Show how devices work together** in your analysis - don't list separately.

Good analysis integrates multiple devices to show unified rhetorical effect.
