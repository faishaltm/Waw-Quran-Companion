#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quranic Balaghah Analysis - Advanced Features (Tier 3)

Analyzes 6 advanced rhetorical devices:
1. Iltifat (Grammatical Shifts) - Person, tense, number shifts
2. Wasl/Fasl (Conjunction/Disjunction) - Sentence connection analysis
3. Muqabala (Parallel Contrasts) - Parallel opposing structures
4. Isti'anaf (Rhetorical Resumption) - Independent sentence resumption
5. Hadhf (Ellipsis Detection) - Missing grammatical elements
6. Tafsir Context Integration - Link features with historical context

Output: data/linguistic/balaghah_advanced.json

Based on research outlined in docs/BALAGHAH_IMPLEMENTATION_FEASIBILITY.md
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime


# Add loaders path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loaders'))


class IltifatAnalyzer:
    """
    Analyzes Iltifat (التفات) - Grammatical Shifts

    Detects deliberate shifts in:
    - Person (1st ↔ 2nd ↔ 3rd)
    - Number (singular ↔ dual ↔ plural)
    - Tense (perfect ↔ imperfect ↔ imperative)
    - Gender (masculine ↔ feminine)

    These shifts create rhetorical effects like:
    - Direct address (3rd → 2nd person)
    - Vivid narration (past → present tense)
    - Inclusivity (singular → plural)
    """

    def __init__(self, morphology_segments):
        """
        Initialize with morphology segments data

        Args:
            morphology_segments: Dict from morphology_segments.json
        """
        self.morphology = morphology_segments

    def analyze_verse_sequence(self, chapter_num, verses_data):
        """
        Detect iltifat shifts across a sequence of verses

        Args:
            chapter_num: Chapter number
            verses_data: List of verse dicts with 'number' and 'text'

        Returns:
            List of iltifat shift instances
        """
        shifts = []

        for i in range(len(verses_data) - 1):
            curr_verse = verses_data[i]
            next_verse = verses_data[i + 1]

            curr_num = curr_verse['number']
            next_num = next_verse['number']

            # Get morphology for both verses
            curr_morph = self._get_verse_morphology(chapter_num, curr_num)
            next_morph = self._get_verse_morphology(chapter_num, next_num)

            if not curr_morph or not next_morph:
                continue

            # Detect different types of shifts
            person_shift = self._detect_person_shift(
                chapter_num, curr_num, next_num, curr_morph, next_morph
            )
            if person_shift:
                shifts.append(person_shift)

            tense_shift = self._detect_tense_shift(
                chapter_num, curr_num, next_num, curr_morph, next_morph
            )
            if tense_shift:
                shifts.append(tense_shift)

            number_shift = self._detect_number_shift(
                chapter_num, curr_num, next_num, curr_morph, next_morph
            )
            if number_shift:
                shifts.append(number_shift)

        return shifts

    def _get_verse_morphology(self, chapter, verse):
        """Get morphology for a verse"""
        chapter_key = str(chapter)
        verse_key = str(verse)

        if chapter_key in self.morphology:
            if verse_key in self.morphology[chapter_key]:
                return self.morphology[chapter_key][verse_key]
        return None

    def _detect_person_shift(self, chapter, verse1, verse2, morph1, morph2):
        """Detect person shift between verses"""
        # Extract predominant person from each verse
        person1, examples1 = self._extract_predominant_person(morph1)
        person2, examples2 = self._extract_predominant_person(morph2)

        if person1 and person2 and person1 != person2:
            pattern = {
                'type': 'person_shift',
                'detected_pattern': {
                    'from_person': person1,
                    'to_person': person2,
                    'from_verse': verse1,
                    'to_verse': verse2,
                    'shift_description': f"{person1} → {person2}"
                }
            }

            # Add evidence - ONE word from each verse
            if examples1 and examples2:
                pattern['detected_pattern']['evidence'] = {
                    'from': {
                        'verse': verse1,
                        'word': examples1[0]['word'],
                        'text': examples1[0]['arabic']
                    },
                    'to': {
                        'verse': verse2,
                        'word': examples2[0]['word'],
                        'text': examples2[0]['arabic']
                    }
                }

            return pattern
        return None

    def _detect_tense_shift(self, chapter, verse1, verse2, morph1, morph2):
        """Detect tense shift between verses"""
        tense1, examples1 = self._extract_predominant_tense(morph1)
        tense2, examples2 = self._extract_predominant_tense(morph2)

        if tense1 and tense2 and tense1 != tense2:
            pattern = {
                'type': 'tense_shift',
                'detected_pattern': {
                    'from_tense': tense1,
                    'to_tense': tense2,
                    'from_verse': verse1,
                    'to_verse': verse2,
                    'shift_description': f"{tense1} → {tense2}"
                }
            }

            # Add evidence - ONE word from each verse
            if examples1 and examples2:
                pattern['detected_pattern']['evidence'] = {
                    'from': {
                        'verse': verse1,
                        'word': examples1[0]['word'],
                        'text': examples1[0]['arabic']
                    },
                    'to': {
                        'verse': verse2,
                        'word': examples2[0]['word'],
                        'text': examples2[0]['arabic']
                    }
                }

            return pattern
        return None

    def _detect_number_shift(self, chapter, verse1, verse2, morph1, morph2):
        """Detect number shift between verses"""
        number1, examples1 = self._extract_predominant_number(morph1)
        number2, examples2 = self._extract_predominant_number(morph2)

        if number1 and number2 and number1 != number2:
            pattern = {
                'type': 'number_shift',
                'detected_pattern': {
                    'from_number': number1,
                    'to_number': number2,
                    'from_verse': verse1,
                    'to_verse': verse2,
                    'shift_description': f"{number1} → {number2}"
                }
            }

            # Add evidence - ONE word from each verse
            if examples1 and examples2:
                pattern['detected_pattern']['evidence'] = {
                    'from': {
                        'verse': verse1,
                        'word': examples1[0]['word'],
                        'text': examples1[0]['arabic']
                    },
                    'to': {
                        'verse': verse2,
                        'word': examples2[0]['word'],
                        'text': examples2[0]['arabic']
                    }
                }

            return pattern
        return None

    def _extract_predominant_person(self, verse_morph):
        """Extract most common person marker from verse with examples

        Returns:
            tuple: (predominant_person, list of example dicts with full word text)
        """
        person_markers = []
        person_words = {'1st': {}, '2nd': {}, '3rd': {}}  # word_num -> full_text

        for word_num, segments in verse_morph.items():
            word_person_type = None
            # Concatenate all segments to get full word
            full_word = ''.join([seg.get('arabic', '') for seg in segments])
            main_pos = segments[0].get('pos', '') if segments else ''

            for seg in segments:
                if seg['pos'] in ['V', 'PRON']:  # Verbs and pronouns carry person
                    features = seg.get('features', {})

                    # Check for person markers (1p, 2ms, 3mp, etc.)
                    for key in features.keys():
                        if key in ['1p', '1s', '1d']:
                            word_person_type = '1st'
                        elif key in ['2ms', '2fs', '2mp', '2fp', '2d']:
                            word_person_type = '2nd'
                        elif key in ['3ms', '3fs', '3mp', '3fp', '3d']:
                            word_person_type = '3rd'

                    if word_person_type:
                        break  # Found person marker for this word

            if word_person_type:
                person_markers.append(word_person_type)
                # Store full word (not segment)
                if word_num not in person_words[word_person_type]:
                    person_words[word_person_type][word_num] = {
                        'word': int(word_num),
                        'arabic': full_word,
                        'pos': main_pos
                    }

        if person_markers:
            # Return most common
            predominant = Counter(person_markers).most_common(1)[0][0]
            return predominant, list(person_words[predominant].values())[:5]  # Max 5
        return None, []

    def _extract_predominant_tense(self, verse_morph):
        """Extract most common tense from verse with examples

        Returns:
            tuple: (predominant_tense, list of example dicts with full word text)
        """
        tense_markers = []
        tense_words = {'perfect': {}, 'imperfect': {}, 'imperative': {}}  # word_num -> full_text

        for word_num, segments in verse_morph.items():
            word_tense_type = None
            # Concatenate all segments to get full word
            full_word = ''.join([seg.get('arabic', '') for seg in segments])

            for seg in segments:
                if seg['pos'] == 'V':  # Only verbs have tense
                    features = seg.get('features', {})

                    if 'perf' in features:
                        word_tense_type = 'perfect'
                    elif 'impf' in features:
                        word_tense_type = 'imperfect'
                    elif 'impv' in features:
                        word_tense_type = 'imperative'

                    if word_tense_type:
                        break  # Found tense marker for this word

            if word_tense_type:
                tense_markers.append(word_tense_type)
                # Store full word (not segment)
                if word_num not in tense_words[word_tense_type]:
                    tense_words[word_tense_type][word_num] = {
                        'word': int(word_num),
                        'arabic': full_word,
                        'pos': 'V'
                    }

        if tense_markers:
            predominant = Counter(tense_markers).most_common(1)[0][0]
            return predominant, list(tense_words[predominant].values())[:5]  # Max 5
        return None, []

    def _extract_predominant_number(self, verse_morph):
        """Extract most common number from verse with examples

        Returns:
            tuple: (predominant_number, list of example dicts with full word text)
        """
        number_markers = []
        number_words = {'singular': {}, 'dual': {}, 'plural': {}}  # word_num -> full_text

        for word_num, segments in verse_morph.items():
            word_number_type = None
            # Concatenate all segments to get full word
            full_word = ''.join([seg.get('arabic', '') for seg in segments])
            main_pos = segments[0].get('pos', '') if segments else ''

            for seg in segments:
                features = seg.get('features', {})

                # Check for explicit number markers
                if 's' in features or any(k in features for k in ['1s', '2ms', '2fs', '3ms', '3fs']):
                    word_number_type = 'singular'
                elif 'd' in features or any(k in features for k in ['2d', '3d']):
                    word_number_type = 'dual'
                elif 'p' in features or any(k in features for k in ['1p', '2mp', '2fp', '3mp', '3fp']):
                    word_number_type = 'plural'

                if word_number_type:
                    break  # Found number marker for this word

            if word_number_type:
                number_markers.append(word_number_type)
                # Store full word (not segment)
                if word_num not in number_words[word_number_type]:
                    number_words[word_number_type][word_num] = {
                        'word': int(word_num),
                        'arabic': full_word,
                        'pos': main_pos
                    }

        if number_markers:
            predominant = Counter(number_markers).most_common(1)[0][0]
            # Return list of unique words (values from dict)
            return predominant, list(number_words[predominant].values())[:5]  # Max 5
        return None, []


