# Quran Linguistic Analysis Telegram Bot

This is a Python-based Telegram bot that provides detailed linguistic analysis of the Quran.

## 📖 Project Overview

This bot is designed to be an interactive companion for deep Quranic study. It uses a pre-generated comprehensive JSON file (`quran_comprehensive.json`) which aggregates data from multiple sources.

**Key Features:**
* **Morphological Data:** Detailed breakdown of word roots, forms, and grammar.
* **Syntactic Dependencies:** Analysis of sentence structure and grammatical relationships.
* **Named Entities:** Identification of people, places, and significant entities.
* **Balaghah (Rhetorical Analysis):** In-depth look at linguistic eloquence.
* **Contextual Data:** Integration of *Tafsir* (commentary) and *Asbab al-Nuzul* (reasons for revelation).

---

## ⚙️ Building and Running

### Dependencies

The project dependencies are listed in `scripts/deployment/requirements.txt`. Key libraries include:
* `python-telegram-bot`
* `python-dotenv`
* `openai`
* `httpx`

### Setup Instructions

Follow these steps to set up the environment and run the bot:

**1. Install Dependencies**
```bash
pip install -r scripts/deployment/requirements.txt```

**2. Configure Environment**
Create a .env file in the scripts/deployment/ directory with the following content:

```OPENAI_API_KEY=<your-openai-api-key>
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>```

**3. Generate Data The bot relies on a core data file (quran_comprehensive.json).**
Run the generation script to merge raw data from the data/ directory:

```Bash
python scripts/tools/generate_comprehensive_quran.py```

**4. Run the Bot**
Launch the bot using the deployment script:

```Bash
python scripts/deployment/quran_telegram_bot.py```

💻 **Development Conventions**
Project Structure:
- api/: Contains core logic, session management, and conversation handlers.
- tools/: Scripts for data processing and analysis.
- data/: Storage for raw source files and the generated JSON output.

Type Safety: The project uses Python type hints extensively for better code quality and maintainability.
CLI Tools: A command-line interface is used for generating the comprehensive data file.
