#!/usr/bin/env python3
"""
Get complete linguistic information for a Quranic verse or verse range
Now uses quran_comprehensive.json as single source of truth

Usage: Run the script and enter chapter:verse or chapter:verse1-verse2 when prompted
Example: 1:1 or 1:1-7
"""

import json
import os
import sys
import re

# Add path to loaders directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loaders'))


def filter_empty_values(obj):
    """
    Recursively remove empty values from dict/list to clean output.

    Removes:
    - Keys with empty dict {}
    - Keys with empty list []
    - Keys with None/null
    - Keys with empty strings ""

    Keeps only keys with actual data.

    This ensures the output to users/LLMs is clean and focused,
    containing only interesting findings without empty placeholders.
    """
    if isinstance(obj, dict):
        filtered = {}
        for k, v in obj.items():
            # Recursively filter the value first
            filtered_value = filter_empty_values(v)

            # Only keep if value is not empty
            if filtered_value not in ({}, [], None, ""):
                filtered[k] = filtered_value

        return filtered if filtered else {}

    elif isinstance(obj, list):
        # Filter each item in the list
        filtered = [filter_empty_values(item) for item in obj]
        # Remove empty items
        filtered = [item for item in filtered if item not in ({}, [], None, "")]
        return filtered

    else:
        # Return primitives as-is
        return obj


def load_comprehensive_quran(filepath):
    """Load the comprehensive Quran data file"""
    print(f"Loading comprehensive Quran data from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  Loaded {len(data['chapters'])} chapters")
    return data


def load_lemmas_dictionary(filepath):
    """Load lemmas dictionary with English translations

    Returns dict with both Buckwalter and Unicode lookups
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Build lookup dict: Both Buckwalter and Unicode -> English
        lookup = {}
        for entry in data.get('lemmas', []):
            buckwalter = entry.get('buckwalter')
            unicode_lemma = entry.get('unicode')
            english = entry.get('english')

            if buckwalter and english:
                lookup[buckwalter] = english
            if unicode_lemma and english:
                lookup[unicode_lemma] = english  # Also key by Unicode

        return lookup
    except:
        return {}


def load_dependencies(filepath):
    """Load syntactic dependency data"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('dependencies', [])
    except:
        return []


def load_named_entities(filepath):
    """Load named entity and concept annotations"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('entities', [])
    except:
        return []


def load_pause_marks(filepath):
    """Load tajweed pause mark annotations"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('pause_marks', [])
    except:
        return []


