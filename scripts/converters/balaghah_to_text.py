#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert structured balaghah JSON features to natural language text.
Creates LLM-friendly readable descriptions of rhetorical devices.

Usage:
    from balaghah_to_text import convert_verse_to_text
    text_analysis = convert_verse_to_text(verse_data, root_meanings_dict)
"""

import json
import os
from pathlib import Path


def load_root_meanings():
    """Load root meanings dictionary from file."""
    try:
        script_dir = Path(__file__).parent
        root_meanings_path = script_dir.parent.parent / 'data' / 'linguistic' / 'root_meanings.json'

        with open(root_meanings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('roots', {})
    except:
        return {}


def get_root_meaning(root, root_meanings_dict):
    """Get English meaning for an Arabic root."""
    if root and root in root_meanings_dict:
        return root_meanings_dict[root].get('meaning', '')
    return None


def convert_saj(saj_data, verse_num):
    """Convert saj' (rhyme) data to text."""
    if not saj_data:
        return None

    pattern = saj_data.get('pattern', '')
    seq_length = saj_data.get('sequence_length', '')
    position = saj_data.get('position_in_sequence', '')

    if pattern and seq_length:
        return f"The verse exhibits saj' (rhymed prose) with the pattern '{pattern}', continuing for {seq_length} verses (position {position} in sequence)."

    return None


def convert_jinas(jinas_data, root_meanings_dict):
    """Convert jinas (wordplay) data to text."""
    if not jinas_data:
        return None

    # Handle both list and dict formats
    patterns = []
    if isinstance(jinas_data, list):
        # If it's already a list of patterns
        patterns = jinas_data
    elif isinstance(jinas_data, dict):
        # If it's a dict with 'jinas_patterns' key
        patterns = jinas_data.get('jinas_patterns', [])

    if not patterns:
        return None

    descriptions = []
    for pattern in patterns:
        # Skip if pattern is not a dict
        if not isinstance(pattern, dict):
            continue

        # Handle different jinas data structures
        # Structure 1: word1/word2 are direct strings
        if isinstance(pattern.get('word1'), str):
            word1 = pattern.get('word1', '')
            word2 = pattern.get('word2', '')
            # Roots might be in 'roots' array or individual fields
            roots = pattern.get('roots', [])
            if len(roots) >= 2:
                root1, root2 = roots[0], roots[1]
            else:
                root1 = pattern.get('root1', '')
                root2 = pattern.get('root2', '')
        # Structure 2: word1/word2 are nested dicts with 'arabic' and 'root'
        else:
            word1 = pattern.get('word1', {}).get('arabic', '')
            word2 = pattern.get('word2', {}).get('arabic', '')
            root1 = pattern.get('word1', {}).get('root', '')
            root2 = pattern.get('word2', {}).get('root', '')

        jinas_type = pattern.get('type', 'wordplay').replace('jinas_', '').replace('_', ' ')

        if word1 and word2:
            desc = f"The verse contains jinas ({jinas_type}) between '{word1}' and '{word2}'"

            if root1 and root2:
                if root1 == root2:
                    meaning = get_root_meaning(root1, root_meanings_dict)
                    meaning_text = f" (both from root {root1}" + (f" meaning '{meaning}'" if meaning else "") + ")"
                    desc += meaning_text
                else:
                    desc += f" (from roots {root1} and {root2})"

            descriptions.append(desc + ".")

    return ' '.join(descriptions) if descriptions else None


def convert_takrar(takrar_data, root_meanings_dict):
    """Convert takrar (repetition) data to text."""
    if not takrar_data or not takrar_data.get('root_repetitions'):
        return None

    descriptions = []
    for rep in takrar_data['root_repetitions']:
        root = rep.get('root', '')
        count = rep.get('count', 0)
        verses = rep.get('verses', [])
        lemmas = rep.get('lemmas', [])

        if root and count > 1:
            meaning = get_root_meaning(root, root_meanings_dict)
            meaning_text = f" (meaning '{meaning}')" if meaning else ""

            verse_list = ', '.join(str(v) for v in verses)
            lemma_list = ', '.join(set(lemmas[:5]))  # Limit to 5 unique lemmas

            desc = f"Root {root}{meaning_text} repeats {count} times in verses {verse_list}"
            if lemma_list:
                desc += f" with forms {lemma_list}"

            descriptions.append(desc + ".")

    return ' '.join(descriptions) if descriptions else None


