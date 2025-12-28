#!/usr/bin/env python3
"""
Get comparative information for TWO Quranic chapters
Extracts and correlates data for comparative balaghah analysis

Usage: Run the script and enter chapter1:chapter2 when prompted
Example: 68:69
"""

import json
import os
import sys
import re
from collections import defaultdict

# Add path to loaders and tools directories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loaders'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from metadata_loader import MetadataLoader
from get_verse_info_v2 import (
    load_comprehensive_quran,
    extract_verse_info_compact,
    buckwalter_to_arabic_root
)


# ============================================================================
# COMPARATIVE ANALYSIS FUNCTIONS
# ============================================================================

def detect_sequential_bridge(chapter1_data, chapter2_data):
    """
    Analyze how Chapter 1 ending connects to Chapter 2 opening

    Examines:
    - Last 3 verses of Chapter 1
    - First 3 verses of Chapter 2
    - Thematic/narrative continuity
    - Shared roots and concepts

    Returns:
        Dict with connection type and description, or None
    """
    ch1_verses = chapter1_data['verses']
    ch2_verses = chapter2_data['verses']

    if not ch1_verses or not ch2_verses:
        return None

    # Get last 3 verses of Chapter 1
    last_verses_ch1 = ch1_verses[-3:] if len(ch1_verses) >= 3 else ch1_verses

    # Get first 3 verses of Chapter 2
    first_verses_ch2 = ch2_verses[:3] if len(ch2_verses) >= 3 else ch2_verses

    # Extract roots from endings and openings
    ch1_ending_roots = set()
    ch1_ending_text = []

    for verse in last_verses_ch1:
        ch1_ending_text.append({
            'verse': verse['verse_number'],
            'text': verse['text'],
            'translation': verse.get('translation', '')
        })

        # Extract roots from root_repetitions
        root_reps = verse.get('root_repetitions', {})
        for root in root_reps.keys():
            ch1_ending_roots.add(root)

    ch2_opening_roots = set()
    ch2_opening_text = []

    for verse in first_verses_ch2:
        ch2_opening_text.append({
            'verse': verse['verse_number'],
            'text': verse['text'],
            'translation': verse.get('translation', '')
        })

        # Extract roots from root_repetitions
        root_reps = verse.get('root_repetitions', {})
        for root in root_reps.keys():
            ch2_opening_roots.add(root)

    # Find shared roots
    shared_roots = ch1_ending_roots & ch2_opening_roots

    # Analyze connection type
    connection_type = None
    description = ""

    # Check for question-answer pattern
    ch1_last_translation = last_verses_ch1[-1].get('translation', '').lower()

    if '?' in ch1_last_translation or any(word in ch1_last_translation for word in ['who', 'what', 'where', 'when', 'why', 'how']):
        connection_type = 'question_answer'
        description = "Chapter 1 ends with a question or challenge that Chapter 2 addresses"

    # Check for threat-demonstration pattern
    elif any(word in ch1_last_translation for word in ['warn', 'threat', 'deny', 'reject', 'leave']):
        connection_type = 'threat_demonstration'
        description = "Chapter 1 ends with warning/threat, Chapter 2 demonstrates fulfillment"

    # Check for continuation pattern (shared roots)
    elif shared_roots:
        connection_type = 'thematic_continuation'
        description = f"Thematic continuation through {len(shared_roots)} shared roots"

    # Default to sequential
    else:
        connection_type = 'sequential'
        description = "Sequential placement without explicit bridge"

    result = {
        'connection_type': connection_type,
        'description': description,
        'chapter1_ending': {
            'verses': ch1_ending_text,
            'key_phrase': last_verses_ch1[-1].get('translation', '')[:100]
        },
        'chapter2_opening': {
            'verses': ch2_opening_text,
            'key_phrase': first_verses_ch2[0].get('translation', '')[:100]
        }
    }

    if shared_roots:
        result['shared_roots'] = sorted(list(shared_roots))

    return result


