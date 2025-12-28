"""
Quran Analysis Telegram Bot (Single Service)
Uses ConversationManager directly, no FastAPI backend
Streaming LLM responses with 1.5s throttling
"""
import os
import sys
import time
import json
import asyncio
import functools
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatAction
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.conversation_manager import ConversationManager
from api.chapter_context_generator import ChapterContextGenerator
from api.data_loader import QuranDataLoader
from api.section_session_manager import SectionSessionManager
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    OPENAI_API_KEY,
    CONTEXT_WINDOW_THRESHOLD
)

# Load .env
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

# Re-read after load_dotenv
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_USER = os.getenv("TELEGRAM_ADMIN_USER", "")  # Admin user ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Streaming update interval (seconds)
STREAM_UPDATE_INTERVAL = 1.5

# Allowed users file path
ALLOWED_USERS_FILE = Path(__file__).parent / "allowed_users.json"
PENDING_REGISTRATIONS_FILE = Path(__file__).parent / "pending_registrations.json"


# ===== User Management =====
def load_allowed_users() -> list:
    """Load allowed users from JSON file"""
    if ALLOWED_USERS_FILE.exists():
        try:
            with open(ALLOWED_USERS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('users', [])
        except Exception:
            pass
    # Default: admin only
    return [TELEGRAM_ADMIN_USER] if TELEGRAM_ADMIN_USER else []


def save_allowed_users(users: list):
    """Save allowed users to JSON file"""
    with open(ALLOWED_USERS_FILE, 'w') as f:
        json.dump({'users': users}, f, indent=2)


def load_pending_registrations() -> dict:
    """Load pending registration requests"""
    if PENDING_REGISTRATIONS_FILE.exists():
        try:
            with open(PENDING_REGISTRATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_pending_registrations(pending: dict):
    """Save pending registration requests"""
    with open(PENDING_REGISTRATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)


def is_user_allowed(user_id: int) -> bool:
    """Check if user is allowed"""
    users = load_allowed_users()
    return str(user_id) in users or str(user_id) == TELEGRAM_ADMIN_USER


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return str(user_id) == TELEGRAM_ADMIN_USER


def is_pending_registration(user_id: int) -> bool:
    """Check if user has pending registration"""
    pending = load_pending_registrations()
    return str(user_id) in pending


# ===== User Session Storage =====
# {telegram_user_id: {session_id, surah, current_verse, ...}}
user_sessions: Dict[int, Dict[str, Any]] = {}


# ===== Whitelist Decorator =====
def whitelist_only(func):
    """Decorator to restrict access to whitelisted users only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_user_allowed(user_id):
            if is_pending_registration(user_id):
                await update.message.reply_text(
                    "Registrasi Anda sedang menunggu persetujuan admin.\n"
                    "Mohon tunggu."
                )
            else:
                await update.message.reply_text(
                    "Maaf, Anda tidak memiliki akses ke bot ini.\n\n"
                    "Gunakan /register <nama> untuk mendaftar.\n"
                    "Contoh: /register Ahmad Fauzi"
                )
            return
        return await func(update, context)
    return wrapper


def admin_only(func):
    """Decorator to restrict access to admin only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text(
                "Perintah ini hanya untuk admin."
            )
            return
        return await func(update, context)
    return wrapper


# ===== Initialize Components =====
cache_manager: Optional[CacheManager] = None
session_manager: Optional[SessionManager] = None
openai_client: Optional[OpenAI] = None
data_loader: Optional[QuranDataLoader] = None
chapter_generator: Optional[ChapterContextGenerator] = None
conv_manager: Optional[ConversationManager] = None
section_manager: Optional[SectionSessionManager] = None
verse_analysis_prompt: str = ""


def initialize_components():
    """Initialize all components"""
    global cache_manager, session_manager, openai_client
    global data_loader, chapter_generator, conv_manager, section_manager
    global verse_analysis_prompt

    print("Initializing components...")

    cache_manager = CacheManager()
    session_manager = SessionManager(cache_manager)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    data_loader = QuranDataLoader()
    # Pass shared data_loader to avoid repeated loading
    chapter_generator = ChapterContextGenerator(cache_manager, openai_client, data_loader)
    conv_manager = ConversationManager(
        cache_manager,
        session_manager,
        openai_client,
        data_loader
    )
    # Initialize section session manager
    section_manager = SectionSessionManager(cache_manager, data_loader)

    # Load verse analysis prompt
    verse_prompt_path = Path(__file__).parent / "prompts" / "verse_analysis_prompt.txt"
    with open(verse_prompt_path, 'r', encoding='utf-8') as f:
        verse_analysis_prompt = f.read()
    print(f"Verse analysis prompt loaded: {len(verse_analysis_prompt)} chars")

    print("Components initialized successfully")


# ===== Telegram Formatting Helper =====
import re

def fix_unclosed_html_tags(text: str) -> str:
    """
    Fix unclosed HTML tags to prevent Telegram parse errors.
    Counts opening and closing tags and adds missing closing tags.
    """
    tags = ['b', 'i', 'code', 'pre']

    for tag in tags:
        # Count opening and closing tags
        open_count = len(re.findall(f'<{tag}>', text))
        close_count = len(re.findall(f'</{tag}>', text))

        # Add missing closing tags at the end
        if open_count > close_count:
            text += f'</{tag}>' * (open_count - close_count)
        # Remove extra closing tags (shouldn't happen, but just in case)
        elif close_count > open_count:
            for _ in range(close_count - open_count):
                # Remove the last extra closing tag
                text = re.sub(f'</{tag}>(?!.*</{tag}>)', '', text, count=1)

    return text


def markdown_to_telegram_html(text: str) -> str:
    """
    Convert standard markdown to Telegram HTML format.
    Telegram HTML supports: <b>, <i>, <code>, <pre>
    """
    if not text:
        return text

    # Escape HTML special characters first (except our converted tags)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Convert headers (### Header -> <b>Header</b>)
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)

    # Convert bold: **text** -> <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # Convert italic: *text* or _text_ -> <i>text</i>
    # Be careful not to match already converted bold
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'_([^_]+)_', r'<i>\1</i>', text)

    # Convert inline code: `code` -> <code>code</code>
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Convert code blocks: ```code``` -> <pre>code</pre>
    text = re.sub(r'```[\w]*\n?(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)

    # Convert horizontal rules: --- or *** -> empty line
    text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)

    # Fix any unclosed tags
    text = fix_unclosed_html_tags(text)

    return text