class WaslFaslAnalyzer:
    """
    Analyzes Wasl/Fasl (الوصل والفصل) - Conjunction/Disjunction

    Wasl (وصل): Joining sentences with conjunctions (و، ف، ثم)
    Fasl (فصل): Leaving sentences separate (no conjunction)

    Detects:
    - Sentence boundaries (using dependencies)
    - Presence/absence of conjunctions
    - Type of conjunction used

    Rhetorical purposes:
    - Wasl: Continuity, sequence, addition
    - Fasl: Contrast, explanation, answer to implicit question
    """

    def __init__(self, dependencies_data, morphology_segments):
        """
        Initialize with dependencies and morphology

        Args:
            dependencies_data: List from dependencies_full.json
            morphology_segments: Dict from morphology_segments.json
        """
        self.dependencies = dependencies_data
        self.morphology = morphology_segments

        # Index dependencies by location for fast lookup
        self.deps_index = self._build_deps_index()

    def _build_deps_index(self):
        """Build index: (chapter, verse) -> list of dependencies"""
        index = defaultdict(list)
        for dep in self.dependencies:
            chapter = dep['child']['chapter']
            verse = dep['child']['verse']
            index[(chapter, verse)].append(dep)
        return index

    def analyze_verse(self, chapter_num, verse_num, verse_text):
        """
        Analyze wasl/fasl patterns in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number
            verse_text: Arabic text of verse

        Returns:
            Dict with wasl/fasl patterns or None
        """
        # Get dependencies for this verse
        verse_deps = self.deps_index.get((chapter_num, verse_num), [])

        if not verse_deps:
            return None

        # Find sentence boundaries (VS/NS root nodes)
        sentence_roots = [
            d for d in verse_deps
            if d['relation']['code'] in ['VS', 'NS']
        ]

        if len(sentence_roots) < 2:
            # Need at least 2 sentences to analyze wasl/fasl
            return None

        # Check conjunctions between sentences
        patterns = []
        conjunctions_found = [
            d for d in verse_deps
            if d['relation']['code'] == 'conj'
        ]

        for i in range(len(sentence_roots) - 1):
            sent1 = sentence_roots[i]
            sent2 = sentence_roots[i + 1]

            # Check if there's a conjunction connecting these
            has_conj = any(
                c['parent']['word'] == sent1['child']['word'] and
                c['child']['word'] == sent2['child']['word']
                for c in conjunctions_found
            )

            pattern = {
                'type': 'wasl' if has_conj else 'fasl',
                'from_sentence': i + 1,
                'to_sentence': i + 2,
                'from_word': sent1['child']['word'],
                'to_word': sent2['child']['word']
            }

            # Get conjunction word if wasl
            if has_conj:
                conj_word = self._get_conjunction_word(
                    chapter_num, verse_num, sent2['child']['word']
                )
                pattern['conjunction'] = conj_word

            patterns.append(pattern)

        if not patterns:
            return None

        return {
            'wasl_fasl_patterns': patterns,
            'total_sentences': len(sentence_roots),
            'wasl_count': sum(1 for p in patterns if p['type'] == 'wasl'),
            'fasl_count': sum(1 for p in patterns if p['type'] == 'fasl')
        }

    def _get_conjunction_word(self, chapter, verse, word_num):
        """Get the conjunction word text from morphology"""
        verse_morph = self._get_verse_morphology(chapter, verse)
        if not verse_morph:
            return None

        word_key = str(word_num)
        if word_key not in verse_morph:
            return None

        segments = verse_morph[word_key]
        # Check first segment for conjunction
        if segments and 'conj' in segments[0].get('features', {}):
            return segments[0].get('arabic', '')

        return None

    def _get_verse_morphology(self, chapter, verse):
        """Get morphology for a verse"""
        chapter_key = str(chapter)
        verse_key = str(verse)

        if chapter_key in self.morphology:
            if verse_key in self.morphology[chapter_key]:
                return self.morphology[chapter_key][verse_key]
        return None