def analyze_ring_structures(chapter1_data, chapter2_data, comprehensive_data):
    """
    Map ring compositions (chiastic structures) within and across chapters

    Three levels:
    1. Internal rings within each chapter
    2. Paired ring (chapters forming larger structure)
    3. Center identification (thematic core)

    Returns:
        Dict with ring structure analysis
    """
    result = {}

    # LEVEL 1: Internal ring detection for each chapter
    ch1_internal = detect_internal_ring(chapter1_data, comprehensive_data)
    ch2_internal = detect_internal_ring(chapter2_data, comprehensive_data)

    if ch1_internal:
        result['chapter1_internal_ring'] = ch1_internal

    if ch2_internal:
        result['chapter2_internal_ring'] = ch2_internal

    # LEVEL 2: Paired ring detection (chapters forming larger structure)
    paired_ring = detect_paired_ring(chapter1_data, chapter2_data)

    if paired_ring:
        result['paired_ring'] = paired_ring

    return result if result else None


def detect_internal_ring(chapter_data, comprehensive_data):
    """
    Detect internal ring structure within a single chapter

    Pattern: A-B-C-B'-A' where C is center

    Indicators:
    - Matching roots/themes at start and end
    - Symmetrical section headings
    - Center contains unique concentration

    Returns:
        Dict with ring pattern or None
    """
    verses = chapter_data['verses']
    chapter_num = chapter_data['metadata']['chapter_number']

    if len(verses) < 5:
        return None  # Too short for ring

    # Get section headings from metadata
    section_headings = chapter_data['metadata'].get('section_headings', {})

    if not section_headings:
        return None

    # Parse sections
    sections = []
    for verse_range, heading in section_headings.items():
        if '-' in verse_range:
            start, end = verse_range.split('-')
            sections.append({
                'start': int(start),
                'end': int(end),
                'heading': heading
            })
        else:
            verse_num = int(verse_range)
            sections.append({
                'start': verse_num,
                'end': verse_num,
                'heading': heading
            })

    sections.sort(key=lambda x: x['start'])

    if len(sections) < 3:
        return None  # Need at least 3 sections for A-B-A'

    # Check for ring pattern by comparing first and last sections
    first_section = sections[0]
    last_section = sections[-1]

    # Extract roots from first and last sections
    first_roots = extract_section_roots(verses, first_section['start'], first_section['end'])
    last_roots = extract_section_roots(verses, last_section['start'], last_section['end'])

    shared_roots = first_roots & last_roots

    # Ring detected if significant root overlap
    if len(shared_roots) >= 2:
        # Find center (middle section)
        center_idx = len(sections) // 2
        center_section = sections[center_idx]

        return {
            'detected': True,
            'pattern': f"A-...-A' ({len(sections)} sections)",
            'center': {
                'section_heading': center_section['heading'],
                'verses': f"{center_section['start']}-{center_section['end']}"
            },
            'opening_section': first_section['heading'],
            'closing_section': last_section['heading'],
            'shared_roots': sorted(list(shared_roots)),
            'total_sections': len(sections)
        }

    return None


def extract_section_roots(verses, start_verse, end_verse):
    """Extract all roots from verses in a section range"""
    roots = set()

    for verse in verses:
        verse_num = verse['verse_number']
        if start_verse <= verse_num <= end_verse:
            # Extract from root_repetitions
            root_reps = verse.get('root_repetitions', {})
            for root in root_reps.keys():
                roots.add(root)

    return roots


def detect_paired_ring(chapter1_data, chapter2_data):
    """
    Detect if two chapters form a paired ring structure

    Pattern: Ch1 (A-B-C) mirrors Ch2 (C'-B'-A')

    Returns:
        Dict with paired ring info or None
    """
    # Compare opening of Ch1 with ending of Ch2
    ch1_opening_roots = extract_section_roots(
        chapter1_data['verses'],
        1,
        min(5, len(chapter1_data['verses']))
    )

    ch2_ending_verse = len(chapter2_data['verses'])
    ch2_ending_roots = extract_section_roots(
        chapter2_data['verses'],
        max(1, ch2_ending_verse - 4),
        ch2_ending_verse
    )

    shared_roots = ch1_opening_roots & ch2_ending_roots

    if len(shared_roots) >= 2:
        return {
            'detected': True,
            'pattern': 'Chapter 1 opening mirrors Chapter 2 ending',
            'description': 'Paired chiastic structure across chapter boundary',
            'shared_roots': sorted(list(shared_roots))
        }

    return None