def safe_send_message(text: str, parse_mode: str = "HTML") -> tuple:
    """
    Returns (text, parse_mode) tuple, falling back to plain text if HTML is invalid.
    """
    if parse_mode == "HTML":
        # Try to validate by checking tag balance
        text = fix_unclosed_html_tags(text)
    return text, parse_mode


# ===== Streaming Helper =====
async def stream_to_telegram(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session_id: str,
    user_message: str,
    include_verse_data: Dict = None
) -> str:
    """
    Stream OpenAI response to Telegram with throttled updates

    Args:
        update: Telegram update
        context: Telegram context
        session_id: Conversation session ID
        user_message: User's message
        include_verse_data: Optional verse data

    Returns:
        Complete response text
    """
    chat_id = update.effective_chat.id

    # Send initial message
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="..."
    )
    message_id = msg.message_id
    last_update_time = time.time()
    last_text = ""

    async def on_chunk(accumulated_text: str):
        """Callback for each chunk - throttled updates"""
        nonlocal last_update_time, last_text

        current_time = time.time()

        # Update message every STREAM_UPDATE_INTERVAL seconds
        # Only update if text is within Telegram limit (4096 chars)
        if current_time - last_update_time >= STREAM_UPDATE_INTERVAL:
            # Only update if text actually changed AND within limit
            if accumulated_text != last_text and len(accumulated_text) <= 3900:
                try:
                    display_text = accumulated_text + " ..."
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=display_text
                    )
                    last_text = accumulated_text
                    last_update_time = current_time
                except Exception:
                    pass  # Ignore edit errors (rate limits, etc.)

    # Stream the message
    full_response = await conv_manager.stream_message_async(
        session_id,
        user_message,
        on_chunk=on_chunk,
        include_verse_data=include_verse_data
    )

    # Final update with complete text (convert to HTML)
    async def send_with_fallback(text: str, use_edit: bool = False, msg_id: int = None):
        """Send message with HTML, fallback to plain text if fails"""
        formatted = markdown_to_telegram_html(text)
        try:
            if use_edit and msg_id:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=formatted,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(chat_id=chat_id, text=formatted, parse_mode="HTML")
        except Exception as html_error:
            # Fallback to plain text without formatting
            print(f"HTML parse error, falling back to plain text: {html_error}")
            try:
                if use_edit and msg_id:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=text
                    )
                else:
                    await context.bot.send_message(chat_id=chat_id, text=text)
            except Exception:
                pass

    try:
        # Split if too long
        if len(full_response) > 4000:
            # Delete the streaming message first
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass  # Ignore if can't delete

            # Send complete response in chunks as new messages
            chunks = [full_response[i:i+4000] for i in range(0, len(full_response), 4000)]
            for chunk in chunks:
                await send_with_fallback(chunk)
        else:
            await send_with_fallback(full_response, use_edit=True, msg_id=message_id)

    except Exception as e:
        print(f"Error in final update: {e}")
        traceback.print_exc()
        # Last resort - try plain text
        try:
            await context.bot.send_message(chat_id=chat_id, text=full_response[:4000])
        except Exception:
            pass

    return full_response


# ===== Command Handlers =====

@whitelist_only
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome = """Assalamu'alaikum!

Selamat datang di Quran Analysis Bot.
Analisis balaghah AYAT PER AYAT dengan konteks Section tematik.

PERINTAH:
/surah <N> - Mulai session dengan surah N
/next atau /n - Analisis ayat berikutnya
/verse <N> - Jump ke ayat spesifik
/status - Status session + progress
/clear - Clear conversation
/cancel - Batalkan session
/help - Bantuan

ALUR:
/surah 2 -> /next (overview section 1) -> /next (ayat 1) -> /next (ayat 2) -> ...

Setiap memasuki section baru, bot akan memberikan overview dengan heading deskriptif (misal: "Qualities of the Believers").

FREE CHAT:
Ketik pesan apapun untuk tanya lebih detail.
"""
    await update.message.reply_text(welcome)


