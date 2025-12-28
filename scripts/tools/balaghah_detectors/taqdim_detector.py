"""
Taqdim wa Ta'khir (Word Order) Detector

Detects word order variations from expected Arabic sentence patterns.
Arabic has two main sentence types:
1. Verbal Sentence (VS): Expected order is Verb-Subject-Object (VSO)
2. Nominal Sentence (NS): Expected order is Subject-Predicate (Mubtada-Khabar)

When elements are advanced (taqdim) or delayed (ta'khir), it creates rhetorical effects.
"""

def detect_taqdim_takhir(verse_dependencies, verse_morphology):
    """
    Detect word order variations from expected patterns.

    Args:
        verse_dependencies: List of dependency relations for the verse
        verse_morphology: List of morphological data for each word

    Returns:
        Dict with taqdim_takhir_patterns or None if no patterns found
    """

    if not verse_dependencies or not verse_morphology:
        return None

    patterns = []

    # Step 1: Identify sentence roots (VS = Verbal, NS = Nominal)
    sentence_roots = [
        dep for dep in verse_dependencies
        if dep.get('relation', {}).get('code') in ['VS', 'NS']
    ]

    for sentence_root in sentence_roots:
        sent_type = sentence_root['relation']['code']  # VS or NS
        root_word_num = sentence_root['child']['word']

        # Step 2: Find elements of this sentence
        sentence_elements = find_sentence_elements(
            root_word_num,
            verse_dependencies
        )

        # Step 3: Determine expected vs actual order
        if sent_type == 'VS':
            # Expected: Verb → Subject → Object
            expected_order = determine_vs_expected_order(sentence_elements)
            actual_order = get_actual_word_order(sentence_elements)

        elif sent_type == 'NS':
            # Expected: Subject (Mubtada) → Predicate (Khabar)
            expected_order = determine_ns_expected_order(sentence_elements)
            actual_order = get_actual_word_order(sentence_elements)
        else:
            continue

        # Step 4: Compare orders and detect deviations
        deviations = compare_orders(expected_order, actual_order)

        if deviations:
            for dev in deviations:
                word_text = get_word_text(dev['word_num'], verse_morphology)
                patterns.append({
                    'sentence_type': sent_type,
                    'element_advanced': dev['element'],  # e.g., 'object', 'predicate'
                    'expected_position': dev['expected_pos'],
                    'actual_position': dev['actual_pos'],
                    'word_text': word_text,
                    'word_num': dev['word_num'],
                    'rhetorical_candidates': [
                        'restriction (qasr)',
                        'glorification (ta\'zim)',
                        'emphasis (tawkid)',
                        'anticipation (tashwiq)'
                    ]
                    # LLM determines which purpose applies
                })

    return {'taqdim_takhir_patterns': patterns} if patterns else None


def find_sentence_elements(root_word, dependencies):
    """
    Extract all elements of a sentence from dependency tree.

    Args:
        root_word: Word number of the sentence root
        dependencies: List of all dependencies in the verse

    Returns:
        Dict with keys like 'verb', 'subject', 'object', 'predicate', etc.
    """
    elements = {}

    for dep in dependencies:
        # Check if this dependency's parent is the root word
        parent_word = dep.get('parent', {}).get('word')
        if parent_word == root_word:
            relation_code = dep.get('relation', {}).get('code')
            child_word = dep.get('child', {}).get('word')

            # Skip embedded elements (where child = parent = root)
            # These are pronouns embedded in verbs, not separate syntactic elements
            if child_word == parent_word:
                continue

            if relation_code == 'subj':
                elements['subject'] = child_word
            elif relation_code == 'obj':
                elements['object'] = child_word
            elif relation_code == 'pred':
                elements['predicate'] = child_word
            elif relation_code == 'PP':  # Prepositional phrase
                if 'prepositional_phrases' not in elements:
                    elements['prepositional_phrases'] = []
                elements['prepositional_phrases'].append(child_word)
            elif relation_code == 'adj':  # Adjective
                if 'adjectives' not in elements:
                    elements['adjectives'] = []
                elements['adjectives'].append(child_word)

    # The root word itself is the verb (VS) or subject (NS)
    elements['root'] = root_word

    return elements


def determine_vs_expected_order(elements):
    """
    For verbal sentences, expected order is VSO (Verb-Subject-Object).

    Args:
        elements: Dict of sentence elements

    Returns:
        List of tuples (element_type, word_num) in expected order
    """
    order = []

    # Expected: Verb first
    if 'root' in elements:
        order.append(('verb', elements['root']))

    # Then subject
    if 'subject' in elements:
        order.append(('subject', elements['subject']))

    # Then object
    if 'object' in elements:
        order.append(('object', elements['object']))

    # Prepositional phrases typically come after
    if 'prepositional_phrases' in elements:
        for pp in elements['prepositional_phrases']:
            order.append(('prepositional_phrase', pp))

    return order


def determine_ns_expected_order(elements):
    """
    For nominal sentences, expected order is Subject-Predicate (Mubtada-Khabar).

    Args:
        elements: Dict of sentence elements

    Returns:
        List of tuples (element_type, word_num) in expected order
    """
    order = []

    # Expected: Subject (mubtada) first
    if 'root' in elements:
        order.append(('subject', elements['root']))

    # Then predicate (khabar)
    if 'predicate' in elements:
        order.append(('predicate', elements['predicate']))

    return order


def get_actual_word_order(elements):
    """
    Get actual word order from elements based on word numbers.

    Args:
        elements: Dict of sentence elements

    Returns:
        List of tuples (element_type, word_num) sorted by word_num
    """
    actual = []

    # Collect all elements with their word numbers
    if 'root' in elements:
        actual.append(('root', elements['root']))
    if 'subject' in elements:
        actual.append(('subject', elements['subject']))
    if 'object' in elements:
        actual.append(('object', elements['object']))
    if 'predicate' in elements:
        actual.append(('predicate', elements['predicate']))
    if 'prepositional_phrases' in elements:
        for pp in elements['prepositional_phrases']:
            actual.append(('prepositional_phrase', pp))

    # Sort by word number (actual position in text)
    actual.sort(key=lambda x: x[1])

    return actual


def compare_orders(expected, actual):
    """
    Compare expected vs actual word order, return deviations.

    Args:
        expected: List of (element_type, word_num) in expected order
        actual: List of (element_type, word_num) in actual order

    Returns:
        List of deviation dicts
    """
    deviations = []

    for i, (element_type, word_num) in enumerate(expected):
        # Find actual position of this element
        actual_pos = None
        for j, (actual_type, actual_word) in enumerate(actual):
            if actual_word == word_num:
                actual_pos = j
                break

        # If positions don't match, it's a deviation
        if actual_pos is not None and actual_pos != i:
            deviations.append({
                'element': element_type,
                'word_num': word_num,
                'expected_pos': i + 1,  # 1-indexed for human readability
                'actual_pos': actual_pos + 1
            })

    return deviations


def get_word_text(word_num, morphology):
    """
    Get the Arabic text for a word number from morphology data.

    Args:
        word_num: Word number to find
        morphology: List of word morphology data

    Returns:
        Arabic text string or empty string if not found
    """
    for word in morphology:
        if word.get('word_number') == word_num:
            return word.get('text', '')

    return ''