def compare_balaghah_frequencies(chapter1_data, chapter2_data):
    """
    Statistical comparison of balaghah devices across both chapters

    Compares:
    - Saj' patterns and consistency
    - Iltifat shifts
    - Muqatta'at presence/absence
    - Verb forms distribution
    - Interrogatives, oaths, emphasis

    Returns:
        Dict with comparative frequencies
    """
    result = {}

    # SAJ' COMPARISON
    saj_ch1 = analyze_saj_patterns(chapter1_data)
    saj_ch2 = analyze_saj_patterns(chapter2_data)

    if saj_ch1 or saj_ch2:
        result['saj_patterns'] = {
            'chapter1': saj_ch1,
            'chapter2': saj_ch2
        }

    # MUQATTA'AT COMPARISON
    muqattaat_ch1 = check_muqattaat(chapter1_data)
    muqattaat_ch2 = check_muqattaat(chapter2_data)

    result['muqattaat_comparison'] = {
        'chapter1': muqattaat_ch1,
        'chapter2': muqattaat_ch2,
        'significance': interpret_muqattaat_difference(muqattaat_ch1, muqattaat_ch2)
    }

    # ILTIFAT COMPARISON
    iltifat_ch1 = count_iltifat_shifts(chapter1_data)
    iltifat_ch2 = count_iltifat_shifts(chapter2_data)

    if iltifat_ch1['total'] > 0 or iltifat_ch2['total'] > 0:
        result['iltifat_frequency'] = {
            'chapter1': iltifat_ch1,
            'chapter2': iltifat_ch2
        }

    # VERB FORMS COMPARISON
    verbs_ch1 = analyze_verb_forms(chapter1_data)
    verbs_ch2 = analyze_verb_forms(chapter2_data)

    if verbs_ch1 or verbs_ch2:
        result['verb_forms'] = {
            'chapter1': verbs_ch1,
            'chapter2': verbs_ch2
        }

    # QASAM (OATH) COMPARISON
    qasam_ch1 = count_qasam(chapter1_data)
    qasam_ch2 = count_qasam(chapter2_data)

    if qasam_ch1['count'] > 0 or qasam_ch2['count'] > 0:
        result['qasam_comparison'] = {
            'chapter1': qasam_ch1,
            'chapter2': qasam_ch2
        }

    # INTERROGATIVE COMPARISON
    interrog_ch1 = count_interrogatives(chapter1_data)
    interrog_ch2 = count_interrogatives(chapter2_data)

    if interrog_ch1['count'] > 0 or interrog_ch2['count'] > 0:
        result['interrogative_comparison'] = {
            'chapter1': interrog_ch1,
            'chapter2': interrog_ch2
        }

    return result


def analyze_saj_patterns(chapter_data):
    """Analyze saj' (rhyme) patterns in a chapter"""
    verses = chapter_data['verses']

    # Collect all saj data
    patterns = defaultdict(int)
    total_verses = len(verses)
    verses_with_saj = 0

    for verse in verses:
        balaghah = verse.get('balaghah', {})
        saj = balaghah.get('saj')

        if saj:
            verses_with_saj += 1
            pattern = saj.get('ending_pattern', 'unknown')
            patterns[pattern] += 1

    if not patterns:
        return None

    # Find dominant pattern
    dominant_pattern = max(patterns.items(), key=lambda x: x[1])

    # Calculate consistency (percentage of dominant pattern)
    consistency = (dominant_pattern[1] / total_verses) * 100 if total_verses > 0 else 0

    return {
        'dominant_pattern': dominant_pattern[0],
        'dominant_count': dominant_pattern[1],
        'total_verses': total_verses,
        'verses_with_saj': verses_with_saj,
        'consistency_percentage': round(consistency, 1),
        'all_patterns': dict(patterns)
    }