class MuqabalaAnalyzer:
    """
    Analyzes Muqabala (المقابلة) - Parallel Contrasts

    Muqabala is more complex than simple antithesis (tibaq).
    It involves parallel structures with multiple contrasting elements.

    Example: "They have eyes but see not, ears but hear not"
             (parallel structure + semantic opposition)

    Detects:
    - Parallel syntactic structures (repeated POS patterns)
    - Semantic contrasts within parallel structures
    - Multiple antithesis pairs
    """

    def __init__(self, morphology_segments, lemmas_dict):
        """
        Initialize with morphology data and lemmas dictionary

        Args:
            morphology_segments: Dict from morphology_segments.json
            lemmas_dict: Dict from lemmas_dictionary.json (root -> translations)
        """
        self.morphology = morphology_segments
        self.lemmas = lemmas_dict

    def analyze_verse(self, chapter_num, verse_num, verse_text):
        """
        Detect muqabala patterns in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number
            verse_text: Arabic text

        Returns:
            Dict with muqabala patterns or None
        """
        verse_morph = self._get_verse_morphology(chapter_num, verse_num)
        if not verse_morph:
            return None

        # Extract POS sequences for pattern matching
        pos_sequences = self._extract_pos_sequences(verse_morph)

        # Find repeated POS patterns (potential parallel structures)
        parallel_patterns = self._find_parallel_pos_patterns(pos_sequences)

        if not parallel_patterns:
            return None

        # Check if parallel structures have semantic contrasts
        muqabala_candidates = []

        for pattern in parallel_patterns:
            # Extract content words from each occurrence
            occurrences = pattern['occurrences']

            if len(occurrences) < 2:
                continue

            # Compare first two occurrences
            occ1 = occurrences[0]
            occ2 = occurrences[1]

            # Map POS patterns to actual words with translations
            structure1 = self._map_pattern_to_words(
                pattern['pos_pattern'],
                occ1['word_range'],
                verse_morph,
                self.lemmas
            )
            structure2 = self._map_pattern_to_words(
                pattern['pos_pattern'],
                occ2['word_range'],
                verse_morph,
                self.lemmas
            )

            candidate = {
                'syntactic_pattern': pattern['pos_pattern'],
                'structure1': structure1,
                'structure2': structure2,
                'parallelism_type': 'syntactic'
            }

            muqabala_candidates.append(candidate)

        if not muqabala_candidates:
            return None

        return {
            'muqabala_patterns': muqabala_candidates,
            'count': len(muqabala_candidates)
        }

    def _get_verse_morphology(self, chapter, verse):
        """Get morphology for a verse"""
        chapter_key = str(chapter)
        verse_key = str(verse)

        if chapter_key in self.morphology:
            if verse_key in self.morphology[chapter_key]:
                return self.morphology[chapter_key][verse_key]
        return None

    def _extract_pos_sequences(self, verse_morph):
        """Extract POS tag sequences from verse"""
        sequences = []

        # Get words in order
        word_nums = sorted([int(k) for k in verse_morph.keys()])

        for word_num in word_nums:
            word_key = str(word_num)
            segments = verse_morph[word_key]

            # Get POS of first segment (main word type)
            if segments:
                pos = segments[0]['pos']
                sequences.append({
                    'word_num': word_num,
                    'pos': pos
                })

        return sequences

    def _ranges_overlap(self, range1, range2):
        """Check if two word ranges overlap"""
        set1 = set(range1)
        set2 = set(range2)
        return bool(set1 & set2)  # True if intersection exists

    def _find_parallel_pos_patterns(self, pos_sequences):
        """Find repeated POS patterns (2-4 words long)"""
        patterns = []
        seq_length = len(pos_sequences)

        # Try patterns of length 2-4
        for pattern_len in range(2, 5):
            if pattern_len > seq_length:
                break

            # Sliding window
            for i in range(seq_length - pattern_len + 1):
                window = pos_sequences[i:i + pattern_len]
                pos_pattern = tuple([w['pos'] for w in window])

                # Look for same pattern later in verse
                for j in range(i + pattern_len, seq_length - pattern_len + 1):
                    window2 = pos_sequences[j:j + pattern_len]
                    pos_pattern2 = tuple([w['pos'] for w in window2])

                    if pos_pattern == pos_pattern2:
                        # Check for overlaps with existing patterns
                        range1 = list(range(window[0]['word_num'], window[-1]['word_num'] + 1))
                        range2 = list(range(window2[0]['word_num'], window2[-1]['word_num'] + 1))

                        # Check if either range overlaps with any existing pattern
                        overlaps = False
                        for existing in patterns:
                            for occ in existing['occurrences']:
                                if (self._ranges_overlap(range1, occ['word_range']) or
                                    self._ranges_overlap(range2, occ['word_range'])):
                                    overlaps = True
                                    break
                            if overlaps:
                                break

                        # Only add if no overlaps (prevents confusing duplicate patterns)
                        if not overlaps:
                            patterns.append({
                                'pos_pattern': list(pos_pattern),
                                'pattern_length': pattern_len,
                                'occurrences': [
                                    {
                                        'word_range': range1,
                                        'start_word': window[0]['word_num'],
                                        'end_word': window[-1]['word_num']
                                    },
                                    {
                                        'word_range': range2,
                                        'start_word': window2[0]['word_num'],
                                        'end_word': window2[-1]['word_num']
                                    }
                                ]
                            })

        return patterns

    def _map_pattern_to_words(self, pos_pattern, word_range, verse_morph, lemmas_dict):
        """
        Map each POS tag in pattern to actual word with translation.

        Returns: Dictionary mapping POS tag to word info
        Example: {"P": {"arabic": "عَلَىٰ", "translation": "upon"},
                  "V": {"arabic": "أَتَىٰ", "root": "أتي", "translation": "came"}}
        """
        pattern_words = {}

        # Get words in the pattern range
        for idx, word_num in enumerate(word_range):
            if idx >= len(pos_pattern):
                break

            pos_tag = pos_pattern[idx]
            word_key = str(word_num)

            if word_key in verse_morph:
                segments = verse_morph[word_key]

                # Find segment matching this POS tag
                for seg in segments:
                    if seg['pos'] == pos_tag:
                        # Get translation from lemmas dictionary (use lemma, not root)
                        translation = None
                        root = seg['features'].get('root')
                        lemma = seg['features'].get('lem')  # Lemma matches lemmas_dict keys

                        if lemma and lemma in lemmas_dict:
                            # Get first translation from lemmas dictionary
                            translations = lemmas_dict[lemma]
                            if translations:
                                translation = translations[0]

                        # Create word info
                        word_info = {
                            'arabic': seg['arabic'],
                            'translation': translation
                        }

                        # Add root for content words (root is for analysis, lemma is for translation)
                        if pos_tag in ['N', 'V', 'ADJ'] and root:
                            word_info['root'] = root

                        # Use POS tag with index if multiple same tags
                        key = pos_tag
                        counter = 1
                        while key in pattern_words:
                            key = f"{pos_tag}_{counter}"
                            counter += 1

                        pattern_words[key] = word_info
                        break

        return pattern_words


