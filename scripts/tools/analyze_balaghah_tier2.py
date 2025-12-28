#!/usr/bin/env python3
"""
Quranic Balaghah Analysis - Tier 2
Analyzes Ilm al-Ma'ani (Contextual Appropriateness) devices:
1. Iltifat - Grammatical shifts (person/number/tense)
2. Sentence Types - Khabar vs Insha' classification
3. Verb Forms - Distribution of VF:1 to VF:10
4. Definiteness - DEF vs INDEF patterns

Output: data/linguistic/balaghah_tier2.json
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

# Add parent directories to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')


class MaaniAnalyzer:
    """Analyzes Ilm al-Ma'ani (Contextual Appropriateness) devices"""

    def __init__(self, morphology_data):
        """
        Initialize with morphology data

        Args:
            morphology_data: List of morphology entries with location, features
        """
        self.morphology_data = morphology_data

        # Build lookup index: (chapter, verse) -> [words]
        self.verse_index = {}
        for entry in morphology_data:
            loc = entry['location']
            key = (loc['chapter'], loc['verse'])
            if key not in self.verse_index:
                self.verse_index[key] = []
            self.verse_index[key].append(entry)

    def analyze_verse(self, chapter_num, verse_num, verse_text):
        """
        Analyze Ma'ani devices in a verse

        Returns:
            Dict with sentence_type, definiteness, verb_forms
        """
        verse_words = self.verse_index.get((chapter_num, verse_num), [])

        if not verse_words:
            return {
                'sentence_type': None,
                'definiteness': None,
                'verb_forms': None
            }

        # Sentence type classification
        sentence_type = self._classify_sentence_type(verse_words)

        # Definiteness pattern
        definiteness = self._analyze_definiteness(verse_words)

        # Verb forms
        verb_forms = self._analyze_verb_forms(verse_words)

        return {
            'sentence_type': sentence_type,
            'definiteness': definiteness,
            'verb_forms': verb_forms
        }

    def _classify_sentence_type(self, verse_words):
        """
        Classify sentence type: Khabar (informative) vs Insha' (performative)

        Binary classification:
        - Insha': Has specific markers (imperative, question, prohibition, wish, vocative)
        - Khabar: Everything else (no insha' markers)

        Subtypes:
        - Khabar: verbal, nominal, oath, particle-initial
        - Insha': command, prohibition, question, wish, vocative
        """
        if not verse_words:
            return None

        # STEP 1: Scan ENTIRE sentence for Insha' markers (not just first word)
        for word in verse_words:
            pos = word['morphology']['pos']
            features = word['morphology'].get('features', {})
            surface = word.get('surface_tanzil', '')

            # Imperative verb → Insha' (command)
            if features.get('tense') == 'IMPV':
                return {
                    'type': 'insha',
                    'subtype': 'command',
                    'description': 'Command (imperative verb)'
                }

            # Question particles → Insha' (interrogative)
            if surface in ['أَ', 'هَلْ', 'مَا', 'مَن', 'مَنْ', 'أَيْنَ', 'كَيْفَ', 'مَتَى', 'أَيَّانَ', 'أَنَّى', 'كَمْ']:
                return {
                    'type': 'insha',
                    'subtype': 'question',
                    'description': 'Question (interrogative particle)'
                }

            # Prohibition particle لا → Insha' (prohibition)
            if surface in ['لَا', 'لا'] and pos == 'P':
                # Check if followed by verb to confirm prohibition
                word_idx = verse_words.index(word)
                if word_idx + 1 < len(verse_words):
                    next_word = verse_words[word_idx + 1]
                    if next_word['morphology']['pos'] == 'V':
                        return {
                            'type': 'insha',
                            'subtype': 'prohibition',
                            'description': 'Prohibition (لا + verb)'
                        }

            # Wish particles → Insha' (wish)
            if surface in ['لَيْتَ', 'لَعَلَّ', 'لَوْ']:
                return {
                    'type': 'insha',
                    'subtype': 'wish',
                    'description': 'Wish/hope particle'
                }

            # Vocative particles → Insha' (call)
            if surface in ['يَا', 'أَيُّهَا', 'أَيَّتُهَا']:
                return {
                    'type': 'insha',
                    'subtype': 'vocative',
                    'description': 'Vocative (calling)'
                }

        # STEP 2: No Insha' markers found → Khabar (by definition)
        # Determine khabar subtype based on structure

        first_word = verse_words[0]
        first_pos = first_word['morphology']['pos']
        first_surface = first_word.get('surface_tanzil', '')

        # Check for disconnected letters (الحروف المقطعة) - special case
        # These are often followed by oath structures
        disconnected_letters = ['نٓ', 'ص', 'حمٓ', 'طسمٓ', 'طس', 'يسٓ', 'طه', 'ق', 'الٓمٓ', 'الٓمٓصٓ', 'الٓرٓ', 'الٓمٓرٓ', 'كٓهٓيٓعٓصٓ']
        if first_surface in disconnected_letters:
            # Check if second word starts with oath particle
            if len(verse_words) > 1:
                second_surface = verse_words[1].get('surface_tanzil', '')
                # Check if second word starts with وَ/بِ/تَ (oath particles)
                if second_surface and second_surface[0] in ['و', 'ب', 'ت']:
                    return {
                        'type': 'khabar',
                        'subtype': 'oath',
                        'description': f'Oath with disconnected letter ({first_surface})'
                    }
            return {
                'type': 'khabar',
                'subtype': 'disconnected-letter',
                'description': f'Starts with disconnected letter ({first_surface})'
            }

        # Check for oath particles (و/ب/ت of qasam) at start of verse
        if first_surface in ['وَ', 'و', 'بِ', 'ب', 'تَ', 'ت'] and first_pos == 'P':
            # Check if this is oath context (followed by noun typically)
            if len(verse_words) > 1 and verse_words[1]['morphology']['pos'] in ['N', 'P']:
                return {
                    'type': 'khabar',
                    'subtype': 'oath',
                    'description': 'Oath sentence (qasam particle)'
                }

        # Also check if first word starts with oath particle (وَالقلم، بالكتاب، etc.)
        if first_surface and first_surface[0] in ['و', 'ب', 'ت']:
            # Check if followed by noun (typical oath structure)
            # In Arabic, oath is typically: particle + definite noun (ال)
            if len(first_surface) > 1 and (first_surface[1:3] == 'ال' or first_pos == 'P'):
                return {
                    'type': 'khabar',
                    'subtype': 'oath',
                    'description': 'Oath sentence (qasam particle)'
                }

        # Verbal sentence (starts with verb)
        if first_pos == 'V':
            return {
                'type': 'khabar',
                'subtype': 'verbal',
                'description': 'Verbal sentence (starts with verb)'
            }

        # Nominal sentence (starts with noun)
        elif first_pos == 'N':
            return {
                'type': 'khabar',
                'subtype': 'nominal',
                'description': 'Nominal sentence (starts with noun)'
            }

        # Particle-initial (starts with particle, but not oath)
        elif first_pos == 'P':
            return {
                'type': 'khabar',
                'subtype': 'particle-initial',
                'description': f'Starts with particle ({first_surface})'
            }

        # Fallback (shouldn't happen, but default to nominal)
        return {
            'type': 'khabar',
            'subtype': 'nominal',
            'description': 'Informative sentence'
        }

    def _analyze_definiteness(self, verse_words):
        """
        Analyze definiteness patterns (ال vs تنوين)

        Returns:
            Dict with pattern and statistics
        """
        pattern = []
        def_count = 0
        indef_count = 0

        for word in verse_words:
            if word['morphology']['pos'] == 'N':
                features = word['morphology'].get('features', {})
                def_status = features.get('definiteness')

                if def_status == 'DEF':
                    pattern.append('DEF')
                    def_count += 1
                elif def_status == 'INDEF':
                    pattern.append('INDEF')
                    indef_count += 1

        if not pattern:
            return None

        return {
            'pattern': pattern,
            'definite_count': def_count,
            'indefinite_count': indef_count,
            'total_nouns': len(pattern)
        }

    def _analyze_verb_forms(self, verse_words):
        """
        Analyze distribution of Arabic verb forms (VF:1 to VF:10)

        Returns:
            Dict with form counts and predominant form
        """
        form_counts = Counter()

        for word in verse_words:
            if word['morphology']['pos'] == 'V':
                features = word['morphology'].get('features', {})
                verb_form = features.get('verb_form')

                if verb_form:
                    form_counts[f'VF:{verb_form}'] += 1

        if not form_counts:
            return None

        predominant = form_counts.most_common(1)[0] if form_counts else None

        return {
            'distribution': dict(form_counts),
            'predominant_form': predominant[0] if predominant else None,
            'predominant_count': predominant[1] if predominant else 0,
            'total_verbs': sum(form_counts.values())
        }

    def detect_iltifat_sequences(self, chapter_verses):
        """
        Detect Iltifat (grammatical shifts) across consecutive verses

        Detects:
        - Person shifts (3rd → 2nd → 1st)
        - Number shifts (S → D → P)
        - Tense shifts (PERF → IMPF)

        Returns:
            List of shift instances
        """
        shifts = []

        for i in range(len(chapter_verses) - 1):
            curr_verse = chapter_verses[i]
            next_verse = chapter_verses[i + 1]

            curr_num = curr_verse['number']
            next_num = next_verse['number']

            # Get verse morphology
            curr_words = self.verse_index.get((curr_verse['chapter'], curr_num), [])
            next_words = self.verse_index.get((next_verse['chapter'], next_num), [])

            if not curr_words or not next_words:
                continue

            # Get predominant person
            curr_person = self._get_predominant_person(curr_words)
            next_person = self._get_predominant_person(next_words)

            # Get predominant number
            curr_number = self._get_predominant_number(curr_words)
            next_number = self._get_predominant_number(next_words)

            # Get predominant tense
            curr_tense = self._get_predominant_tense(curr_words)
            next_tense = self._get_predominant_tense(next_words)

            # Detect shifts
            if curr_person and next_person and curr_person != next_person:
                shifts.append({
                    'type': 'person',
                    'from_verse': curr_num,
                    'to_verse': next_num,
                    'from_value': curr_person,
                    'to_value': next_person,
                    'effect': self._describe_person_shift(curr_person, next_person)
                })

            if curr_number and next_number and curr_number != next_number:
                shifts.append({
                    'type': 'number',
                    'from_verse': curr_num,
                    'to_verse': next_num,
                    'from_value': curr_number,
                    'to_value': next_number,
                    'effect': 'Shift in grammatical number'
                })

            if curr_tense and next_tense and curr_tense != next_tense:
                shifts.append({
                    'type': 'tense',
                    'from_verse': curr_num,
                    'to_verse': next_num,
                    'from_value': curr_tense,
                    'to_value': next_tense,
                    'effect': 'Shift in verb tense/aspect'
                })

        return shifts

    def _get_predominant_person(self, verse_words):
        """Extract predominant person (1, 2, 3) from verse"""
        persons = []
        for word in verse_words:
            features = word['morphology'].get('features', {})
            person = features.get('person')
            if person:
                persons.append(person)

        if not persons:
            return None

        return Counter(persons).most_common(1)[0][0]

    def _get_predominant_number(self, verse_words):
        """Extract predominant number (S, D, P) from verse"""
        numbers = []
        for word in verse_words:
            features = word['morphology'].get('features', {})
            number = features.get('number')
            if number:
                numbers.append(number)

        if not numbers:
            return None

        return Counter(numbers).most_common(1)[0][0]

    def _get_predominant_tense(self, verse_words):
        """Extract predominant tense (PERF, IMPF, IMPV) from verse"""
        tenses = []
        for word in verse_words:
            if word['morphology']['pos'] == 'V':
                features = word['morphology'].get('features', {})
                tense = features.get('tense')
                if tense:
                    tenses.append(tense)

        if not tenses:
            return None

        return Counter(tenses).most_common(1)[0][0]

    def _describe_person_shift(self, from_person, to_person):
        """Describe rhetorical effect of person shift"""
        shift_map = {
            ('3', '2'): 'Shift from third to second person (addressing directly)',
            ('2', '3'): 'Shift from second to third person (distancing)',
            ('3', '1'): 'Shift from third to first person (personalizing)',
            ('1', '3'): 'Shift from first to third person (objectifying)',
            ('1', '2'): 'Shift from first to second person (engaging)',
            ('2', '1'): 'Shift from second to first person (personalizing)'
        }
        return shift_map.get((from_person, to_person), 'Person shift')


