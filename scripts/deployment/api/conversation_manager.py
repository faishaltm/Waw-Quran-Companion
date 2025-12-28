"""
Conversation Manager for Real Chat Session
Maintains conversation history and handles OpenAI interactions
"""
import json
import sys
from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.data_loader import QuranDataLoader
from config.settings import (
    get_balaghah_guide_path,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    CONTEXT_WINDOW_THRESHOLD
)


class ConversationManager:
    """
    Manages real conversation sessions with OpenAI
    - Maintains conversation history
    - Balaghah guide sent once at start
    - Supports free chat and verse analysis
    - Auto-summarize when approaching token limit
    """

    # Token threshold for triggering summarize (80% of limit)
    SUMMARIZE_THRESHOLD = int(CONTEXT_WINDOW_THRESHOLD * 0.8)

    def __init__(
        self,
        cache_manager: CacheManager,
        session_manager: SessionManager,
        openai_client: OpenAI,
        data_loader: QuranDataLoader = None
    ):
        """
        Initialize conversation manager

        Args:
            cache_manager: Cache manager instance
            session_manager: Session manager instance
            openai_client: OpenAI client instance
            data_loader: Data loader instance (optional, will create if not provided)
        """
        self.cache = cache_manager
        self.session = session_manager
        self.client = openai_client
        self.loader = data_loader or QuranDataLoader()

        # Load balaghah guide once
        guide_path = get_balaghah_guide_path()
        with open(guide_path, 'r', encoding='utf-8') as f:
            self.balaghah_guide = f.read()

        # Load verse analysis prompt
        verse_prompt_path = Path(__file__).parent.parent / "prompts" / "verse_analysis_prompt.txt"
        with open(verse_prompt_path, 'r', encoding='utf-8') as f:
            self.verse_analysis_prompt = f.read()

    def start_conversation(
        self,
        session_id: str,
        surah_num: int,
        chapter_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start a new conversation with system prompt + balaghah guide + chapter context

        Args:
            session_id: Session UUID
            surah_num: Surah number
            chapter_context: Chapter context dict (from ChapterContextGenerator)

        Returns:
            Conversation dict
        """
        # Build system prompt
        system_content = self._build_system_prompt(surah_num, chapter_context)

        # Create conversation structure
        conversation = {
            "session_id": session_id,
            "surah": surah_num,
            "created_at": datetime.now().isoformat(),
            "messages": [
                {"role": "system", "content": system_content}
            ],
            "estimated_tokens": self._estimate_tokens(system_content),
            "summarize_history": [],
            "current_verse": 0
        }

        # Save to file
        self.cache.save_conversation(session_id, conversation)

        return conversation

    def _build_system_prompt(self, surah_num: int, chapter_context: Dict[str, Any]) -> str:
        """
        Build system prompt with balaghah guide and chapter context

        Args:
            surah_num: Surah number
            chapter_context: Chapter context dict

        Returns:
            System prompt string
        """
        # Get chapter metadata
        chapter_meta = self.loader.get_chapter_metadata(surah_num)

        system_prompt = f"""Anda adalah asisten analisis Al-Quran yang ahli dalam balaghah (retorika Arab).

PANDUAN BALAGHAH:
{self.balaghah_guide}

KONTEKS SURAH {surah_num} ({chapter_meta.get('name_arabic', '')}):
Konteks surah telah diberikan di pesan pertama Anda. Gunakan informasi tersebut untuk analisis.

INSTRUKSI:
1. Ketika user meminta analisis ayat, berikan penjelasan mendalam dalam Bahasa Indonesia
2. Identifikasi dan jelaskan perangkat balaghah yang ada
3. Hubungkan dengan konteks surah (yang sudah Anda jelaskan) dan ayat sebelumnya (munasabat)
4. Gunakan bahasa yang mudah dipahami pembaca umum
5. Jika user bertanya tentang topik lain terkait ayat, jawab berdasarkan pengetahuan Anda
6. Selalu merujuk pada data yang diberikan (tafsir, morfologi, dll) jika relevan"""

        return system_prompt

    def start_conversation_with_introduction(
        self,
        session_id: str,
        surah_num: int,
        user_introduction: str
    ) -> None:
        """
        Initialize conversation with user_introduction as first assistant message

        This creates a conversation where the user_introduction is the first message
        from the assistant, establishing context for all subsequent interactions.

        Args:
            session_id: Conversation session ID
            surah_num: Surah number
            user_introduction: Comprehensive chapter introduction text
        """
        # Build simplified system prompt (no chapter context - it's in first message)
        system_prompt = self._build_system_prompt(surah_num, chapter_context=None)

        # Initialize conversation with user_introduction as first assistant message
        conversation = {
            "session_id": session_id,
            "surah": surah_num,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": user_introduction}  # KEY: First message
            ],
            "estimated_tokens": self._estimate_tokens(system_prompt + user_introduction),
            "created_at": datetime.now().isoformat()
        }

        # Save conversation to cache
        self.cache.save_conversation(session_id, conversation)

        print(f"[ConversationManager] Initialized conversation with introduction ({len(user_introduction)} chars)")

    def send_message(
        self,
        session_id: str,
        user_message: str,
        include_verse_data: Dict = None
    ) -> str:
        """
        Send a message and get response, maintaining conversation history

        Args:
            session_id: Session UUID
            user_message: User's message
            include_verse_data: Optional verse data to include with message

        Returns:
            Assistant's response text
        """
        # Load conversation
        conversation = self.cache.get_conversation(session_id)
        if not conversation:
            raise ValueError(f"Conversation {session_id} not found")

        # Check if need to summarize
        if conversation.get('estimated_tokens', 0) > self.SUMMARIZE_THRESHOLD:
            conversation = self._summarize_and_reset(session_id, conversation)

        # Build user message content
        if include_verse_data:
            user_content = json.dumps({
                "message": user_message,
                "verse_data": include_verse_data
            }, ensure_ascii=False)
        else:
            user_content = user_message

        # Add user message to history
        conversation['messages'].append({
            "role": "user",
            "content": user_content
        })

        # Send to OpenAI
        response_text, tokens_used = self._call_openai(conversation['messages'])

        # Add assistant response to history
        conversation['messages'].append({
            "role": "assistant",
            "content": response_text
        })

        # Update token estimate
        conversation['estimated_tokens'] += self._estimate_tokens(user_content) + self._estimate_tokens(response_text)

        # Save conversation
        self.cache.save_conversation(session_id, conversation)

        return response_text

    def analyze_verse(
        self,
        session_id: str,
        surah_num: int,
        verse_num: int,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a specific verse using the conversation

        Args:
            session_id: Session UUID
            surah_num: Surah number
            verse_num: Verse number
            use_cache: Whether to check verse cache first

        Returns:
            Analysis result dict
        """
        # Check verse cache first
        if use_cache:
            cached = self.cache.get_verse_analysis(surah_num, verse_num)
            if cached:
                # Add cached analysis to conversation as context
                self._add_cached_to_conversation(session_id, verse_num, cached)
                return {
                    "verse": verse_num,
                    "explanation": cached.get('explanation', ''),
                    "from_cache": True,
                    "tokens_used": 0
                }

        # Load verse data
        verse_data = self.loader.get_verse_full_data(surah_num, verse_num)

        # Build detailed analysis prompt using comprehensive template
        user_message = f"""Analisis ayat {surah_num}:{verse_num} dengan struktur 5 paragraf.

{self.verse_analysis_prompt}

DATA AYAT (dalam JSON):
Gunakan data berikut untuk analisis Anda."""

        # Send message with verse data
        response = self.send_message(session_id, user_message, include_verse_data=verse_data)

        # Update current verse in conversation
        conversation = self.cache.get_conversation(session_id)
        if conversation:
            conversation['current_verse'] = verse_num
            self.cache.save_conversation(session_id, conversation)

        # Cache the analysis
        analysis_result = {
            "surah": surah_num,
            "verse": verse_num,
            "explanation": response,
            "tokens_used": self._estimate_tokens(response),
            "from_cache": False
        }
        self.cache.save_verse_analysis(surah_num, verse_num, analysis_result)

        return analysis_result

    def _add_cached_to_conversation(self, session_id: str, verse_num: int, cached: Dict):
        """Add cached analysis to conversation as context (without API call)"""
        conversation = self.cache.get_conversation(session_id)
        if not conversation:
            return

        # Add as a note in conversation
        note = f"[Catatan: Analisis ayat {verse_num} dari cache]\n{cached.get('explanation', '')[:500]}..."

        conversation['messages'].append({
            "role": "assistant",
            "content": note
        })
        conversation['current_verse'] = verse_num
        conversation['estimated_tokens'] += self._estimate_tokens(note)

        self.cache.save_conversation(session_id, conversation)

    def _call_openai(self, messages: List[Dict]) -> tuple:
        """
        Call OpenAI API with streaming

        Args:
            messages: List of message dicts

        Returns:
            tuple: (response_text, tokens_used)
        """
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
                stream=True,
                stream_options={"include_usage": True}
            )

            full_text = ""
            tokens_used = 0
            input_tokens = 0
            output_tokens = 0

            for chunk in response:
                if not chunk.choices:
                    if hasattr(chunk, "usage") and chunk.usage is not None:
                        tokens_used = chunk.usage.total_tokens
                        input_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                        output_tokens = getattr(chunk.usage, 'completion_tokens', 0)
                    continue

                content = chunk.choices[0].delta.content
                if content is not None:
                    # Stream to console
                    try:
                        print(content, end="", flush=True)
                    except UnicodeEncodeError:
                        safe_content = content.encode('ascii', 'replace').decode('ascii')
                        print(safe_content, end="", flush=True)
                    full_text += content

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    tokens_used = chunk.usage.total_tokens
                    input_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                    output_tokens = getattr(chunk.usage, 'completion_tokens', 0)

            print()  # New line after streaming
            print(f"[Token Usage] Input: {input_tokens:,} | Output: {output_tokens:,} | Total: {tokens_used:,}")

            return full_text, tokens_used

        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise

    def _summarize_and_reset(self, session_id: str, conversation: Dict) -> Dict:
        """
        Summarize conversation and start fresh when approaching token limit

        Args:
            session_id: Session UUID
            conversation: Current conversation dict

        Returns:
            New conversation dict with summary
        """
        print("\n[Token limit approaching, summarizing conversation...]\n")

        # Build summarize prompt
        summarize_prompt = f"""Ringkas percakapan analisis Quran ini secara singkat namun informatif:
- Ayat-ayat yang sudah dianalisis dan poin utamanya
- Perangkat balaghah yang teridentifikasi
- Tema penting yang dibahas
- Pertanyaan dan jawaban penting

Buat ringkasan yang bisa digunakan sebagai konteks untuk melanjutkan diskusi."""

        # Get summary (without adding to current conversation)
        messages_for_summary = conversation['messages'] + [
            {"role": "user", "content": summarize_prompt}
        ]

        summary_response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages_for_summary,
            temperature=0.5
        )
        summary_text = summary_response.choices[0].message.content

        # Save old conversation to history
        conversation['summarize_history'].append({
            "summarized_at": datetime.now().isoformat(),
            "messages_count": len(conversation['messages']),
            "summary": summary_text
        })

        # Create new conversation with summary as context
        system_msg = conversation['messages'][0]  # Keep original system prompt

        new_conversation = {
            "session_id": session_id,
            "surah": conversation['surah'],
            "created_at": conversation['created_at'],
            "messages": [
                system_msg,
                {
                    "role": "assistant",
                    "content": f"[Ringkasan percakapan sebelumnya]\n\n{summary_text}"
                }
            ],
            "estimated_tokens": self._estimate_tokens(system_msg['content']) + self._estimate_tokens(summary_text),
            "summarize_history": conversation['summarize_history'],
            "current_verse": conversation.get('current_verse', 0)
        }

        # Save new conversation
        self.cache.save_conversation(session_id, new_conversation)

        print("[Conversation summarized and reset]\n")

        return new_conversation

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough estimate: chars / 4)

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return len(text) // 4

    async def stream_message_async(
        self,
        session_id: str,
        user_message: str,
        on_chunk: Callable[[str], Awaitable[None]] = None,
        include_verse_data: Dict = None
    ) -> str:
        """
        Async streaming message with callback for Telegram integration

        Args:
            session_id: Session UUID
            user_message: User's message
            on_chunk: Async callback called with accumulated text
            include_verse_data: Optional verse data to include

        Returns:
            Complete response text
        """
        # Load conversation
        conversation = self.cache.get_conversation(session_id)
        if not conversation:
            raise ValueError(f"Conversation {session_id} not found")

        # Check if need to summarize
        if conversation.get('estimated_tokens', 0) > self.SUMMARIZE_THRESHOLD:
            conversation = self._summarize_and_reset(session_id, conversation)

        # Build user message content
        if include_verse_data:
            user_content = json.dumps({
                "message": user_message,
                "verse_data": include_verse_data
            }, ensure_ascii=False)
        else:
            user_content = user_message

        # Add user message to history
        conversation['messages'].append({
            "role": "user",
            "content": user_content
        })

        # Stream from OpenAI
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation['messages'],
                temperature=OPENAI_TEMPERATURE,
                stream=True,
                stream_options={"include_usage": True}
            )

            accumulated = ""
            tokens_used = 0
            input_tokens = 0
            output_tokens = 0

            for chunk in response:
                if not chunk.choices:
                    if hasattr(chunk, "usage") and chunk.usage is not None:
                        tokens_used = chunk.usage.total_tokens
                        input_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                        output_tokens = getattr(chunk.usage, 'completion_tokens', 0)
                    continue

                content = chunk.choices[0].delta.content
                if content:
                    accumulated += content

                    # Call async callback if provided
                    if on_chunk:
                        await on_chunk(accumulated)

                if hasattr(chunk, "usage") and chunk.usage is not None:
                    tokens_used = chunk.usage.total_tokens
                    input_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                    output_tokens = getattr(chunk.usage, 'completion_tokens', 0)

            # Add assistant response to history
            conversation['messages'].append({
                "role": "assistant",
                "content": accumulated
            })

            # Update token estimate
            conversation['estimated_tokens'] += self._estimate_tokens(user_content) + self._estimate_tokens(accumulated)

            # Log token usage
            print(f"[Token Usage] Input: {input_tokens:,} | Output: {output_tokens:,} | Total: {tokens_used:,} | Session: {conversation['estimated_tokens']:,} est.")

            # Save conversation
            self.cache.save_conversation(session_id, conversation)

            return accumulated

        except Exception as e:
            print(f"Error in stream_message_async: {e}")
            raise

    async def analyze_verse_async(
        self,
        session_id: str,
        surah_num: int,
        verse_num: int,
        on_chunk: Callable[[str], Awaitable[None]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Async verse analysis with streaming callback

        Args:
            session_id: Session UUID
            surah_num: Surah number
            verse_num: Verse number
            on_chunk: Async callback for streaming updates
            use_cache: Whether to check verse cache first

        Returns:
            Analysis result dict
        """
        # Check verse cache first
        if use_cache:
            cached = self.cache.get_verse_analysis(surah_num, verse_num)
            if cached:
                # Add cached analysis to conversation as context
                self._add_cached_to_conversation(session_id, verse_num, cached)

                # If callback provided, send cached content
                if on_chunk:
                    await on_chunk(cached.get('explanation', ''))

                return {
                    "verse": verse_num,
                    "explanation": cached.get('explanation', ''),
                    "from_cache": True,
                    "tokens_used": 0
                }

        # Load verse data
        verse_data = self.loader.get_verse_full_data(surah_num, verse_num)

        # Build detailed analysis prompt using comprehensive template
        user_message = f"""Analisis ayat {surah_num}:{verse_num} dengan struktur 5 paragraf.

{self.verse_analysis_prompt}

DATA AYAT (dalam JSON):
Gunakan data berikut untuk analisis Anda."""

        # Stream message with verse data
        response = await self.stream_message_async(
            session_id,
            user_message,
            on_chunk=on_chunk,
            include_verse_data=verse_data
        )

        # Update current verse in conversation
        conversation = self.cache.get_conversation(session_id)
        if conversation:
            conversation['current_verse'] = verse_num
            self.cache.save_conversation(session_id, conversation)

        # Cache the analysis
        analysis_result = {
            "surah": surah_num,
            "verse": verse_num,
            "explanation": response,
            "tokens_used": self._estimate_tokens(response),
            "from_cache": False
        }
        self.cache.save_verse_analysis(surah_num, verse_num, analysis_result)

        return analysis_result

    def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a conversation

        Args:
            session_id: Session UUID

        Returns:
            Stats dict
        """
        conversation = self.cache.get_conversation(session_id)
        if not conversation:
            return {"error": "Conversation not found"}

        return {
            "session_id": session_id,
            "surah": conversation.get('surah'),
            "messages_count": len(conversation.get('messages', [])),
            "estimated_tokens": conversation.get('estimated_tokens', 0),
            "token_limit": CONTEXT_WINDOW_THRESHOLD,
            "usage_percent": round(conversation.get('estimated_tokens', 0) / CONTEXT_WINDOW_THRESHOLD * 100, 1),
            "summarize_count": len(conversation.get('summarize_history', [])),
            "current_verse": conversation.get('current_verse', 0)
        }

    # ===== Ruku-Based Session Methods =====

    def start_ruku_conversation(
        self,
        session_id: str,
        surah_num: int,
        ruku_index: int,
        chapter_context: Dict[str, Any],
        accumulated_summary: Optional[Dict] = None,
        current_ruku_data: Optional[Dict] = None,
        next_ruku_preview: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start a new conversation for a specific ruku with accumulated context

        Args:
            session_id: Session UUID
            surah_num: Surah number
            ruku_index: 0-based ruku index within chapter
            chapter_context: Chapter context dict
            accumulated_summary: Summary from previous rukus (optional)
            current_ruku_data: Full data for current ruku
            next_ruku_preview: Preview of next ruku

        Returns:
            Conversation dict
        """
        # Build enhanced system prompt with ruku context
        system_content = self._build_ruku_system_prompt(
            surah_num,
            ruku_index,
            chapter_context,
            accumulated_summary,
            current_ruku_data,
            next_ruku_preview
        )

        # Create conversation structure
        conversation = {
            "session_id": session_id,
            "surah": surah_num,
            "ruku_index": ruku_index,
            "created_at": datetime.now().isoformat(),
            "messages": [
                {"role": "system", "content": system_content}
            ],
            "estimated_tokens": self._estimate_tokens(system_content),
            "summarize_history": [],
            "current_verse": current_ruku_data.get('ruku_info', {}).get('verse_start', 0) if current_ruku_data else 0
        }

        # Save to file
        self.cache.save_conversation(session_id, conversation)

        return conversation

    def _build_ruku_system_prompt(
        self,
        surah_num: int,
        ruku_index: int,
        chapter_context: Dict[str, Any],
        accumulated_summary: Optional[Dict],
        current_ruku_data: Optional[Dict],
        next_ruku_preview: Optional[Dict]
    ) -> str:
        """
        Build system prompt for ruku-based session

        Args:
            surah_num: Surah number
            ruku_index: Ruku index
            chapter_context: Chapter context
            accumulated_summary: Previous rukus summary
            current_ruku_data: Current ruku data
            next_ruku_preview: Next ruku preview

        Returns:
            System prompt string
        """
        chapter_meta = self.loader.get_chapter_metadata(surah_num)
        context_text = self._format_chapter_context(chapter_context, chapter_meta)

        # Build accumulated summary section
        accumulated_text = ""
        if accumulated_summary and accumulated_summary.get('accumulated_summary'):
            acc = accumulated_summary['accumulated_summary']
            parts = []

            if acc.get('themes'):
                parts.append(f"Tema: {', '.join(acc['themes'][:5])}")

            if acc.get('balaghah_correlations'):
                correlations = []
                for c in acc['balaghah_correlations'][:5]:
                    correlations.append(f"- {c.get('device')}: ayat {c.get('verses', [])}")
                parts.append(f"Balaghah berkorelasi:\n" + "\n".join(correlations))

            if acc.get('unresolved_patterns'):
                patterns = []
                for p in acc['unresolved_patterns'][:3]:
                    patterns.append(f"- {p.get('type')}: dari ayat {p.get('setup_verse')}")
                parts.append(f"Pola belum selesai:\n" + "\n".join(patterns))

            if acc.get('key_terms'):
                terms = [f"{t.get('term')}" for t in acc['key_terms'][:5]]
                parts.append(f"Istilah kunci: {', '.join(terms)}")

            if parts:
                accumulated_text = "\n\nKONTEKS DARI RUKU SEBELUMNYA:\n" + "\n".join(parts)

        # Build current ruku section
        current_ruku_text = ""
        if current_ruku_data:
            ruku_info = current_ruku_data.get('ruku_info', {})
            current_ruku_text = f"""

RUKU SAAT INI (Ruku {ruku_index + 1}):
Ayat: {ruku_info.get('verse_start')}-{ruku_info.get('verse_end')} ({ruku_info.get('verse_count')} ayat)
"""

        # Build next ruku preview
        preview_text = ""
        if next_ruku_preview and not next_ruku_preview.get('is_last'):
            heading = next_ruku_preview.get('section_heading', '')
            preview_text = f"""

PREVIEW RUKU BERIKUTNYA:
Ayat: {next_ruku_preview.get('verse_start')}-{next_ruku_preview.get('verse_end')}"""
            if heading:
                preview_text += f"\nTema: {heading}"

        system_prompt = f"""Anda adalah asisten analisis Al-Quran yang ahli dalam balaghah (retorika Arab).

PANDUAN BALAGHAH:
{self.balaghah_guide}

KONTEKS SURAH {surah_num} ({chapter_meta.get('name_arabic', '')}):
{context_text}{accumulated_text}{current_ruku_text}{preview_text}

INSTRUKSI:
1. Analisis ayat-ayat dalam ruku ini secara mendalam dalam Bahasa Indonesia
2. Identifikasi dan jelaskan perangkat balaghah yang ada
3. Hubungkan dengan konteks dari ruku sebelumnya jika relevan (munasabat)
4. Perhatikan pola balaghah yang mungkin berlanjut ke ruku berikutnya
5. Gunakan bahasa yang mudah dipahami pembaca umum
6. Catat istilah Arab penting dan device balaghah yang teridentifikasi"""

        return system_prompt

    async def extract_carryover_info(
        self,
        session_id: str,
        surah_num: int,
        ruku_index: int
    ) -> Dict[str, Any]:
        """
        Extract information to carry over to next session

        Args:
            session_id: Current session ID
            surah_num: Surah number
            ruku_index: Completed ruku index

        Returns:
            Extracted info dict
        """
        conversation = self.cache.get_conversation(session_id)
        if not conversation:
            return {}

        # Get ruku verse range for context
        ruku_info = conversation.get('ruku_info', {})
        verse_start = ruku_info.get('verse_start', 1)
        verse_end = ruku_info.get('verse_end', 10)

        extraction_prompt = f"""
Ruku {ruku_index + 1} (ayat {verse_start}-{verse_end}) telah selesai dianalisis.
Ekstrak informasi PENTING yang harus dibawa ke ruku berikutnya.

## FORMAT OUTPUT (JSON only, no other text):
{{
  "themes_developed": ["tema 1 yang berkembang", "tema 2"],
  "balaghah_correlations": [
    {{"device": "nama device", "verses": [1, 5, 8], "note": "akan berlanjut karena..."}}
  ],
  "unresolved_patterns": [
    {{"type": "contrast/parallel/buildup", "setup_verse": 5, "expected": "kemungkinan resolution"}}
  ],
  "key_arabic_terms": [
    {{"term": "istilah Arab", "meaning": "arti", "significance": "kenapa penting"}}
  ],
  "connections_to_track": [
    {{"from_verse": 3, "note": "perlu diingat karena..."}}
  ]
}}

PENTING:
- Output HANYA JSON, tanpa penjelasan tambahan
- Hanya ekstrak yang RELEVAN untuk ruku berikutnya
- Fokus pada pola yang belum selesai
- Maksimal 1500 tokens
"""

        # Add extraction prompt to conversation
        messages = conversation['messages'] + [
            {"role": "user", "content": extraction_prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.3,  # Lower temperature for structured output
                max_completion_tokens=2000  # GPT-5.1 uses max_completion_tokens
            )

            response_text = response.choices[0].message.content

            # Parse JSON from response
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            extraction = json.loads(response_text.strip())
            return extraction

        except json.JSONDecodeError as e:
            print(f"Error parsing extraction JSON: {e}")
            print(f"Response was: {response_text[:500]}")
            return {
                "themes_developed": [],
                "balaghah_correlations": [],
                "unresolved_patterns": [],
                "key_arabic_terms": [],
                "connections_to_track": []
            }
        except Exception as e:
            print(f"Error extracting carryover info: {e}")
            return {}


if __name__ == "__main__":
    # Test conversation manager
    import os
    from cache_manager import CacheManager
    from session_manager import SessionManager

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        exit(1)

    client = OpenAI(api_key=api_key)
    cache = CacheManager()
    session_mgr = SessionManager(cache)

    conv_manager = ConversationManager(cache, session_mgr, client)

    print("ConversationManager initialized successfully")
    print(f"Balaghah guide loaded: {len(conv_manager.balaghah_guide)} chars")