class IstianafAnalyzer:
    """
    Analyzes Isti'anaf (الاستئناف) - Rhetorical Resumption

    Isti'anaf occurs when a new independent sentence resumes or emphasizes
    the meaning of the previous sentence with rhetorical effect.

    Unlike simple continuation, isti'anaf creates:
    - Emphasis through repetition of theme
    - Clarification of previous meaning
    - Explanation or elaboration

    Detects:
    - Independent sentences (from dependencies)
    - Semantic continuity (shared roots/themes)
    - Resumption patterns
    """

    def __init__(self, dependencies_data, morphology_segments):
        """
        Initialize with dependencies and morphology

        Args:
            dependencies_data: List from dependencies_full.json
            morphology_segments: Dict from morphology_segments.json
        """
        self.dependencies = dependencies_data
        self.morphology = morphology_segments
        self.deps_index = self._build_deps_index()

    def _build_deps_index(self):
        """Build index for dependencies"""
        index = defaultdict(list)
        for dep in self.dependencies:
            chapter = dep['child']['chapter']
            verse = dep['child']['verse']
            index[(chapter, verse)].append(dep)
        return index

    def analyze_verse(self, chapter_num, verse_num):
        """
        Detect isti'anaf candidates in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number

        Returns:
            Dict with isti'anaf patterns or None
        """
        # Get dependencies for verse
        verse_deps = self.deps_index.get((chapter_num, verse_num), [])

        if not verse_deps:
            return None

        # Find independent sentences (VS/NS roots)
        sentences = [
            d for d in verse_deps
            if d['relation']['code'] in ['VS', 'NS']
        ]

        if len(sentences) < 2:
            return None

        # Check semantic continuity between consecutive sentences
        istianaf_candidates = []

        for i in range(len(sentences) - 1):
            sent1 = sentences[i]
            sent2 = sentences[i + 1]

            # Get roots in each sentence
            roots1 = self._get_sentence_roots(chapter_num, verse_num, sent1)
            roots2 = self._get_sentence_roots(chapter_num, verse_num, sent2)

            # Find shared roots
            shared_roots = set(roots1) & set(roots2)

            if shared_roots:
                candidate = {
                    'sentence1_word': sent1['child']['word'],
                    'sentence2_word': sent2['child']['word'],
                    'shared_roots': list(shared_roots),
                    'sentence1_type': sent1['relation']['code'],
                    'sentence2_type': sent2['relation']['code'],
                    # How this pattern was detected (LLM infers rhetorical type from context)
                    'detection_method': 'root_repetition'
                }
                istianaf_candidates.append(candidate)

        if not istianaf_candidates:
            return None

        return {
            'istianaf_patterns': istianaf_candidates,
            'count': len(istianaf_candidates)
        }

    def _get_sentence_roots(self, chapter, verse, sentence_dep):
        """Get all roots in a sentence"""
        verse_morph = self._get_verse_morphology(chapter, verse)
        if not verse_morph:
            return []

        roots = []

        # Get words belonging to this sentence (simplified: just the sentence root word)
        word_num = sentence_dep['child']['word']
        word_key = str(word_num)

        if word_key in verse_morph:
            for seg in verse_morph[word_key]:
                root = seg['features'].get('root')
                if root:
                    roots.append(root)

        return roots

    def _get_verse_morphology(self, chapter, verse):
        """Get morphology for a verse"""
        chapter_key = str(chapter)
        verse_key = str(verse)

        if chapter_key in self.morphology:
            if verse_key in self.morphology[chapter_key]:
                return self.morphology[chapter_key][verse_key]
        return None


