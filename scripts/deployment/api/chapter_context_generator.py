"""
Chapter Context Generator
Generates comprehensive understanding of a surah for context
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cache_manager import CacheManager
from api.data_loader import QuranDataLoader
from config.settings import (
    load_prompt,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    SHORT_SURAH_THRESHOLD
)


class ChapterContextGenerator:
    """
    Generates chapter-level understanding using OpenAI
    Uses hybrid approach: full load for short surahs, tool-based for long
    """

    def __init__(self, cache_manager: CacheManager, openai_client: OpenAI, data_loader: QuranDataLoader = None):
        """
        Initialize generator

        Args:
            cache_manager: Cache manager instance
            openai_client: OpenAI client instance
            data_loader: Optional QuranDataLoader instance (reuse to avoid repeated loading)
        """
        self.cache = cache_manager
        self.client = openai_client
        self.loader = data_loader or QuranDataLoader()

    def get_or_generate(self, surah_num: int, force_regenerate: bool = False) -> Dict[str, Any]:
        """
        Get chapter context from cache or generate new

        Args:
            surah_num: Surah number (1-114)
            force_regenerate: Force regeneration even if cached

        Returns:
            Chapter context dict
        """
        # Check cache first
        if not force_regenerate:
            cached = self.cache.get_chapter_context(surah_num)

            print(f"=== CACHE DEBUG START (Surah {surah_num}) ===")

            if cached:
                print(f"  [OK] Cache returned by cache manager")
                print(f"  [DEBUG] Cache type: {type(cached)}")
                print(f"  [DEBUG] Cache keys: {list(cached.keys())}")
                print(f"  [DEBUG] Has 'user_introduction': {'user_introduction' in cached}")
                print(f"  [DEBUG] Has 'main_themes': {'main_themes' in cached}")
                print(f"  [DEBUG] Has 'structure_overview': {'structure_overview' in cached}")
                print(f"  [DEBUG] user_introduction length: {len(cached.get('user_introduction', ''))}")

                # Check if old format (has multiple fields beyond basics)
                if 'user_introduction' not in cached:
                    print(f"  [!] REJECT REASON: Missing 'user_introduction' field")
                    cached = None
                elif 'main_themes' in cached or 'structure_overview' in cached:
                    print(f"  [!] REJECT REASON: Has old format fields")
                    cached = None
                else:
                    print(f"  [OK] CACHE ACCEPTED - Using cached data")
                    print(f"=== CACHE DEBUG END ===")
                    return cached
            else:
                print(f"  [X] Cache manager returned None (file not found or parse error)")

            print(f"=== CACHE DEBUG END ===")

        # Generate new context
        print(f"Generating chapter context for surah {surah_num}...")

        # Determine approach based on surah length
        chapter_meta = self.loader.get_chapter_metadata(surah_num)
        verse_count = chapter_meta['verses_count']  # Fixed: was 'verses'

        if verse_count <= SHORT_SURAH_THRESHOLD:
            context = self._generate_short_surah(surah_num, chapter_meta)
        else:
            context = self._generate_long_surah(surah_num, chapter_meta)

        # Save to cache
        self.cache.save_chapter_context(surah_num, context)

        return context

    def _generate_short_surah(self, surah_num: int, chapter_meta: Dict) -> Dict[str, Any]:
        """
        Generate context for surah (full load approach - used for ALL surahs now)

        Args:
            surah_num: Surah number
            chapter_meta: Chapter metadata

        Returns:
            Chapter context dict
        """
        print(f"Using FULL LOAD approach for surah {surah_num} ({chapter_meta['verses_count']} verses)")

        # Load ALL verses
        all_verses = self.loader.get_all_verses_in_surah(surah_num)

        # Simplify verse data for prompt
        simplified_verses = []
        for v in all_verses:
            simplified_verses.append({
                "verse": v['verse'],
                "arabic": v.get('arabic', ''),
                "english": v.get('english', '')
            })

        # Load surah introduction (Maududi's Tafhim)
        surah_intro = self.loader.get_surah_context(surah_num)

        # Get section headings as dict
        section_headings = self.loader.get_all_section_headings(surah_num)
        section_dict = {}
        for s in section_headings:
            key = f"{s['verse_start']}-{s['verse_end']}"
            section_dict[key] = s['heading']

        # Load prompt template
        system_prompt = load_prompt("chapter_context_short.txt")

        # Prepare RICH metadata like user's example
        metadata = {
            "chapter_number": surah_num,
            "name_arabic": chapter_meta.get('name_arabic', ''),
            "revelation_place": chapter_meta.get('revelation_place', ''),
            "revelation_order": chapter_meta.get('revelation_order', 0),
            "verses_count": chapter_meta.get('verses_count', 0),
            "section_headings": section_dict
        }

        # Add introduction if available
        if surah_intro and isinstance(surah_intro, dict):
            metadata["introduction"] = surah_intro.get('text', '')
            metadata["introduction_source"] = surah_intro.get('source', '')
        elif surah_intro and isinstance(surah_intro, str):
            metadata["introduction"] = surah_intro

        # Prepare user message with rich data
        user_data = {
            "chapter": surah_num,
            "metadata": metadata,
            "verses": simplified_verses
        }

        # Call OpenAI
        try:
            print("Calling OpenAI API...")

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_data, ensure_ascii=False)}
                ],
                temperature=OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}  # Force JSON output
            )

            print("Received response, parsing JSON...")

            # Parse response
            context = json.loads(response.choices[0].message.content)

            print(f"[OK] Generated context (tokens: {response.usage.total_tokens:,})")

            return context

        except Exception as e:
            print(f"Error generating context for surah {surah_num}: {e}")
            raise

    def _generate_long_surah(self, surah_num: int, chapter_meta: Dict) -> Dict[str, Any]:
        """
        Generate context for long surah (tool-augmented approach)

        Args:
            surah_num: Surah number
            chapter_meta: Chapter metadata

        Returns:
            Chapter context dict
        """
        print(f"Using TOOL-BASED approach for surah {surah_num} ({chapter_meta['verses_count']} verses)")

        # Define tool for LLM to retrieve verses
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_verses_range",
                    "description": "Get a range of verses from the current surah to read and understand",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_verse": {
                                "type": "integer",
                                "description": "First verse number to retrieve"
                            },
                            "end_verse": {
                                "type": "integer",
                                "description": "Last verse number to retrieve"
                            }
                        },
                        "required": ["start_verse", "end_verse"]
                    }
                }
            }
        ]

        # Load system prompt
        system_prompt = load_prompt("chapter_context_long.txt")

        # Get section headings for structure
        section_headings = self.loader.get_all_section_headings(surah_num)
        surah_intro = self.loader.get_surah_context(surah_num)

        # Initial message
        initial_data = {
            "surah_number": surah_num,
            "surah_name": chapter_meta.get('name_arabic', 'N/A'),  # Fixed: was 'name'
            "total_verses": chapter_meta['verses_count'],  # Fixed: was 'verses'
            "revelation_place": chapter_meta['revelation_place'],
            "section_headings": section_headings,
            "intro": surah_intro or "No introduction available"
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(initial_data, ensure_ascii=False)}
        ]

        total_tokens = 0
        max_iterations = 10  # Prevent infinite loops

        # Conversation loop
        for iteration in range(max_iterations):
            try:
                print(f"Iteration {iteration + 1}/{max_iterations}... Calling OpenAI...")

                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    tools=tools,
                    temperature=OPENAI_TEMPERATURE
                )

                total_tokens += response.usage.total_tokens
                message = response.choices[0].message

                # Check if LLM wants to call a tool
                if message.tool_calls:
                    # Execute tool calls
                    for tool_call in message.tool_calls:
                        if tool_call.function.name == "get_verses_range":
                            # Parse arguments
                            args = json.loads(tool_call.function.arguments)
                            start_v = args['start_verse']
                            end_v = args['end_verse']

                            print(f"  >> LLM requested verses {start_v}-{end_v}, loading...")

                            # Get verses data
                            verses_data = self._get_verses_range(surah_num, start_v, end_v)

                            print(f"  [OK] Loaded {len(verses_data)} verses")

                            # Add assistant message with tool call
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call.model_dump()]
                            })

                            # Add tool response
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(verses_data, ensure_ascii=False)
                            })
                else:
                    # No more tool calls, LLM is done
                    print("Parsing final JSON response...")

                    # Check if content exists
                    if not message.content:
                        print(f"Warning: Empty response content at iteration {iteration + 1}")
                        print("Retrying...")
                        continue

                    # Debug: show first 200 chars of response (safe print for Unicode)
                    try:
                        print(f"Response preview: {message.content[:200]}...")
                    except UnicodeEncodeError:
                        safe_preview = message.content[:200].encode('ascii', 'replace').decode('ascii')
                        print(f"Response preview: {safe_preview}...")

                    # Parse final response as JSON
                    try:
                        context = json.loads(message.content)
                    except json.JSONDecodeError as je:
                        print(f"JSON parse error: {je}")
                        print(f"Raw content: {message.content[:500]}")
                        # Try to extract JSON from markdown code block
                        import re
                        json_match = re.search(r'```json\s*(.*?)\s*```', message.content, re.DOTALL)
                        if json_match:
                            print("Found JSON in code block, trying to parse...")
                            context = json.loads(json_match.group(1))
                        else:
                            raise

                    print(f"[OK] Generated context (tokens: {total_tokens:,}, iterations: {iteration + 1})")

                    return context

            except Exception as e:
                print(f"Error in iteration {iteration}: {e}")
                raise

        # If we hit max iterations, return error
        raise RuntimeError(f"Max iterations ({max_iterations}) reached for surah {surah_num}")

    def _get_verses_range(self, surah_num: int, start_verse: int, end_verse: int) -> list:
        """
        Tool function: Get range of verses

        Args:
            surah_num: Surah number
            start_verse: First verse
            end_verse: Last verse

        Returns:
            List of verse dicts
        """
        verses = []

        for v in range(start_verse, end_verse + 1):
            verse_data = self.loader.get_verse_full_data(surah_num, v)
            verses.append({
                "verse": v,
                "arabic": verse_data.get('arabic', ''),
                "english": verse_data.get('english', ''),
                "section": verse_data.get('section_heading', '')
            })

        return verses


if __name__ == "__main__":
    # Test chapter context generator
    import os
    from cache_manager import CacheManager

    # Initialize
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        exit(1)

    client = OpenAI(api_key=api_key)
    cache = CacheManager()
    generator = ChapterContextGenerator(cache, client)

    # Test with short surah (Al-Qalam, 68, 52 verses)
    print("Testing short surah (68)...")
    context = generator.get_or_generate(68)
    print(f"Context keys: {context.keys()}")
    print(f"Main themes: {context.get('main_themes', [])}")

    # Test with long surah (Al-Baqarah, 2, 286 verses) - commented out to save cost
    # print("\nTesting long surah (2)...")
    # context = generator.get_or_generate(2)
    # print(f"Context keys: {context.keys()}")