def check_muqattaat(chapter_data):
    """Check if chapter has muqatta'at (disconnected letters)"""
    verses = chapter_data['verses']

    if not verses:
        return {'has_muqattaat': False}

    first_verse = verses[0]
    balaghah = first_verse.get('balaghah', {})
    muqattaat = balaghah.get('muqattaat')

    if muqattaat and muqattaat.get('has_muqattaat'):
        return {
            'has_muqattaat': True,
            'letters': muqattaat.get('letters'),
            'note': muqattaat.get('note', '')
        }

    return {'has_muqattaat': False}


def interpret_muqattaat_difference(muq_ch1, muq_ch2):
    """Interpret the significance of muqatta'at presence/absence"""
    has_ch1 = muq_ch1.get('has_muqattaat', False)
    has_ch2 = muq_ch2.get('has_muqattaat', False)

    if has_ch1 and not has_ch2:
        return "Chapter 1 uses alerting device (muqatta'at) while Chapter 2 engages directly - suggests different audience states or chronological maturity"
    elif not has_ch1 and has_ch2:
        return "Chapter 2 uses alerting device (muqatta'at) while Chapter 1 engages directly"
    elif has_ch1 and has_ch2:
        return "Both chapters use muqatta'at - consistent alerting strategy"
    else:
        return "Neither chapter uses muqatta'at - direct engagement in both"


def count_iltifat_shifts(chapter_data):
    """Count iltifat (grammatical shifts) in chapter"""
    verses = chapter_data['verses']

    shift_types = defaultdict(int)
    total_shifts = 0

    for verse in verses:
        balaghah = verse.get('balaghah', {})
        iltifat = balaghah.get('iltifat')

        if iltifat and isinstance(iltifat, list):
            for shift in iltifat:
                shift_type = shift.get('type', 'unknown')
                shift_types[shift_type] += 1
                total_shifts += 1

    return {
        'total': total_shifts,
        'shift_types': dict(shift_types)
    }


def analyze_verb_forms(chapter_data):
    """Analyze verb form distribution in chapter"""
    verses = chapter_data['verses']

    form_counts = defaultdict(int)
    total_forms = 0

    for verse in verses:
        balaghah = verse.get('balaghah', {})
        maani = balaghah.get('maani', {})
        verb_forms = maani.get('verb_forms', [])

        for vf in verb_forms:
            form_num = vf.get('form')
            count = vf.get('count', 1)
            if form_num:
                form_counts[form_num] += count
                total_forms += count

    if not form_counts:
        return None

    # Find dominant form
    dominant_form = max(form_counts.items(), key=lambda x: x[1])

    return {
        'dominant_form': dominant_form[0],
        'dominant_count': dominant_form[1],
        'total_verb_forms': total_forms,
        'distribution': dict(form_counts)
    }


def count_qasam(chapter_data):
    """Count qasam (oaths) in chapter"""
    verses = chapter_data['verses']
    total = 0
    elements = []

    for verse in verses:
        balaghah = verse.get('balaghah', {})
        qasam = balaghah.get('qasam')

        if qasam and qasam.get('has_qasam'):
            count = qasam.get('count', 0)
            total += count
            elements.extend(qasam.get('elements', []))

    return {
        'count': total,
        'elements': elements[:5]  # First 5 examples
    }


def count_interrogatives(chapter_data):
    """Count interrogative particles in chapter"""
    verses = chapter_data['verses']
    total = 0
    particles = []

    for verse in verses:
        balaghah = verse.get('balaghah', {})
        interrog = balaghah.get('interrogative')

        if interrog and interrog.get('has_interrogative'):
            count = interrog.get('count', 0)
            total += count
            particles.extend(interrog.get('particles', []))

    return {
        'count': total,
        'particles': particles[:5]  # First 5 examples
    }


