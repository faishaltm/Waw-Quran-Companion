"""
Tashbih (Simile/Comparison) Detector

Detects tashbih candidates by finding comparison particles.
The LLM will then complete the full analysis (tenor, vehicle, ground).

Comparison particles in Arabic:
- كَ (ka) - like, as
- كَأَنَّ (ka'anna) - as if, as though
- مِثْلُ (mithl) - similar to, like
- شَبَهَ (shabaha) - resembles
"""


def detect_tashbih_candidates(verse_morphology, verse_segments=None):
    """
    Detect tashbih candidates by finding comparison particles.

    A complete tashbih has 4 elements:
    1. Mushabbah (Tenor) - what is being compared
    2. Mushabbah bihi (Vehicle) - what it's compared to
    3. Wajh al-shabah (Ground) - the shared quality
    4. Adāt al-tashbīh (Particle) - the comparison particle

    This function detects element 4, and provides context for LLM to find 1-3.

    Args:
        verse_morphology: List of simplified word morphology data
        verse_segments: Dict of raw morphology segments by word number (optional)

    Returns:
        Dict with tashbih_candidates or None if no candidates found
    """

    if not verse_morphology:
        return None

    # Comparison particles (lemmas)
    comparison_particles = {
        'ك': 'ka (like, as)',
        'كأن': 'ka\'anna (as if)',
        'كأنّ': 'ka\'anna (as if)',
        'مثل': 'mithl (similar to)',
        'شبه': 'shabaha (resembles)',
        'أشبه': 'ashbaha (more resembling)'
    }

    # Pronouns that contain كَ but are not comparison particles
    pronouns_with_ka = [
        'إِيَّاكَ',  # You (accusative)
        'إياك',
        'ذَٰلِكَ',   # That
        'ذلك',
        'أُولَٰئِكَ', # Those
        'أولئك',
        'كَذَٰلِكَ',  # Thus, like that (demonstrative, not comparison)
        'كذلك'
    ]

    candidates = []

    for i, word in enumerate(verse_morphology):
        lemma = word.get('lemma', '')
        word_text = word.get('text', '')
        word_num = word.get('word_number', i + 1)
        root = word.get('root', '')

        # Check lemma first
        particle_found = None
        particle_type = None

        if lemma in comparison_particles:
            particle_found = lemma
            particle_type = comparison_particles[lemma]

        # Check if كَ appears as a PREFIX particle (using segments if available)
        if not particle_found and verse_segments:
            word_num_str = str(word_num)
            if word_num_str in verse_segments:
                segments = verse_segments[word_num_str]

                # Check if any PREFIX segment is a comparison particle
                for seg in segments:
                    if seg.get('segment_type') == 'PREFIX':
                        seg_lemma = seg.get('lemma', '')
                        seg_text = seg.get('arabic', '')

                        if seg_lemma in comparison_particles:
                            particle_found = seg_lemma
                            particle_type = f"{comparison_particles[seg_lemma]} - prefix"
                            break

                        # Check for كَ particle prefix
                        if seg_text == 'كَ' or seg_lemma == 'ك':
                            # Verify this is not part of a pronoun
                            if word_text not in pronouns_with_ka:
                                particle_found = 'كَ'
                                particle_type = 'ka (like, as) - prefix'
                                break

        # Fallback: Check if word starts with كَ and is not a pronoun (without segments)
        if not particle_found and not verse_segments:
            if word_text.startswith('كَ') and word_text not in pronouns_with_ka:
                # Additional check: if root starts with ك, it's likely part of the root, not a particle
                if not (root and root.startswith('ك')):
                    particle_found = 'كَ'
                    particle_type = 'ka (like, as) - detected at word start'

        # Check root for شبه
        if not particle_found and root == 'شبه':
            particle_found = root
            particle_type = 'shabaha (resembles) - root form'

        if particle_found:
            # Get context words (before and after)
            context_before = []
            context_after = []

            # Get up to 3 words before
            for j in range(max(0, i - 3), i):
                if j < len(verse_morphology):
                    context_before.append({
                        'text': verse_morphology[j].get('text', ''),
                        'word_num': verse_morphology[j].get('word_number', j + 1),
                        'lemma': verse_morphology[j].get('lemma', ''),
                        'root': verse_morphology[j].get('root', '')
                    })

            # Get up to 3 words after
            for j in range(i + 1, min(len(verse_morphology), i + 4)):
                context_after.append({
                    'text': verse_morphology[j].get('text', ''),
                    'word_num': verse_morphology[j].get('word_number', j + 1),
                    'lemma': verse_morphology[j].get('lemma', ''),
                    'root': verse_morphology[j].get('root', '')
                })

            candidates.append({
                'particle': particle_found,
                'particle_type': particle_type,
                'word_num': word_num,
                'word_text': word_text,
                'context_before': context_before,
                'context_after': context_after,
                'instruction': 'LLM should identify: tenor (before particle), vehicle (after particle), and shared quality'
            })

    # Filter out false positives (demonstratives like كَذَٰلِكَ)
    candidates = filter_false_positives(candidates)

    return {'tashbih_candidates': candidates} if candidates else None


def filter_false_positives(candidates):
    """
    Filter out false positive comparison particles.

    Some particles like كَ appear in demonstratives (كَذَٰلِكَ - thus, like that)
    which are not true tashbih.

    Args:
        candidates: List of tashbih candidates

    Returns:
        Filtered list of candidates
    """
    filtered = []

    for candidate in candidates:
        word_text = candidate.get('word_text', '')

        # Skip demonstratives
        if 'كَذَٰلِكَ' in word_text or 'كذلك' in word_text:
            continue

        # Skip if it's just a demonstrative particle without comparison
        if word_text in ['كَذَا', 'كذا']:
            continue

        # If particle is مثل, check if it's in idafa (possessive) construction
        # مَثَلُهُمْ (their example) is valid tashbih
        # This is fine, keep it

        filtered.append(candidate)

    return filtered


def analyze_tashbih_structure(candidate, verse_morphology):
    """
    Helper function to analyze the structure around a tashbih particle.
    This can be used by the LLM or in future enhancements.

    Args:
        candidate: Tashbih candidate dict
        verse_morphology: Full verse morphology

    Returns:
        Dict with structural analysis
    """

    analysis = {
        'particle_position': candidate['word_num'],
        'total_words': len(verse_morphology)
    }

    # Identify noun phrases before and after
    # This is a simplified analysis - full NP chunking would require dependency parsing

    context_before = candidate.get('context_before', [])
    context_after = candidate.get('context_after', [])

    # Look for nouns before (potential tenor)
    tenor_candidates = []
    for ctx in context_before:
        # Check if word is a noun (simplified - would need full morphology)
        if ctx.get('lemma'):  # Has lemma suggests it's a content word
            tenor_candidates.append(ctx['text'])

    # Look for nouns after (potential vehicle)
    vehicle_candidates = []
    for ctx in context_after:
        if ctx.get('lemma'):
            vehicle_candidates.append(ctx['text'])

    analysis['tenor_candidates'] = tenor_candidates
    analysis['vehicle_candidates'] = vehicle_candidates

    return analysis
