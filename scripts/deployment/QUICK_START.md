# Quick Start Guide - Telegram Bot

## 🚀 5 Menit Setup

### Step 1: Setup Bot Token (2 menit)

1. **Buka Telegram**, cari `@BotFather`
2. Kirim: `/newbot`
3. Ikuti instruksi, dapatkan **token**
4. Edit file `.env`, tambahkan:
   ```
   TELEGRAM_BOT_TOKEN=your-token-here
   ```

### Step 2: Start Servers (1 menit)

**Terminal 1** - Run API Server:
```bash
run_server.bat
```

**Terminal 2** - Run Telegram Bot:
```bash
run_telegram_bot.bat
```

### Step 3: Test Bot (2 menit)

1. Buka Telegram, cari bot Anda
2. Klik **Start**
3. Ketik: `/read 114:1-6`
4. Klik tombol **"Baca Ayat Pertama"**
5. Enjoy! 🎉

---

## 📝 Quick Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Mulai bot | - |
| `/read` | Baca ayat | `/read 68:1-10` |
| `/progress` | Lihat progress | - |
| `/cancel` | Batalkan sesi | - |
| `/help` | Bantuan | - |

---

## 🔍 Troubleshooting

**Bot tidak respon?**
→ Pastikan kedua terminal (API + Bot) masih running

**"Cannot connect to API"?**
→ Start `run_server.bat` dulu, baru `run_telegram_bot.bat`

**Timeout?**
→ Normal untuk chapter panjang, tunggu ~30 detik

---

## 📚 Dokumentasi Lengkap

- Setup detail: `TELEGRAM_SETUP.md`
- API docs: `README.md`
- Architecture: `IMPLEMENTATION_SUMMARY.md`

---

Selamat membaca Al-Quran! 📖✨
