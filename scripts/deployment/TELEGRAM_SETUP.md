# Setup Telegram Bot - Panduan Lengkap

## 📱 Langkah 1: Buat Telegram Bot

### 1.1 Buka BotFather
1. Buka Telegram
2. Cari `@BotFather` (akun resmi Telegram)
3. Klik **Start**

### 1.2 Buat Bot Baru
1. Kirim perintah: `/newbot`
2. BotFather akan tanya nama bot:
   ```
   Alright, a new bot. How are we going to call it? Please choose a name for your bot.
   ```
   Ketik nama bot, misalnya: **Quran Reading Assistant**

3. BotFather akan tanya username bot (harus diakhiri dengan 'bot'):
   ```
   Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
   ```
   Ketik username, misalnya: **quran_reading_bot**

4. Jika sukses, BotFather akan kirim pesan berisi **Token**:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/quran_reading_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789

   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

5. **COPY TOKEN** tersebut! (jangan share ke siapa-siapa)

### 1.3 Optional: Set Bot Info
Kirim perintah ke BotFather untuk customize bot:

**Set Description**:
```
/setdescription
```
Pilih bot Anda, lalu kirim:
```
Asisten membaca dan memahami Al-Quran dengan analisis mendalam dalam Bahasa Indonesia. Didukung oleh AI untuk menjelaskan makna, balaghah (retorika), dan tafsir dari berbagai sumber.
```

**Set About Text**:
```
/setabouttext
```
Pilih bot, lalu kirim:
```
Bot asisten memahami Al-Quran dengan penjelasan mendalam. Gunakan /start untuk mulai.
```

**Set Commands** (untuk menu):
```
/setcommands
```
Pilih bot, lalu paste ini:
```
start - Mulai bot dan lihat panduan
read - Baca ayat (format: /read 68:1-10)
progress - Lihat progress bacaan
cancel - Batalkan sesi bacaan
help - Tampilkan bantuan
```

---

## 🔧 Langkah 2: Configure Bot Token

### 2.1 Edit File .env
1. Buka file `.env` di folder `scripts/deployment/`
2. Tambahkan baris baru dengan token dari BotFather:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```
   (ganti dengan token asli Anda)

3. File `.env` sekarang berisi:
   ```
   OPENAI_API_KEY=sk-your-openai-key-here
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```

4. **Save** file

---

## 🚀 Langkah 3: Jalankan Bot

### 3.1 Pastikan API Server Running
Bot Telegram berkomunikasi dengan FastAPI server, jadi server harus running dulu:

```bash
# Terminal 1: Run API Server
run_server.bat
```

Pastikan muncul:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 3.2 Jalankan Telegram Bot
Buka **terminal/command prompt BARU** (jangan tutup yang running server):

```bash
# Terminal 2: Run Telegram Bot
run_telegram_bot.bat
```

Atau manual:
```bash
cd D:\Script\Project\quran\scripts\deployment
python telegram_bot.py
```

Jika sukses, akan muncul:
```
Starting Telegram Bot...
API Base URL: http://localhost:8000
Bot is running... Press Ctrl+C to stop
```

---

## 📱 Langkah 4: Test Bot di Telegram

### 4.1 Cari Bot Anda
1. Buka Telegram
2. Search username bot Anda (misal: `@quran_reading_bot`)
3. Klik **Start**

### 4.2 Test Commands

**1. Start Bot**:
```
/start
```
Bot akan kirim welcome message dengan panduan.

**2. Read Surah**:
```
/read 68:1-5
```
Bot akan:
- Memuat konteks Surah Al-Qalam
- Kirim overview (tema, struktur)
- Tampilkan tombol "Baca Ayat Pertama"

**3. Klik Tombol "📖 Baca Ayat Pertama"**
Bot akan kirim penjelasan ayat 68:1 lengkap dengan:
- Teks Arab
- Terjemahan
- Penjelasan mendalam
- Analisis balaghah
- Tombol "▶️ Lanjut"

**4. Klik "▶️ Lanjut"**
Bot akan kirim ayat berikutnya (68:2), dst.

**5. Check Progress**:
```
/progress
```
Bot akan kirim progress bar dan statistik.

---

## 🎯 Contoh Penggunaan

### Example 1: Baca Surah Pendek
```
User: /read 114:1-6
Bot: [Kirim konteks Surah An-Nas]
     [Tombol: Baca Ayat Pertama]

