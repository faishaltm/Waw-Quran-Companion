"""
Pydantic models for deployment API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ReadingRequest(BaseModel):
    """Request to start reading session"""
    verse_range: str  # Format: "68:1-10"


class ChapterContext(BaseModel):
    """Chapter-level understanding"""
    surah_number: int
    surah_name: str
    main_themes: List[str]
    structure: Dict[str, Any]
    key_verses: Dict[str, str]
    narrative_flow: str
    revelation_context: str


class VerseAnalysis(BaseModel):
    """Verse-level analysis result"""
    surah: int
    verse: int
    explanation: str
    tokens_used: int
    has_balaghah_guide: bool
    context_reset: bool = False
    from_cache: bool = False


class SessionState(BaseModel):
    """Active reading session state"""
    session_id: str
    surah: int
    verse_range: List[int]
    created_at: str
    verses_analyzed: int
    verses_analyzed_list: List[Dict[str, Any]]
    total_tokens: int
    conversation_id: Optional[str] = None
    context_resets: int = 0


class VerseData(BaseModel):
    """Complete verse data"""
    surah: int
    verse: int
    arabic: str
    english: str
    section_heading: Optional[str] = None
    morphology: Optional[List[Dict]] = None
    tafsir: Optional[Dict[str, str]] = None
    balaghah_features: Optional[Dict] = None
    asbab_nuzul: Optional[Any] = None
    root_repetitions: Optional[Dict] = None
