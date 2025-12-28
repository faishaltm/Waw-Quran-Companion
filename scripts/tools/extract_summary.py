#!/usr/bin/env python3
import json

def analyze(filename, output):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ch = data['chapter']
    output.write(f"\n{'='*70}\n")
    output.write(f"CHAPTER {ch} ANALYSIS\n")
    output.write(f"{'='*70}\n\n")

    # Metadata
    meta = data['metadata']
    output.write("METADATA:\n")
    output.write(f"  Name: {meta['name_arabic']} ({meta.get('name_translation', 'N/A')})\n")
    output.write(f"  Revelation: {meta['revelation_place']}, order: {meta['revelation_order']}\n")
    output.write(f"  Verses: {meta['verses_count']}\n")
    if 'mixed_revelation' in meta:
        output.write(f"  Mixed: {meta['mixed_revelation']}\n")

    output.write("\n  Section Headings:\n")
    for verses, heading in meta['section_headings'].items():
        output.write(f"    {verses}: {heading}\n")

    # Count patterns
    saj_patterns = {}
    iltifat_count = 0
    hadhf_count = 0
    muqabala_count = 0
    qasam_count = 0
    tibaq_count = 0
    root_freq = {}

    for v in data['verses']:
        analysis = v.get('analysis', '')

        if "saj' (rhymed prose)" in analysis:
            # Extract pattern
            idx = analysis.find("pattern '")
            if idx != -1:
                idx += 9
                end = analysis.find("'", idx)
                pattern = analysis[idx:end] if end != -1 else "?"
                saj_patterns[pattern] = saj_patterns.get(pattern, 0) + 1

        if 'iltifat' in analysis:
            iltifat_count += 1
        if 'hadhf' in analysis:
            hadhf_count += 1
        if 'muqabala' in analysis:
            muqabala_count += 1
        if 'qasam' in analysis or 'oath' in analysis.lower():
            qasam_count += 1
        if 'tibaq' in analysis or 'antithesis' in analysis:
            tibaq_count += 1

        # Count roots
        for root in v.get('root_repetitions', {}).keys():
            root_freq[root] = root_freq.get(root, 0) + 1

    output.write("\n\nBALAGHAH PATTERNS:\n")
    output.write(f"\n  Saj' patterns:\n")
    for pattern, count in sorted(saj_patterns.items(), key=lambda x: -x[1]):
        # Use transliteration
        if pattern == 'ن':
            pattern_name = "nun"
        elif pattern == 'ة':
            pattern_name = "taa marbuta"
        elif pattern == 'م':
            pattern_name = "mim"
        else:
            pattern_name = pattern
        output.write(f"    {pattern_name}: {count} verses\n")

    output.write(f"\n  Iltifat: {iltifat_count} verses\n")
    output.write(f"  Hadhf (ellipsis): {hadhf_count} verses\n")
    output.write(f"  Muqabala (antithesis): {muqabala_count} verses\n")
    output.write(f"  Qasam (oath): {qasam_count} verses\n")
    output.write(f"  Tibaq: {tibaq_count} verses\n")

    output.write(f"\n  Top 15 Recurring Roots:\n")
    sorted_roots = sorted(root_freq.items(), key=lambda x: -x[1])
    for root, count in sorted_roots[:15]:
        output.write(f"    {root}: {count}\n")

# Main
with open('balaghah_summary.txt', 'w', encoding='utf-8') as out:
    analyze('verse_68_1-52_v2.json', out)
    analyze('verse_69_1-52_v2.json', out)

print("Analysis written to balaghah_summary.txt")
