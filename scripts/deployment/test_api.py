"""
Simple test script for the API
Tests core functionality without needing Postman
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section separator"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_start_session():
    """Test starting a reading session"""
    print_section("Testing Start Session")

    data = {
        "verse_range": "68:1-5",
        "user_id": "test_user"
    }

    print(f"Request: POST /start")
    print(f"Body: {json.dumps(data, indent=2)}")

    response = requests.post(f"{BASE_URL}/start", json=data)

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nSession ID: {result['session_id']}")
        print(f"Surah: {result['surah']} - {result['surah_name']}")
        print(f"Verse Range: {result['verse_range']}")
        print(f"Total Verses: {result['total_verses']}")

        # Print chapter context summary
        chapter_ctx = result.get('chapter_context', {})
        print(f"\nChapter Context:")
        print(f"  Main Themes: {chapter_ctx.get('main_themes', [])}")
        print(f"  Generation Method: {chapter_ctx.get('_generation_method', 'N/A')}")
        print(f"  Tokens Used: {chapter_ctx.get('_tokens_used', 'N/A')}")

        return result['session_id']
    else:
        print(f"Error: {response.text}")
        return None


def test_continue_verse(session_id, verse_num=1):
    """Test continuing to next verse"""
    print_section(f"Testing Continue Verse #{verse_num}")

    print(f"Request: POST /sessions/{session_id}/continue")

    response = requests.post(f"{BASE_URL}/sessions/{session_id}/continue")

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nVerse: {result['verse']}")
        print(f"From Cache: {result['from_cache']}")
        print(f"Tokens Used: {result['tokens_used']}")
        print(f"Mode: {result['mode']}")

        # Print analysis (first 300 chars)
        analysis = result.get('analysis', '')
        print(f"\nAnalysis (preview):")
        print(analysis[:300] + "..." if len(analysis) > 300 else analysis)

        # Print progress
        progress = result.get('progress', {})
        print(f"\nProgress:")
        print(f"  Verses Analyzed: {progress.get('verses_analyzed')}/{progress.get('total_verses')}")
        print(f"  Progress: {progress.get('progress_percentage')}%")
        print(f"  Total Tokens: {progress.get('total_tokens_used')}")
        print(f"  Complete: {progress.get('complete')}")

        return not result.get('complete', False)
    else:
        print(f"Error: {response.text}")
        return False


def test_get_progress(session_id):
    """Test getting session progress"""
    print_section("Testing Get Progress")

    response = requests.get(f"{BASE_URL}/sessions/{session_id}/progress")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nProgress: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_cache_stats():
    """Test cache statistics"""
    print_section("Testing Cache Stats")

    response = requests.get(f"{BASE_URL}/cache/stats")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\nCache Stats: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def run_full_test():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("  QURAN READING API - TEST SUITE")
    print("="*60)

    # 1. Test health
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        print("   Start with: uvicorn api.main:app --reload")
        return

    time.sleep(1)

    # 2. Test start session
    session_id = test_start_session()
    if not session_id:
        print("\n❌ Failed to start session")
        return

    time.sleep(2)

    # 3. Test continue verses (read 3 verses)
    for i in range(1, 4):
        time.sleep(1)
        can_continue = test_continue_verse(session_id, i)
        if not can_continue:
            print("\n✅ Session completed!")
            break

    time.sleep(1)

    # 4. Test progress
    test_get_progress(session_id)

    time.sleep(1)

    # 5. Test cache stats
    test_cache_stats()

    print("\n" + "="*60)
    print("  TEST SUITE COMPLETED")
    print("="*60)


if __name__ == "__main__":
    try:
        run_full_test()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   cd scripts/deployment")
        print("   uvicorn api.main:app --reload")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