def analyze_thematic_parallels(chapter1_data, chapter2_data):
    """
    Analyze thematic parallels and contrasts between chapters

    Examines:
    - Shared roots and semantic development
    - Section parallels (same themes, different treatments)
    - Conceptual echoes across chapters

    Returns:
        Dict with thematic analysis
    """
    result = {}

    # SHARED ROOTS ANALYSIS
    shared_roots = find_shared_roots(chapter1_data, chapter2_data)

    if shared_roots:
        result['shared_roots'] = shared_roots

    # SECTION PARALLELS
    section_parallels = find_section_parallels(chapter1_data, chapter2_data)

    if section_parallels:
        result['section_parallels'] = section_parallels

    # CONCEPTUAL ECHOES (named entities)
    conceptual_echoes = find_conceptual_echoes(chapter1_data, chapter2_data)

    if conceptual_echoes:
        result['conceptual_echoes'] = conceptual_echoes

    return result if result else None


def find_shared_roots(chapter1_data, chapter2_data):
    """Find roots appearing in BOTH chapters with usage analysis

    Extracts roots from root_repetitions data in verses
    """
    ch1_roots = defaultdict(set)  # Use sets to track unique verses
    ch2_roots = defaultdict(set)

    # Collect roots from Chapter 1 via root_repetitions
    for verse in chapter1_data['verses']:
        verse_num = verse['verse_number']
        root_reps = verse.get('root_repetitions', {})

        # Each key in root_repetitions is a root
        for root in root_reps.keys():
            ch1_roots[root].add(verse_num)

    # Collect roots from Chapter 2
    for verse in chapter2_data['verses']:
        verse_num = verse['verse_number']
        root_reps = verse.get('root_repetitions', {})

        for root in root_reps.keys():
            ch2_roots[root].add(verse_num)

    # Find shared roots
    shared = []
    for root in ch1_roots:
        if root in ch2_roots:
            shared.append({
                'root': root,
                'chapter1_occurrences': len(ch1_roots[root]),
                'chapter2_occurrences': len(ch2_roots[root]),
                'chapter1_verses': sorted(list(ch1_roots[root])),
                'chapter2_verses': sorted(list(ch2_roots[root]))
            })

    # Sort by total frequency
    shared.sort(key=lambda x: x['chapter1_occurrences'] + x['chapter2_occurrences'], reverse=True)

    return shared if shared else None


def find_section_parallels(chapter1_data, chapter2_data):
    """Find thematic parallels in section structure"""
    ch1_sections = chapter1_data['metadata'].get('section_headings', {})
    ch2_sections = chapter2_data['metadata'].get('section_headings', {})

    if not ch1_sections or not ch2_sections:
        return None

    # Look for similar themes in section headings
    parallels = []

    # Keywords to identify common themes
    theme_keywords = {
        'believers': ['believer', 'faithful', 'righteous'],
        'deniers': ['denier', 'reject', 'disbeliev', 'unbeliev'],
        'resurrection': ['resurrection', 'day of judgment', 'hereafter'],
        'punishment': ['punishment', 'torment', 'penalty'],
        'reward': ['reward', 'paradise', 'garden'],
        'warning': ['warning', 'admonition'],
        'prophet': ['prophet', 'messenger'],
        'creation': ['creation', 'create', 'sign'],
        'guidance': ['guidance', 'guide', 'path']
    }

    for theme, keywords in theme_keywords.items():
        ch1_has = any(any(kw in heading.lower() for kw in keywords) for heading in ch1_sections.values())
        ch2_has = any(any(kw in heading.lower() for kw in keywords) for heading in ch2_sections.values())

        if ch1_has and ch2_has:
            # Find specific sections
            ch1_sections_with_theme = [
                {'range': r, 'heading': h}
                for r, h in ch1_sections.items()
                if any(kw in h.lower() for kw in keywords)
            ]
            ch2_sections_with_theme = [
                {'range': r, 'heading': h}
                for r, h in ch2_sections.items()
                if any(kw in h.lower() for kw in keywords)
            ]

            parallels.append({
                'theme': theme,
                'chapter1_sections': ch1_sections_with_theme,
                'chapter2_sections': ch2_sections_with_theme,
                'note': f"Both chapters address '{theme}' theme in different structural positions"
            })

    return parallels if parallels else None


