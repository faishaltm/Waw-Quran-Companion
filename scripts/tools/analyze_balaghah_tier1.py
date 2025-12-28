#!/usr/bin/env python3
"""
Quranic Balaghah Analysis - Tier 1
Analyzes the entire Quran for three rhetorical devices:
1. Saj' (Rhymed Prose)
2. Takrar (Repetition - 4 types)
3. Jinas (Wordplay/Paronomasia)

Output: data/linguistic/balaghah_tier1.json
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher

# Add parent directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')

# ==================== HELPER FUNCTIONS ====================

# Arabic diacritics to remove for phonetic comparison
ARABIC_DIACRITICS = [
    '\u064B',  # Tanwin Fath
    '\u064C',  # Tanwin Damm
    '\u064D',  # Tanwin Kasr
    '\u064E',  # Fatha
    '\u064F',  # Damma
    '\u0650',  # Kasra
    '\u0651',  # Shadda
    '\u0652',  # Sukun
    '\u0653',  # Maddah
    '\u0654',  # Hamza above
    '\u0655',  # Hamza below
    '\u0656',  # Subscript Alif
    '\u0657',  # Inverted Damma
    '\u0658',  # Mark Noon Ghunna
    '\u0670',  # Alif Khanjariyah
]

def remove_diacritics(text):
    """Remove all Arabic diacritical marks from text"""
    for diacritic in ARABIC_DIACRITICS:
        text = text.replace(diacritic, '')
    return text

def extract_verse_ending(verse_text, length=3):
    """
    Extract the ending pattern of a verse (last N letters without diacritics)

    Args:
        verse_text: Arabic verse text
        length: Number of letters to extract from end

    Returns:
        Ending pattern string
    """
    if not verse_text:
        return ""

    # Remove diacritics
    clean_text = remove_diacritics(verse_text.strip())

    # Get last word
    words = clean_text.split()
    if not words:
        return ""

    last_word = words[-1]

    # Extract last N letters
    ending = last_word[-length:] if len(last_word) >= length else last_word

    return ending


def extract_phonetic_ending(verse_text):
    """
    Extract the phonetic (sound-based) ending pattern of a verse

    Maps Arabic endings to phonetic representations:
    - Long vowels: aa, ii, uu
    - Tanween + alif: aa
    - Final consonants: preserved

    Args:
        verse_text: Arabic verse text

    Returns:
        Phonetic pattern string
    """
    if not verse_text:
        return ""

    # Get last word without diacritics
    clean_text = remove_diacritics(verse_text.strip())
    words = clean_text.split()
    if not words:
        return ""

    last_word = words[-1]

    # Phonetic mapping rules (check from end of word)
    # Long vowel patterns
    if last_word.endswith('ا'):
        # Check if preceded by ي or ى (yaa + alif = "aa")
        if len(last_word) >= 2 and last_word[-2] in ['ي', 'ى']:
            return 'yaa'  # "يا" sound
        # Tanween + alif also makes "aa" sound
        return 'aa'

    elif last_word.endswith('ى'):
        return 'aa'  # Alif maqsura = "aa"

    elif last_word.endswith('ي'):
        return 'ii'  # Long i

    elif last_word.endswith('و'):
        return 'uu'  # Long u

    elif last_word.endswith('ين'):
        return 'iin'  # Common plural/dual ending

    elif last_word.endswith('ون'):
        return 'uun'  # Masculine plural

    # Single consonant endings (common in Saj')
    elif last_word.endswith('ر'):
        return 'r'
    elif last_word.endswith('ن'):
        return 'n'
    elif last_word.endswith('م'):
        return 'm'
    elif last_word.endswith('ل'):
        return 'l'
    elif last_word.endswith('د'):
        return 'd'
    elif last_word.endswith('ت'):
        return 't'

    # Default: return last 2 characters
    return last_word[-2:] if len(last_word) >= 2 else last_word

def calculate_similarity(str1, str2):
    """
    Calculate character-level similarity between two Arabic strings.

    Returns:
        float: Similarity ratio from 0.0 to 1.0 where:
               - 1.0 = Perfect match (100% identical characters)
               - 0.5 = 50% character similarity
               - 0.0 = Completely different strings

    Algorithm:
        Uses Python's difflib.SequenceMatcher.ratio()
        Formula: 2.0 * M / T
        where M = number of matching characters
              T = total characters in both strings

    Example:
        calculate_similarity("الرَّحْمَٰنِ", "الرَّحِيمِ")
        Returns ~0.6 (similar but different forms from root رحم)

    Note:
        Diacritics are removed before comparison for robust
        matching of Arabic text variants.
    """
    if not str1 or not str2:
        return 0.0

    # Remove diacritics for comparison
    clean1 = remove_diacritics(str1)
    clean2 = remove_diacritics(str2)

    return SequenceMatcher(None, clean1, clean2).ratio()

def find_repeated_subsequences(sequence, min_length=2):
    """
    Find repeated subsequences in a sequence (e.g., POS tags)

    Args:
        sequence: List of elements
        min_length: Minimum length of pattern to detect

    Returns:
        Dict of {pattern: count}
    """
    if not sequence or len(sequence) < min_length * 2:
        return {}

    patterns = defaultdict(int)
    n = len(sequence)

    # Try all possible pattern lengths
    for length in range(min_length, n // 2 + 1):
        # Try all starting positions
        for i in range(n - length + 1):
            pattern = tuple(sequence[i:i+length])

            # Search for this pattern elsewhere in sequence
            for j in range(i + length, n - length + 1):
                if tuple(sequence[j:j+length]) == pattern:
                    patterns[pattern] += 1
                    break  # Count each unique pattern once per occurrence

    # Filter out patterns with no repetitions
    return {k: v for k, v in patterns.items() if v > 0}


# ==================== SAJ' ANALYZER ====================

class SajAnalyzer:
    """Analyzes rhymed prose patterns (Saj') with adaptive pattern detection"""

    def __init__(self, min_sequence_length=2):
        """
        Initialize saj' analyzer with adaptive pattern detection

        Args:
            min_sequence_length: Minimum consecutive verses to count as saj' (default: 2)
        """
        self.min_sequence_length = min_sequence_length

    def analyze_chapter(self, verses):
        """
        Analyze saj' patterns for an entire chapter using ADAPTIVE ALGORITHM

        Tests multiple approaches and selects the best:
        1. Multiple letter lengths (1-4 letters)
        2. Phonetic (sound-based) patterns

        Selects pattern with highest coverage and consistency.

        Args:
            verses: List of verse dicts with 'text' field

        Returns:
            Dict with chapter-level and verse-level analysis
        """
        if not verses:
            return None

        total_verses = len(verses)

        # Test multiple pattern detection approaches
        candidates = []

        # 1. Test literal patterns with different lengths (1-4 letters)
        for length in range(1, 5):
            endings = []
            for verse in verses:
                ending = extract_verse_ending(verse['text'], length)
                endings.append(ending)

            sequences = self._find_saj_sequences(endings)
            verses_in_saj = sum(seq['length'] for seq in sequences)
            coverage = verses_in_saj / total_verses if total_verses > 0 else 0

            # Calculate pattern consistency (how many unique patterns)
            unique_patterns = len(set(endings))

            candidates.append({
                'mode': f'literal_{length}',
                'length': length,
                'endings': endings,
                'sequences': sequences,
                'coverage': coverage,
                'unique_patterns': unique_patterns,
                'score': self._calculate_score(coverage, unique_patterns, total_verses)
            })

        # 2. Test phonetic (sound-based) patterns
        phonetic_endings = []
        for verse in verses:
            ending = extract_phonetic_ending(verse['text'])
            phonetic_endings.append(ending)

        phonetic_sequences = self._find_saj_sequences(phonetic_endings)
        phonetic_verses_in_saj = sum(seq['length'] for seq in phonetic_sequences)
        phonetic_coverage = phonetic_verses_in_saj / total_verses if total_verses > 0 else 0
        phonetic_unique = len(set(phonetic_endings))

        candidates.append({
            'mode': 'phonetic',
            'length': None,
            'endings': phonetic_endings,
            'sequences': phonetic_sequences,
            'coverage': phonetic_coverage,
            'unique_patterns': phonetic_unique,
            'score': self._calculate_score(phonetic_coverage, phonetic_unique, total_verses)
        })

        # Select best approach (highest score)
        best = max(candidates, key=lambda x: x['score'])

        # Build verse details using best approach
        endings = best['endings']
        saj_sequences = best['sequences']

        verse_details = []
        for i, verse in enumerate(verses):
            # Find which sequence (if any) this verse belongs to
            sequence_info = None
            for seq in saj_sequences:
                if seq['start_verse'] <= i + 1 <= seq['end_verse']:
                    sequence_info = {
                        'sequence_id': seq['id'],
                        'pattern': seq['pattern'],
                        'sequence_length': seq['length'],
                        'position_in_sequence': i + 1 - seq['start_verse'] + 1
                    }
                    break

            verse_details.append({
                'verse_number': verse['number'],
                'ending_pattern': endings[i],
                'in_saj_sequence': sequence_info is not None,
                'saj_sequence': sequence_info
            })

        # Calculate chapter-level statistics
        verses_in_saj = sum(1 for v in verse_details if v['in_saj_sequence'])
        saj_coverage = verses_in_saj / total_verses if total_verses > 0 else 0

        # Find most common ending pattern
        ending_counts = Counter(endings)
        most_common_pattern = ending_counts.most_common(1)[0][0] if ending_counts else ""

        return {
            'chapter_summary': {
                'total_verses': total_verses,
                'total_saj_sequences': len(saj_sequences),
                'verses_in_saj': verses_in_saj,
                'saj_coverage': round(saj_coverage, 3),
                'most_common_pattern': most_common_pattern,
                'unique_patterns': len(ending_counts),
                'sequences': saj_sequences,
                'detection_mode': best['mode']  # NEW: track which mode was used
            },
            'verse_details': verse_details
        }

    def _calculate_score(self, coverage, unique_patterns, total_verses):
        """
        Calculate quality score for a pattern detection approach

        Higher score = better pattern detection

        Args:
            coverage: Fraction of verses in saj' sequences (0-1)
            unique_patterns: Number of unique ending patterns
            total_verses: Total number of verses

        Returns:
            Score (higher is better)
        """
        # Coverage is most important (weight: 70%)
        coverage_score = coverage * 0.7

        # Prefer fewer unique patterns (more consistency), but not too few
        # Ideal: 2-5 patterns for variety
        if unique_patterns == 1:
            # Single pattern = entire chapter is one rhyme (good!)
            consistency_score = 0.3
        elif 2 <= unique_patterns <= 5:
            # Multiple patterns with good variety (very good!)
            consistency_score = 0.3
        elif unique_patterns <= total_verses * 0.3:
            # Moderate number of patterns (acceptable)
            consistency_score = 0.2
        else:
            # Too many patterns = weak rhyming (bad)
            consistency_score = 0.1

        return coverage_score + consistency_score

    def _find_saj_sequences(self, endings):
        """
        Find all consecutive verse sequences with matching endings

        Args:
            endings: List of ending patterns for each verse

        Returns:
            List of saj' sequence dicts
        """
        if not endings:
            return []

        sequences = []
        sequence_id = 1
        i = 0

        while i < len(endings):
            current_pattern = endings[i]
            sequence_start = i
            sequence_length = 1

            # Look ahead for consecutive verses with same ending
            j = i + 1
            while j < len(endings) and endings[j] == current_pattern:
                sequence_length += 1
                j += 1

            # If sequence meets minimum length, record it
            if sequence_length >= self.min_sequence_length:
                sequences.append({
                    'id': sequence_id,
                    'pattern': current_pattern,
                    'start_verse': sequence_start + 1,  # 1-indexed
                    'end_verse': sequence_start + sequence_length,  # 1-indexed
                    'length': sequence_length
                })
                sequence_id += 1
                i = j  # Skip past this sequence
            else:
                i += 1  # Move to next verse

        return sequences


# ==================== TAKRAR ANALYZER ====================

class TakrarAnalyzer:
    """Analyzes repetition patterns (Takrar) - 4 types"""

    def __init__(self, morphology_data):
        """
        Initialize with morphology data for root/lemma analysis

        Args:
            morphology_data: List of morphology entries with location, root, lemma, pos
        """
        self.morphology_data = morphology_data

        # Build lookup index: (chapter, verse, word) -> morphology entry
        self.morph_index = {}
        for entry in morphology_data:
            loc = entry['location']
            key = (loc['chapter'], loc['verse'], loc['word'])
            if key not in self.morph_index:
                self.morph_index[key] = []
            self.morph_index[key].append(entry)

    def analyze_verse(self, chapter_num, verse_num, verse_text):
        """
        Analyze all 4 types of repetition in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number
            verse_text: Arabic text

        Returns:
            Dict with all repetition types
        """
        # Type 1: Word-level (exact matches)
        word_rep = self._detect_word_repetition(verse_text)

        # Type 2-4: Root, Lemma, Structural (require morphology)
        root_rep = self._detect_root_repetition(chapter_num, verse_num)
        lemma_rep = self._detect_lemma_repetition(chapter_num, verse_num)
        structural = self._detect_structural_repetition(chapter_num, verse_num)

        return {
            'word_level': word_rep,
            'root_level': root_rep,
            'lemma_level': lemma_rep,
            'structural_patterns': structural
        }

    def _detect_word_repetition(self, verse_text):
        """Detect exact word repetitions"""
        words = verse_text.strip().split()
        word_counts = Counter(words)

        # Return only words that appear 2+ times
        return {word: count for word, count in word_counts.items() if count > 1}

    def _detect_root_repetition(self, chapter, verse):
        """Detect root repetitions using morphology data"""
        roots = []

        # Get all morphology entries for this verse
        verse_morphs = self._get_verse_morphology(chapter, verse)

        for morph in verse_morphs:
            if 'root' in morph['morphology'] and morph['morphology']['root']:
                roots.append(morph['morphology']['root'])

        root_counts = Counter(roots)
        return {root: count for root, count in root_counts.items() if count > 1}

    def _detect_lemma_repetition(self, chapter, verse):
        """Detect lemma repetitions using morphology data"""
        lemmas = []

        verse_morphs = self._get_verse_morphology(chapter, verse)

        for morph in verse_morphs:
            if 'lemma' in morph['morphology'] and morph['morphology']['lemma']:
                lemmas.append(morph['morphology']['lemma'])

        lemma_counts = Counter(lemmas)
        return {lemma: count for lemma, count in lemma_counts.items() if count > 1}

    def _detect_structural_repetition(self, chapter, verse):
        """Detect repeated POS patterns"""
        pos_sequence = []

        verse_morphs = self._get_verse_morphology(chapter, verse)

        for morph in verse_morphs:
            if 'pos' in morph['morphology'] and morph['morphology']['pos']:
                pos_sequence.append(morph['morphology']['pos'])

        # Find repeated subsequences
        repeated = find_repeated_subsequences(pos_sequence, min_length=2)

        # Convert tuples back to lists for JSON serialization
        return [{'pattern': list(pattern), 'count': count + 1}
                for pattern, count in repeated.items()]

    def _get_verse_morphology(self, chapter, verse):
        """Get all morphology entries for a specific verse"""
        verse_morphs = []

        # Iterate through all possible word positions
        for word_num in range(1, 100):  # Reasonable upper bound
            key = (chapter, verse, word_num)
            if key in self.morph_index:
                verse_morphs.extend(self.morph_index[key])

        return verse_morphs

    def detect_positional_root_patterns(self, chapter_num, verses, min_sequence=3):
        """
        Detect root-based repetition patterns at specific word positions across verses

        This captures Takrar patterns where consecutive verses share the same root
        at the same structural position (e.g., verses all starting with "قُلْ")

        Args:
            chapter_num: Chapter number
            verses: List of verse dicts with 'text' and 'number' fields
            min_sequence: Minimum consecutive verses to form a pattern (default: 3)

        Returns:
            List of pattern dicts with:
                - root: The repeated root (e.g., "qwl")
                - position: Word position (1-indexed)
                - position_type: "opening", "middle", or "ending"
                - word_form: The actual word form (e.g., "قُلْ")
                - verses: List of verse numbers in pattern
                - verse_count: Number of verses in pattern
                - sequence_ranges: List of [start, end] ranges for consecutive sequences
        """
        patterns = []

        if not verses:
            return patterns

        # Determine max word position in chapter
        max_position = max(len(v['text'].split()) for v in verses)

        # Check each word position
        for position in range(1, max_position + 1):
            position_data = []

            # Collect roots at this position across all verses
            for verse in verses:
                verse_num = verse['number']
                root = self._get_root_at_position(chapter_num, verse_num, position)

                if root:
                    word = self._get_word_at_position(verse['text'], position)
                    position_data.append({
                        'verse': verse_num,
                        'root': root,
                        'word': word
                    })

            # Find consecutive sequences with matching roots
            if len(position_data) >= min_sequence:
                sequences = self._find_consecutive_root_sequences(position_data, min_sequence)

                # Store valid patterns
                for seq in sequences:
                    pattern_type = self._classify_position_type(position, max_position)
                    patterns.append({
                        'root': seq['root'],
                        'position': position,
                        'position_type': pattern_type,
                        'word_form': seq['word_form'],
                        'verses': seq['verses'],
                        'verse_count': len(seq['verses']),
                        'sequence_ranges': seq['ranges']
                    })

        return patterns

    def _get_root_at_position(self, chapter, verse, position):
        """
        Get the root of the word at a specific position in a verse

        Args:
            chapter: Chapter number
            verse: Verse number
            position: Word position (1-indexed)

        Returns:
            Root string or None if not found
        """
        key = (chapter, verse, position)
        if key in self.morph_index and self.morph_index[key]:
            # Get first segment's root (usually the stem)
            for entry in self.morph_index[key]:
                if 'root' in entry['morphology'] and entry['morphology']['root']:
                    return entry['morphology']['root']
        return None

    def _get_word_at_position(self, verse_text, position):
        """
        Extract the word at a specific position from verse text

        Args:
            verse_text: Arabic verse text
            position: Word position (1-indexed)

        Returns:
            Word string or None if position out of range
        """
        words = verse_text.strip().split()
        if 1 <= position <= len(words):
            return words[position - 1]
        return None

    def _find_consecutive_root_sequences(self, position_data, min_length):
        """
        Find sequences where consecutive verses share the same root at a position

        Args:
            position_data: List of dicts with 'verse', 'root', 'word' keys
            min_length: Minimum sequence length to be considered a pattern

        Returns:
            List of sequence dicts with root, verses, word_form, ranges
        """
        if not position_data or len(position_data) < min_length:
            return []

        sequences = []
        i = 0

        while i < len(position_data):
            current_root = position_data[i]['root']
            current_word = position_data[i]['word']
            sequence_verses = [position_data[i]['verse']]
            sequence_start = i

            # Look ahead for consecutive verses with same root
            j = i + 1
            while j < len(position_data) and position_data[j]['root'] == current_root:
                sequence_verses.append(position_data[j]['verse'])
                j += 1

            # If sequence meets minimum length, record it
            if len(sequence_verses) >= min_length:
                # Build ranges of consecutive verse numbers
                ranges = []
                range_start = sequence_verses[0]
                prev_verse = sequence_verses[0]

                for verse in sequence_verses[1:]:
                    if verse != prev_verse + 1:
                        # End current range
                        ranges.append([range_start, prev_verse])
                        range_start = verse
                    prev_verse = verse

                # Add final range
                ranges.append([range_start, prev_verse])

                sequences.append({
                    'root': current_root,
                    'word_form': current_word,
                    'verses': sequence_verses,
                    'ranges': ranges
                })

                i = j  # Skip past this sequence
            else:
                i += 1  # Move to next verse

        return sequences

    def _classify_position_type(self, position, max_position):
        """
        Classify word position as 'opening', 'middle', or 'ending'

        Args:
            position: Word position (1-indexed)
            max_position: Maximum word position in chapter

        Returns:
            String: "opening", "middle", or "ending"
        """
        if position == 1:
            return 'opening'
        elif position >= max_position - 1:
            return 'ending'
        else:
            return 'middle'

    def calculate_chapter_summary(self, verse_analyses, positional_patterns=None):
        """
        Calculate chapter-level takrar summary including positional patterns

        Args:
            verse_analyses: List of verse analysis dicts
            positional_patterns: Optional list of positional root patterns

        Returns:
            Dict with takrar summary
        """
        total_word_reps = sum(
            sum(v['takrar']['word_level'].values())
            for v in verse_analyses if 'takrar' in v
        )

        total_root_reps = sum(
            sum(v['takrar']['root_level'].values())
            for v in verse_analyses if 'takrar' in v
        )

        # Find most repeated root across chapter
        all_roots = Counter()
        for verse in verse_analyses:
            if 'takrar' in verse:
                all_roots.update(verse['takrar']['root_level'])

        most_repeated_root = all_roots.most_common(1)[0][0] if all_roots else None

        summary = {
            'total_word_repetitions': total_word_reps,
            'total_root_repetitions': total_root_reps,
            'most_repeated_root': most_repeated_root
        }

        # Add positional patterns if provided
        if positional_patterns:
            summary['positional_root_patterns'] = positional_patterns

        return summary


# ==================== JINAS ANALYZER ====================

class JinasAnalyzer:
    """Analyzes wordplay/paronomasia (Jinas)"""

    def __init__(self, morphology_data, similarity_threshold=0.75):
        """
        Initialize with morphology data and similarity threshold

        Args:
            morphology_data: List of morphology entries
            similarity_threshold: Minimum similarity to consider jinas (0-1)
        """
        self.morphology_data = morphology_data
        self.similarity_threshold = similarity_threshold

        # Build lookup index
        self.morph_index = {}
        for entry in morphology_data:
            loc = entry['location']
            key = (loc['chapter'], loc['verse'], loc['word'])
            if key not in self.morph_index:
                self.morph_index[key] = []
            self.morph_index[key].append(entry)

    def analyze_verse(self, chapter_num, verse_num, verse_text):
        """
        Find all jinas (wordplay) instances in a verse

        Args:
            chapter_num: Chapter number
            verse_num: Verse number
            verse_text: Arabic text

        Returns:
            List of jinas instances
        """
        words = verse_text.strip().split()

        if len(words) < 2:
            return []

        jinas_instances = []

        # Compare all word pairs
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                word1 = words[i]
                word2 = words[j]

                # Calculate similarity
                similarity = calculate_similarity(word1, word2)

                if similarity >= self.similarity_threshold:
                    # Get roots to verify different meanings
                    root1 = self._get_word_root(chapter_num, verse_num, i + 1)
                    root2 = self._get_word_root(chapter_num, verse_num, j + 1)

                    # Only jinas if roots differ (or if same root, it's derivational jinas)
                    if root1 and root2:
                        jinas_type = self._classify_jinas(word1, word2, root1, root2)

                        # Skip if None (identical words with same root = takrar, not jinas)
                        if jinas_type:
                            jinas_instances.append({
                                'word1': word1,
                                'word2': word2,
                                'positions': [i + 1, j + 1],
                                'similarity': round(similarity, 3),
                                'type': jinas_type,
                                'roots': [root1, root2]
                            })

        return jinas_instances

    def _get_word_root(self, chapter, verse, word_num):
        """Get the root of a specific word"""
        key = (chapter, verse, word_num)
        if key in self.morph_index and self.morph_index[key]:
            # Get first segment's root (usually the stem)
            for entry in self.morph_index[key]:
                if 'root' in entry['morphology'] and entry['morphology']['root']:
                    return entry['morphology']['root']
        return None

    def _classify_jinas(self, word1, word2, root1, root2):
        """
        Classify jinas type

        Types:
        - jinas_tamm: Identical spelling, different roots
        - jinas_ishtiqaq: Same root, different forms (derivational)
        - jinas_qalb: Reversed letters
        - jinas_ghayr_tamm: High similarity, different roots
        """
        clean1 = remove_diacritics(word1)
        clean2 = remove_diacritics(word2)

        # Filter out identical words with same root (this is takrar/repetition, not jinas)
        # Jinas requires semantic distinction even with phonetic similarity
        if clean1 == clean2 and root1 == root2:
            return None

        # Complete jinas (identical)
        if clean1 == clean2 and root1 != root2:
            return "jinas_tamm"

        # Derivational jinas (same root)
        if root1 == root2:
            return "jinas_ishtiqaq"

        # Reversal jinas
        if clean1 == clean2[::-1]:
            return "jinas_qalb"

        # Incomplete jinas (high similarity, different meaning)
        return "jinas_ghayr_tamm"


# ==================== MAIN PROCESSING ====================

def load_quran_text(filepath):
    """Load Quran text from JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_morphology_data(filepath):
    """
    Load morphology data from JSON and flatten to list of entries

    Handles both old morphology_full.json (flat) and new morphology_aligned.json (hierarchical)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    morphology = data['morphology']

    # Check if already flat list or hierarchical
    if morphology and isinstance(morphology[0], dict) and 'verses' in morphology[0]:
        # Hierarchical structure (morphology_aligned.json) - flatten it
        flat_list = []
        for chapter in morphology:
            for verse in chapter['verses']:
                for word in verse['words']:
                    flat_list.append(word)
        return flat_list
    else:
        # Already flat list (old format)
        return morphology

def analyze_full_quran():
    """Main function to analyze entire Quran"""
    print("=" * 70)
    print("QURANIC BALAGHAH ANALYSIS - TIER 1")
    print("Devices: Saj' (Rhyme), Takrar (Repetition), Jinas (Wordplay)")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    quran_path = os.path.join(project_root, 'data', 'text', 'quran_text.json')
    morph_path = os.path.join(project_root, 'data', 'linguistic', 'morphology_aligned.json')

    quran_data = load_quran_text(quran_path)
    morphology = load_morphology_data(morph_path)

    print(f"  Loaded {len(quran_data['chapters'])} chapters")
    print(f"  Loaded {len(morphology)} morphology entries")
    print()

    # Initialize analyzers
    print("Initializing analyzers...")
    saj_analyzer = SajAnalyzer()
    takrar_analyzer = TakrarAnalyzer(morphology)
    jinas_analyzer = JinasAnalyzer(morphology)
    print("  [OK] Saj' Analyzer")
    print("  [OK] Takrar Analyzer")
    print("  [OK] Jinas Analyzer")
    print()

    # Process all chapters
    print("Processing Quran (114 chapters, 6,236 verses)...")
    print()

    results = {
        'metadata': {
            'source': 'Quranic Balaghah Analysis - Tier 1',
            'version': '1.0',
            'devices': ['saj', 'takrar', 'jinas'],
            'total_chapters': len(quran_data['chapters']),
            'total_verses': quran_data['metadata']['verses_count'],
            'analysis_date': datetime.now().isoformat()
        },
        'chapters': []
    }

    total_verses_processed = 0

    for chapter_data in quran_data['chapters']:
        chapter_num = chapter_data['number']
        chapter_name = chapter_data['name']
        verses = chapter_data['verses']

        print(f"  Chapter {chapter_num:3d}: ({len(verses)} verses)...", end=' ')

        # Analyze saj' for entire chapter
        saj_analysis = saj_analyzer.analyze_chapter(verses)

        # Analyze takrar and jinas for each verse
        verse_analyses = []
        for verse in verses:
            verse_num = verse['number']
            verse_text = verse['text']

            takrar = takrar_analyzer.analyze_verse(chapter_num, verse_num, verse_text)
            jinas = jinas_analyzer.analyze_verse(chapter_num, verse_num, verse_text)

            verse_analyses.append({
                'verse': verse_num,
                'text': verse_text,
                'takrar': takrar,
                'jinas': jinas
            })

        # Detect positional root patterns for entire chapter
        positional_patterns = takrar_analyzer.detect_positional_root_patterns(
            chapter_num, verses, min_sequence=3
        )

        # Calculate chapter-level takrar summary with positional patterns
        takrar_summary = takrar_analyzer.calculate_chapter_summary(
            verse_analyses, positional_patterns
        )

        # Match positional patterns to individual verses
        for verse_analysis in verse_analyses:
            verse_num = verse_analysis['verse']
            verse_patterns = []

            for pattern in positional_patterns:
                if verse_num in pattern['verses']:
                    verse_patterns.append({
                        'position': pattern['position'],
                        'position_type': pattern['position_type'],
                        'root': pattern['root'],
                        'word': pattern['word_form'],
                        'in_pattern': True,
                        'total_verses_in_pattern': pattern['verse_count']
                    })

            # Add positional patterns to verse takrar data
            verse_analysis['takrar']['positional_patterns'] = verse_patterns

        # Combine saj' verse details with takrar/jinas
        for i, verse_detail in enumerate(saj_analysis['verse_details']):
            verse_detail['text'] = verses[i]['text']
            verse_detail['saj'] = {
                'ending_pattern': verse_detail.pop('ending_pattern'),
                'in_saj_sequence': verse_detail.pop('in_saj_sequence'),
                'saj_sequence': verse_detail.pop('saj_sequence')
            }
            verse_detail['takrar'] = verse_analyses[i]['takrar']
            verse_detail['jinas'] = verse_analyses[i]['jinas']

        # Store chapter results
        results['chapters'].append({
            'chapter': chapter_num,
            'name_arabic': chapter_name,
            'verses_count': len(verses),
            'saj_summary': saj_analysis['chapter_summary'],
            'takrar_summary': takrar_summary,
            'verses': saj_analysis['verse_details']
        })

        total_verses_processed += len(verses)
        print("[OK]")

    print()
    print(f"Processed {total_verses_processed} verses across {len(results['chapters'])} chapters")
    print()

    # Save results
    output_path = os.path.join(project_root, 'data', 'linguistic', 'balaghah_tier1.json')
    print(f"Saving results to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Calculate file size
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"  [OK] Saved {file_size:.2f} MB")
    print()

    # Print summary statistics
    print("=" * 70)
    print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
    print("=" * 70)

    # Saj' statistics
    total_saj_sequences = sum(c['saj_summary']['total_saj_sequences']
                              for c in results['chapters'])
    total_verses_in_saj = sum(c['saj_summary']['verses_in_saj']
                             for c in results['chapters'])
    chapters_with_saj = sum(1 for c in results['chapters']
                           if c['saj_summary']['total_saj_sequences'] > 0)

    # Find chapters with high saj' coverage
    high_coverage_chapters = sum(1 for c in results['chapters']
                                if c['saj_summary']['saj_coverage'] >= 0.7)

    print(f"Saj' (Rhymed Prose):")
    print(f"  Total sequences found:     {total_saj_sequences}")
    print(f"  Chapters with saj':        {chapters_with_saj} / 114")
    print(f"  Total verses in saj':      {total_verses_in_saj} / 6,236")
    print(f"  High coverage chapters:    {high_coverage_chapters} (>=70% verses in saj')")
    print()

    # Takrar statistics
    total_word_reps = sum(c['takrar_summary']['total_word_repetitions']
                          for c in results['chapters'])
    total_root_reps = sum(c['takrar_summary']['total_root_repetitions']
                          for c in results['chapters'])

    # Positional pattern statistics
    total_pos_patterns = sum(
        len(c['takrar_summary'].get('positional_root_patterns', []))
        for c in results['chapters']
    )
    chapters_with_pos_patterns = sum(
        1 for c in results['chapters']
        if c['takrar_summary'].get('positional_root_patterns', [])
    )

    print(f"Takrar (Repetition):")
    print(f"  Total word repetitions: {total_word_reps}")
    print(f"  Total root repetitions: {total_root_reps}")
    print(f"  Positional root patterns: {total_pos_patterns}")
    print(f"  Chapters with positional patterns: {chapters_with_pos_patterns} / 114")
    print()

    # Jinas statistics
    total_jinas = sum(len(v['jinas']) for c in results['chapters']
                      for v in c['verses'])

    print(f"Jinas (Wordplay):")
    print(f"  Total instances: {total_jinas}")
    print()

    print("Analysis saved to: data/linguistic/balaghah_tier1.json")
    print("=" * 70)


if __name__ == '__main__':
    try:
        analyze_full_quran()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