def convert_iltifat(iltifat_data):
    """Convert iltifat (grammatical shift) data to text."""
    if not iltifat_data:
        return None

    descriptions = []
    for shift in iltifat_data:
        shift_type = shift.get('type', '')
        pattern = shift.get('detected_pattern', {})

        from_val = pattern.get('from_' + shift_type.replace('_shift', ''), '')
        to_val = pattern.get('to_' + shift_type.replace('_shift', ''), '')
        from_verse = pattern.get('from_verse', '')
        to_verse = pattern.get('to_verse', '')

        evidence = shift.get('detected_pattern', {}).get('evidence', {})
        from_word = evidence.get('from', {}).get('text', '')
        to_word = evidence.get('to', {}).get('text', '')

        if from_val and to_val:
            shift_name = shift_type.replace('_', ' ')
            desc = f"There is iltifat ({shift_name}) from {from_val}"

            if from_word:
                desc += f" ('{from_word}')"

            desc += f" to {to_val}"

            if to_word:
                desc += f" ('{to_word}')"

            if from_verse and to_verse:
                desc += f" between verses {from_verse} and {to_verse}"

            descriptions.append(desc + ".")

    return ' '.join(descriptions) if descriptions else None


def convert_hadhf(hadhf_data, root_meanings_dict):
    """Convert hadhf (ellipsis) data to text."""
    if not hadhf_data or not hadhf_data.get('hadhf_patterns'):
        return None

    descriptions = []
    for pattern in hadhf_data['hadhf_patterns']:
        ellipsis_type = pattern.get('type', 'ellipsis')
        verb_text = pattern.get('verb_text', '')
        verb_root = pattern.get('verb_root', '')

        desc = f"The verse exhibits hadhf ({ellipsis_type.replace('_', ' ')})"

        if verb_text:
            desc += f" in the verb '{verb_text}'"

        if verb_root:
            meaning = get_root_meaning(verb_root, root_meanings_dict)
            desc += f" from root {verb_root}"
            if meaning:
                desc += f" (meaning '{meaning}')"

        descriptions.append(desc + ", where the omitted element is understood from context.")

    return ' '.join(descriptions) if descriptions else None


def convert_qasam(qasam_data, root_meanings_dict):
    """Convert qasam (oath) data to text."""
    if not qasam_data or not qasam_data.get('has_qasam'):
        return None

    elements = qasam_data.get('elements', [])
    if not elements:
        return None

    descriptions = []
    for elem in elements:
        particle = elem.get('particle', '')
        word_text = elem.get('word_text', '')
        lemma = elem.get('lemma', '')
        root = elem.get('root', '')

        desc = f"The verse contains qasam (oath) using the particle '{particle}' before '{word_text}'"

        if lemma:
            desc += f" ({lemma})"

        if root:
            meaning = get_root_meaning(root, root_meanings_dict)
            desc += f", from root {root}"
            if meaning:
                desc += f" meaning '{meaning}'"

        descriptions.append(desc + ".")

    return ' '.join(descriptions) if descriptions else None


def convert_muqattaat(muqattaat_data):
    """Convert muqatta'at (disconnected letters) data to text."""
    if not muqattaat_data or not muqattaat_data.get('has_muqattaat'):
        return None

    letters = muqattaat_data.get('letters', '')
    note = muqattaat_data.get('note', '')

    if letters:
        desc = f"The verse begins with muqatta'at (disconnected letters) '{letters}'"
        if note:
            desc += f" - {note}"
        return desc + "."

    return None