class HadhfAnalyzer:
    """
    Analyzes Hadhf (الحذف) - Ellipsis

    Hadhf is the deliberate omission of grammatical elements for:
    - Brevity and conciseness
    - Emphasis on what remains
    - Assumption of known context
    - Dramatic effect

    Detects:
    - Transitive verbs without objects
    - Nominal sentences without predicates
    - Conditional sentences without apodosis
    - Other grammatical ellipsis patterns
    """

    def __init__(self, dependencies_data, morphology_segments):
        """
        Initialize with dependencies and morphology

        Args:
            dependencies_data: List from dependencies_full.json
            morphology_segments: Dict from morphology_segments.json
        """
        self.dependencies = dependencies_data
        self.morphology = morphology_segments
        self.deps_index = self._build_deps_index()

    def _build_deps_index(self):
        """Build index for dependencies"""
        index = defaultdict(list)
        for dep in self.dependencies:
            chapter = dep['child']['chapter']
            verse = dep['child']['verse']
            index[(chapter, verse)].append(dep)
        return index

    def analyze_verse(self, chapter_num, verse_num):
        """
        Detect ellipsis candidates in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number

        Returns:
            Dict with hadhf patterns or None
        """
        verse_deps = self.deps_index.get((chapter_num, verse_num), [])
        verse_morph = self._get_verse_morphology(chapter_num, verse_num)

        if not verse_deps or not verse_morph:
            return None

        hadhf_candidates = []

        # Pattern 1: Verbs without expected objects
        # Find all verbs in the verse
        for word_key, segments in verse_morph.items():
            for seg in segments:
                if seg['pos'] == 'V':
                    word_num = int(word_key)

                    # Check if this verb has an object in dependencies
                    has_object = any(
                        d['relation']['code'] == 'obj' and
                        d['parent']['word'] == word_num
                        for d in verse_deps
                    )

                    if not has_object:
                        # Potential omitted object
                        hadhf_candidates.append({
                            'type': 'omitted_object',
                            'verb_word': word_num,
                            'verb_text': seg['arabic'],
                            'verb_root': seg['features'].get('root')
                        })

        # Pattern 2: Nominal sentences without predicates
        nominal_sentences = [
            d for d in verse_deps
            if d['relation']['code'] == 'NS'
        ]

        for ns in nominal_sentences:
            subject_word = ns['child']['word']

            # Check if predicate exists
            has_predicate = any(
                d['relation']['code'] == 'pred' and
                d['child']['word'] == subject_word
                for d in verse_deps
            )

            if not has_predicate:
                hadhf_candidates.append({
                    'type': 'omitted_predicate',
                    'subject_word': subject_word
                })

        if not hadhf_candidates:
            return None

        return {
            'hadhf_patterns': hadhf_candidates,
            'count': len(hadhf_candidates)
        }

    def _get_verse_morphology(self, chapter, verse):
        """Get morphology for a verse"""
        chapter_key = str(chapter)
        verse_key = str(verse)

        if chapter_key in self.morphology:
            if verse_key in self.morphology[chapter_key]:
                return self.morphology[chapter_key][verse_key]
        return None