def find_conceptual_echoes(chapter1_data, chapter2_data):
    """Find shared conceptual references (named entities)"""
    # This would analyze named_entities if present in verse data
    # For now, return placeholder
    return None


def analyze_chronological_context(chapter1_num, chapter2_num, metadata_loader):
    """
    Analyze chronological relationship and stylistic maturation

    Uses revelation order to determine:
    - Temporal span between revelations
    - Period classification (early/middle/late Meccan/Medinan)
    - Stylistic maturation indicators

    Returns:
        Dict with chronological analysis
    """
    if not metadata_loader:
        return None

    # Get revelation order data
    rev_ch1 = metadata_loader.get_revelation_order(chapter1_num)
    rev_ch2 = metadata_loader.get_revelation_order(chapter2_num)

    if not rev_ch1 or not rev_ch2:
        return None

    order_ch1 = rev_ch1.get('revelation_order')
    order_ch2 = rev_ch2.get('revelation_order')

    if not order_ch1 or not order_ch2:
        return None

    # Calculate temporal span
    revelations_between = abs(order_ch2 - order_ch1) - 1

    # Get period classification
    ch1_meta = metadata_loader.get_chapter_metadata(chapter1_num)
    ch2_meta = metadata_loader.get_chapter_metadata(chapter2_num)

    period_ch1 = ch1_meta.get('revelation_place', 'unknown')
    period_ch2 = ch2_meta.get('revelation_place', 'unknown')

    # Classify as early/middle/late
    period_class_ch1 = classify_period(order_ch1, period_ch1)
    period_class_ch2 = classify_period(order_ch2, period_ch2)

    result = {
        'revelation_order_chapter1': order_ch1,
        'revelation_order_chapter2': order_ch2,
        'revelations_between': revelations_between,
        'period_chapter1': period_class_ch1,
        'period_chapter2': period_class_ch2,
        'chronological_relationship': determine_chronological_relationship(order_ch1, order_ch2)
    }

    # Add stylistic maturation analysis if chapters are far apart
    if revelations_between > 10:
        maturation = analyze_stylistic_maturation(period_class_ch1, period_class_ch2, revelations_between)
        if maturation:
            result['stylistic_maturation'] = maturation

    return result


def classify_period(revelation_order, revelation_place):
    """Classify revelation into early/middle/late within Meccan/Medinan"""
    if revelation_place == 'makkah':
        if revelation_order <= 30:
            return 'early_meccan'
        elif revelation_order <= 70:
            return 'middle_meccan'
        else:
            return 'late_meccan'
    elif revelation_place == 'madinah':
        if revelation_order <= 95:
            return 'early_medinan'
        else:
            return 'late_medinan'

    return 'unknown'


def determine_chronological_relationship(order1, order2):
    """Determine relationship between two chapters chronologically"""
    diff = abs(order2 - order1)

    if diff == 1:
        return 'consecutive'
    elif diff <= 10:
        return 'close'
    elif diff <= 50:
        return 'moderate_gap'
    else:
        return 'distant'


