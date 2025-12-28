"""
Configuration settings for deployment
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ===== Load .env file =====
# Load from deployment directory
ENV_PATH = Path(__file__).parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"Loaded .env from: {ENV_PATH}")
else:
    print(f"Warning: .env file not found at {ENV_PATH}")

# ===== Paths =====
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
PROMPTS_DIR = BASE_DIR / "prompts"

# Project root (where data/ and scripts/ are located)
PROJECT_ROOT = BASE_DIR.parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# ===== OpenAI Settings =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-5.1"  # GPT-5.1: 400K context, 128K output
OPENAI_TEMPERATURE = 0.7

# ===== Context Window Management =====
CONTEXT_WINDOW_THRESHOLD = 400000  # GPT-5.1 context window
SHORT_SURAH_THRESHOLD = 300  # verses - use full load for ALL surahs (max is 286 for Al-Baqarah)

# ===== Session-Based Ruku Management =====
SESSION_BOUNDARY = "ruku"  # "ruku" for traditional 556 divisions
MAX_ACCUMULATED_SUMMARY_TOKENS = 5000  # Limit accumulated summary size

# ===== Memory Settings =====
RECENT_VERSES_MEMORY = 3  # Keep last N verses in detailed memory

# ===== Cache Settings =====
CACHE_ENABLED = True
SESSION_CLEANUP_DAYS = 7  # Delete sessions older than N days

# ===== Telegram Bot Settings (if using) =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USERS = os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",")

# ===== Cost Tracking =====
ENABLE_COST_TRACKING = True
COST_PER_1K_INPUT_TOKENS = 0.0025  # GPT-4o: $2.50 per 1M tokens
COST_PER_1K_OUTPUT_TOKENS = 0.0100  # GPT-4o: $10.00 per 1M tokens


def load_prompt(prompt_name: str) -> str:
    """
    Load prompt template from prompts directory

    Args:
        prompt_name: Name of prompt file (e.g., "chapter_context_short.txt")

    Returns:
        Prompt text
    """
    prompt_path = PROMPTS_DIR / prompt_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_balaghah_guide_path() -> Path:
    """Get path to balaghah guide v4"""
    return PROJECT_ROOT / "docs" / "skills" / "balaghah_quick_reference_v4_expanded.md"


def validate_config() -> bool:
    """
    Validate that all required config is present

    Returns:
        True if valid

    Raises:
        ValueError: If config is invalid
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    if not DATA_DIR.exists():
        raise ValueError(f"Data directory not found: {DATA_DIR}")

    if not get_balaghah_guide_path().exists():
        raise ValueError(f"Balaghah guide not found: {get_balaghah_guide_path()}")

    return True


if __name__ == "__main__":
    # Test config
    print("Configuration:")
    print(f"  BASE_DIR: {BASE_DIR}")
    print(f"  PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"  DATA_DIR: {DATA_DIR}")
    print(f"  CACHE_DIR: {CACHE_DIR}")
    print(f"  OpenAI Model: {OPENAI_MODEL}")
    print(f"  Context Threshold: {CONTEXT_WINDOW_THRESHOLD}")

    try:
        validate_config()
        print("\nConfiguration is valid!")
    except ValueError as e:
        print(f"\nConfiguration error: {e}")

    # Test load prompt
    try:
        prompt = load_prompt("chapter_context_short.txt")
        print(f"\nLoaded prompt (first 100 chars): {prompt[:100]}...")
    except Exception as e:
        print(f"\nError loading prompt: {e}")
