# Quran Telegram Bot - Deployment Guide

## Directory Structure (Updated)

```
quran/
├── scripts/
│   ├── deployment/
│   │   ├── quran_telegram_bot.py          # Main bot
│   │   ├── .env                            # API keys (create new)
│   │   ├── requirements.txt                # Python deps
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py                 # REQUIRED
│   │   │   ├── cache_manager.py
│   │   │   ├── session_manager.py
│   │   │   ├── conversation_manager.py
│   │   │   ├── chapter_context_generator.py
│   │   │   ├── data_loader.py
│   │   │   └── ruku_session_manager.py     # NEW - ruku-based sessions
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py                 # REQUIRED
│   │   │   └── settings.py
│   │   │
│   │   ├── prompts/
│   │   │   ├── chapter_context_short.txt
│   │   │   ├── chapter_context_long.txt
│   │   │   └── verse_analysis_prompt.txt   # NEW - comprehensive per-verse
│   │   │
│   │   └── cache/                          # Create empty dirs
│   │       ├── chapters/
│   │       ├── verses/
│   │       ├── sessions/
│   │       ├── conversations/
│   │       ├── chats/                      # NEW
│   │       └── summaries/                  # NEW - ruku accumulated
│   │
│   ├── loaders/
│   │   └── metadata_loader.py              # Used by data_loader
│   │
│   └── tools/
│       ├── get_verse_info_v3.py            # Used by data_loader
│       └── balaghah_detectors/             # NEW - required by get_verse_info_v3
│           ├── __init__.py
│           ├── taqdim_detector.py
│           ├── tibaq_detector.py
│           └── tashbih_detector.py
│
├── data/
│   ├── quran_comprehensive.json            # 226 MB - MAIN DATA
│   ├── linguistic/
│   │   └── morphology_segments.json        # 39 MB
│   └── metadata/
│       ├── chapter_metadata.json
│       ├── tafsir_kashshaf_arabic.json
│       ├── tafsir_maarif_en.json
│       ├── tafsir_ibn_kathir_en.json
│       ├── asbab_nuzul_index.json
│       ├── surah_context_qurancom.json
│       ├── revelation_order.json
│       ├── ruku_divisions.json             # 556 traditional divisions
│       ├── clear_quran_sections.json
│       ├── tafsir_index.json               # NEW - required by metadata_loader
│       └── surah_info.json                 # NEW - required by metadata_loader
│
└── docs/
    └── skills/
        └── balaghah_quick_reference_v4_expanded.md  # Balaghah guide
```

## Files NOT Needed for Telegram Bot
These are for FastAPI mode (unused):
- `api/main.py`
- `api/models.py`
- `api/verse_analyzer.py`
- `prompts/verse_analysis_initial.txt`
- `prompts/verse_analysis_continue.txt`
- `prompts/verse_analysis_reset.txt`

## Environment File (.env)

Create in `scripts/deployment/`:
```
OPENAI_API_KEY=sk-your-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_USER=your-telegram-user-id
```

## Requirements (requirements.txt)

```
python-telegram-bot==22.5
python-dotenv
openai
httpx
```

## Step-by-Step Deployment

### 1. Prepare VM
```bash
ssh user@your-vm-ip
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip -y
mkdir -p ~/quran
cd ~/quran
```

### 2. Upload Files
From local machine:
```bash
# Core scripts
rsync -avz --progress \
  --include='quran_telegram_bot.py' \
  --include='requirements.txt' \
  --include='api/***' \
  --include='config/***' \
  --include='prompts/***' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='venv' \
  --exclude='cache' \
  --exclude='*.bat' \
  --exclude='debug_*' \
  --exclude='test_*' \
  --exclude='*.md' \
  D:/Script/Project/quran/scripts/deployment/ user@vm-ip:~/quran/scripts/deployment/

# Loaders & tools
rsync -avz D:/Script/Project/quran/scripts/loaders/metadata_loader.py user@vm-ip:~/quran/scripts/loaders/
rsync -avz D:/Script/Project/quran/scripts/tools/get_verse_info_v3.py user@vm-ip:~/quran/scripts/tools/

# Data files (LARGE)
rsync -avz --progress D:/Script/Project/quran/data/ user@vm-ip:~/quran/data/

# Balaghah guide
rsync -avz D:/Script/Project/quran/docs/skills/balaghah_quick_reference_v4_expanded.md user@vm-ip:~/quran/docs/skills/
```

### 3. Setup Environment
```bash
cd ~/quran/scripts/deployment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create .env
```bash
nano .env
```
Add your keys (see Environment File section above)

### 5. Create Cache Directories
```bash
mkdir -p cache/{chapters,verses,sessions,conversations,chats,summaries}
```

### 6. Test Run
```bash
source venv/bin/activate
python quran_telegram_bot.py
```

### 7. Run as Service (Production)
```bash
sudo nano /etc/systemd/system/quran-bot.service
```

```ini
[Unit]
Description=Quran Analysis Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/quran/scripts/deployment
Environment=PATH=/home/your-username/quran/scripts/deployment/venv/bin
ExecStart=/home/your-username/quran/scripts/deployment/venv/bin/python quran_telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable quran-bot
sudo systemctl start quran-bot
sudo systemctl status quran-bot
journalctl -u quran-bot -f  # View logs
```

## Size Estimate

| Component | Size |
|-----------|------|
| scripts/deployment/* | ~100 KB |
| scripts/loaders/metadata_loader.py | ~15 KB |
| scripts/tools/get_verse_info_v3.py | ~20 KB |
| data/quran_comprehensive.json | 226 MB |
| data/linguistic/morphology_segments.json | 39 MB |
| data/metadata/* (9 files) | ~50 MB |
| docs/skills/balaghah_guide | ~50 KB |
| **TOTAL** | **~315 MB** |