def analyze_stylistic_maturation(period1, period2, revelations_between):
    """
    Analyze stylistic maturation between two periods

    Early Meccan → Late Meccan indicators:
    - Emotional → Logical
    - Personal → Universal
    - Indirect → Direct
    - Phonetic consistency → Variation

    Returns:
        Dict with maturation indicators
    """
    # Map periods to maturity levels
    maturity_order = [
        'early_meccan',
        'middle_meccan',
        'late_meccan',
        'early_medinan',
        'late_medinan'
    ]

    try:
        idx1 = maturity_order.index(period1)
        idx2 = maturity_order.index(period2)
    except ValueError:
        return None

    if idx2 <= idx1:
        return None  # No maturation (second is earlier or same)

    # Determine characteristics
    early_chars = []
    late_chars = []

    if 'early' in period1:
        early_chars = [
            'Emotional appeals and vivid imagery',
            'Personal address to Prophet and opponents',
            'Indirect argumentation through parables',
            'High phonetic consistency (saj\' dominance)',
            'Short, punchy verses',
            'Oath usage for emphasis'
        ]

    if 'late' in period2:
        late_chars = [
            'Logical argumentation and proofs',
            'Universal address to all humanity',
            'Direct statements and commands',
            'Phonetic variation for semantic emphasis',
            'Longer, complex verses',
            'Reduced oath usage'
        ]

    return {
        'evolution_span': f'{revelations_between} revelations',
        'early_characteristics': early_chars,
        'late_characteristics': late_chars,
        'note': f'Stylistic evolution from {period1} to {period2}'
    }


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_two_chapter_info_comparative(chapter1_num, chapter2_num, comprehensive_data, metadata_loader):
    """
    Extract comprehensive comparative information for two chapters

    Returns complete structure with:
    - Individual chapter data (full extraction)
    - Comparative analysis (bridges, rings, balaghah, themes, chronology)

    Args:
        chapter1_num: First chapter number (1-114)
        chapter2_num: Second chapter number (1-114)
        comprehensive_data: Loaded comprehensive Quran data
        metadata_loader: MetadataLoader instance

    Returns:
        Dict with complete comparative analysis
    """
    # Validate input
    if chapter1_num < 1 or chapter1_num > 114 or chapter2_num < 1 or chapter2_num > 114:
        raise ValueError("Chapter numbers must be between 1 and 114")

    print(f"\nExtracting Chapter {chapter1_num} data...")

    # Extract full data for Chapter 1
    chapter1_data = extract_verse_info_compact(
        chapter1_num,
        1,  # verse_start
        get_chapter_verse_count(chapter1_num, comprehensive_data),  # verse_end
        comprehensive_data
    )

    print(f"Extracting Chapter {chapter2_num} data...")

    # Extract full data for Chapter 2
    chapter2_data = extract_verse_info_compact(
        chapter2_num,
        1,
        get_chapter_verse_count(chapter2_num, comprehensive_data),
        comprehensive_data
    )

    print("Performing comparative analysis...")

    # Build comparative analysis
    comparative_analysis = {}

    # 1. Sequential Bridge Analysis
    print("  - Analyzing sequential bridge...")
    sequential_bridge = detect_sequential_bridge(chapter1_data, chapter2_data)
    if sequential_bridge:
        comparative_analysis['sequential_bridge'] = sequential_bridge

    # 2. Ring Structure Analysis
    print("  - Mapping ring structures...")
    ring_structures = analyze_ring_structures(chapter1_data, chapter2_data, comprehensive_data)
    if ring_structures:
        comparative_analysis['ring_structures'] = ring_structures

    # 3. Balaghah Comparison
    print("  - Comparing balaghah frequencies...")
    balaghah_comparison = compare_balaghah_frequencies(chapter1_data, chapter2_data)
    if balaghah_comparison:
        comparative_analysis['balaghah_comparison'] = balaghah_comparison

    # 4. Thematic Parallels
    print("  - Analyzing thematic parallels...")
    thematic_parallels = analyze_thematic_parallels(chapter1_data, chapter2_data)
    if thematic_parallels:
        comparative_analysis['thematic_parallels'] = thematic_parallels

    # 5. Chronological Context
    print("  - Analyzing chronological context...")
    chronological_context = analyze_chronological_context(chapter1_num, chapter2_num, metadata_loader)
    if chronological_context:
        comparative_analysis['chronological_context'] = chronological_context

    # Build final result
    result = {
        'chapter_pair': [chapter1_num, chapter2_num],
        'chapter1': chapter1_data,
        'chapter2': chapter2_data,
        'comparative_analysis': comparative_analysis
    }

    # Add temporal span to top level for easy access
    if chronological_context:
        result['temporal_span'] = {
            'revelation_order_1': chronological_context.get('revelation_order_chapter1'),
            'revelation_order_2': chronological_context.get('revelation_order_chapter2'),
            'revelations_between': chronological_context.get('revelations_between'),
            'period_1': chronological_context.get('period_chapter1'),
            'period_2': chronological_context.get('period_chapter2')
        }

    print("Comparative analysis complete!\n")

    return result