def convert_interrogative(interrogative_data):
    """Convert interrogative particles to text."""
    if not interrogative_data or not interrogative_data.get('has_interrogative'):
        return None

    particles = interrogative_data.get('particles', [])
    if not particles:
        return None

    particle_texts = []
    for p in particles:
        particle = p.get('particle', '')
        word_text = p.get('word_text', '')

        if particle:
            text = f"'{particle}'"
            if word_text:
                text += f" (in '{word_text}')"
            particle_texts.append(text)

    if particle_texts:
        return f"The verse uses interrogative particle(s) {', '.join(particle_texts)}, creating a rhetorical question."

    return None


def convert_restriction(restriction_data):
    """Convert restriction (hasr) particles to text."""
    if not restriction_data or not restriction_data.get('has_restriction'):
        return None

    patterns = restriction_data.get('patterns', [])
    if not patterns:
        return None

    desc_list = []
    for pattern in patterns:
        pattern_type = pattern.get('type', '')
        word_text = pattern.get('word_text', '')

        if pattern_type == 'innama':
            desc = f"The verse uses restriction pattern 'إنما' (innama)"
        elif pattern_type == 'ma_illa':
            desc = f"The verse uses restriction pattern 'ما...إلا' (nothing except)"
        else:
            desc = f"The verse uses restriction pattern"

        if word_text:
            desc += f" in '{word_text}'"

        desc_list.append(desc + ", emphasizing exclusivity.")

    return ' '.join(desc_list) if desc_list else None


def convert_emphasis(emphasis_data):
    """Convert emphasis particles to text."""
    if not emphasis_data or not emphasis_data.get('has_emphasis'):
        return None

    particles = emphasis_data.get('particles', [])
    if not particles:
        return None

    particle_texts = []
    for p in particles:
        particle = p.get('particle', '')
        word_text = p.get('word_text', '')

        if particle:
            text = f"'{particle}'"
            if word_text:
                text += f" (in '{word_text}')"
            particle_texts.append(text)

    if particle_texts:
        return f"The verse employs emphasis particle(s) {', '.join(particle_texts)} for assertive emphasis."

    return None


def convert_muqabala(muqabala_data):
    """Convert muqabala (parallelism) to text."""
    if not muqabala_data or not muqabala_data.get('muqabala_patterns'):
        return None

    descriptions = []
    for pattern in muqabala_data['muqabala_patterns']:
        parallelism_type = pattern.get('parallelism_type', 'parallelism')
        structure1 = pattern.get('structure1', {})
        structure2 = pattern.get('structure2', {})

        # Extract words from structures
        words1 = []
        words2 = []

        for key in sorted(structure1.keys()):
            if isinstance(structure1[key], dict):
                arabic = structure1[key].get('arabic', '')
                if arabic:
                    words1.append(arabic)

        for key in sorted(structure2.keys()):
            if isinstance(structure2[key], dict):
                arabic = structure2[key].get('arabic', '')
                if arabic:
                    words2.append(arabic)

        if words1 or words2:
            str1 = ' '.join(words1) if words1 else '...'
            str2 = ' '.join(words2) if words2 else '...'

            desc = f"The verse exhibits muqabala ({parallelism_type}) between structures '{str1}' and '{str2}'"
            descriptions.append(desc + ".")

    return ' '.join(descriptions) if descriptions else None


def convert_maani(maani_data):
    """Convert ma'ani (meanings/semantics) features to text."""
    if not maani_data:
        return None

    descriptions = []

    # Sentence type
    sentence_type = maani_data.get('sentence_type', {})
    if sentence_type:
        sent_type = sentence_type.get('type', '')
        subtype = sentence_type.get('subtype', '')
        desc_text = sentence_type.get('description', '')

        if sent_type:
            desc = f"The verse is {sent_type}"
            if subtype:
                desc += f" ({subtype})"
            if desc_text:
                desc += f": {desc_text}"
            descriptions.append(desc + ".")

    # Definiteness
    definiteness = maani_data.get('definiteness', {})
    if definiteness:
        definite = definiteness.get('definite', {})
        indefinite = definiteness.get('indefinite', {})

        if definite and definite.get('count', 0) > 0:
            lemmas = definite.get('lemmas', [])[:3]  # First 3
            if lemmas:
                lemma_str = ', '.join(lemmas)
                descriptions.append(f"Definite nouns include {lemma_str}.")

        if indefinite and indefinite.get('count', 0) > 0:
            count = indefinite.get('count', 0)
            lemmas = indefinite.get('lemmas', [])[:3]  # First 3
            if lemmas:
                lemma_str = ', '.join(lemmas)
                descriptions.append(f"Contains {count} indefinite noun(s): {lemma_str}, indicating general or non-specific entities.")
            else:
                descriptions.append(f"Contains {count} indefinite noun(s), indicating general or non-specific entities.")

    return ' '.join(descriptions) if descriptions else None


