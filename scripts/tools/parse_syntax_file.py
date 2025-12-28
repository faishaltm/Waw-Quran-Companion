#!/usr/bin/env python3
"""
Parse syntax.txt file from Quranic Corpus WAR to extract dependency relationships

Maps relation types to Arabic labels based on corpus documentation:
https://corpus.quran.com/documentation/syntaxrelation.jsp
"""

import re

# Relation type mappings (English -> Arabic)
RELATION_MAP = {
    # Nominal Dependencies
    'adj': ('صفة', 'Adjective'),
    'poss': ('مضاف إليه', 'Possessive'),
    'pred': ('مبتدأ وخبر', 'Predicate'),
    'app': ('بدل', 'Apposition'),
    'spec': ('تمييز', 'Specification'),
    'cpnd': ('مركب', 'Compound'),

    # Verbal Dependencies
    'subj': ('فاعل', 'Subject'),
    'pass': ('نائب فاعل', 'Passive subject'),
    'obj': ('مفعول به', 'Object'),
    'subjx': ('اسم كان', 'Subject of special verb'),
    'predx': ('خبر كان', 'Predicate of special verb'),
    'impv': ('أمر', 'Imperative'),
    'imrs': ('جواب أمر', 'Imperative result'),
    'pro': ('نهي', 'Prohibition'),

    # Phrases and Clauses
    'gen': ('جار ومجرور', 'Prepositional phrase'),
    'link': ('متعلق', 'PP attachment'),
    'conj': ('معطوف', 'Coordinating conjunction'),
    'sub': ('صلة', 'Subordinate clause'),
    'cond': ('شرط', 'Condition'),
    'rslt': ('جواب شرط', 'Result'),

    # Adverbial
    'circ': ('حال', 'Circumstantial'),
    'cog': ('مفعول مطلق', 'Cognate accusative'),
    'prp': ('المفعول لأجله', 'Accusative of purpose'),
    'com': ('المفعول معه', 'Comitative'),

    # Other common ones
    'mod': ('نعت', 'Modifier'),
    'tmz': ('تمييز', 'Specification'),
}

def parse_syntax_file(input_file, output_file, chapters_verses):
    """
    Parse syntax.txt and extract dependencies for specified scope

    Args:
        input_file: Path to syntax.txt
        output_file: Path to output tab-delimited file
        chapters_verses: Dict {chapter: [verses]} for scope filtering
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by verse sections
    verses = re.split(r'-- Verse \((\d+):(\d+)\)', content)[1:]  # Skip first empty

    dependencies = []
    node_map = {}  # Maps node names (n1, n2, etc.) to word locations

    for i in range(0, len(verses), 3):
        chapter = int(verses[i])
        verse = int(verses[i+1])
        verse_content = verses[i+2]

        # Check if in scope (None means all verses)
        if chapters_verses is not None:
            if chapter not in chapters_verses or verse not in chapters_verses[chapter]:
                continue

        if i % 300 == 0:  # Progress indicator for full Quran
            print(f"Parsing verse ({chapter}:{verse})...")

        # Clear node map for each verse
        node_map = {}

        # Parse word assignments
        # Examples:
        # n1 = word(1:1:1)
        # n2, n3 = word(1:1:1)  # Multiple nodes for one word (segments)
        # n1 = V(*)  # Hidden node
        word_pattern = r'(n\d+(?:,\s*n\d+)*)\s*=\s*(?:word|reference)\(([^)]+)\)'
        for match in re.finditer(word_pattern, verse_content):
            nodes = [n.strip() for n in match.group(1).split(',')]
            location = match.group(2)

            for node in nodes:
                node_map[node] = location

        # Parse edges (dependency relationships)
        # Format: relation_type(child - parent)
        # Example: gen(n3 - n2)
        edge_pattern = r'(\w+)\((n\d+)\s*-\s*(n\d+)\)'
        for match in re.finditer(edge_pattern, verse_content):
            relation_type = match.group(1)
            child_node = match.group(2)
            parent_node = match.group(3)

            # Get locations
            child_loc = node_map.get(child_node)
            parent_loc = node_map.get(parent_node)

            if not child_loc or not parent_loc:
                # Skip if nodes are hidden or not mapped
                continue

            # Get Arabic and English labels
            if relation_type in RELATION_MAP:
                arabic_rel, english_rel = RELATION_MAP[relation_type]
            else:
                arabic_rel = relation_type
                english_rel = relation_type

            dependencies.append({
                'child': f"({child_loc})",
                'parent': f"({parent_loc})",
                'relation': relation_type,
                'arabic': arabic_rel,
                'english': english_rel
            })

            print(f"  ({child_loc}) -> ({parent_loc}) | {relation_type}")

    # Write output
    print(f"\nWriting {len(dependencies)} dependencies to {output_file}...")

    # Determine scope description
    if chapters_verses is None:
        scope_desc = "Full Quran (114 chapters, 6236 verses)"
    else:
        scope_desc = "Al-Fatihah (1:1-7) + Al-Baqarah (2:1-10)"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Quranic Arabic Corpus - Dependency Treebank Data\n")
        f.write(f"# Scope: {scope_desc}\n")
        f.write("# Format: CHILD | PARENT | RELATION | ARABIC_LABEL | ENGLISH_LABEL\n")
        f.write("#\n")
        f.write("# Source: Extracted from syntax.txt in quranic-corpus.war\n")
        f.write("# Notation: CHILD -> PARENT (child depends on parent)\n")
        f.write("#\n")
        f.write("CHILD\tPARENT\tRELATION\tARABIC_LABEL\tENGLISH_LABEL\n")

        for dep in dependencies:
            f.write(f"{dep['child']}\t{dep['parent']}\t{dep['relation']}\t{dep['arabic']}\t{dep['english']}\n")

    print(f"Done! Wrote {len(dependencies)} dependencies.")
    return len(dependencies)


if __name__ == "__main__":
    # Full Quran scope - all 114 chapters
    import sys

    # Check if we should do full Quran or limited scope
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("Processing FULL QURAN (all 114 chapters)...")
        chapters_verses = None  # None means process all verses
        output_file = "extracted-war/WEB-INF/classes/com/quran/corpus/quranic-corpus-dependencies-full.txt"
    else:
        # MVP scope (default)
        print("Processing MVP scope (Al-Fatihah + Al-Baqarah 1-10)...")
        chapters_verses = {
            1: list(range(1, 8)),   # Al-Fatihah: verses 1-7
            2: list(range(1, 11))   # Al-Baqarah: verses 1-10
        }
        import os
        output_dir = "quranic-corpus-dependencies-0.4"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "quranic-corpus-dependencies-0.4.txt")

    input_file = "extracted-war/WEB-INF/classes/com/quran/corpus/syntax.txt"
    count = parse_syntax_file(input_file, output_file, chapters_verses)

    print(f"\nSummary:")
    print(f"  Extracted {count} dependency relationships")
    print(f"  Output: {output_file}")