@whitelist_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id

    help_text = """PANDUAN QURAN ANALYSIS BOT
(Analisis Ayat per Ayat dengan Konteks Section Tematik)

PERINTAH UTAMA:
/surah <N> - Mulai session baru dengan surah N
/next atau /n - Analisis ayat berikutnya
/verse <N> - Jump ke ayat spesifik
/prev atau /p - Kembali 1 ayat
/status - Lihat status session + progress
/clear - Reset conversation
/cancel - Batalkan session

APA ITU SECTION?
Section adalah pembagian tematik Al-Quran (1,966 bagian dari Clear Quran).
Setiap section memiliki heading deskriptif yang menjelaskan tema (contoh: "Qualities of the Believers", "The Story of Abraham").
Bot menggunakan section untuk memberikan konteks tematik yang lebih detail.

ALUR PENGGUNAAN:
1. /surah 2 - Mulai Surah Al-Baqarah + lihat pengantar komprehensif
2. /next - BOT TAMPILKAN OVERVIEW SECTION 1 (dengan heading tema)
3. /next - Analisis Ayat 1
4. /next - Analisis Ayat 2
5. ... (lanjut per ayat)
6. Di akhir section, bot ekstrak konteks
7. /next - OVERVIEW SECTION 2 (dengan konteks dari Section 1 + heading baru)
8. /next - Analisis ayat berikutnya
   ... dst

KEUNGGULAN:
- Analisis detail per ayat
- Overview setiap masuk section baru dengan heading deskriptif
- Konteks terhubung antar section
- Pola balaghah terlacak lintas ayat
- Section lebih granular (avg 3 ayat vs ruku tradisional 11 ayat)

FREE CHAT:
Ketik pertanyaan apapun tentang ayat yang sedang dibahas.
"""

    # Add admin commands if user is admin
    if is_admin(user_id):
        help_text += """
ADMIN - USER MANAGEMENT:
/adduser <id> - Tambah user langsung
/removeuser <id> - Hapus user
/listusers - Lihat daftar users

ADMIN - REGISTRASI:
/pending - Lihat pending registrasi
/approve <id> - Setujui registrasi
/reject <id> - Tolak registrasi
"""

    await update.message.reply_text(help_text)