def extract_key_words(words_data, root_meanings_dict):
    """Extract key words with root meanings."""
    if not words_data:
        return None

    key_words = []
    seen_roots = set()

    for word in words_data:
        root = word.get('root')
        lemma = word.get('lemma')
        root_meaning = word.get('root_meaning')

        # Only include words with roots, meanings, and avoid duplicates
        if root and root_meaning and root not in seen_roots:
            seen_roots.add(root)

            # Build key word entry with full meaning (no truncation)
            entry = root
            if lemma:
                entry += f" ({lemma} - {root_meaning})"
            else:
                # No lemma, just root and meaning
                entry += f" - {root_meaning}"

            key_words.append(entry)

    if key_words:
        return "Key words: " + ', '.join(key_words[:5]) + "."  # Limit to 5

    return None


def convert_taqdim_takhir(taqdim_data):
    """Convert taqdim wa ta'khir (word order) data to text."""
    if not taqdim_data or not isinstance(taqdim_data, dict):
        return None

    patterns = taqdim_data.get('taqdim_takhir_patterns', [])
    if not patterns:
        return None

    descriptions = []
    for pattern in patterns:
        element = pattern.get('element_advanced', 'element')
        word_text = pattern.get('word_text', '')
        expected_pos = pattern.get('expected_position', '')
        actual_pos = pattern.get('actual_position', '')
        sent_type = pattern.get('sentence_type', '')

        # Skip patterns with empty word_text (embedded pronouns, etc.)
        if not word_text:
            continue

        # Describe sentence type
        sent_desc = "verbal sentence" if sent_type == "VS" else "nominal sentence"

        desc = f"Word order variation detected: '{word_text}' ({element}) is advanced from position {expected_pos} to position {actual_pos} in this {sent_desc}."

        # Add rhetorical candidates
        candidates = pattern.get('rhetorical_candidates', [])
        if candidates:
            desc += f" Possible rhetorical purposes: {', '.join(candidates)}."

        descriptions.append(desc)

    if descriptions:
        return " ".join(descriptions)

    return None


def convert_tibaq(tibaq_data):
    """Convert tibaq (antithesis) data to text."""
    if not tibaq_data or not isinstance(tibaq_data, dict):
        return None

    patterns = tibaq_data.get('tibaq_patterns', [])
    if not patterns:
        return None

    descriptions = []
    for pattern in patterns:
        tib_type = pattern.get('type', 'tibaq')
        word1_data = pattern.get('word1', {})
        word2_data = pattern.get('word2', {})
        opposition_type = pattern.get('opposition_type', 'semantic')

        word1_text = word1_data.get('text', '')
        word1_root = word1_data.get('root', '')
        word2_text = word2_data.get('text', '')
        word2_root = word2_data.get('root', '')

        meaning1 = pattern.get('meaning1', '')
        meaning2 = pattern.get('meaning2', '')

        # Describe type
        if tib_type == 'tibaq_al_ijab':
            type_desc = "positive antithesis (ṭibāq al-ījāb)"
        elif tib_type == 'tibaq_al_salb':
            type_desc = "negative antithesis (ṭibāq al-salb)"
        else:
            type_desc = "antithesis (ṭibāq)"

        desc = f"The verse contains {type_desc} between '{word1_text}' ({word1_root}: {meaning1}) and '{word2_text}' ({word2_root}: {meaning2}), creating {opposition_type} opposition."

        descriptions.append(desc)

    if descriptions:
        return " ".join(descriptions)

    return None