def load_quran_text(filepath):
    """Load Quran text JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def load_morphology_data(filepath):
    """
    Load morphology data from JSON and flatten to list of entries

    Handles morphology_aligned.json (hierarchical structure)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    morphology = data['morphology']

    # Flatten hierarchical structure
    if morphology and isinstance(morphology[0], dict) and 'verses' in morphology[0]:
        flat_list = []
        for chapter in morphology:
            for verse in chapter['verses']:
                for word in verse['words']:
                    flat_list.append(word)
        return flat_list
    else:
        return morphology


def analyze_full_quran():
    """Main function to analyze entire Quran"""
    print("=" * 70)
    print("QURANIC BALAGHAH ANALYSIS - TIER 2")
    print("Devices: Ma'ani (Iltifat, Sentence Types, Verb Forms, Definiteness)")
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

    # Initialize analyzer
    print("Initializing Ma'ani Analyzer...")
    maani_analyzer = MaaniAnalyzer(morphology)
    print("  [OK]")
    print()

    # Process all chapters
    print("Processing Quran (114 chapters, 6,236 verses)...")
    print()

    results = {
        'metadata': {
            'source': 'Quranic Balaghah Analysis - Tier 2',
            'version': '1.0',
            'tier': 2,
            'devices': ['maani_sentence_types', 'maani_iltifat', 'maani_verb_forms', 'maani_definiteness'],
            'total_chapters': len(quran_data['chapters']),
            'total_verses': quran_data['metadata']['verses_count'],
            'analysis_date': datetime.now().isoformat()
        },
        'chapters': []
    }

    total_verses_processed = 0
    total_iltifat = 0

    for chapter in quran_data['chapters']:
        chapter_num = chapter['number']
        chapter_name = chapter.get('name', f'Chapter {chapter_num}')
        verses = chapter['verses']

        print(f"  Chapter {chapter_num:3d}: ({len(verses)} verses)...", end=' ', flush=True)

        # Analyze each verse
        chapter_verses_analysis = []

        for verse in verses:
            verse_num = verse['number']
            verse_text = verse['text']

            # Analyze verse-level Ma'ani
            verse_analysis = maani_analyzer.analyze_verse(chapter_num, verse_num, verse_text)

            chapter_verses_analysis.append({
                'verse_number': verse_num,
                'text': verse_text,
                'maani': verse_analysis
            })

            total_verses_processed += 1

        # Detect Iltifat sequences for chapter
        chapter_verses_with_chapter = [{'chapter': chapter_num, 'number': v['number']} for v in verses]
        iltifat_shifts = maani_analyzer.detect_iltifat_sequences(chapter_verses_with_chapter)
        total_iltifat += len(iltifat_shifts)

        # Build chapter summary
        sentence_types = Counter()
        verb_form_counts = Counter()
        total_def_count = 0
        total_indef_count = 0

        for v_analysis in chapter_verses_analysis:
            maani = v_analysis['maani']

            # Sentence types
            if maani['sentence_type']:
                st = maani['sentence_type']
                key = f"{st['type']}_{st['subtype']}"
                sentence_types[key] += 1

            # Verb forms
            if maani['verb_forms']:
                vf = maani['verb_forms']
                for form, count in vf['distribution'].items():
                    verb_form_counts[form] += count

            # Definiteness
            if maani['definiteness']:
                total_def_count += maani['definiteness']['definite_count']
                total_indef_count += maani['definiteness']['indefinite_count']

        chapter_result = {
            'chapter': chapter_num,
            'name_arabic': chapter_name,
            'verses_count': len(verses),
            'maani_summary': {
                'sentence_types': dict(sentence_types),
                'verb_forms': dict(verb_form_counts),
                'definiteness': {
                    'total_definite': total_def_count,
                    'total_indefinite': total_indef_count
                },
                'iltifat_shifts': len(iltifat_shifts)
            },
            'iltifat': iltifat_shifts if iltifat_shifts else [],
            'verses': chapter_verses_analysis
        }

        results['chapters'].append(chapter_result)
        print("[OK]")

    print()
    print(f"Processed {total_verses_processed} verses across 114 chapters")
    print()

    # Save results
    output_path = os.path.join(project_root, 'data', 'linguistic', 'balaghah_tier2.json')
    print(f"Saving results to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)
    print(f"  [OK] Saved {file_size_mb:.2f} MB")
    print()

    # Summary statistics
    print("=" * 70)
    print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Ma'ani Analyses:")
    print(f"  Total Iltifat shifts:     {total_iltifat}")
    print(f"  Chapters with Iltifat:    {sum(1 for c in results['chapters'] if c['maani_summary']['iltifat_shifts'] > 0)} / 114")
    print()
    print(f"Analysis saved to: data/linguistic/balaghah_tier2.json")
    print("=" * 70)


if __name__ == '__main__':
    try:
        analyze_full_quran()
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
