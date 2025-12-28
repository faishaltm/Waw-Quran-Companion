# Quran Reading System - Deployment

Sistem pembacaan Al-Quran ayat per ayat dengan analisis mendalam menggunakan AI (OpenAI GPT-4o).

## Fitur Utama

- **Chapter-level Context**: Sistem "membaca" seluruh surah untuk memahami konteks keseluruhan
- **Verse-by-verse Analysis**: Penjelasan detail setiap ayat dalam Bahasa Indonesia
- **Intelligent Caching**: Hasil analisis disimpan untuk efisiensi biaya
- **Memory Management**: Otomatis handle context window dengan smart compression
- **Balaghah Analysis**: Analisis retorika Al-Quran menggunakan guide v4
- **Multiple Tafsir**: Akses ke 3 sumber tafsir (Al-Kashshaf, Ma'arif, Ibn Kathir)

## Arsitektur

```
User Input: "68:1-10"
    ↓
1. Chapter Context (cached setelah pertama kali)
   - Short surah (<50 ayat): Full load
   - Long surah (>50 ayat): Tool-based retrieval
    ↓
2. Verse-by-verse Analysis
   - First verse: Include balaghah guide
   - Continue: Reuse guide dari memory
   - Reset: Re-inject guide jika context penuh
    ↓
3. Cache & Return
   - JSON cache per chapter/verse
   - Session tracking dengan SQLite-like JSON files
```

## Setup

### 1. Install Dependencies

```bash
cd scripts/deployment
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` dan isi OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Verify Data Files

Pastikan file-file berikut ada di project root:

```
D:\Script\Project\quran\
├── data/
│   ├── quran_comprehensive.json
│   └── metadata/
│       ├── tafsir_*.json
│       └── ...
├── scripts/
│   ├── loaders/
│   │   └── metadata_loader.py
│   └── deployment/   # This directory
└── docs/
    └── skills/
        └── balaghah_quick_reference_v4_expanded.md
```

## Running the API

### Option 1: FastAPI Server

```bash
cd scripts/deployment/api
python -m uvicorn main:app --reload --port 8000
```

API akan tersedia di: `http://localhost:8000`

Dokumentasi interaktif: `http://localhost:8000/docs`

### Option 2: Telegram Bot (Coming Soon)

```bash
cd scripts/deployment
python telegram_bot.py
```

## API Usage

### 1. Start Reading Session

```bash
POST http://localhost:8000/start

Body:
{
  "verse_range": "68:1-10",
  "user_id": "optional_user_id"
}

Response:
{
  "session_id": "abc-123-def-456",
  "surah": 68,
  "surah_name": "Al-Qalam",
  "verse_range": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "total_verses": 10,
  "chapter_context": {
    "main_themes": [...],
    "structure": {...},
    "narrative_flow": "..."
  },
  "message": "Chapter context ready. Use /sessions/{session_id}/continue to read first verse."
}
```

### 2. Continue to Next Verse

```bash
POST http://localhost:8000/sessions/{session_id}/continue

Response:
{
  "session_id": "abc-123-def-456",
  "verse": 1,
  "surah": 68,
  "analysis": "=== AYAT 1 ===\n\nنٓۚ وَٱلْقَلَمِ وَمَا يَسْطُرُونَ\n\nNun. By the pen and what they write...",
  "from_cache": false,
  "tokens_used": 1523,
  "mode": "first_verse",
  "progress": {
    "verses_analyzed": 1,
    "total_verses": 10,
    "progress_percentage": 10.0,
    "complete": false
  },
  "next_action": "/sessions/{session_id}/continue"
}
```

### 3. Get Progress

```bash
GET http://localhost:8000/sessions/{session_id}/progress

Response:
{
  "session_id": "abc-123-def-456",
  "verses_analyzed": 3,
  "total_verses": 10,
  "progress_percentage": 30.0,
  "total_tokens_used": 4521,
  "context_resets": 0,
  "complete": false,
  "next_verse": 4
}
```

### 4. Cache Statistics

```bash
GET http://localhost:8000/cache/stats

Response:
{
  "chapters_cached": 5,
  "verses_cached": 127,
  "active_sessions": 3
}
```

## File Structure

```
scripts/deployment/
├── api/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app
│   ├── cache_manager.py             # JSON cache handling
│   ├── session_manager.py           # Session tracking
│   ├── chapter_context_generator.py # Chapter-level analysis
│   ├── verse_analyzer.py            # Verse-level analysis
│   ├── data_loader.py               # Wrapper for existing loaders
│   └── models.py                    # Pydantic models
│
├── cache/                           # Cache storage (gitignore)
│   ├── chapters/
│   │   └── chapter_68_context.json
│   ├── verses/
│   │   └── verse_68_1_analysis.json
│   └── sessions/
│       └── session_abc123.json
│
├── prompts/
│   ├── chapter_context_short.txt    # Short surah prompt
│   ├── chapter_context_long.txt     # Long surah prompt
│   ├── verse_analysis_initial.txt   # First verse
│   ├── verse_analysis_continue.txt  # Continuation
│   └── verse_analysis_reset.txt     # Context reset
│
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuration
│
├── requirements.txt
├── .env.example
└── README.md                        # This file
```

## Cache Strategy

### Chapter Context
- **Cached**: Forever (rarely changes)
- **File**: `cache/chapters/chapter_{N}_context.json`
- **Cost**: One-time generation per surah
  - Short surah: ~$0.025
  - Long surah: ~$0.030

### Verse Analysis
- **Cached**: Forever (per verse)
- **File**: `cache/verses/verse_{surah}_{verse}_analysis.json`
- **Cost**: Only first time
  - First verse (with guide): ~$0.05
  - Continue (no guide): ~$0.0125
  - Reset: ~$0.05

### Sessions
- **Cached**: 7 days (auto-cleanup)
- **File**: `cache/sessions/session_{uuid}.json`
- **Tracks**: Progress, tokens, conversation state

## Memory Management

### Context Window Tracking

System otomatis monitor token usage:

1. **First Verse** (0 tokens used)
   - Include balaghah guide (~15K tokens)
   - Total: ~20K tokens

2. **Continuation** (< 100K tokens)
   - Reuse guide dari conversation memory
   - Total: ~5K tokens per verse

3. **Context Reset** (> 100K tokens)
   - Fresh conversation
   - Re-inject balaghah guide
   - Send summary ayat sebelumnya (reference only)
   - Total: ~20K tokens

### Example Session (Al-Baqarah 150-160, 11 verses)

```
Verse 1:  20K tokens (first + guide)
Verse 2:   5K tokens (continue)
Verse 3:   5K tokens (continue)
...
Verse 10:  5K tokens (continue)
Verse 11:  5K tokens (continue)
---
Total: 70K tokens (no reset needed)
Cost: $0.20 first time, $0 after cached
```

## Cost Estimation

### GPT-4o Pricing
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens

### Example Costs

**Single Session (10 verses, not cached)**:
- Chapter context: $0.03
- First verse: $0.05
- 9 verses continue: $0.11
- **Total: $0.19**

**Same Session (cached)**:
- **Total: $0.00** (all from cache)

**Monthly (100 unique sessions)**:
- ~$20

**Monthly (1000 unique sessions)**:
- ~$200

## Configuration

Edit `config/settings.py` untuk customize:

```python
# Context window threshold (tokens before reset)
CONTEXT_WINDOW_THRESHOLD = 100000

# Short surah threshold (verses)
SHORT_SURAH_THRESHOLD = 50

# Recent verses in memory
RECENT_VERSES_MEMORY = 3

# OpenAI model
OPENAI_MODEL = "gpt-4o"  # or "gpt-4-turbo"
OPENAI_TEMPERATURE = 0.7
```

## Testing

### Test Components Individually

```bash
# Test cache manager
cd api
python cache_manager.py

# Test session manager
python session_manager.py

# Test data loader
python data_loader.py

# Test chapter generator (requires OpenAI key)
python chapter_context_generator.py

# Test verse analyzer (requires OpenAI key)
python verse_analyzer.py
```

### Test Full API

```bash
# Start server
uvicorn main:app --reload

# In another terminal, test with curl
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"verse_range": "68:1-5"}'

# Copy session_id from response, then:
curl -X POST http://localhost:8000/sessions/{session_id}/continue
```

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable not set"

Solution:
```bash
export OPENAI_API_KEY=sk-your-key-here
# Or set in .env file
```

### Error: "Chapter context for surah X not found"

Solution: Chapter context harus di-generate dulu melalui `/start` endpoint.

### Error: "Data directory not found"

Solution: Pastikan running dari `scripts/deployment/` dan struktur project benar.

### Cache Not Working

Clear cache dan regenerate:
```bash
curl -X DELETE http://localhost:8000/cache/clear?cache_type=all
```

## Roadmap

- [x] Core API dengan FastAPI
- [x] Intelligent caching
- [x] Memory management
- [x] Chapter context generation
- [x] Verse-by-verse analysis
- [ ] Telegram bot interface
- [ ] Cost tracking dashboard
- [ ] Multi-user support
- [ ] Rate limiting
- [ ] Admin panel

## License

Menggunakan data dari:
- Quranic Arabic Corpus (http://corpus.quran.com)
- Tanzil Quran Text (http://tanzil.net)
- OpenITI (https://github.com/OpenITI)
- spa5k/tafsir_api (GitHub)

See `docs/DATA_SOURCES.md` untuk attribution lengkap.

## Contact

For issues or questions, refer to main project documentation.
