"""
Tibaq (Antithesis) Detector

Detects tibaq - the use of antonyms (opposites) in the same verse or passage.

Two types:
1. Tibaq al-ijab (positive): Direct opposites (day/night, light/darkness)
2. Tibaq al-salb (negative): Word + its negation (know/not know)
"""

import json
import os


def load_antonym_dict():
    """
    Load the antonym dictionary from JSON file.

    Returns:
        Dict mapping roots to their antonyms
    """
    # Get the path to the antonym dictionary
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    antonym_file = os.path.join(project_root, 'data', 'linguistic', 'root_antonyms.json')

    try:
        with open(antonym_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('antonym_pairs', [])
    except FileNotFoundError:
        print(f"Warning: Antonym dictionary not found at {antonym_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing antonym dictionary: {e}")
        return []


def detect_tibaq(verse_words, antonym_pairs=None):
    """
    Detect tibaq - use of antonyms in same verse/passage.

    Args:
        verse_words: List of word dicts with 'root', 'lemma', 'text', 'word_number'
        antonym_pairs: Optional list of antonym pairs (loads from file if not provided)

    Returns:
        Dict with tibaq_patterns or None if no patterns found
    """

    if not verse_words:
        return None

    # Load antonym dictionary if not provided
    if antonym_pairs is None:
        antonym_pairs = load_antonym_dict()

    if not antonym_pairs:
        return None

    # Create a lookup dict for faster antonym checking
    antonym_lookup = build_antonym_lookup(antonym_pairs)

    tibaq_instances = []

    # Extract all roots from verse
    roots_in_verse = []
    for word in verse_words:
        root = word.get('root')
        lemma = word.get('lemma')
        word_text = word.get('text')
        word_num = word.get('word_number')

        if root:
            roots_in_verse.append({
                'root': root,
                'lemma': lemma,
                'text': word_text,
                'word_num': word_num
            })

    # Check pairs of roots for opposition
    for i, root1_data in enumerate(roots_in_verse):
        for j, root2_data in enumerate(roots_in_verse[i+1:], start=i+1):
            root1 = root1_data['root']
            root2 = root2_data['root']

            # Check if these roots are antonyms
            antonym_info = are_antonyms(root1, root2, antonym_lookup)

            if antonym_info:
                tibaq_instances.append({
                    'type': 'tibaq_al_ijab',  # Positive antithesis
                    'word1': {
                        'text': root1_data['text'],
                        'root': root1,
                        'lemma': root1_data['lemma'],
                        'word_num': root1_data['word_num']
                    },
                    'word2': {
                        'text': root2_data['text'],
                        'root': root2,
                        'lemma': root2_data['lemma'],
                        'word_num': root2_data['word_num']
                    },
                    'opposition_type': antonym_info['opposition_type'],
                    'meaning1': antonym_info['meaning1'],
                    'meaning2': antonym_info['meaning2']
                })

    # Detect negative antithesis (word + negation)
    # This is more complex and requires analysis of negation particles
    negation_instances = detect_negative_tibaq(roots_in_verse)
    if negation_instances:
        tibaq_instances.extend(negation_instances)

    return {'tibaq_patterns': tibaq_instances} if tibaq_instances else None


def build_antonym_lookup(antonym_pairs):
    """
    Build a lookup dict for fast antonym checking.

    Args:
        antonym_pairs: List of antonym pair dicts

    Returns:
        Dict mapping root to list of its antonyms with metadata
    """
    lookup = {}

    for pair in antonym_pairs:
        root1 = pair.get('root1')
        root2 = pair.get('root2')
        opposition_type = pair.get('opposition_type')
        meaning1 = pair.get('meaning1')
        meaning2 = pair.get('meaning2')

        if root1 and root2:
            # Add bidirectional mapping
            if root1 not in lookup:
                lookup[root1] = []
            lookup[root1].append({
                'antonym': root2,
                'opposition_type': opposition_type,
                'meaning1': meaning1,
                'meaning2': meaning2
            })

            if root2 not in lookup:
                lookup[root2] = []
            lookup[root2].append({
                'antonym': root1,
                'opposition_type': opposition_type,
                'meaning1': meaning2,
                'meaning2': meaning1
            })

    return lookup


def are_antonyms(root1, root2, antonym_lookup):
    """
    Check if two roots are semantic opposites.

    Args:
        root1: First root
        root2: Second root
        antonym_lookup: Antonym lookup dict

    Returns:
        Dict with antonym info if they are opposites, None otherwise
    """
    if root1 in antonym_lookup:
        for antonym_info in antonym_lookup[root1]:
            if antonym_info['antonym'] == root2:
                return antonym_info

    return None


def detect_negative_tibaq(roots_in_verse):
    """
    Detect negative antithesis (tibaq al-salb) - word + its negation.

    Args:
        roots_in_verse: List of root data dicts

    Returns:
        List of negative tibaq instances
    """
    # Negation particles in Arabic
    negation_particles = {'لا', 'ما', 'لم', 'لن', 'غير'}

    negative_instances = []

    # This is a simplified detection
    # Full implementation would need to parse verb forms and negation contexts
    # For now, we check if same root appears with and without negation markers

    root_occurrences = {}

    for root_data in roots_in_verse:
        root = root_data['root']
        word_text = root_data['text']

        # Check if word contains negation
        has_negation = any(neg in word_text for neg in negation_particles)

        if root not in root_occurrences:
            root_occurrences[root] = {'positive': [], 'negative': []}

        if has_negation:
            root_occurrences[root]['negative'].append(root_data)
        else:
            root_occurrences[root]['positive'].append(root_data)

    # Find roots that appear both with and without negation
    for root, occurrences in root_occurrences.items():
        if occurrences['positive'] and occurrences['negative']:
            # Found negative tibaq
            for pos_data in occurrences['positive']:
                for neg_data in occurrences['negative']:
                    negative_instances.append({
                        'type': 'tibaq_al_salb',  # Negative antithesis
                        'word1': {
                            'text': pos_data['text'],
                            'root': pos_data['root'],
                            'lemma': pos_data['lemma'],
                            'word_num': pos_data['word_num']
                        },
                        'word2': {
                            'text': neg_data['text'],
                            'root': neg_data['root'],
                            'lemma': neg_data['lemma'],
                            'word_num': neg_data['word_num']
                        },
                        'opposition_type': 'negation',
                        'meaning1': 'affirmative form',
                        'meaning2': 'negative form'
                    })

    return negative_instances