def convert_tashbih(tashbih_data):
    """Convert tashbih (simile/comparison) candidate data to text."""
    if not tashbih_data or not isinstance(tashbih_data, dict):
        return None

    candidates = tashbih_data.get('tashbih_candidates', [])
    if not candidates:
        return None

    descriptions = []
    for candidate in candidates:
        particle = candidate.get('particle', '')
        particle_type = candidate.get('particle_type', '')
        word_text = candidate.get('word_text', '')

        # Get context
        context_before = candidate.get('context_before', [])
        context_after = candidate.get('context_after', [])

        desc = f"Comparison particle detected: '{word_text}' ({particle_type})."

        # Add tenor candidates (before particle)
        if context_before:
            tenor_words = [w.get('text', '') for w in context_before if w.get('text')]
            if tenor_words:
                desc += f" Tenor (what's being compared) likely includes: {', '.join(tenor_words[-2:])}."  # Last 2 words

        # Add vehicle candidates (after particle)
        if context_after:
            vehicle_words = [w.get('text', '') for w in context_after if w.get('text')]
            if vehicle_words:
                desc += f" Vehicle (compared to) likely includes: {', '.join(vehicle_words[:2])}."  # First 2 words

        desc += " This suggests tashbīh (explicit comparison/simile) - analyze to identify the complete four elements: tenor, vehicle, ground, and particle."

        descriptions.append(desc)

    if descriptions:
        return " ".join(descriptions)

    return None


def convert_root_repetitions(root_reps, root_meanings_dict):
    """
    Convert root repetitions data to natural language text.

    Args:
        root_reps: Dictionary of {root: repetition_data}
        root_meanings_dict: Dictionary of root meanings

    Returns:
        String describing root repetitions with verse contexts
    """
    if not root_reps:
        return None

    descriptions = []

    for root, rep_data in root_reps.items():
        # Skip subsequent occurrences (already mentioned)
        if not rep_data.get('first_occurrence_in_extraction', False):
            continue

        lemmas = rep_data.get('lemmas', [])
        translations = rep_data.get('translations', [])
        other_verses = rep_data.get('other_verses', [])
        total = rep_data.get('total_occurrences_in_chapter', 0)

        if not other_verses:
            continue

        # Build root description with meaning
        root_desc = f"The root {root}"
        if lemmas:
            lemma_list = ', '.join(lemmas[:3])  # Limit to 3
            root_desc += f" ({lemma_list})"
        if translations:
            trans_list = translations[0][:100]  # First translation, max 100 chars
            root_desc += f" which has the root meaning '{trans_list}'"

        # Build verse references with context
        verse_refs = []
        for v_ctx in other_verses:
            verse_num = v_ctx.get('verse', '')
            text = v_ctx.get('text', '')
            translation = v_ctx.get('translation', '')
            section = v_ctx.get('section_heading', '')

            # Create reference with full verse text
            ref = f"verse {verse_num}"
            if section:
                ref += f" ('{section}')"
            if translation:
                # Add full translation
                ref += f": \"{translation}\""

            verse_refs.append(ref)

        # Combine into description
        if verse_refs:
            verse_list = "; ".join(verse_refs)
            desc = f"{root_desc} here is also repeated in {verse_list}."
            descriptions.append(desc)

    return ' '.join(descriptions) if descriptions else None