@whitelist_only
async def cmd_surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /surah <N> command - Start session with surah N (section-based)"""
    user_id = update.effective_user.id

    # Parse surah number
    if not context.args:
        await update.message.reply_text(
            "Format: /surah <nomor>\nContoh: /surah 68"
        )
        return

    try:
        surah_num = int(context.args[0])
        if surah_num < 1 or surah_num > 114:
            await update.message.reply_text("Nomor surah harus 1-114")
            return
    except ValueError:
        await update.message.reply_text("Nomor surah harus angka")
        return

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    loading_msg = await update.message.reply_text(
        f"Memuat Surah {surah_num}...\n"
        "Ini mungkin memakan waktu jika surah belum pernah dibuka."
    )

    try:
        # Get chapter metadata
        chapter_meta = data_loader.get_chapter_metadata(surah_num)
        total_verses = chapter_meta.get('verses_count', 0)

        # Get section info for this chapter
        sections = section_manager.get_sections_for_chapter(surah_num)
        total_sections = len(sections)

        # Generate or get cached chapter context
        chapter_context = chapter_generator.get_or_generate(surah_num)
        user_introduction = chapter_context.get('user_introduction', '')

        # Get accumulated summary (from previous sessions if any)
        accumulated = section_manager.get_accumulated_summary(surah_num)

        # Determine starting section (continue from where left off or start fresh)
        start_section_index = 0
        if accumulated:
            last_completed = accumulated.get('last_section_completed', -1)
            if last_completed >= 0 and last_completed < total_sections - 1:
                start_section_index = last_completed + 1

        # Create session
        verse_range = list(range(1, total_verses + 1))
        session_id = session_manager.create_session(surah_num, verse_range, str(user_id))

        # Initialize conversation with user_introduction as first assistant message
        conv_manager.start_conversation_with_introduction(
            session_id=session_id,
            surah_num=surah_num,
            user_introduction=user_introduction
        )

        # Store user session with section tracking
        user_sessions[user_id] = {
            "session_id": session_id,
            "surah": surah_num,
            "current_verse": 0,
            "total_verses": total_verses,
            "surah_name": chapter_meta.get('name_arabic', ''),
            "surah_name_en": chapter_meta.get('name_english', ''),
            # Section tracking
            "total_sections": total_sections,
            "current_section": start_section_index,
            "section_overview_shown": False,  # True after section overview is displayed
            "chapter_context": chapter_context
        }

        # Delete loading message
        await loading_msg.delete()

        # Format chapter info - show LLM-generated user_introduction
        # Header
        response = f"=== Surah {surah_num}: {chapter_meta.get('name_arabic', '')} ===\n"
        response += f"{chapter_meta.get('name_english', '')} | {total_verses} ayat | {chapter_meta.get('revelation_place', '')}\n"
        response += f"Sections: {total_sections} bagian tematik\n\n"

        # Show the comprehensive user_introduction from LLM
        if user_introduction:
            response += user_introduction
        else:
            # Fallback to old format if user_introduction not available
            themes = chapter_context.get('main_themes', [])
            narrative = chapter_context.get('narrative_flow', '')

            response += "TEMA UTAMA:\n"
            for i, theme in enumerate(themes[:5], 1):
                response += f"{i}. {theme}\n"

            if narrative:
                response += f"\nALUR NARATIF:\n{narrative}\n"

        # Show section preview with headings
        if total_sections > 0:
            response += f"\n\nSECTION OVERVIEW:\n"
            for i, section in enumerate(sections[:5]):  # Show first 5 sections
                heading = section.get('heading', 'No heading')
                section_label = f"Section {i+1}: {heading}\n  Ayat {section['verse_start']}-{section['verse_end']}"
                if i == start_section_index:
                    section_label += " <-- mulai"
                response += f"  {section_label}\n"
            if total_sections > 5:
                response += f"  ... dan {total_sections - 5} section lainnya\n"

        # Progress info if continuing
        if start_section_index > 0:
            current_section_heading = sections[start_section_index].get('heading', 'No heading')
            response += f"\n[Melanjutkan dari Section {start_section_index + 1}: {current_section_heading}]"

        # Show next section info
        if start_section_index < total_sections:
            next_section = sections[start_section_index]
            next_heading = next_section.get('heading', 'No heading')
            response += f"\n\nKetik /next untuk mulai analisis Section {start_section_index + 1}:\n\"{next_heading}\""

        # Send response with HTML fallback
        async def send_chunk(text: str):
            formatted = markdown_to_telegram_html(text)
            try:
                await update.message.reply_text(formatted, parse_mode="HTML")
            except Exception:
                # Fallback to plain text
                await update.message.reply_text(text)

        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await send_chunk(chunk)
        else:
            await send_chunk(response)

    except Exception as e:
        await loading_msg.edit_text(f"Error: {str(e)}")
        print(f"Error in cmd_surah: {e}")
        traceback.print_exc()


@whitelist_only
async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /next or /n command - Analyze next verse (verse-by-verse with section overview)"""
    user_id = update.effective_user.id

    # Check session
    if user_id not in user_sessions:
        await update.message.reply_text(
            "Belum ada session aktif.\nGunakan /surah <N> untuk memulai."
        )
        return

    session = user_sessions[user_id]
    session_id = session['session_id']
    surah_num = session['surah']
    current_verse = session['current_verse']
    total_verses = session['total_verses']
    total_sections = session.get('total_sections', 0)
    current_section = session.get('current_section', 0)
    section_overview_shown = session.get('section_overview_shown', False)
    chapter_context = session.get('chapter_context', {})

    # Check if surah complete
    if current_verse >= total_verses:
        await update.message.reply_text(
            f"Surah {surah_num} sudah selesai! ({total_verses} ayat)\n"
            "Gunakan /surah <N> untuk memulai surah lain."
        )
        return

    # Get current section data
    section_data = section_manager.get_section_by_index(surah_num, current_section)
    if not section_data:
        await update.message.reply_text("Error: Section data tidak ditemukan.")
        return

    section_verse_start = section_data.get('verse_start', 1)
    section_verse_end = section_data.get('verse_end', 1)
    section_heading = section_data.get('heading', 'No heading')

    # Show typing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    try:
        # ===== STEP 1: Show section overview if entering new section =====
        if not section_overview_shown:
            loading_msg = await update.message.reply_text(
                f"📖 Menyiapkan overview Section {current_section + 1}:\n\"{section_heading}\"\n\nMenggunakan metodologi tafsir tematik..."
            )

            # Get accumulated summary from previous sections
            accumulated = section_manager.get_accumulated_summary(surah_num)

            # Generate comprehensive overview prompt using tafsir methodology
            # (includes: 'Amud, Munasabat, Nazm, Preview Balaghah, Pertanyaan Kunci)
            overview_prompt, section_full_data = section_manager.generate_section_overview_prompt(
                surah_num, current_section, accumulated
            )

            if not overview_prompt:
                await loading_msg.edit_text("Error: Tidak dapat memuat data section.")
                return

            await loading_msg.delete()

            # Stream overview
            response = await stream_to_telegram(
                update, context, session_id,
                overview_prompt, include_verse_data=None
            )

            # Mark overview as shown
            session['section_overview_shown'] = True

            # Show next step with section heading
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"\n📖 === SECTION {current_section + 1}: {section_heading} ===\nAyat {section_verse_start}-{section_verse_end}\n\nKetik /next untuk mulai analisis Ayat {section_verse_start}"
            )
            return

        # ===== STEP 2: Analyze next verse =====
        next_verse = current_verse + 1

        # Check verse cache
        cached = cache_manager.get_verse_analysis(surah_num, next_verse)

        if cached:
            # Use cached response
            loading_msg = await update.message.reply_text(f"Memuat ayat {next_verse} dari cache...")
            analysis_text = cached.get('analysis', cached.get('content', str(cached)))
            await loading_msg.delete()

            # Send cached analysis with HTML fallback
            async def send_cached_chunk(text: str):
                formatted = markdown_to_telegram_html(text)
                try:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=formatted, parse_mode="HTML")
                except Exception:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

            if len(analysis_text) > 4000:
                chunks = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
                for chunk in chunks:
                    await send_cached_chunk(chunk)
            else:
                await send_cached_chunk(analysis_text)

            session_manager.add_verse(session_id, next_verse, from_cache=True, tokens_used=0)

        else:
            # Analyze with streaming
            loading_msg = await update.message.reply_text(f"Menganalisis ayat {next_verse}...")

            verse_data = data_loader.get_verse_full_data(surah_num, next_verse)

            # Build detailed analysis prompt using comprehensive template
            user_message = f"""Analisis ayat {surah_num}:{next_verse} dengan struktur 5 paragraf.

{verse_analysis_prompt}

DATA AYAT (dalam JSON):
Gunakan data berikut untuk analisis Anda."""

            await loading_msg.delete()

            response_text = await stream_to_telegram(
                update, context, session_id,
                user_message, include_verse_data=verse_data
            )

            # Save to cache
            cache_manager.save_verse_analysis(surah_num, next_verse, {
                'analysis': response_text,
                'surah': surah_num,
                'verse': next_verse
            })

            session_manager.add_verse(session_id, next_verse, from_cache=False, tokens_used=0)

        # Update current verse
        session['current_verse'] = next_verse

        # ===== STEP 3: Check if section complete =====
        if next_verse >= section_verse_end:
            # End of section - extract carryover
            extraction_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Mengekstrak konteks untuk section berikutnya..."
            )

            try:
                extraction = await conv_manager.extract_carryover_info(
                    session_id, surah_num, current_section
                )

                if extraction:
                    section_manager.merge_extraction_into_summary(
                        surah_num, current_section, extraction
                    )

                await extraction_msg.delete()
            except Exception as ext_err:
                print(f"Error extracting carryover: {ext_err}")
                try:
                    await extraction_msg.edit_text("(Ekstraksi selesai)")
                    await asyncio.sleep(1)
                    await extraction_msg.delete()
                except Exception:
                    pass

            # Advance to next section
            session['current_section'] = current_section + 1
            session['section_overview_shown'] = False  # Reset for next section

            # Check if surah complete
            next_preview = section_manager.get_next_section_preview(surah_num, current_section)

            if next_preview and not next_preview.get('is_last'):
                next_heading = next_preview.get('section_heading', 'No heading')
                progress_msg = (
                    f"\n✅ === AKHIR SECTION {current_section + 1}/{total_sections} ===\n"
                    f"\"{section_heading}\" selesai!\n\n"
                    f"Ketik /next untuk overview Section {current_section + 2}:\n"
                    f"\"{next_heading}\"\n"
                    f"(Ayat {next_preview.get('verse_start')}-{next_preview.get('verse_end')})"
                )
            else:
                progress_msg = (
                    f"\n🎉 === SURAH {surah_num} SELESAI ===\n"
                    f"Semua {total_sections} section ({total_verses} ayat) telah dianalisis.\n"
                    "Gunakan /surah <N> untuk memulai surah lain."
                )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=progress_msg
            )
        else:
            # Show progress within section
            verses_in_section = section_verse_end - section_verse_start + 1
            verse_position = next_verse - section_verse_start + 1
            progress_msg = f"\n[Ayat {next_verse} - {verse_position}/{verses_in_section} dalam Section {current_section + 1}: \"{section_heading}\"] /next untuk lanjut"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=progress_msg
            )

    except Exception as e:
        print(f"Error in cmd_next: {e}")
        traceback.print_exc()
        await update.message.reply_text(
            f"Error: {str(e)}\n\nCoba /next lagi atau /status untuk cek session."
        )


