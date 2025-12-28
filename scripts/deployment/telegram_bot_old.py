"""
Telegram Bot for Quran Reading System
Connects to FastAPI backend
"""
import os
import sys
from pathlib import Path
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import requests

# Load environment variables
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://localhost:8000"  # FastAPI server

# User sessions (in-memory, will reset on bot restart)
# Format: {telegram_user_id: {"session_id": "uuid", "current_verse": int}}
user_sessions = {}


# ===== Helper Functions =====

def format_verse_message(verse_data: dict) -> str:
    """Format verse analysis for Telegram message"""

    analysis = verse_data.get('analysis', '')
    verse_num = verse_data.get('verse', 0)
    surah = verse_data.get('surah', 0)
    from_cache = verse_data.get('from_cache', False)

    # Build message
    message = f"📖 **Surah {surah}, Ayat {verse_num}**\n\n"
    message += analysis
    message += f"\n\n{'💾 (Dari cache)' if from_cache else '✨ (Fresh analysis)'}"

    return message


def format_chapter_context(chapter_data: dict, verse_range: list) -> str:
    """Format chapter context for initial message"""

    surah_name = chapter_data.get('surah_name', '')
    main_themes = chapter_data.get('main_themes', [])
    narrative_flow = chapter_data.get('narrative_flow', '')

    message = f"📚 **{surah_name}**\n\n"
    message += f"🎯 **Tema Utama:**\n"
    for i, theme in enumerate(main_themes, 1):
        message += f"{i}. {theme}\n"

    message += f"\n📖 **Ayat yang akan dibaca:** {verse_range[0]}-{verse_range[-1]}\n"
    message += f"📊 **Total:** {len(verse_range)} ayat\n\n"
    message += f"💡 **Alur Naratif:**\n{narrative_flow}\n"

    return message


def get_progress_bar(current: int, total: int) -> str:
    """Create progress bar"""
    percentage = (current / total) * 100
    filled = int(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{bar} {percentage:.0f}%"


# ===== Command Handlers =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""

    welcome_message = """
🌟 **Assalamu'alaikum!**

Selamat datang di **Quran Reading Bot** - Asisten memahami Al-Quran dengan analisis mendalam.

🎯 **Cara Menggunakan:**

1️⃣ Ketik `/read` diikuti ayat yang ingin dibaca
   Contoh: `/read 68:1-10`

2️⃣ Bot akan berikan konteks surah

3️⃣ Klik tombol **"Baca Ayat Pertama"** untuk mulai

4️⃣ Setelah selesai baca, klik **"Lanjut"** untuk ayat berikutnya

📚 **Fitur:**
- ✅ Penjelasan dalam Bahasa Indonesia
- ✅ Analisis balaghah (retorika Al-Quran)
- ✅ Referensi tafsir (Al-Kashshaf, Ma'arif, Ibn Kathir)
- ✅ Context-aware (bot "ingat" ayat sebelumnya)

💡 **Contoh perintah:**
• `/read 1:1-7` - Baca Surah Al-Fatihah
• `/read 2:255` - Baca Ayat Kursi
• `/read 68:1-52` - Baca Surah Al-Qalam lengkap
• `/progress` - Lihat progress bacaan
• `/help` - Bantuan

Silakan ketik `/read [surah:ayat]` untuk mulai! 📖
"""

    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""

    help_text = """
📖 **Bantuan Quran Reading Bot**

**Perintah yang tersedia:**

/start - Mulai bot dan lihat panduan
/read <surah:ayat> - Mulai sesi bacaan baru
/progress - Lihat progress bacaan saat ini
/cancel - Batalkan sesi bacaan
/help - Tampilkan bantuan ini

**Format perintah /read:**

• Single ayat: `/read 2:255`
• Range ayat: `/read 68:1-10`
• Full surah: `/read 114:1-6`

**Contoh sesi bacaan:**

1. Ketik: `/read 68:1-5`
2. Bot kirim konteks surah
3. Klik "Baca Ayat Pertama"
4. Bot kirim penjelasan ayat 1
5. Klik "Lanjut" untuk ayat 2
6. Ulangi sampai selesai

**Tips:**
• Bot "mengingat" ayat sebelumnya saat menjelaskan ayat berikutnya
• Hasil analisis di-cache untuk efisiensi
• Anda bisa pause dan lanjutkan kapan saja

Butuh bantuan? Hubungi admin.
"""

    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )


async def read_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /read command"""

    user_id = update.effective_user.id

    # Check if user provided verse range
    if not context.args:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: `/read <surah:ayat>`\n\n"
            "Contoh:\n"
            "• `/read 68:1-10`\n"
            "• `/read 1:1-7`\n"
            "• `/read 2:255`",
            parse_mode='Markdown'
        )
        return

    verse_range = context.args[0]

    # Send loading message
    loading_msg = await update.message.reply_text(
        "⏳ Memuat konteks surah...\n"
        "Ini mungkin memakan waktu beberapa detik jika surah belum pernah dibuka sebelumnya."
    )

    try:
        # Call API to start session
        response = requests.post(
            f"{API_BASE_URL}/start",
            json={
                "verse_range": verse_range,
                "user_id": str(user_id)
            },
            timeout=60  # 60 second timeout for chapter context generation
        )

        if response.status_code != 200:
            error_detail = response.json().get('detail', 'Unknown error')
            await loading_msg.edit_text(
                f"❌ Error: {error_detail}\n\n"
                "Pastikan format sudah benar: `/read surah:ayat`",
                parse_mode='Markdown'
            )
            return

        result = response.json()
        session_id = result['session_id']
        chapter_context = result['chapter_context']
        verse_range_list = result['verse_range']

        # Save session to user_sessions
        user_sessions[user_id] = {
            "session_id": session_id,
            "current_verse": 0,
            "total_verses": len(verse_range_list),
            "verse_range": verse_range_list,
            "surah": result['surah']
        }

        # Delete loading message
        await loading_msg.delete()

        # Format and send chapter context
        context_message = format_chapter_context(chapter_context, verse_range_list)

        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("📖 Baca Ayat Pertama", callback_data="continue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            context_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except requests.exceptions.Timeout:
        await loading_msg.edit_text(
            "⏱️ Request timeout. Server membutuhkan waktu terlalu lama.\n"
            "Ini bisa terjadi untuk surah yang panjang.\n"
            "Silakan coba lagi dalam beberapa saat."
        )
    except requests.exceptions.ConnectionError:
        await loading_msg.edit_text(
            "❌ Tidak dapat terhubung ke server API.\n"
            "Pastikan server FastAPI sedang berjalan di http://localhost:8000"
        )
    except Exception as e:
        await loading_msg.edit_text(
            f"❌ Terjadi error: {str(e)}\n\n"
            "Silakan coba lagi atau hubungi admin."
        )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command"""

    user_id = update.effective_user.id

    # Check if user has active session
    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ Anda belum memiliki sesi bacaan aktif.\n\n"
            "Gunakan `/read <surah:ayat>` untuk memulai.",
            parse_mode='Markdown'
        )
        return

    session = user_sessions[user_id]
    session_id = session['session_id']

    try:
        # Get progress from API
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/progress")

        if response.status_code != 200:
            await update.message.reply_text("❌ Error mengambil progress.")
            return

        progress_data = response.json()

        verses_done = progress_data['verses_analyzed']
        total_verses = progress_data['total_verses']
        progress_pct = progress_data['progress_percentage']
        tokens_used = progress_data['total_tokens_used']

        progress_bar = get_progress_bar(verses_done, total_verses)

        message = f"📊 **Progress Bacaan**\n\n"
        message += f"{progress_bar}\n\n"
        message += f"📖 Ayat dibaca: {verses_done}/{total_verses}\n"
        message += f"📈 Progress: {progress_pct}%\n"
        message += f"🔢 Tokens digunakan: {tokens_used:,}\n"

        if progress_data['complete']:
            message += f"\n✅ **Selesai!** Semua ayat telah dibaca."
        else:
            message += f"\n▶️ Lanjutkan dengan tombol **Lanjut** pada pesan terakhir."

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""

    user_id = update.effective_user.id

    if user_id in user_sessions:
        del user_sessions[user_id]
        await update.message.reply_text(
            "✅ Sesi bacaan dibatalkan.\n\n"
            "Gunakan `/read <surah:ayat>` untuk mulai sesi baru.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Tidak ada sesi aktif untuk dibatalkan.",
            parse_mode='Markdown'
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Check if user has active session
    if user_id not in user_sessions:
        await query.edit_message_text(
            "❌ Sesi Anda sudah tidak aktif.\n\n"
            "Gunakan `/read <surah:ayat>` untuk memulai sesi baru.",
            parse_mode='Markdown'
        )
        return

    session = user_sessions[user_id]
    session_id = session['session_id']

    if query.data == "continue":
        # Send loading message
        await query.edit_message_reply_markup(reply_markup=None)  # Remove buttons

        loading_msg = await query.message.reply_text("⏳ Memuat ayat...")

        try:
            # Call API to get next verse
            response = requests.post(
                f"{API_BASE_URL}/sessions/{session_id}/continue",
                timeout=30
            )

            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Unknown error')
                await loading_msg.edit_text(f"❌ Error: {error_detail}")
                return

            result = response.json()

            # Check if complete
            if result.get('complete'):
                await loading_msg.delete()
                await query.message.reply_text(
                    "🎉 **Alhamdulillah!**\n\n"
                    "Anda telah menyelesaikan semua ayat dalam range ini.\n\n"
                    "✅ Sesi selesai.\n\n"
                    "Gunakan `/read <surah:ayat>` untuk membaca ayat lain.",
                    parse_mode='Markdown'
                )
                # Remove session
                del user_sessions[user_id]
                return

            # Update session
            session['current_verse'] += 1

            # Delete loading message
            await loading_msg.delete()

            # Format and send verse analysis
            verse_message = format_verse_message(result)

            # Progress info
            progress = result['progress']
            progress_text = f"\n\n📊 Progress: {progress['verses_analyzed']}/{progress['total_verses']}"
            verse_message += progress_text

            # Create continue button
            keyboard = [
                [InlineKeyboardButton("▶️ Lanjut", callback_data="continue")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send in chunks if too long (Telegram max 4096 chars)
            if len(verse_message) > 4000:
                # Split message
                parts = [verse_message[i:i+4000] for i in range(0, len(verse_message), 4000)]

                for i, part in enumerate(parts[:-1]):
                    await query.message.reply_text(part, parse_mode='Markdown')

                # Last part with button
                await query.message.reply_text(
                    parts[-1],
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_text(
                    verse_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )

        except requests.exceptions.Timeout:
            await loading_msg.edit_text(
                "⏱️ Request timeout. Silakan coba lagi."
            )
        except Exception as e:
            await loading_msg.edit_text(
                f"❌ Error: {str(e)}\n\n"
                "Silakan coba lagi atau gunakan `/cancel` untuk membatalkan sesi."
            )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""

    await update.message.reply_text(
        "❓ Perintah tidak dikenali.\n\n"
        "Gunakan `/help` untuk melihat daftar perintah.",
        parse_mode='Markdown'
    )


# ===== Main Function =====

def main():
    """Start the bot"""

    print("DEBUG: Starting main()")

    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file")
        return

    print(f"DEBUG: Token found (length: {len(TELEGRAM_BOT_TOKEN)})")
    print("Starting Telegram Bot...")
    print(f"API Base URL: {API_BASE_URL}")

    # Create application
    print("DEBUG: Creating application...")
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        print("DEBUG: Application created successfully")
    except Exception as e:
        print(f"ERROR: Failed to create application: {e}")
        return

    # Add handlers
    print("DEBUG: Adding handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("read", read_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Handle unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    print("DEBUG: All handlers added")

    # Start bot
    print("Bot is running... Press Ctrl+C to stop")
    print("DEBUG: Starting polling...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"ERROR: Polling failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