class TafsirContextIntegrator:
    """
    Integrates all balaghah features with historical context

    Links:
    - Linguistic patterns (iltifat, wasl/fasl, etc.)
    - Asbab al-nuzul (occasions of revelation)
    - Chapter metadata (Meccan/Medinan, revelation order)
    - Thematic context

    Creates holistic interpretation framework for LLM
    """

    def __init__(self, asbab_nuzul_data, chapter_metadata):
        """
        Initialize with metadata

        Args:
            asbab_nuzul_data: Dict from asbab_nuzul_index.json
            chapter_metadata: Dict from chapter_metadata.json
        """
        self.asbab_nuzul = asbab_nuzul_data
        self.chapter_metadata = chapter_metadata

    def integrate_context(self, chapter_num, verse_num, balaghah_features):
        """
        Combine linguistic features with historical context

        Args:
            chapter_num: Chapter number
            verse_num: Verse number
            balaghah_features: Dict with detected balaghah features

        Returns:
            Integrated context dict
        """
        # Get historical context
        asbab_key = f"{chapter_num}:{verse_num}"
        occasions = self.asbab_nuzul.get(asbab_key, [])

        # Get chapter metadata
        chapter_meta = self.chapter_metadata.get(str(chapter_num), {})

        integrated = {
            'linguistic_features_summary': self._summarize_features(balaghah_features)
        }

        # Only add asbab nuzul info if this verse has occasions
        if len(occasions) > 0:
            integrated['asbab_nuzul_info'] = {
                'has_occasions': True,
                'occasions_count': len(occasions)
            }

        # Add asbab nuzul summary if available (for LLM context)
        if occasions:
            integrated['asbab_nuzul_summary'] = [
                {
                    'verse_range': occ.get('verse_range'),
                    'occasion_preview': occ.get('occasion', '')[:200] + '...' if len(occ.get('occasion', '')) > 200 else occ.get('occasion', '')
                }
                for occ in occasions[:2]  # First 2 occasions
            ]

        return integrated

    def _summarize_features(self, features):
        """Create comprehensive summary of ALL detected balaghah features"""
        summary = []

        # Tier 1 Features (Basic)
        if features.get('saj'):
            saj = features['saj']
            summary.append(f"saj' (rhyme pattern: {saj.get('pattern', 'unknown')}, sequence: {saj.get('sequence_length', 0)} verses)")

        if features.get('jinas'):
            count = len(features['jinas'])
            summary.append(f"jinas (wordplay: {count} pairs)")

        if features.get('repeated_roots'):
            count = len(features['repeated_roots'])
            summary.append(f"takrar (root repetition: {count} roots)")

        # Tier 2 Features (Ma'ani)
        if features.get('maani'):
            maani = features['maani']
            if maani.get('sentence_type'):
                sent_type = maani['sentence_type']
                summary.append(f"sentence type: {sent_type.get('type')} - {sent_type.get('subtype', '')}")

        # Advanced Features (Tier 3)
        if features.get('iltifat'):
            shifts = features['iltifat']
            shift_types = [s['type'].replace('_shift', '') for s in shifts]
            summary.append(f"iltifat (shifts: {', '.join(shift_types)})")

        if features.get('wasl_fasl'):
            wf = features['wasl_fasl']
            summary.append(f"wasl/fasl (conjunction: {wf['wasl_count']} wasl, {wf['fasl_count']} fasl)")

        if features.get('muqabala'):
            summary.append(f"muqabala (parallelism: {features['muqabala']['count']} patterns)")

        if features.get('istianaf'):
            summary.append(f"isti'anaf (resumption: {features['istianaf']['count']} instances)")

        if features.get('hadhf'):
            summary.append(f"hadhf (ellipsis: {features['hadhf']['count']} omissions)")

        return summary if summary else ['no rhetorical features detected']