@whitelist_only
async def cmd_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /prev or /p command - Go to previous verse"""
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text(
            "Belum ada session aktif.\nGunakan /surah <N> untuk memulai."
        )
        return

    session = user_sessions[user_id]
    current_verse = session.get('current_verse', 0)
    surah_num = session['surah']

    if current_verse <= 1:
        await update.message.reply_text("Sudah di ayat pertama.")
        return

    # Go back one verse
    prev_verse = current_verse - 1
    session['current_verse'] = prev_verse

    # Check if we're now in a different (previous) section
    new_section_index = section_manager.get_current_section_index(surah_num, prev_verse)
    current_section = session.get('current_section', 0)

    if new_section_index < current_section:
        # Moved to previous section
        session['current_section'] = new_section_index
        session['section_overview_shown'] = True  # Already seen this section

    # Get section info for display
    section_data = section_manager.get_section_by_index(surah_num, new_section_index)
    section_info = ""
    if section_data:
        section_heading = section_data.get('heading', 'No heading')
        section_info = f" (Section {new_section_index + 1}: \"{section_heading}\")"

    await update.message.reply_text(
        f"Kembali ke ayat {prev_verse}{section_info}.\n"
        f"Ketik /next untuk menganalisis ayat {prev_verse + 1}."
    )


@whitelist_only
async def cmd_verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /verse <N> command - Analyze single verse"""
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text(
            "Belum ada session aktif.\nGunakan /surah <N> untuk memulai."
        )
        return

    if not context.args:
        await update.message.reply_text("Format: /verse <nomor>\nContoh: /verse 5")
        return

    try:
        verse_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Nomor ayat harus angka")
        return

    session = user_sessions[user_id]
    session_id = session['session_id']
    surah_num = session['surah']
    total_verses = session['total_verses']

    if verse_num < 1 or verse_num > total_verses:
        await update.message.reply_text(f"Nomor ayat harus 1-{total_verses}")
        return

    # Show typing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    loading_msg = await update.message.reply_text(f"Menganalisis ayat {verse_num}...")

    try:
        # Get verse data
        verse_data = data_loader.get_verse_full_data(surah_num, verse_num)

        # Delete loading message
        await loading_msg.delete()

        # Build prompt
        user_message = f"Analisis ayat {verse_num} berikut ini secara detail:"

        # Stream response
        response_text = await stream_to_telegram(
            update, context, session_id,
            user_message, include_verse_data=verse_data
        )

        # Update current verse and section tracking
        session['current_verse'] = verse_num

        # Find which section this verse is in and update session
        section_index = section_manager.get_current_section_index(surah_num, verse_num)
        session['current_section'] = section_index
        session['section_overview_shown'] = True  # Skip overview since we jumped directly

        section_data = section_manager.get_section_by_index(surah_num, section_index)
        if section_data:
            section_heading = section_data.get('heading', 'No heading')
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"[Ayat {verse_num} dalam Section {section_index + 1}: \"{section_heading}\"\n(Ayat {section_data['verse_start']}-{section_data['verse_end']})]"
            )

    except Exception as e:
        print(f"Error in cmd_verse: {e}")
        traceback.print_exc()
        await loading_msg.edit_text(f"Error: {str(e)}")