User: [Klik tombol]
Bot: [Kirim penjelasan ayat 1]
     [Tombol: Lanjut]

User: [Klik Lanjut]
Bot: [Kirim ayat 2]
...
Bot: 🎉 Alhamdulillah! Semua ayat selesai.
```

### Example 2: Baca Range Tertentu
```
User: /read 2:255
Bot: [Kirim konteks Al-Baqarah]
     [Tombol: Baca Ayat Pertama]

User: [Klik tombol]
Bot: [Penjelasan Ayat Kursi lengkap]
     [Tombol: Lanjut]

User: [Klik]
Bot: 🎉 Selesai! (karena cuma 1 ayat)
```

### Example 3: Surah Panjang
```
User: /read 68:1-52
Bot: [Konteks full surah Al-Qalam]

User: [Baca ayat per ayat]
User: /progress
Bot: 📊 Progress: ████████░░ 80%
     📖 Ayat dibaca: 42/52
```

---

## 🔧 Troubleshooting

### Problem 1: Bot tidak merespon
**Solusi**:
- Pastikan `run_telegram_bot.bat` masih running
- Check token di `.env` sudah benar
- Restart bot: Ctrl+C lalu run lagi

### Problem 2: "Tidak dapat terhubung ke server API"
**Solusi**:
- Pastikan FastAPI server running (`run_server.bat`)
- Check http://localhost:8000/health di browser
- Kedua harus running bersamaan (2 terminal)

### Problem 3: "Request timeout"
**Solusi**:
- Normal untuk surah panjang (Al-Baqarah, dll) saat pertama kali
- Server sedang generate chapter context
- Tunggu ~30-60 detik, lalu coba lagi

### Problem 4: Bot crash setelah jawab
**Solusi**:
- Check error di terminal
- Biasanya OpenAI API issue
- Verify OPENAI_API_KEY masih valid

---

## 📊 Monitoring

### Check Bot Status
Terminal yang running `telegram_bot.py` akan show log:
```
Starting Telegram Bot...
API Base URL: http://localhost:8000
Bot is running... Press Ctrl+C to stop

[Akan muncul log setiap user interaction]
```

### Check API Status
Terminal yang running `uvicorn` akan show API calls:
```
INFO:     127.0.0.1:12345 - "POST /start HTTP/1.1" 200 OK
INFO:     127.0.0.1:12345 - "POST /sessions/abc-123/continue HTTP/1.1" 200 OK
```

### Stop Bot
- Bot: Press **Ctrl+C** di terminal `run_telegram_bot.bat`
- API: Press **Ctrl+C** di terminal `run_server.bat`

---

## 💡 Tips

1. **Running Permanently**:
   - Untuk production, gunakan `screen` atau `tmux` di Linux
   - Atau deploy ke cloud (Heroku, Railway, dll)

2. **Multiple Users**:
   - Bot support multiple users secara bersamaan
   - Setiap user punya session terpisah
   - Cache verse analysis shared (efisien)

3. **Privacy**:
   - Bot hanya bisa diakses user yang chat dengan bot
   - Tidak perlu setting privacy khusus

4. **Cost Tracking**:
   - Check `/cache/stats` di API untuk lihat berapa verse cached
   - Cached verse = $0 cost untuk user berikutnya

---

## 🎉 Selesai!

Bot Telegram Anda siap digunakan!

**Next Steps**:
- Share bot ke teman/keluarga
- Monitor usage dan cost
- Customize prompts jika perlu
- Deploy to cloud untuk akses 24/7

Butuh bantuan? Check logs di terminal atau tanya admin.