class UnifiedBalaghahAnalyzer:
    """
    Main coordinator class that runs all 6 balaghah analyzers

    Orchestrates:
    1. IltifatAnalyzer - Grammatical shifts
    2. WaslFaslAnalyzer - Conjunction/disjunction
    3. MuqabalaAnalyzer - Parallel contrasts
    4. IstianafAnalyzer - Rhetorical resumption
    5. HadhfAnalyzer - Ellipsis detection
    6. TafsirContextIntegrator - Historical integration
    """

    def __init__(self, data_dir):
        """
        Load all required data sources and initialize analyzers

        Args:
            data_dir: Path to data directory
        """
        print("Loading data sources...")

        # Load morphology segments
        print("  - morphology_segments.json")
        morph_path = os.path.join(data_dir, 'linguistic', 'morphology_segments.json')
        with open(morph_path, 'r', encoding='utf-8') as f:
            morph_data = json.load(f)
            self.morphology = morph_data['morphology']

        # Load dependencies
        print("  - dependencies_full.json")
        deps_path = os.path.join(data_dir, 'linguistic', 'dependencies_full.json')
        with open(deps_path, 'r', encoding='utf-8') as f:
            deps_data = json.load(f)
            self.dependencies = deps_data['dependencies']

        # Load pause marks (for wasl/fasl)
        print("  - pause_marks.json")
        pause_path = os.path.join(data_dir, 'linguistic', 'pause_marks.json')
        with open(pause_path, 'r', encoding='utf-8') as f:
            pause_data = json.load(f)
            self.pause_marks = pause_data.get('pause_marks', [])

        # Load asbab al-nuzul
        print("  - asbab_nuzul_index.json")
        asbab_path = os.path.join(data_dir, 'metadata', 'asbab_nuzul_index.json')
        with open(asbab_path, 'r', encoding='utf-8') as f:
            self.asbab_nuzul = json.load(f)

        # Load chapter metadata
        print("  - chapter_metadata.json")
        chapter_path = os.path.join(data_dir, 'metadata', 'chapter_metadata.json')
        with open(chapter_path, 'r', encoding='utf-8') as f:
            self.chapter_metadata = json.load(f)

        # Load Quran text
        print("  - quran_text.json")
        quran_path = os.path.join(data_dir, 'text', 'quran_text.json')
        with open(quran_path, 'r', encoding='utf-8') as f:
            self.quran_text = json.load(f)

        # Load lemmas dictionary (for muqabala word translations)
        print("  - lemmas_dictionary.json")
        lemmas_path = os.path.join(data_dir, 'linguistic', 'lemmas_dictionary.json')
        with open(lemmas_path, 'r', encoding='utf-8') as f:
            lemmas_data = json.load(f)
            # Transform array into dictionary keyed by unicode root
            lemmas_array = lemmas_data.get('lemmas', [])
            self.lemmas = {}
            for lemma in lemmas_array:
                root = lemma.get('unicode', '')
                translation = lemma.get('english', '')
                if root:
                    # Store as list to match expected format in _map_pattern_to_words
                    if root not in self.lemmas:
                        self.lemmas[root] = []
                    if translation:
                        self.lemmas[root].append(translation)

        print("\nInitializing analyzers...")

        # Initialize feature analyzers
        self.iltifat_analyzer = IltifatAnalyzer(self.morphology)
        self.wasl_fasl_analyzer = WaslFaslAnalyzer(self.dependencies, self.morphology)
        self.muqabala_analyzer = MuqabalaAnalyzer(self.morphology, self.lemmas)
        self.istianaf_analyzer = IstianafAnalyzer(self.dependencies, self.morphology)
        self.hadhf_analyzer = HadhfAnalyzer(self.dependencies, self.morphology)
        self.tafsir_integrator = TafsirContextIntegrator(self.asbab_nuzul, self.chapter_metadata)

        print("Ready!\n")

    def analyze_full_quran(self):
        """
        Analyze all 114 chapters for 6 advanced balaghah features

        Returns:
            Complete analysis in JSON-serializable format
        """
        result = {
            'metadata': {
                'version': '1.0',
                'analysis_type': 'Advanced Balaghah Features (Tier 3)',
                'features': [
                    'iltifat',
                    'wasl_fasl',
                    'muqabala',
                    'istianaf',
                    'hadhf',
                    'tafsir_integration'
                ],
                'generated': datetime.now().isoformat(),
                'description': 'Advanced rhetorical analysis with LLM-ready interpretation prompts'
            },
            'chapters': []
        }

        # Analyze each chapter
        total_chapters = len(self.quran_text['chapters'])

        for idx, chapter_data in enumerate(self.quran_text['chapters'], 1):
            chapter_num = chapter_data['number']
            verses = chapter_data['verses']

            print(f"[{idx}/{total_chapters}] Analyzing Chapter {chapter_num} ({len(verses)} verses)...")

            chapter_result = {
                'chapter': chapter_num,
                'name_arabic': chapter_data.get('name'),
                'verses_count': len(verses),
                'verses': []
            }

            # Analyze each verse
            for verse in verses:
                verse_num = verse['number']
                verse_text = verse['text']

                verse_analysis = {
                    'verse_number': verse_num
                }

                # 2. Wasl/Fasl
                wasl_fasl = self.wasl_fasl_analyzer.analyze_verse(
                    chapter_num, verse_num, verse_text
                )
                if wasl_fasl and wasl_fasl.get('wasl_fasl_patterns'):
                    verse_analysis['wasl_fasl'] = wasl_fasl

                # 3. Muqabala
                muqabala = self.muqabala_analyzer.analyze_verse(
                    chapter_num, verse_num, verse_text
                )
                if muqabala and muqabala.get('muqabala_patterns'):
                    verse_analysis['muqabala'] = muqabala

                # 4. Isti'anaf
                istianaf = self.istianaf_analyzer.analyze_verse(
                    chapter_num, verse_num
                )
                if istianaf and istianaf.get('istianaf_patterns'):
                    verse_analysis['istianaf'] = istianaf

                # 5. Hadhf
                hadhf = self.hadhf_analyzer.analyze_verse(
                    chapter_num, verse_num
                )
                if hadhf and hadhf.get('hadhf_patterns'):
                    verse_analysis['hadhf'] = hadhf

                # 6. Tafsir Context Integration (always include)
                tafsir_context = self.tafsir_integrator.integrate_context(
                    chapter_num, verse_num, verse_analysis
                )
                verse_analysis['tafsir_context'] = tafsir_context

                # Only add verse if it has some features
                if len(verse_analysis) > 2:  # More than just verse_number and tafsir_context
                    chapter_result['verses'].append(verse_analysis)

            # 1. Iltifat (cross-verse analysis, done at chapter level)
            chapter_iltifat = self.iltifat_analyzer.analyze_verse_sequence(
                chapter_num, verses
            )
            if chapter_iltifat:
                chapter_result['iltifat'] = chapter_iltifat

            result['chapters'].append(chapter_result)

        return result

    def analyze_single_chapter(self, chapter_num):
        """
        Analyze a single chapter (for testing)

        Args:
            chapter_num: Chapter number (1-114)

        Returns:
            Analysis for that chapter
        """
        # Find chapter data
        chapter_data = None
        for ch in self.quran_text['chapters']:
            if ch['number'] == chapter_num:
                chapter_data = ch
                break

        if not chapter_data:
            raise ValueError(f"Chapter {chapter_num} not found")

        print(f"Analyzing Chapter {chapter_num} ({len(chapter_data['verses'])} verses)...\n")

        verses = chapter_data['verses']

        chapter_result = {
            'chapter': chapter_num,
            'name_arabic': chapter_data.get('name'),
            'verses_count': len(verses),
            'verses': []
        }

        # Analyze each verse
        for verse in verses:
            verse_num = verse['number']
            verse_text = verse['text']

            print(f"  Verse {verse_num}...")

            verse_analysis = {
                'verse_number': verse_num
            }

            # Run all analyzers
            wasl_fasl = self.wasl_fasl_analyzer.analyze_verse(
                chapter_num, verse_num, verse_text
            )
            if wasl_fasl:
                verse_analysis['wasl_fasl'] = wasl_fasl

            muqabala = self.muqabala_analyzer.analyze_verse(
                chapter_num, verse_num, verse_text
            )
            if muqabala:
                verse_analysis['muqabala'] = muqabala

            istianaf = self.istianaf_analyzer.analyze_verse(
                chapter_num, verse_num
            )
            if istianaf:
                verse_analysis['istianaf'] = istianaf

            hadhf = self.hadhf_analyzer.analyze_verse(
                chapter_num, verse_num
            )
            if hadhf:
                verse_analysis['hadhf'] = hadhf

            tafsir_context = self.tafsir_integrator.integrate_context(
                chapter_num, verse_num, verse_analysis
            )
            verse_analysis['tafsir_context'] = tafsir_context

            if len(verse_analysis) > 1:
                chapter_result['verses'].append(verse_analysis)

        # Iltifat (cross-verse)
        chapter_iltifat = self.iltifat_analyzer.analyze_verse_sequence(
            chapter_num, verses
        )
        if chapter_iltifat:
            chapter_result['iltifat'] = chapter_iltifat

        return chapter_result