def load_root_meanings(filepath):
    """Load root meanings dictionary from Lane's Lexicon

    Returns dict mapping Arabic root -> meaning data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('roots', {})
    except:
        return {}


def get_lemma_translation(lemma_buckwalter, lemmas_dict):
    """
    Get English translation for a lemma

    Args:
        lemma_buckwalter: Lemma in Buckwalter transliteration
        lemmas_dict: Dictionary mapping Buckwalter -> English

    Returns:
        English translation or None if not found
    """
    if not lemma_buckwalter or not lemmas_dict:
        return None

    return lemmas_dict.get(lemma_buckwalter)


def filter_dependencies_by_verse(dependencies, chapter_num, verse_num):
    """
    Filter dependencies for a specific verse

    Args:
        dependencies: List of all dependencies
        chapter_num: Chapter number
        verse_num: Verse number

    Returns:
        List of dependency relations for this verse
    """
    verse_deps = []
    for dep in dependencies:
        child_loc = dep.get('child', {})
        if child_loc.get('chapter') == chapter_num and child_loc.get('verse') == verse_num:
            verse_deps.append(dep)
    return verse_deps


def filter_named_entities_by_verse(entities, chapter_num, verse_num):
    """
    Filter named entities for a specific verse

    Args:
        entities: List of all entities
        chapter_num: Chapter number
        verse_num: Verse number

    Returns:
        List of named entities for this verse
    """
    verse_entities = []
    for entity in entities:
        loc = entity.get('location', {}).get('start', {})
        if loc.get('chapter') == chapter_num and loc.get('verse') == verse_num:
            verse_entities.append(entity)
    return verse_entities


def chapter_verse_to_absolute(chapter_num, verse_num, comprehensive_data):
    """
    Convert chapter:verse reference to absolute verse number (1-6236)

    Args:
        chapter_num: Chapter number (1-114)
        verse_num: Verse number within chapter
        comprehensive_data: The comprehensive Quran data structure

    Returns:
        Absolute verse number
    """
    absolute_num = 0
    for chapter in comprehensive_data.get('chapters', []):
        ch_num = chapter.get('chapter_number')  # Note: key is 'chapter_number' not 'number'
        if ch_num is None:
            continue
        if ch_num < chapter_num:
            # Add all verses from previous chapters
            absolute_num += len(chapter.get('verses', []))
        elif ch_num == chapter_num:
            # Add verses up to the target verse
            absolute_num += verse_num
            break
    return absolute_num

def filter_pause_marks_by_verse(pause_marks, absolute_verse_num):
    """
    Filter pause marks for a specific verse using absolute verse number

    Note: The 'chapter' field in pause_marks.json actually stores the
    absolute verse number (1-6236), not the chapter number.

    Args:
        pause_marks: List of all pause marks
        absolute_verse_num: Absolute verse number (1-6236)

    Returns:
        List of pause marks for this verse
    """
    verse_marks = []
    for mark in pause_marks:
        loc = mark.get('location', {})
        # The 'chapter' field actually stores absolute verse number
        if loc.get('chapter') == absolute_verse_num:
            verse_marks.append(mark)
    return verse_marks


# ============================================================================
# Balaghah Enrichment Functions
# ============================================================================

def consolidate_saj_sequences(saj_list, verses_data):
    """
    Consolidate redundant saj' data by grouping verses in same sequence

    BEFORE (redundant):
    [
      {"verse": 4, "data": {"ending_pattern": "ر", "saj_sequence": {...}, ...}},
      {"verse": 5, "data": {"ending_pattern": "ر", "saj_sequence": {...}, ...}}
    ]

    AFTER (consolidated):
    [
      {
        "sequence": {"sequence_id": 1, "pattern": "ر", "total_verses": 21},
        "verses": [
          {"verse": 4, "position": 4, "rhyme_word": {"word": 10, "text": "..."}},
          {"verse": 5, "position": 5, "rhyme_word": {"word": 12, "text": "..."}}
        ]
      }
    ]
    """
    if not saj_list:
        return None

    # Group by sequence_id
    from collections import defaultdict
    sequences = defaultdict(list)

    for saj_entry in saj_list:
        verse_num = saj_entry['verse']
        saj_data = saj_entry['data']

        if not saj_data.get('in_saj_sequence'):
            continue

        seq_info = saj_data.get('saj_sequence', {})
        seq_id = seq_info.get('sequence_id')

        # Get rhyming word from verses_data
        verse_data = next((v for v in verses_data if v['verse_number'] == verse_num), None)
        rhyme_word_text = ''
        rhyme_word_num = None

        if verse_data:
            words = verse_data.get('words', [])
            if words:
                last_word = words[-1]
                rhyme_word_text = last_word.get('text', '')
                rhyme_word_num = len(words)

        # Add to sequence group
        sequences[seq_id].append({
            'verse': verse_num,
            'position': seq_info.get('position_in_sequence'),
            'rhyme_word': {
                'word': rhyme_word_num,
                'text': rhyme_word_text
            },
            '_seq_info': seq_info  # Temporary, for extracting common data
        })

    # Build consolidated structure
    consolidated = []
    for seq_id, verse_list in sorted(sequences.items()):
        if not verse_list:
            continue

        # Extract common sequence info from first verse
        first_verse = verse_list[0]
        seq_info = first_verse['_seq_info']

        # Remove temporary _seq_info from all verses
        for v in verse_list:
            del v['_seq_info']

        # Sort verses by position
        verse_list.sort(key=lambda v: v['position'])

        consolidated.append({
            'sequence': {
                'sequence_id': seq_id,
                'pattern': seq_info.get('pattern'),
                'total_verses': seq_info.get('sequence_length')
            },
            'verses': verse_list
        })

    # If only one sequence, simplify structure
    if len(consolidated) == 1:
        return consolidated[0]

    return consolidated if consolidated else None


def enrich_structural_patterns(structural_patterns, verses_data):
    """
    Enrich structural patterns with semantic interpretation AND actual word examples

    Aggregates patterns, filters for significance (count >= 4), and adds:
    - Linguistic meaning (VSO, SVO, Idafa, etc.)
    - Actual word examples with verse:word locations and text

    Scans verses to find actual instances of each pattern by matching POS sequences
    """
    if not structural_patterns:
        return None

    # Aggregate patterns by converting to dict keyed by tuple
    pattern_counts = {}
    for item in structural_patterns:
        pattern = item.get('pattern', [])
        count = item.get('count', 0)
        pattern_key = tuple(pattern)

        if pattern_key in pattern_counts:
            pattern_counts[pattern_key] += count
        else:
            pattern_counts[pattern_key] = count

    # Build POS sequence for all verses to find pattern examples
    verse_pos_data = []
    for verse_data in verses_data:
        verse_num = verse_data['verse_number']
        words_with_pos = []

        for word in verse_data.get('words', []):
            word_num = word['word_number']
            text = word.get('text', '')

            # Get POS from first morphology segment
            pos = None
            morphology = word.get('morphology', [])
            if morphology:
                first_seg = morphology[0]
                morph_data = first_seg.get('morphology', {})
                pos = morph_data.get('pos')

            if pos:
                words_with_pos.append({
                    'word': word_num,
                    'text': text,
                    'pos': pos
                })

        verse_pos_data.append({
            'verse': verse_num,
            'words': words_with_pos
        })

    # Filter for significant patterns (count >= 4) and find examples
    significant_patterns = []
    for pattern_tuple, count in pattern_counts.items():
        if count >= 4:
            pattern_list = list(pattern_tuple)
            interpretation = interpret_pattern(pattern_list)

            # Find examples of this pattern in verses (limit to 3)
            examples = []
            pattern_len = len(pattern_list)

            for verse_info in verse_pos_data:
                if len(examples) >= 3:
                    break

                verse_num = verse_info['verse']
                words = verse_info['words']

                # Sliding window to find pattern matches
                for i in range(len(words) - pattern_len + 1):
                    window = words[i:i + pattern_len]
                    window_pos = [w['pos'] for w in window]

                    # Check if this window matches the pattern
                    if window_pos == pattern_list:
                        examples.append({
                            'verse': verse_num,
                            'words': [
                                {
                                    'pos': w['pos'],
                                    'word': w['word'],
                                    'text': w['text']
                                }
                                for w in window
                            ]
                        })
                        break  # One example per verse max

            significant_patterns.append({
                'pattern': pattern_list,
                'count': count,
                'interpretation': interpretation,
                'examples': examples
            })

    # Sort by count descending
    significant_patterns.sort(key=lambda x: x['count'], reverse=True)

    # Add parallelism note if multiple patterns exist
    if len(significant_patterns) > 1:
        return {
            'patterns': significant_patterns,
            'parallelism_note': 'Multiple repeated patterns indicate structural parallelism - a rhetorical device creating balance, rhythm, and emphasis through systematic repetition'
        }
    elif significant_patterns:
        return {'patterns': significant_patterns}
    else:
        return None


def interpret_pattern(pattern):
    """
    Interpret the linguistic meaning of a structural pattern

    Based on Arabic syntax research:
    - VSO order = verbal sentence (action-oriented)
    - SVO order = nominal sentence (entity/state-oriented)
    - Construct state = genitive relationship
    - Prepositional phrases = spatial/temporal/relational context
    """
    if not pattern:
        return "Unknown pattern"

    pattern_str = '-'.join(pattern)

    # Two-element patterns
    if len(pattern) == 2:
        if pattern == ['V', 'N']:
            return "Verbal sentence structure (VSO): Action-focused, emphasizes what happens before who does it"
        elif pattern == ['N', 'V']:
            return "Nominal sentence structure (SVO): Entity-focused, emphasizes who/what before the action"
        elif pattern == ['N', 'N']:
            return "Idafa (construct state): Genitive relationship between nouns (possession, attribution, or specification)"
        elif pattern == ['P', 'N']:
            return "Prepositional phrase: Adds spatial, temporal, or relational context"
        elif pattern == ['ADJ', 'N']:
            return "Adjectival phrase: Noun modification (attribute or quality)"
        elif pattern == ['V', 'P']:
            return "Verb with preposition: Action with directional or contextual element"

    # Three-element patterns
    elif len(pattern) == 3:
        if pattern == ['V', 'N', 'N']:
            return "Verbal sentence with object + complement: Complete action statement"
        elif pattern == ['N', 'N', 'V']:
            return "Nominal structure with compound subject: Entity-focused with action"
        elif pattern == ['P', 'N', 'N']:
            return "Extended prepositional phrase: Complex relational context"
        elif pattern == ['N', 'V', 'N']:
            return "Subject-Verb-Object structure: Balanced narrative form"

    # Four+ element patterns
    elif len(pattern) >= 4:
        return f"Complex structure ({len(pattern)} elements): Extended clause with multiple components creating elaborate meaning"

    # Fallback for unrecognized patterns
    return f"Pattern: {pattern_str} (count indicates structural repetition)"


def buckwalter_to_arabic_root(buckwalter):
    """
    Convert Buckwalter transliteration to Arabic script for roots

    Simplified converter for common root letters
    """
    if not buckwalter or not isinstance(buckwalter, str):
        return buckwalter

    # Buckwalter to Arabic mapping for root letters
    conversion = {
        'A': 'ا', 'b': 'ب', 't': 'ت', 'v': 'ث', 'j': 'ج', 'H': 'ح',
        'x': 'خ', 'd': 'د', '*': 'ذ', 'r': 'ر', 'z': 'ز', 's': 'س',
        '$': 'ش', 'S': 'ص', 'D': 'ض', 'T': 'ط', 'Z': 'ظ', 'E': 'ع',
        'g': 'غ', 'f': 'ف', 'q': 'ق', 'k': 'ك', 'l': 'ل', 'm': 'م',
        'n': 'ن', 'h': 'ه', 'w': 'و', 'y': 'ي', 'Y': 'ى', 'p': 'ة',
        "'": 'ء', '>': 'ء', '<': 'ء', '&': 'ء', '}': 'ء', '{': 'ا',  # Hamza variants + alif
        # Diacritics/vowels to skip
        '^': '', '`': '', '~': '', 'a': '', 'u': '', 'i': '', 'o': '', 'F': '', 'N': '', 'K': '', '_': ''
    }

    arabic = ''
    for char in buckwalter:
        arabic += conversion.get(char, char)

    return arabic


def enrich_takrar_with_locations(verses_data, takrar_data):
    """
    Enrich Takrar (repetition) data with lemma examples (NOT word locations)

    WARNING: Word numbering mismatch between morphology and text sources means
    word locations are unreliable. Instead, we show lemmas (dictionary forms)
    converted from Buckwalter to Arabic.

    IMPORTANT: Handles format mismatch:
    - takrar_data has roots in Arabic script (e.g., "قول")
    - morphology has roots in Buckwalter (e.g., "qwl")
    - We convert Buckwalter to Arabic for matching
    """
    if not takrar_data:
        return takrar_data

    enriched = {}

    # Enrich root-level repetitions with lemmas
    if takrar_data.get('root_level'):
        root_lemmas = {}

        for verse_data in verses_data:
            words = verse_data.get('words', [])

            for word in words:
                morphology = word.get('morphology', [])
                if morphology:
                    first_seg = morphology[0]
                    morph_data = first_seg.get('morphology', {})
                    root_buckwalter = morph_data.get('root')  # In Buckwalter format

                    if root_buckwalter:
                        # Convert Buckwalter to Arabic for matching
                        root_arabic = buckwalter_to_arabic_root(root_buckwalter)

                        if root_arabic in takrar_data['root_level']:
                            # Get lemma and convert to Arabic
                            lemma_buckwalter = morph_data.get('lemma', '')
                            lemma_arabic = buckwalter_to_arabic_root(lemma_buckwalter) if lemma_buckwalter else '?'

                            if root_arabic not in root_lemmas:
                                root_lemmas[root_arabic] = set()  # Use set to avoid duplicates

                            root_lemmas[root_arabic].add(lemma_arabic)

        # Build enriched root repetitions with lemmas (not locations)
        enriched_roots = {}
        for root, count in takrar_data['root_level'].items():
            enriched_data = {'count': count}

            if root in root_lemmas:
                enriched_data['lemmas'] = sorted(list(root_lemmas[root]))
                enriched_data['note'] = 'Lemmas shown (dictionary forms). Word locations not shown due to data alignment issues.'
            else:
                enriched_data['lemmas'] = []

            enriched_roots[root] = enriched_data

        enriched['root_repetitions'] = enriched_roots

    # Keep other takrar fields as-is
    if takrar_data.get('word_level'):
        enriched['word_level'] = takrar_data['word_level']

    if takrar_data.get('lemma_level'):
        enriched['lemma_level'] = takrar_data['lemma_level']

    if takrar_data.get('structural_patterns'):
        # Enrich structural patterns with semantic interpretation and actual word examples
        enriched_patterns = enrich_structural_patterns(
            takrar_data['structural_patterns'],
            verses_data
        )
        if enriched_patterns:
            enriched['structural_patterns'] = enriched_patterns

    if takrar_data.get('positional_patterns'):
        # Positional patterns already have word info from tier1
        enriched['positional_patterns'] = takrar_data['positional_patterns']

    return enriched if enriched else takrar_data


def parse_verb_form_from_features(features_raw):
    """
    Extract verb form from features_raw string

    Pattern: "(Roman numeral)" like "(II)", "(IV)", "(X)"
    Converts to: "VF:2", "VF:4", "VF:10"
    """
    import re

    # Roman to Arabic numeral mapping
    roman_to_num = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15
    }

    # Match pattern like "(II)" or "(IV)"
    match = re.search(r'\(([IVX]+)\)', features_raw)
    if match:
        roman = match.group(1)
        if roman in roman_to_num:
            return roman_to_num[roman]

    return None


def parse_definiteness_from_features(features_raw, pos):
    """
    Extract definiteness from features_raw string

    "Al+" prefix indicates definite article (DEF)
    No "Al+" and POS is N/ADJ indicates indefinite (INDEF)
    """
    if not pos or pos not in ['N', 'ADJ']:
        return None

    # Check for definite article prefix
    if 'Al+' in features_raw or 'al+' in features_raw:
        return 'DEF'
    else:
        return 'INDEF'


def get_verb_form_meaning(form_num):
    """
    Get the meaning/description of Arabic verb forms (awzan)

    Based on standard Arabic grammar:
    Form I (فَعَلَ) = basic meaning
    Form II (فَعَّلَ) = causative/intensive
    Form III (فَاعَلَ) = reciprocal/attempt
    etc.
    """
    meanings = {
        1: "Form I (فَعَلَ): Basic triliteral root - simple action",
        2: "Form II (فَعَّلَ): Causative/intensive - to cause to do, do repeatedly",
        3: "Form III (فَاعَلَ): Reciprocal/attempt - to do with/to someone",
        4: "Form IV (أَفْعَلَ): Causative - to cause to do, make someone do",
        5: "Form V (تَفَعَّلَ): Reflexive of Form II - to become, pretend",
        6: "Form VI (تَفَاعَلَ): Reflexive of Form III - to do mutually",
        7: "Form VII (اِنْفَعَلَ): Passive/reflexive - to be done (passive sense)",
        8: "Form VIII (اِفْتَعَلَ): Reflexive - to do for oneself",
        9: "Form IX (اِفْعَلَّ): Colors and defects - to become (a color/state)",
        10: "Form X (اِسْتَفْعَلَ): Seeking/requesting - to seek to do, ask for",
        11: "Form XI (اِفْعَالَّ): Rare - colors and defects",
        12: "Form XII (اِفْعَوْعَلَ): Rare - colors",
        15: "Form XV (اِفْعَنْلَلَ): Quadriliteral form"
    }

    return meanings.get(form_num, f"Form {form_num}: Advanced/rare form")


def enrich_verb_forms(verses_data, maani_data, lemmas_dict=None):
    """
    Enrich Ma'ani verb forms data with actual verbs + meanings + translations

    Parses features_raw to extract verb form from "(Roman)" pattern
    Adds semantic meaning for each form
    Shows actual verb words (not locations due to alignment issues)
    Adds English translations from lemmas dictionary
    """
    if not maani_data:
        return maani_data

    # Collect all verbs from verses
    verb_forms_found = {}

    for verse_data in verses_data:
        verse_num = verse_data['verse_number']
        words = verse_data.get('words', [])

        for word in words:
            morphology = word.get('morphology', [])
            if morphology:
                first_seg = morphology[0]
                morph_data = first_seg.get('morphology', {})

                # Check if it's a verb
                if morph_data.get('pos') == 'V':
                    # Parse verb form from features_raw
                    features_raw = morph_data.get('features_raw', '')
                    verb_form_num = parse_verb_form_from_features(features_raw)

                    # Get lemma as example (not actual word text due to alignment)
                    lemma_buck = morph_data.get('lemma', '')
                    lemma_arabic = buckwalter_to_arabic_root(lemma_buck) if lemma_buck else '?'

                    if verb_form_num:
                        form_key = f'VF:{verb_form_num}'

                        if form_key not in verb_forms_found:
                            verb_forms_found[form_key] = {
                                'form': verb_form_num,
                                'meaning': get_verb_form_meaning(verb_form_num),
                                'lemmas': set(),  # Use set to avoid duplicates
                                'lemmas_buckwalter': set()
                            }

                        verb_forms_found[form_key]['lemmas'].add(lemma_arabic)
                        if lemma_buck:
                            verb_forms_found[form_key]['lemmas_buckwalter'].add(lemma_buck)

    # Convert to output format
    if verb_forms_found:
        enriched_forms = []
        for form_key, data in sorted(verb_forms_found.items()):
            form_entry = {
                'form': data['form'],
                'meaning': data['meaning'],
                'lemmas': sorted(list(data['lemmas'])),
                'count': len(data['lemmas'])
            }

            # Add translations if lemmas_dict available
            if lemmas_dict:
                translations = []
                for buck in data['lemmas_buckwalter']:
                    trans = get_lemma_translation(buck, lemmas_dict)
                    if trans:
                        translations.append(trans)
                if translations:
                    form_entry['translations'] = translations

            enriched_forms.append(form_entry)

        maani_data['verb_forms'] = enriched_forms
    else:
        # Remove verb_forms if no verbs found
        maani_data.pop('verb_forms', None)

    return maani_data


def enrich_definiteness(verses_data, maani_data):
    """
    Enrich Ma'ani definiteness data with actual lemmas

    Parses features_raw to detect "Al+" prefix for definiteness
    Shows lemmas (dictionary forms) not word locations due to alignment issues
    """
    if not maani_data:
        return maani_data

    definite_lemmas = set()
    indefinite_lemmas = set()

    for verse_data in verses_data:
        words = verse_data.get('words', [])

        for word in words:
            morphology = word.get('morphology', [])
            if morphology:
                first_seg = morphology[0]
                morph_data = first_seg.get('morphology', {})

                # Check POS (only nouns/adjectives have definiteness)
                pos = morph_data.get('pos')
                if pos not in ['N', 'ADJ']:
                    continue

                # Parse definiteness from features_raw
                features_raw = morph_data.get('features_raw', '')
                definiteness = parse_definiteness_from_features(features_raw, pos)

                # Get lemma
                lemma_buck = morph_data.get('lemma', '')
                lemma_arabic = buckwalter_to_arabic_root(lemma_buck) if lemma_buck else None

                if lemma_arabic:
                    if definiteness == 'DEF':
                        definite_lemmas.add(lemma_arabic)
                    elif definiteness == 'INDEF':
                        indefinite_lemmas.add(lemma_arabic)

    # Replace old format with enriched data
    if definite_lemmas or indefinite_lemmas:
        result = {}
        if definite_lemmas:
            result['definite'] = {
                'lemmas': sorted(list(definite_lemmas)),
                'count': len(definite_lemmas),
                'description': 'Words with definite article (ال) - specific/known entities'
            }
        if indefinite_lemmas:
            result['indefinite'] = {
                'lemmas': sorted(list(indefinite_lemmas)),
                'count': len(indefinite_lemmas),
                'description': 'Words without definite article - general/indefinite entities'
            }

        maani_data['definiteness'] = result
    else:
        # Remove definiteness if no words found
        maani_data.pop('definiteness', None)

    return maani_data


def enrich_muqabala(muqabala_data, verses_data, lemmas_dict=None):
    """
    Enrich muqabala (parallelism) patterns with translations

    Args:
        muqabala_data: The muqabala structure from comprehensive data
        verses_data: List of verses to extract morphology from
        lemmas_dict: Dictionary for lemma translations

    Returns:
        Enriched muqabala data with translations added
    """
    if not muqabala_data or not lemmas_dict:
        return muqabala_data

    # Build lookup maps: arabic_lemma -> lemma_buckwalter (for translation)
    # Also: root -> lemma_buckwalter
    lemma_arabic_to_buck = {}
    root_to_lemma_buck = {}

    for verse_data in verses_data:
        words = verse_data.get('words', [])
        for word in words:
            morphology = word.get('morphology', [])
            if morphology:
                morph_entry = morphology[0]
                morph_data = morph_entry.get('morphology', {})

                # Get lemma (already in Unicode Arabic)
                lemma_arabic = morph_data.get('lemma', '')
                root = morph_data.get('root', '')

                if lemma_arabic:
                    # For lemmas_dict lookup, we need Buckwalter
                    # But the comprehensive data has lemma in Arabic Unicode already
                    # We'll use the Arabic lemma as-is for matching
                    lemma_arabic_to_buck[lemma_arabic] = lemma_arabic  # Store for now

                    if root:
                        if root not in root_to_lemma_buck:
                            root_to_lemma_buck[root] = []
                        root_to_lemma_buck[root].append(lemma_arabic)

    # Enrich each muqabala pattern
    enriched_data = muqabala_data.copy()
    patterns = enriched_data.get('muqabala_patterns', [])

    for pattern in patterns:
        # Enrich structure1 and structure2
        for struct_key in ['structure1', 'structure2']:
            if struct_key in pattern:
                structure = pattern[struct_key]

                # Iterate through all elements (P, N, V, etc.)
                for pos_key, element in structure.items():
                    if isinstance(element, dict):
                        # Try using root first (more reliable)
                        root = element.get('root')
                        arabic_text = element.get('arabic', '')

                        lemma_to_translate = None

                        if root and root in root_to_lemma_buck:
                            # Use first lemma for this root
                            lemma_to_translate = root_to_lemma_buck[root][0]
                        elif arabic_text in lemma_arabic_to_buck:
                            # Direct lemma match
                            lemma_to_translate = arabic_text

                        if lemma_to_translate:
                            # Lemma is in Unicode Arabic, look it up directly in lemmas_dict
                            # lemmas_dict keys are in Arabic Unicode
                            if lemma_to_translate in lemmas_dict:
                                translation = lemmas_dict[lemma_to_translate]
                                element['translation'] = translation

    return enriched_data


def _summarize_balaghah_features(features):
    """
    Create comprehensive summary of ALL detected balaghah features

    Args:
        features: Dict with balaghah features from all tiers

    Returns:
        List of summary strings
    """
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

    if features.get('qasam'):
        qasam = features['qasam']
        summary.append(f"qasam (oath: {qasam['count']} elements)")

    if features.get('muqattaat'):
        muqattaat = features['muqattaat']
        summary.append(f"muqatta'at (disconnected letters: {muqattaat['letters']})")

    if features.get('interrogative'):
        interrog = features['interrogative']
        summary.append(f"interrogative (questions: {interrog['count']} particles)")

    if features.get('restriction'):
        restrict = features['restriction']
        summary.append(f"restriction (hasr: {restrict['count']} patterns)")

    if features.get('particles_emphasis'):
        emph = features['particles_emphasis']
        summary.append(f"emphasis particles (ta'kid: {emph['count']} particles)")

    return summary if summary else ['no rhetorical features detected']


def detect_qasam(verse_data):
    """
    Detect qasam (oath) patterns syntactically using word-level morphology

    Qasam indicators:
    - Word starting with وَ (wa) or تَ (ta) at verse start
    - Noun in GENITIVE case
    - That noun is what Allah swears by

    Returns:
        dict with 'has_qasam' flag and 'elements' list, or None
    """
    words = verse_data.get('words', [])
    if not words:
        return None

    oath_elements = []

    # Check first few words for oath pattern
    for i, word in enumerate(words[:5]):  # Check first 5 words
        word_text = word.get('text', '')
        morphology = word.get('morphology', [])

        if not morphology or not word_text:
            continue

        # Get morphology data (word-level from comprehensive data)
        morph_entry = morphology[0]
        morph_data = morph_entry.get('morphology', {})

        pos = morph_data.get('pos')
        features = morph_data.get('features', {})
        case = features.get('case')
        root = morph_data.get('root')
        lemma = morph_data.get('lemma')

        # Detect oath pattern: word starts with وَ or تَ, and has genitive noun
        if (word_text.startswith('وَ') or word_text.startswith('تَ')) and pos == 'N' and case == 'GEN':
            # Determine oath particle from text
            particle = 'و' if word_text.startswith('وَ') else 'ت'

            element = {
                'particle': particle,
                'word_number': word.get('word_number'),
                'word_text': word_text,
                'lemma': lemma
            }

            # Add root if available
            if root:
                element['root'] = root

            oath_elements.append(element)

    if oath_elements:
        return {
            'has_qasam': True,
            'elements': oath_elements,
            'count': len(oath_elements)
        }

    return None


def detect_muqattaat(verse_data):
    """
    Detect muqatta'at (disconnected letters) at verse start

    Muqatta'at are mysterious letters/letter combinations at chapter openings:
    - Examples: ن، الم، حم، طه، يس
    - Usually first word of verse
    - Typically particles (POS:P) or short combinations
    - Single letters or 2-5 letter sequences

    Returns:
        dict with 'has_muqattaat' flag and details, or None
    """
    words = verse_data.get('words', [])
    verse_num = verse_data.get('verse_number')

    # Muqatta'at only appear at verse 1 (chapter openings)
    if not words or verse_num != 1:
        return None

    # Check first word
    first_word = words[0]
    word_text = first_word.get('text', '')
    morphology = first_word.get('morphology', [])

    if not morphology or not word_text:
        return None

    # Get morphology data
    morph_entry = morphology[0]
    morph_data = morph_entry.get('morphology', {})
    pos = morph_data.get('pos')

    # Muqatta'at characteristics:
    # 1. POS is typically 'P' (particle)
    # 2. Short text (1-5 characters, accounting for diacritics)
    # 3. First word of chapter
    word_length = len(word_text)

    if pos == 'P' and word_length <= 6:  # Allow up to 6 chars for diacritics
        return {
            'has_muqattaat': True,
            'letters': word_text,
            'word_number': first_word.get('word_number'),
            'interpretation': 'unknown',  # Meaning is known only to Allah
            'note': 'Disconnected letters at chapter opening'
        }

    return None


def detect_particles(verse_data):
    """
    Detect key particles for balaghah analysis (syntactic detection only)

    Categories:
    1. Interrogative particles: هل، أ، ما، من، متى، أين، كيف
    2. Restriction particles: إنما، ما...إلا pattern
    3. Emphasis particles: إن، أن، لَ (lam), قد، لقد

    Returns:
        dict with particle categories and their occurrences, or None
    """
    words = verse_data.get('words', [])
    if not words:
        return None

    particles_found = {
        'interrogative': [],
        'restriction': [],
        'emphasis': []
    }

    # Interrogative particles (questions)
    interrogative_lemmas = {'هل', 'أ', 'ما', 'من', 'متى', 'أين', 'كيف', 'كم', 'أي', 'أين', 'أنى'}

    # Emphasis particles
    emphasis_lemmas = {'إن', 'إنّ', 'أن', 'أنّ', 'ل', 'قد', 'لقد'}

    # Check each word
    for i, word in enumerate(words):
        word_text = word.get('text', '')
        morphology = word.get('morphology', [])

        if not morphology:
            continue

        morph_entry = morphology[0]
        morph_data = morph_entry.get('morphology', {})

        pos = morph_data.get('pos')
        lemma = morph_data.get('lemma', '')

        # Detect interrogative particles
        if lemma in interrogative_lemmas:
            particles_found['interrogative'].append({
                'particle': lemma,
                'word_number': word.get('word_number'),
                'word_text': word_text,
                'position': 'initial' if i < 3 else 'medial'
            })

        # Detect emphasis particles
        if lemma in emphasis_lemmas or word_text.startswith('لَ'):
            particles_found['emphasis'].append({
                'particle': lemma if lemma in emphasis_lemmas else 'ل',
                'word_number': word.get('word_number'),
                'word_text': word_text,
                'type': 'assertion'
            })

        # Detect restriction: إنما
        if lemma == 'إنما' or word_text == 'إِنَّمَا':
            particles_found['restriction'].append({
                'pattern': 'innama',
                'word_number': word.get('word_number'),
                'word_text': word_text,
                'type': 'exclusive_restriction'
            })

    # Detect restriction pattern: ما...إلا (what...except)
    ma_positions = []
    illa_positions = []

    for i, word in enumerate(words):
        word_text = word.get('text', '')
        morphology = word.get('morphology', [])

        if morphology:
            morph_entry = morphology[0]
            morph_data = morph_entry.get('morphology', {})
            lemma = morph_data.get('lemma', '')

            if lemma == 'ما':
                ma_positions.append((i, word.get('word_number'), word_text))
            elif lemma == 'إلا' or lemma == 'إلّا':
                illa_positions.append((i, word.get('word_number'), word_text))

    # Match ما...إلا patterns
    for ma_idx, ma_word_num, ma_text in ma_positions:
        for illa_idx, illa_word_num, illa_text in illa_positions:
            if illa_idx > ma_idx and (illa_idx - ma_idx) < 10:  # Within 10 words
                particles_found['restriction'].append({
                    'pattern': 'ma_illa',
                    'word_numbers': [ma_word_num, illa_word_num],
                    'words': [ma_text, illa_text],
                    'type': 'exception_restriction',
                    'span': illa_idx - ma_idx
                })

    # Build result
    result = {}
    if particles_found['interrogative']:
        result['interrogative'] = {
            'has_interrogative': True,
            'particles': particles_found['interrogative'],
            'count': len(particles_found['interrogative'])
        }

    if particles_found['restriction']:
        result['restriction'] = {
            'has_restriction': True,
            'patterns': particles_found['restriction'],
            'count': len(particles_found['restriction'])
        }

    if particles_found['emphasis']:
        result['emphasis'] = {
            'has_emphasis': True,
            'particles': particles_found['emphasis'],
            'count': len(particles_found['emphasis'])
        }

    return result if result else None


def distribute_balaghah_to_verses(verses_data, lemmas_dict, chapter_num, comprehensive_data):
    """
    Distribute balaghah features to individual verses + chapter-level aggregates

    Returns 2-level structure:
    1. Chapter-level: Root repetitions (aggregated once)
    2. Verse-level: Individual features per verse

    Includes:
    - Tier 1: saj', takrar, jinas
    - Tier 2: ma'ani (verb forms, definiteness, structural patterns)
    - Advanced: iltifat, wasl/fasl, muqabala, isti'anaf, hadhf, tafsir context

    Args:
        verses_data: List of verse data
        lemmas_dict: Dictionary for lemma translations
        chapter_num: Chapter number for context
        comprehensive_data: Full comprehensive data for metadata

    Returns: tuple (chapter_balaghah, verse_balaghah)
        - chapter_balaghah: Dict with chapter-level patterns
        - verse_balaghah: Dict mapping verse_number -> verse features
    """
    verse_balaghah = {}
    chapter_balaghah = {}

    # Extract metadata for tafsir context generation
    asbab_nuzul_data = comprehensive_data.get('metadata', {}).get('asbab_nuzul', {})
    chapter_metadata = comprehensive_data.get('metadata', {}).get('chapter_metadata', {})

    # Build root repetition map (which verses have which roots)
    root_to_verses = {}
    root_to_lemmas = {}
    root_to_lemmas_buckwalter = {}  # Keep Buckwalter for translation lookup

    for verse_data in verses_data:
        verse_num = verse_data['verse_number']
        words = verse_data.get('words', [])

        # Collect roots from this verse
        for word in words:
            morphology = word.get('morphology', [])
            if morphology:
                first_seg = morphology[0]
                morph_data = first_seg.get('morphology', {})
                root_buck = morph_data.get('root')
                lemma_buck = morph_data.get('lemma')

                if root_buck:
                    root_arabic = buckwalter_to_arabic_root(root_buck)
                    lemma_arabic = buckwalter_to_arabic_root(lemma_buck) if lemma_buck else None

                    if root_arabic not in root_to_verses:
                        root_to_verses[root_arabic] = set()
                        root_to_lemmas[root_arabic] = set()
                        root_to_lemmas_buckwalter[root_arabic] = set()

                    root_to_verses[root_arabic].add(verse_num)
                    if lemma_arabic and lemma_buck:
                        root_to_lemmas[root_arabic].add(lemma_arabic)
                        root_to_lemmas_buckwalter[root_arabic].add(lemma_buck)

    # Filter roots that appear in 2+ verses (repetitions)
    repeated_roots = {root: verses for root, verses in root_to_verses.items() if len(verses) >= 2}

    # Build CHAPTER-LEVEL root repetitions (full data, once only)
    if repeated_roots:
        chapter_root_reps = {}
        for root, verses in repeated_roots.items():
            root_entry = {
                'lemmas': sorted(list(root_to_lemmas[root])),
                'verses': sorted(list(verses)),
                'total_occurrences': len(verses)
            }

            # Add translations if lemmas_dict available
            if lemmas_dict:
                translations = []
                for buck in root_to_lemmas_buckwalter[root]:
                    trans = get_lemma_translation(buck, lemmas_dict)
                    if trans:
                        translations.append(trans)
                if translations:
                    root_entry['translations'] = translations

            chapter_root_reps[root] = root_entry

        chapter_balaghah['root_repetitions'] = chapter_root_reps

    # Distribute balaghah to each verse
    for verse_data in verses_data:
        verse_num = verse_data['verse_number']
        verse_bal = verse_data.get('balaghah', {})

        features = {}

        # Add saj if present (already in flattened format in comprehensive file)
        if verse_bal.get('saj'):
            features['saj'] = verse_bal['saj']

        # Add FULL root repetition details for roots present in this verse
        verse_root_details = {}
        for root, verses in repeated_roots.items():
            if verse_num in verses:
                # Include full details from chapter-level data
                root_entry = {
                    'lemmas': sorted(list(root_to_lemmas[root])),
                    'related_verses': sorted([v for v in verses if v != verse_num]),  # Other verses with this root
                    'total_verses': len(verses),  # Total verses containing this root
                    'appears_in_current_verse': True
                }

                # Add translations if available
                if lemmas_dict:
                    translations = []
                    for buck in root_to_lemmas_buckwalter[root]:
                        trans = get_lemma_translation(buck, lemmas_dict)
                        if trans:
                            translations.append(trans)
                    if translations:
                        root_entry['translations'] = translations

                verse_root_details[root] = root_entry

        if verse_root_details:
            features['root_repetitions'] = verse_root_details

        # Add maani if present - ENRICH with actual words
        if verse_bal.get('maani'):
            maani_data = verse_bal['maani'].copy()

            # Enrich verb_forms with actual verbs and translations
            if maani_data.get('verb_forms'):
                maani_data = enrich_verb_forms([verse_data], maani_data, lemmas_dict)

            # Enrich definiteness with actual words
            if maani_data.get('definiteness'):
                maani_data = enrich_definiteness([verse_data], maani_data)

            features['maani'] = maani_data

        # Add jinas if present
        if verse_bal.get('jinas'):
            features['jinas'] = verse_bal['jinas']

        # Add advanced balaghah features if present
        if verse_bal.get('wasl_fasl'):
            features['wasl_fasl'] = verse_bal['wasl_fasl']

        if verse_bal.get('muqabala'):
            # Enrich muqabala with translations
            muqabala_data = verse_bal['muqabala']
            if lemmas_dict:
                muqabala_data = enrich_muqabala(muqabala_data, [verse_data], lemmas_dict)
            features['muqabala'] = muqabala_data

        if verse_bal.get('istianaf'):
            features['istianaf'] = verse_bal['istianaf']

        if verse_bal.get('hadhf'):
            features['hadhf'] = verse_bal['hadhf']

        if verse_bal.get('iltifat'):
            features['iltifat'] = verse_bal['iltifat']

        # SYNTACTIC DETECTION: Detect qasam (oath) patterns
        qasam_data = detect_qasam(verse_data)
        if qasam_data:
            features['qasam'] = qasam_data

        # SYNTACTIC DETECTION: Detect muqatta'at (disconnected letters)
        muqattaat_data = detect_muqattaat(verse_data)
        if muqattaat_data:
            features['muqattaat'] = muqattaat_data

        # SYNTACTIC DETECTION: Detect particles (interrogative, restriction, emphasis)
        particles_data = detect_particles(verse_data)
        if particles_data:
            if 'interrogative' in particles_data:
                features['interrogative'] = particles_data['interrogative']
            if 'restriction' in particles_data:
                features['restriction'] = particles_data['restriction']
            if 'emphasis' in particles_data:
                features['particles_emphasis'] = particles_data['emphasis']

        # Regenerate comprehensive tafsir_context with ALL merged features
        if features:
            # Create comprehensive linguistic summary
            linguistic_summary = _summarize_balaghah_features(features)

            tafsir_context = {
                'linguistic_features_summary': linguistic_summary
            }

            # Add asbab nuzul info if available for this verse
            asbab_key = f"{chapter_num}:{verse_num}"
            occasions = asbab_nuzul_data.get(asbab_key, [])

            if len(occasions) > 0:
                tafsir_context['asbab_nuzul_info'] = {
                    'has_occasions': True,
                    'occasions_count': len(occasions)
                }

                # Add preview of occasions (first 2)
                tafsir_context['asbab_nuzul_summary'] = [
                    {
                        'verse_range': occ.get('verse_range'),
                        'occasion_preview': occ.get('occasion', '')[:200] + '...' if len(occ.get('occasion', '')) > 200 else occ.get('occasion', '')
                    }
                    for occ in occasions[:2]
                ]

            features['tafsir_context'] = tafsir_context
            verse_balaghah[verse_num] = features

    return chapter_balaghah, verse_balaghah


def format_morphology_segment(segment):
    """
    Format a single morphology segment for display

    Args:
        segment: Dictionary with keys: segment, arabic, buckwalter, pos, features

    Returns:
        Dictionary with formatted morphology information
    """
    formatted = {
        'segment': segment['segment'],
        'arabic': segment['arabic'],
        'pos': segment['pos']
    }

    # Extract key features
    features = segment.get('features', {})

    # Extract root and lemma (in Unicode Arabic)
    if 'root' in features:
        formatted['root'] = features['root']

    if 'lem' in features:
        formatted['lemma'] = features['lem']

    # Extract verb form
    if 'vf' in features:
        formatted['verb_form'] = f"VF:{features['vf']}"

    # Extract morpheme type (prefix, suffix, stem)
    if 'pref' in features:
        formatted['type'] = 'PREFIX'
    elif 'suff' in features:
        formatted['type'] = 'SUFFIX'
    else:
        formatted['type'] = 'STEM'

    # Extract grammatical features
    grammar = []

    # Gender/Number
    if 'ms' in features:
        grammar.append('Masc.Sing')
    elif 'fs' in features:
        grammar.append('Fem.Sing')
    elif 'mp' in features:
        grammar.append('Masc.Plur')
    elif 'fp' in features:
        grammar.append('Fem.Plur')
    elif 'm' in features:
        grammar.append('Masc')
    elif 'f' in features:
        grammar.append('Fem')
    elif 's' in features:
        grammar.append('Sing')
    elif 'p' in features:
        grammar.append('Plur')
    elif 'd' in features:
        grammar.append('Dual')

    # Case
    if 'nom' in features:
        grammar.append('Nominative')
    elif 'acc' in features:
        grammar.append('Accusative')
    elif 'gen' in features:
        grammar.append('Genitive')

    # Tense/Mood for verbs
    if 'perf' in features:
        grammar.append('Perfect')
    elif 'impf' in features:
        grammar.append('Imperfect')
    elif 'impv' in features:
        grammar.append('Imperative')

    if 'mood' in features:
        mood = features['mood']
        if mood == 'IND':
            grammar.append('Indicative')
        elif mood == 'JUS':
            grammar.append('Jussive')

    # Definiteness
    if 'det' in features:
        grammar.append('Definite')
    elif 'indef' in features:
        grammar.append('Indefinite')

    if grammar:
        formatted['grammar'] = ' | '.join(grammar)

    return formatted


def simplify_word_morphology(word_text, segments, root_meanings_dict):
    """
    Simplify morphology from segments to single word-level object.

    Args:
        word_text: The full Arabic word
        segments: List of morphology segments
        root_meanings_dict: Dictionary of root meanings

    Returns:
        Simplified morphology dictionary with essential fields
    """
    # Initialize simplified structure
    simplified = {
        'text': word_text
    }

    # Find the STEM segment (main word, not prefix/suffix)
    stem_segment = None
    for seg in segments:
        features = seg.get('features', {})
        # STEM is the segment without pref or suff flags
        if not features.get('pref') and not features.get('suff'):
            stem_segment = seg
            break

    if not stem_segment:
        # Fallback: use first segment if no clear stem
        stem_segment = segments[0] if segments else {}

    features = stem_segment.get('features', {})
    pos = stem_segment.get('pos', '')

    # Extract root and lemma
    root = features.get('root')
    lemma = features.get('lem')

    if root:
        simplified['root'] = root
        # Add root meaning if available
        if root in root_meanings_dict:
            root_data = root_meanings_dict[root]
            simplified['root_meaning'] = root_data.get('meaning', '')

    if lemma:
        simplified['lemma'] = lemma

    # Part of speech (make it readable)
    pos_map = {
        'N': 'noun',
        'V': 'verb',
        'P': 'particle',
        'PRON': 'pronoun',
        'ADJ': 'adjective',
        'ADV': 'adverb'
    }
    simplified['pos'] = pos_map.get(pos, pos.lower() if pos else None)

    # Definiteness (check for determiner prefix)
    definite = False
    for seg in segments:
        seg_features = seg.get('features', {})
        if seg_features.get('det'):  # Determiner prefix (ال)
            definite = True
            break

    if definite:
        simplified['definite'] = True
    elif features.get('indef'):
        simplified['definite'] = False

    # Case
    if features.get('nom'):
        simplified['case'] = 'nominative'
    elif features.get('acc'):
        simplified['case'] = 'accusative'
    elif features.get('gen'):
        simplified['case'] = 'genitive'

    # Gender
    if features.get('m') or features.get('ms') or features.get('mp'):
        simplified['gender'] = 'masculine'
    elif features.get('f') or features.get('fs') or features.get('fp'):
        simplified['gender'] = 'feminine'

    # Number
    if features.get('s') or features.get('ms') or features.get('fs'):
        simplified['number'] = 'singular'
    elif features.get('d'):
        simplified['number'] = 'dual'
    elif features.get('p') or features.get('mp') or features.get('fp'):
        simplified['number'] = 'plural'

    # Person (for pronouns/verbs)
    if features.get('1p') or features.get('1s'):
        simplified['person'] = '1st'
    elif features.get('2p') or features.get('2s') or features.get('2ms') or features.get('2fs'):
        simplified['person'] = '2nd'
    elif features.get('3p') or features.get('3s') or features.get('3ms') or features.get('3fs'):
        simplified['person'] = '3rd'

    # Verb-specific features
    if pos == 'V':
        # Verb form
        vf = features.get('vf')
        if vf:
            simplified['form'] = int(vf)

        # Tense
        if features.get('perf'):
            simplified['tense'] = 'perfect'
        elif features.get('impf'):
            simplified['tense'] = 'imperfect'
        elif features.get('impv'):
            simplified['tense'] = 'imperative'

        # Mood (for imperfect)
        mood = features.get('mood')
        if mood == 'IND':
            simplified['mood'] = 'indicative'
        elif mood == 'JUS':
            simplified['mood'] = 'jussive'
        elif mood == 'SUBJ':
            simplified['mood'] = 'subjunctive'

    return simplified


def extract_verse_info_compact(chapter_num, verse_start, verse_end, comprehensive_data):
    """
    Extract verse information from comprehensive data with verse-centric balaghah.

    NEW STRUCTURE:
    - Each verse contains its own balaghah features
    - Repetitions show "related_verses" instead of aggregating at top
    - No word locations (data alignment issue)
    - Includes detailed segment-level morphology from morphology_segments.json
    """

    # Load lemmas dictionary for vocabulary translations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lemmas_dict_path = os.path.join(script_dir, '..', '..', 'data', 'linguistic', 'lemmas_dictionary.json')
    lemmas_dict = load_lemmas_dictionary(lemmas_dict_path)

    # Load linguistic data files
    dependencies_path = os.path.join(script_dir, '..', '..', 'data', 'linguistic', 'dependencies_full.json')
    named_entities_path = os.path.join(script_dir, '..', '..', 'data', 'linguistic', 'named_entities_full.json')
    pause_marks_path = os.path.join(script_dir, '..', '..', 'data', 'linguistic', 'pause_marks.json')
    root_meanings_path = os.path.join(script_dir, '..', '..', 'data', 'linguistic', 'root_meanings.json')

    dependencies = load_dependencies(dependencies_path)
    named_entities = load_named_entities(named_entities_path)
    pause_marks = load_pause_marks(pause_marks_path)
    root_meanings = load_root_meanings(root_meanings_path)

    # Load metadata (includes morphology segments)
    try:
        from metadata_loader import MetadataLoader
        metadata_loader = MetadataLoader()
        has_morphology = metadata_loader.morphology_segments is not None
    except Exception as e:
        print(f"Warning: Could not load morphology segments: {e}")
        has_morphology = False
        metadata_loader = None

    # Find the chapter
    chapter_data = None
    for ch in comprehensive_data['chapters']:
        if ch['chapter_number'] == chapter_num:
            chapter_data = ch
            break

    if not chapter_data:
        raise ValueError(f"Chapter {chapter_num} not found")

    # Build result structure
    result = {
        'chapter': chapter_num,
        'verse_start': verse_start,
        'verse_end': verse_end,
        'metadata': {
            'chapter_number': chapter_data['chapter_number'],
            'name_arabic': chapter_data['name_arabic'],
            'revelation_place': chapter_data['revelation_place'],
            'revelation_order': chapter_data['revelation_order'],
            'verses_count': chapter_data['verses_count']
        },
        'verses': []
    }

    # Collect verses for analysis
    verses_data = []
    for verse_data in chapter_data['verses']:
        verse_num = verse_data['verse_number']
        if verse_start <= verse_num <= verse_end:
            verses_data.append(verse_data)

    # Distribute balaghah: chapter-level aggregates + verse-level features
    chapter_balaghah, verse_balaghah_map = distribute_balaghah_to_verses(verses_data, lemmas_dict, chapter_num, comprehensive_data)

    # Build output verses with balaghah
    for verse_data in verses_data:
        verse_num = verse_data['verse_number']

        # Context-first: verse with translation
        verse_output = {
            'verse_number': verse_num,
            'text': verse_data['text'],
            'translation_en': verse_data.get('translation_en')
        }

        # Add tafsir if available
        if verse_data.get('tafsir'):
            verse_output['tafsir'] = verse_data['tafsir']

        # Add asbab nuzul if at start of range
        asbab = verse_data.get('asbab_nuzul', [])
        if asbab:
            filtered_asbab = []
            for entry in asbab:
                verse_range = entry.get('verse_range', str(verse_num))
                if '-' in verse_range:
                    range_start = int(verse_range.split('-')[0])
                else:
                    range_start = int(verse_range)

                if verse_num == range_start:
                    filtered_asbab.append(entry)

            if filtered_asbab:
                verse_output['asbab_nuzul'] = filtered_asbab

        # Add balaghah features for this verse
        if verse_num in verse_balaghah_map:
            verse_output['balaghah'] = verse_balaghah_map[verse_num]

        # Add detailed morphology segments if available
        if has_morphology and metadata_loader:
            verse_morphology = metadata_loader.get_verse_morphology(chapter_num, verse_num)
            if verse_morphology:
                # Format morphology by word
                morphology_by_word = []
                for word_num_str in sorted(verse_morphology.keys(), key=lambda x: int(x)):
                    word_num = int(word_num_str)
                    segments = verse_morphology[word_num_str]

                    # Get word text from verse_data if available
                    word_text = None
                    for word in verse_data.get('words', []):
                        if word.get('word_number') == word_num:
                            word_text = word.get('text', '')
                            break

                    # Use simplified morphology with root meanings
                    word_morphology = simplify_word_morphology(word_text, segments, root_meanings)

                    morphology_by_word.append(word_morphology)

                if morphology_by_word:
                    verse_output['words'] = morphology_by_word

        # Add syntactic dependencies if available
        verse_deps = filter_dependencies_by_verse(dependencies, chapter_num, verse_num)
        if verse_deps:
            verse_output['dependencies'] = verse_deps

        # Add named entities if available
        verse_entities = filter_named_entities_by_verse(named_entities, chapter_num, verse_num)
        if verse_entities:
            verse_output['named_entities'] = verse_entities

        # Add pause marks if available
        # Note: pause marks use absolute verse numbering (1-6236)
        absolute_verse_num = chapter_verse_to_absolute(chapter_num, verse_num, comprehensive_data)
        verse_marks = filter_pause_marks_by_verse(pause_marks, absolute_verse_num)
        if verse_marks:
            verse_output['pause_marks'] = verse_marks

        result['verses'].append(verse_output)

    # Add chapter-level balaghah (aggregated patterns)
    if chapter_balaghah:
        result['chapter_balaghah'] = chapter_balaghah

    # Apply final filtering and return
    result = filter_empty_values(result)
    return result

    """Extract the Arabic text of a word from comprehensive format"""
    # After updating comprehensive generator, word text is stored directly at word level
    return word_data.get('text', '')


def main():
    """Main interactive loop"""
    print("=" * 60)
    print("Quranic Verse Information Retrieval")
    print("Complete Linguistic & Rhetorical Analysis")
    print("=" * 60)
    print()
    print("Enter verse reference in format:")
    print("  - Single verse: chapter:verse (e.g., 1:1)")
    print("  - Verse range: chapter:verse1-verse2 (e.g., 1:1-7)")
    print("  - Full chapter: chapter or chapter:all (e.g., 108 or 1:all)")
    print("  - Type 'quit' to exit")
    print()
    print("Includes: Morphology, Dependencies, Entities, Pause Marks,")
    print("          Tafsir, Asbab Nuzul, Balaghah (Saj', Takrar, Jinas)")
    print()

    # Path to comprehensive data file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    comprehensive_path = os.path.join(project_root, 'data', 'quran_comprehensive.json')

    # Load comprehensive data once
    try:
        comprehensive_data = load_comprehensive_quran(comprehensive_path)
        print()
    except FileNotFoundError:
        print(f"ERROR: Comprehensive data file not found at {comprehensive_path}")
        print("Please run generate_comprehensive_quran.py first")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading comprehensive data: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("Enter verse reference: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            # Parse input
            if not user_input:
                continue

            # Check for full chapter query
            if ':all' in user_input or user_input.isdigit():
                # Full chapter format: chapter or chapter:all
                chapter_match = re.match(r'(\d+)(:all)?', user_input)
                if not chapter_match:
                    print("Invalid format")
                    continue

                chapter = int(chapter_match.group(1))

                # Get verse count from comprehensive data
                chapter_data = None
                for ch in comprehensive_data['chapters']:
                    if ch['chapter_number'] == chapter:
                        chapter_data = ch
                        break

                if not chapter_data:
                    print(f"Chapter {chapter} not found")
                    continue

                verse_start = 1
                verse_end = chapter_data['verses_count']

            # Check if range or single verse
            elif '-' in user_input:
                # Range format: chapter:verse1-verse2
                match = re.match(r'(\d+):(\d+)-(\d+)', user_input)
                if not match:
                    print("Invalid format. Use: chapter:verse1-verse2 (e.g., 1:1-7)")
                    continue

                chapter = int(match.group(1))
                verse_start = int(match.group(2))
                verse_end = int(match.group(3))
            else:
                # Single verse format: chapter:verse
                match = re.match(r'(\d+):(\d+)', user_input)
                if not match:
                    print("Invalid format. Use: chapter:verse (e.g., 1:1)")
                    continue

                chapter = int(match.group(1))
                verse_start = int(match.group(2))
                verse_end = verse_start

            # Validate chapter and verse numbers
            if chapter < 1 or chapter > 114:
                print("Chapter must be between 1 and 114")
                continue

            if verse_start < 1 or verse_end < verse_start:
                print("Invalid verse numbers")
                continue

            print()
            print(f"Retrieving information for Chapter {chapter}, Verse(s) {verse_start}" +
                  (f"-{verse_end}" if verse_end > verse_start else "") + "...")
            print()

            # Extract and format data
            result = extract_verse_info_compact(chapter, verse_start, verse_end, comprehensive_data)

            # Always save to file to avoid truncation
            output_filename = f"verse_{chapter}_{verse_start}"
            if verse_end > verse_start:
                output_filename += f"-{verse_end}"
            output_filename += ".json"

            json_output = json.dumps(result, ensure_ascii=False, indent=2)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(json_output)

            # Print summary to console
            print("-" * 60)
            print(f"[OK] Retrieved Chapter {chapter}, Verse(s) {verse_start}" +
                  (f"-{verse_end}" if verse_end > verse_start else ""))
            print(f"[OK] Output saved to: {output_filename}\"")
            print()

            # Display summary statistics
            verse_count = len(result['verses'])
            print(f"Summary:")
            print(f"  - Total verses: {verse_count}")

            # Try to print chapter name, fallback if console doesn't support Arabic
            try:
                print(f"  - Chapter: {result['metadata']['name_arabic']} ({result['metadata']['revelation_place'].title()})")
            except UnicodeEncodeError:
                print(f"  - Chapter: {chapter} ({result['metadata']['revelation_place'].title()})")

            # Show which verses have balaghah features
            saj_data = result.get('balaghah', {}).get('saj')
            verses_with_saj = 0
            if saj_data:
                if isinstance(saj_data, dict) and 'verses' in saj_data:
                    # Single sequence
                    verses_with_saj = len(saj_data['verses'])
                elif isinstance(saj_data, list):
                    # Multiple sequences
                    verses_with_saj = sum(len(seq.get('verses', [])) for seq in saj_data)

            jinas_data = result.get('balaghah', {}).get('jinas', [])
            verses_with_jinas = len(jinas_data) if jinas_data else 0

            if verses_with_saj > 0:
                print(f"  - Verses with Saj': {verses_with_saj}/{verse_count}")
            if verses_with_jinas > 0:
                print(f"  - Verses with Jinas: {verses_with_jinas}/{verse_count}")

            print()
            print(f"Full details available in: {output_filename}")
            print("-" * 60)
            print()

        except EOFError:
            # End of input from pipe/redirect
            print("\nEnd of input reached. Goodbye!")
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            continue


if __name__ == '__main__':
    main()