@whitelist_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - Show session status with section progress"""
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text(
            "Belum ada session aktif.\nGunakan /surah <N> untuk memulai."
        )
        return

    session = user_sessions[user_id]
    session_id = session['session_id']
    surah_num = session['surah']

    # Get conversation stats
    stats = conv_manager.get_conversation_stats(session_id)

    # Get section progress
    total_sections = session.get('total_sections', 0)
    current_section = session.get('current_section', 0)
    section_progress = section_manager.get_session_progress(surah_num)

    # Get current section info with heading
    current_section_data = section_manager.get_section_by_index(surah_num, current_section)
    section_info = ""
    if current_section_data and current_section < total_sections:
        section_heading = current_section_data.get('heading', 'No heading')
        section_info = f"Section {current_section + 1}: \"{section_heading}\"\nAyat {current_section_data['verse_start']}-{current_section_data['verse_end']}"

    status_msg = f"""=== STATUS SESSION ===

Surah: {session['surah']} ({session['surah_name']})

PROGRESS SECTION:
Section: {current_section + 1}/{total_sections}
Progress: {section_progress.get('progress_percent', 0)}%
{section_info}

AYAT:
Terakhir dianalisis: ayat {session['current_verse']}/{session['total_verses']}

CONVERSATION (Section saat ini):
Messages: {stats.get('messages_count', 0)}
Estimated tokens: {stats.get('estimated_tokens', 0):,}
Token limit: {stats.get('token_limit', 0):,}
Usage: {stats.get('usage_percent', 0)}%
"""

    # Add accumulated summary info if exists
    accumulated = section_manager.get_accumulated_summary(surah_num)
    if accumulated and accumulated.get('accumulated_summary'):
        acc = accumulated['accumulated_summary']
        themes_count = len(acc.get('themes', []))
        correlations_count = len(acc.get('balaghah_correlations', []))
        terms_count = len(acc.get('key_terms', []))

        status_msg += f"""
AKUMULASI KONTEKS:
Tema terlacak: {themes_count}
Korelasi balaghah: {correlations_count}
Istilah kunci: {terms_count}
"""

    await update.message.reply_text(status_msg)


@whitelist_only
async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - Clear conversation, stay in same surah (section reset)"""
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text("Tidak ada session aktif.")
        return

    session = user_sessions[user_id]
    session_id = session['session_id']
    surah_num = session['surah']
    current_section = session.get('current_section', 0)

    # Delete old conversation
    cache_manager.delete_conversation(session_id)

    # Get chapter context (from cache or stored in session)
    chapter_context = session.get('chapter_context') or chapter_generator.get_or_generate(surah_num)
    user_introduction = chapter_context.get('user_introduction', '')

    # Create new session
    total_verses = session['total_verses']
    verse_range = list(range(1, total_verses + 1))
    new_session_id = session_manager.create_session(surah_num, verse_range, str(user_id))

    # Initialize conversation with user_introduction
    conv_manager.start_conversation_with_introduction(
        session_id=new_session_id,
        surah_num=surah_num,
        user_introduction=user_introduction
    )

    # Update user session (keep section position, reset conversation)
    session['session_id'] = new_session_id
    session['section_overview_shown'] = False  # Will show overview again for current section

    # Get current section info with heading
    section_data = section_manager.get_section_by_index(surah_num, current_section)
    section_info = ""
    if section_data:
        section_heading = section_data.get('heading', 'No heading')
        section_info = f"\nSection saat ini: {current_section + 1} \"{section_heading}\"\n(Ayat {section_data['verse_start']}-{section_data['verse_end']})"

    await update.message.reply_text(
        f"Conversation cleared.\n"
        f"Tetap di Surah {surah_num}.{section_info}\n"
        f"Ketik /next untuk menganalisis section saat ini."
    )


