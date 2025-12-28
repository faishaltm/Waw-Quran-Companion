"""Quick verification that data_loader uses v3 format"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "api"))

from data_loader import QuranDataLoader
import json

# Load verse data
loader = QuranDataLoader()
data = loader.get_verse_full_data(68, 5)

# Check format
print("=== Verse Data Format Check ===")
print(f"Has 'balaghah' key: {('balaghah' in data)}")
print(f"Has 'words' key: {('words' in data)}")
print(f"Balaghah type: {type(data.get('balaghah')).__name__ if data.get('balaghah') else 'None'}")
print()

# Show balaghah structure
if data.get('balaghah'):
    print("Balaghah keys:")
    print(json.dumps(list(data['balaghah'].keys()), indent=2))
    print()

    # Show one example (saj' if exists)
    if 'saj' in data['balaghah']:
        print("Example - Saj' structure:")
        print(json.dumps(data['balaghah']['saj'], ensure_ascii=False, indent=2))