def convert_verse_to_text(verse_data, root_meanings_dict=None, section_heading=None, root_repetitions=None):
    """
    Convert a verse's structured data to natural language text.

    Args:
        verse_data: Dictionary containing verse information with balaghah features
        root_meanings_dict: Optional dictionary of root meanings
        section_heading: Optional section heading data (heading, position info)
        root_repetitions: Optional root repetition data with verse contexts

    Returns:
        Dictionary with 'analysis' and 'key_words' fields
    """
    if root_meanings_dict is None:
        root_meanings_dict = load_root_meanings()

    verse_num = verse_data.get('verse_number', '')
    balaghah = verse_data.get('balaghah', {})
    words = verse_data.get('words', [])

    # Collect all feature descriptions
    descriptions = []

    # Add section heading context first
    if section_heading:
        heading = section_heading.get('heading', '')
        position = section_heading.get('position', '')
        if heading and position:
            descriptions.append(f"This verse is discussing '{heading}' that is positioned {position}.")

    # Convert each balaghah feature
    if balaghah:
        # Saj'
        saj_text = convert_saj(balaghah.get('saj'), verse_num)
        if saj_text:
            descriptions.append(saj_text)

        # Jinas
        jinas_text = convert_jinas(balaghah.get('jinas'), root_meanings_dict)
        if jinas_text:
            descriptions.append(jinas_text)

        # Takrar
        takrar_text = convert_takrar(balaghah.get('takrar'), root_meanings_dict)
        if takrar_text:
            descriptions.append(takrar_text)

        # Iltifat
        iltifat_text = convert_iltifat(balaghah.get('iltifat'))
        if iltifat_text:
            descriptions.append(iltifat_text)

        # Hadhf
        hadhf_text = convert_hadhf(balaghah.get('hadhf'), root_meanings_dict)
        if hadhf_text:
            descriptions.append(hadhf_text)

        # Qasam
        qasam_text = convert_qasam(balaghah.get('qasam'), root_meanings_dict)
        if qasam_text:
            descriptions.append(qasam_text)

        # Muqatta'at
        muqattaat_text = convert_muqattaat(balaghah.get('muqattaat'))
        if muqattaat_text:
            descriptions.append(muqattaat_text)

        # Interrogative
        interrogative_text = convert_interrogative(balaghah.get('interrogative'))
        if interrogative_text:
            descriptions.append(interrogative_text)

        # Restriction
        restriction_text = convert_restriction(balaghah.get('restriction'))
        if restriction_text:
            descriptions.append(restriction_text)

        # Emphasis
        emphasis_text = convert_emphasis(balaghah.get('particles_emphasis'))
        if emphasis_text:
            descriptions.append(emphasis_text)

        # Muqabala
        muqabala_text = convert_muqabala(balaghah.get('muqabala'))
        if muqabala_text:
            descriptions.append(muqabala_text)

        # Ma'ani
        maani_text = convert_maani(balaghah.get('maani'))
        if maani_text:
            descriptions.append(maani_text)

        # Taqdim wa Ta'khir (Word Order)
        taqdim_text = convert_taqdim_takhir(balaghah.get('taqdim_takhir'))
        if taqdim_text:
            descriptions.append(taqdim_text)

        # Tibaq (Antithesis)
        tibaq_text = convert_tibaq(balaghah.get('tibaq'))
        if tibaq_text:
            descriptions.append(tibaq_text)

        # Tashbih (Simile/Comparison)
        tashbih_text = convert_tashbih(balaghah.get('tashbih'))
        if tashbih_text:
            descriptions.append(tashbih_text)

    # Add root repetitions with verse context
    if root_repetitions:
        root_reps_text = convert_root_repetitions(root_repetitions, root_meanings_dict)
        if root_reps_text:
            descriptions.append(root_reps_text)

    # Extract key words
    key_words_text = extract_key_words(words, root_meanings_dict)

    # Combine all descriptions
    analysis_text = ' '.join(descriptions) if descriptions else None

    result = {}
    if analysis_text:
        result['analysis'] = analysis_text
    if key_words_text:
        result['key_words'] = key_words_text

    return result if result else {'analysis': 'No significant balaghah features detected in this verse.'}


def main():
    """Test the converter with sample data."""
    # Example usage
    print("Balaghah to Text Converter")
    print("=" * 60)
    print("This module converts structured balaghah JSON to natural language.")
    print("Import and use convert_verse_to_text(verse_data) in your scripts.")


if __name__ == '__main__':
    main()