@whitelist_only
async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command - Cancel session"""
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text("Tidak ada session aktif.")
        return

    session = user_sessions[user_id]
    session_id = session['session_id']

    # Delete conversation
    cache_manager.delete_conversation(session_id)
    cache_manager.delete_session(session_id)

    # Remove from user sessions
    del user_sessions[user_id]

    await update.message.reply_text(
        "Session dibatalkan.\n"
        "Gunakan /surah <N> untuk memulai session baru."
    )


@whitelist_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free text messages - Chat with LLM"""
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_sessions:
        await update.message.reply_text(
            "Belum ada session aktif.\n"
            "Gunakan /surah <N> untuk memulai, atau /help untuk bantuan."
        )
        return

    session = user_sessions[user_id]
    session_id = session['session_id']
    surah_num = session.get('surah', 0)
    current_verse = session.get('current_verse', 0)

    # Show typing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    try:
        # Stream response (free chat, no verse data)
        response_text = await stream_to_telegram(update, context, session_id, text)

        # Save chat to cache
        cache_manager.save_chat(
            surah_num=surah_num,
            verse_num=current_verse,
            user_id=str(user_id),
            question=text,
            answer=response_text
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        print(f"Error in handle_message: {e}")


# ===== Admin Commands =====

@admin_only
async def cmd_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adduser <user_id> - Add user to allowed list (admin only)"""
    if not context.args:
        await update.message.reply_text(
            "Format: /adduser <user_id>\n"
            "Contoh: /adduser 123456789\n\n"
            "Tip: User bisa kirim /myid untuk dapat ID mereka."
        )
        return

    new_user_id = context.args[0].strip()

    # Validate user ID
    if not new_user_id.isdigit():
        await update.message.reply_text("User ID harus berupa angka.")
        return

    users = load_allowed_users()

    if new_user_id in users:
        await update.message.reply_text(f"User {new_user_id} sudah ada dalam daftar.")
        return

    users.append(new_user_id)
    save_allowed_users(users)

    await update.message.reply_text(
        f"User {new_user_id} berhasil ditambahkan.\n"
        f"Total users: {len(users)}"
    )


@admin_only
async def cmd_removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeuser <user_id> - Remove user from allowed list (admin only)"""
    if not context.args:
        await update.message.reply_text("Format: /removeuser <user_id>")
        return

    user_id_to_remove = context.args[0].strip()

    # Cannot remove admin
    if user_id_to_remove == TELEGRAM_ADMIN_USER:
        await update.message.reply_text("Tidak bisa menghapus admin.")
        return

    users = load_allowed_users()

    if user_id_to_remove not in users:
        await update.message.reply_text(f"User {user_id_to_remove} tidak ditemukan.")
        return

    users.remove(user_id_to_remove)
    save_allowed_users(users)

    await update.message.reply_text(
        f"User {user_id_to_remove} berhasil dihapus.\n"
        f"Total users: {len(users)}"
    )


@admin_only
async def cmd_listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listusers - List all allowed users (admin only)"""
    users = load_allowed_users()

    if not users:
        await update.message.reply_text("Belum ada user yang terdaftar.")
        return

    user_list = "\n".join([f"  - {u}" + (" (admin)" if u == TELEGRAM_ADMIN_USER else "") for u in users])
    await update.message.reply_text(
        f"Allowed Users ({len(users)}):\n{user_list}"
    )


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myid - Show user's Telegram ID (public command)"""
    user = update.effective_user
    await update.message.reply_text(
        f"Your Telegram ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'N/A'}\n"
        f"Name: {user.full_name}"
    )


# ===== Registration Commands =====

async def cmd_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /register <name> - Request access to bot (public command)"""
    user = update.effective_user
    user_id = str(user.id)

    # Check if already allowed
    if is_user_allowed(user.id):
        await update.message.reply_text("Anda sudah terdaftar dan memiliki akses.")
        return

    # Check if already pending
    if is_pending_registration(user.id):
        await update.message.reply_text(
            "Permintaan registrasi Anda sedang menunggu persetujuan admin.\n"
            "Mohon tunggu."
        )
        return

    # Get name from args
    if not context.args:
        await update.message.reply_text(
            "Format: /register <nama lengkap>\n"
            "Contoh: /register Ahmad Fauzi"
        )
        return

    name = " ".join(context.args)

    # Save pending registration
    pending = load_pending_registrations()
    pending[user_id] = {
        "name": name,
        "username": user.username or "N/A",
        "telegram_name": user.full_name,
        "registered_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_pending_registrations(pending)

    await update.message.reply_text(
        f"Permintaan registrasi berhasil dikirim!\n\n"
        f"Nama: {name}\n"
        f"ID: {user_id}\n\n"
        f"Mohon tunggu persetujuan dari admin."
    )

    # Notify admin
    if TELEGRAM_ADMIN_USER:
        try:
            admin_msg = (
                f"REGISTRASI BARU\n\n"
                f"Nama: {name}\n"
                f"Telegram: {user.full_name}\n"
                f"Username: @{user.username if user.username else 'N/A'}\n"
                f"ID: {user_id}\n\n"
                f"Gunakan:\n"
                f"/approve {user_id} - untuk menyetujui\n"
                f"/reject {user_id} - untuk menolak"
            )
            await context.bot.send_message(
                chat_id=int(TELEGRAM_ADMIN_USER),
                text=admin_msg
            )
        except Exception as e:
            print(f"Failed to notify admin: {e}")


@admin_only
async def cmd_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pending - List pending registrations (admin only)"""
    pending = load_pending_registrations()

    if not pending:
        await update.message.reply_text("Tidak ada registrasi yang menunggu.")
        return

    msg = f"PENDING REGISTRATIONS ({len(pending)}):\n\n"
    for user_id, info in pending.items():
        msg += f"ID: {user_id}\n"
        msg += f"  Nama: {info.get('name', 'N/A')}\n"
        msg += f"  Username: @{info.get('username', 'N/A')}\n"
        msg += f"  Waktu: {info.get('registered_at', 'N/A')}\n\n"

    msg += "Gunakan /approve <id> atau /reject <id>"
    await update.message.reply_text(msg)


@admin_only
async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve <user_id> - Approve registration (admin only)"""
    if not context.args:
        await update.message.reply_text("Format: /approve <user_id>")
        return

    user_id = context.args[0].strip()
    pending = load_pending_registrations()

    if user_id not in pending:
        await update.message.reply_text(f"User {user_id} tidak ditemukan di pending list.")
        return

    # Get user info before removing from pending
    user_info = pending[user_id]

    # Add to allowed users
    users = load_allowed_users()
    if user_id not in users:
        users.append(user_id)
        save_allowed_users(users)

    # Remove from pending
    del pending[user_id]
    save_pending_registrations(pending)

    await update.message.reply_text(
        f"User {user_info.get('name', user_id)} berhasil disetujui!\n"
        f"Total users: {len(users)}"
    )

    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text=(
                f"Selamat! Registrasi Anda telah DISETUJUI.\n\n"
                f"Anda sekarang bisa menggunakan bot ini.\n"
                f"Ketik /help untuk melihat panduan."
            )
        )
    except Exception as e:
        print(f"Failed to notify user {user_id}: {e}")


@admin_only
async def cmd_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reject <user_id> - Reject registration (admin only)"""
    if not context.args:
        await update.message.reply_text("Format: /reject <user_id>")
        return

    user_id = context.args[0].strip()
    pending = load_pending_registrations()

    if user_id not in pending:
        await update.message.reply_text(f"User {user_id} tidak ditemukan di pending list.")
        return

    # Get user info before removing
    user_info = pending[user_id]

    # Remove from pending
    del pending[user_id]
    save_pending_registrations(pending)

    await update.message.reply_text(
        f"Registrasi {user_info.get('name', user_id)} ditolak."
    )

    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text="Maaf, registrasi Anda tidak disetujui oleh admin."
        )
    except Exception as e:
        print(f"Failed to notify user {user_id}: {e}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "Perintah tidak dikenali.\nGunakan /help untuk melihat daftar perintah."
    )