def main():
    """Main analysis runner"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Quranic Balaghah Analysis - Advanced Features'
    )
    parser.add_argument(
        '--chapter',
        type=int,
        help='Analyze single chapter (1-114) for testing',
        default=None
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: data/linguistic/balaghah_advanced.json)',
        default=None
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Quranic Balaghah Analysis - Advanced Features (Tier 3)")
    print("=" * 70)
    print()
    print("Features:")
    print("  1. Iltifat - Grammatical shifts (person, tense, number)")
    print("  2. Wasl/Fasl - Conjunction/disjunction analysis")
    print("  3. Muqabala - Parallel contrasting structures")
    print("  4. Isti'anaf - Rhetorical resumption")
    print("  5. Hadhf - Ellipsis detection")
    print("  6. Tafsir Integration - Historical context linking")
    print()

    # Determine data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    data_dir = os.path.join(project_root, 'data')

    # Initialize analyzer
    analyzer = UnifiedBalaghahAnalyzer(data_dir)

    # Run analysis
    if args.chapter:
        # Single chapter mode
        print(f"SINGLE CHAPTER MODE: Chapter {args.chapter}\n")
        result = {
            'metadata': {
                'version': '1.0',
                'analysis_type': 'Advanced Balaghah Features (Test)',
                'chapter_tested': args.chapter,
                'features': ['iltifat', 'wasl_fasl', 'muqabala', 'istianaf', 'hadhf', 'tafsir_integration'],
                'generated': datetime.now().isoformat()
            },
            'chapters': [analyzer.analyze_single_chapter(args.chapter)]
        }
    else:
        # Full Quran mode
        print("FULL QURAN MODE: Analyzing all 114 chapters\n")
        result = analyzer.analyze_full_quran()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_filename = f'balaghah_advanced_ch{args.chapter}.json' if args.chapter else 'balaghah_advanced.json'
        output_path = os.path.join(data_dir, 'linguistic', output_filename)

    # Save output
    print(f"\nSaving output to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Print statistics
    print("\nAnalysis Complete!")
    print("=" * 70)

    total_chapters = len(result['chapters'])
    total_verses_analyzed = sum(len(ch.get('verses', [])) for ch in result['chapters'])

    print(f"Chapters analyzed: {total_chapters}")
    print(f"Verses with features: {total_verses_analyzed}")

    # Count features
    feature_counts = {
        'wasl_fasl': 0,
        'muqabala': 0,
        'istianaf': 0,
        'hadhf': 0,
        'iltifat': 0
    }

    for chapter in result['chapters']:
        for verse in chapter.get('verses', []):
            for feature in feature_counts.keys():
                if feature in verse:
                    feature_counts[feature] += 1

        if 'iltifat' in chapter:
            feature_counts['iltifat'] += len(chapter['iltifat'])

    print("\nFeature Distribution:")
    for feature, count in feature_counts.items():
        print(f"  {feature}: {count} instances")

    print(f"\nOutput file size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    print("=" * 70)


if __name__ == '__main__':
    main()