def get_chapter_verse_count(chapter_num, comprehensive_data):
    """Get total verse count for a chapter"""
    for chapter in comprehensive_data['chapters']:
        if chapter['chapter_number'] == chapter_num:
            return chapter['verses_count']
    return 0


# ============================================================================
# MAIN INTERACTIVE LOOP
# ============================================================================

def main():
    """Main interactive loop"""
    print("=" * 70)
    print("Quranic Two-Chapter Comparative Analysis")
    print("Extracts and correlates data for comparative balaghah analysis")
    print("=" * 70)
    print()
    print("Enter two chapter numbers in format:")
    print("  - Two chapters: chapter1:chapter2 (e.g., 68:69)")
    print("  - Type 'quit' to exit")
    print()
    print("Output: Comprehensive comparative analysis with:")
    print("  - Sequential bridge detection")
    print("  - Ring structure mapping")
    print("  - Balaghah frequency comparison")
    print("  - Thematic parallels")
    print("  - Chronological context and maturation")
    print()

    # Load comprehensive data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    comprehensive_path = os.path.join(project_root, 'data', 'quran_comprehensive.json')

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

    # Load metadata
    try:
        metadata_loader = MetadataLoader()
        print()
    except Exception as e:
        print(f"ERROR loading metadata: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("Enter chapter pair (e.g., 68:69): ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            # Parse input
            if not user_input:
                continue

            match = re.match(r'(\d+):(\d+)', user_input)
            if not match:
                print("Invalid format. Use: chapter1:chapter2 (e.g., 68:69)")
                continue

            chapter1 = int(match.group(1))
            chapter2 = int(match.group(2))

            # Validate chapter numbers
            if chapter1 < 1 or chapter1 > 114 or chapter2 < 1 or chapter2 > 114:
                print("Chapter numbers must be between 1 and 114")
                continue

            print()
            print(f"Analyzing Chapters {chapter1} and {chapter2}...")
            print()

            # Extract comparative data
            result = extract_two_chapter_info_comparative(
                chapter1,
                chapter2,
                comprehensive_data,
                metadata_loader
            )

            # Save to file
            output_filename = f"chapters_{chapter1}_{chapter2}_comparative.json"

            json_output = json.dumps(result, ensure_ascii=False, indent=2)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(json_output)

            # Print summary
            print("-" * 70)
            print(f"[OK] Comparative analysis complete for Chapters {chapter1} and {chapter2}")
            print(f"[OK] Output saved to: {output_filename}")
            print()

            # Display summary
            print("Summary:")
            print(f"  Chapter {chapter1}: {result['chapter1']['metadata']['name_arabic']}")
            print(f"  Chapter {chapter2}: {result['chapter2']['metadata']['name_arabic']}")

            if 'temporal_span' in result:
                temp = result['temporal_span']
                print(f"  Revelation order: #{temp['revelation_order_1']} → #{temp['revelation_order_2']}")
                print(f"  Revelations between: {temp['revelations_between']}")
                print(f"  Periods: {temp['period_1']} → {temp['period_2']}")

            comp = result['comparative_analysis']

            if 'sequential_bridge' in comp:
                bridge = comp['sequential_bridge']
                print(f"  Sequential bridge: {bridge['connection_type']}")

            if 'ring_structures' in comp:
                rings = comp['ring_structures']
                if 'chapter1_internal_ring' in rings:
                    print(f"  Chapter {chapter1}: Internal ring detected")
                if 'chapter2_internal_ring' in rings:
                    print(f"  Chapter {chapter2}: Internal ring detected")
                if 'paired_ring' in rings:
                    print(f"  Paired ring structure detected across chapters")

            if 'thematic_parallels' in comp:
                parallels = comp['thematic_parallels']
                if 'shared_roots' in parallels:
                    print(f"  Shared roots: {len(parallels['shared_roots'])}")

            print()
            print(f"Full comparative analysis available in: {output_filename}")
            print("-" * 70)
            print()

        except EOFError:
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