# ===== Bot Setup =====
async def set_commands(application: Application):
    """Set bot commands for menu"""
    commands = [
        BotCommand("start", "Mulai bot"),
        BotCommand("help", "Bantuan"),
        BotCommand("surah", "Mulai surah: /surah <N>"),
        BotCommand("next", "Analisis ayat berikutnya"),
        BotCommand("verse", "Jump ke ayat: /verse <N>"),
        BotCommand("prev", "Kembali 1 ayat"),
        BotCommand("status", "Status session + progress"),
        BotCommand("clear", "Clear conversation"),
        BotCommand("cancel", "Batalkan session"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """Start the bot"""
    print("=" * 50)
    print("QURAN ANALYSIS TELEGRAM BOT")
    print("Verse-by-Verse with Section Context (1,966 thematic divisions)")
    print("=" * 50)

    # Validate config
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    if not TELEGRAM_ADMIN_USER:
        print("WARNING: TELEGRAM_ADMIN_USER not set in .env")

    print(f"Admin user: {TELEGRAM_ADMIN_USER}")
    print(f"Allowed users: {load_allowed_users()}")

    # Initialize components
    initialize_components()

    # Create application with custom request timeouts
    print("Creating Telegram application...")
    import httpx
    # Force IPv4 to avoid IPv6 connectivity issues
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
        httpx_kwargs={"transport": transport}
    )
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .request(request)
        .build()
    )

    # Add handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("surah", cmd_surah))
    application.add_handler(CommandHandler("verse", cmd_verse))
    application.add_handler(CommandHandler("v", cmd_verse))  # Alias
    application.add_handler(CommandHandler("next", cmd_next))
    application.add_handler(CommandHandler("n", cmd_next))  # Alias
    application.add_handler(CommandHandler("prev", cmd_prev))
    application.add_handler(CommandHandler("p", cmd_prev))  # Alias
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("clear", cmd_clear))
    application.add_handler(CommandHandler("cancel", cmd_cancel))

    # Admin commands
    application.add_handler(CommandHandler("adduser", cmd_adduser))
    application.add_handler(CommandHandler("removeuser", cmd_removeuser))
    application.add_handler(CommandHandler("listusers", cmd_listusers))
    application.add_handler(CommandHandler("myid", cmd_myid))

    # Registration commands
    application.add_handler(CommandHandler("register", cmd_register))
    application.add_handler(CommandHandler("pending", cmd_pending))
    application.add_handler(CommandHandler("approve", cmd_approve))
    application.add_handler(CommandHandler("reject", cmd_reject))

    # Handle unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Handle free text (chat)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler for network issues
    async def error_handler(update, context):
        """Handle errors gracefully"""
        import logging
        logging.warning(f"Update {update} caused error: {context.error}")
        # Don't crash on network errors, just log them

    application.add_error_handler(error_handler)

    # Set commands on startup
    application.post_init = set_commands

    # Start bot
    print("Bot is running... Press Ctrl+C to stop")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        bootstrap_retries=5,  # Retry on network errors during startup
        drop_pending_updates=True  # Ignore old messages
    )


if __name__ == "__main__":
    main()
