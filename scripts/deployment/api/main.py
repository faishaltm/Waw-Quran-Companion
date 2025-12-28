"""
FastAPI Main Application
Endpoints for Quran reading system
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cache_manager import CacheManager
from api.session_manager import SessionManager
from api.chapter_context_generator import ChapterContextGenerator
from api.verse_analyzer import VerseAnalyzer
from api.data_loader import QuranDataLoader
from config.settings import OPENAI_API_KEY, validate_config

# Initialize FastAPI app
app = FastAPI(
    title="Quran Reading API",
    description="API for verse-by-verse Quran reading with intelligent context management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (global)
cache_manager = CacheManager()
session_manager = SessionManager(cache_manager)
data_loader = QuranDataLoader()

# OpenAI client (will be initialized in startup)
openai_client = None
chapter_generator = None
verse_analyzer = None


# ===== Pydantic Models =====

class ReadingRequest(BaseModel):
    """Request to start reading session"""
    verse_range: str  # Format: "68:1-10"
    user_id: str = None  # Optional user identifier


class ContinueRequest(BaseModel):
    """Request to continue to next verse"""
    pass  # No body needed, session_id in path


# ===== Startup/Shutdown Events =====

@app.on_event("startup")
async def startup_event():
    """Initialize OpenAI client and components on startup"""
    global openai_client, chapter_generator, verse_analyzer

    print("Initializing Quran Reading API...")

    # Validate configuration
    try:
        validate_config()
        print("  Configuration validated")
    except Exception as e:
        print(f"  Configuration error: {e}")
        raise

    # Initialize OpenAI client
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("  OpenAI client initialized")

    # Initialize generators
    chapter_generator = ChapterContextGenerator(cache_manager, openai_client)
    verse_analyzer = VerseAnalyzer(cache_manager, session_manager, openai_client)
    print("  Chapter generator and verse analyzer initialized")

    print("API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Quran Reading API...")
    # Cleanup old sessions
    deleted = session_manager.cleanup_old_sessions(days_old=7)
    print(f"  Cleaned up {deleted} old sessions")
    print("API shut down")


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Quran Reading API",
        "version": "1.0.0",
        "endpoints": {
            "start_reading": "POST /start",
            "continue_reading": "POST /sessions/{session_id}/continue",
            "get_progress": "GET /sessions/{session_id}/progress",
            "cache_stats": "GET /cache/stats"
        }
    }


@app.post("/start")
async def start_reading(request: ReadingRequest) -> Dict[str, Any]:
    """
    Start new reading session

    Args:
        request: ReadingRequest with verse_range (e.g., "68:1-10")

    Returns:
        Session info with chapter context
    """
    try:
        # Parse verse range
        surah_num, verse_nums = data_loader.parse_verse_range(request.verse_range)

        print(f"\n=== Starting session for {request.verse_range} ===")

        # Generate/retrieve chapter context
        chapter_context = chapter_generator.get_or_generate(surah_num)

        # Create session
        session_id = session_manager.create_session(
            surah_num,
            verse_nums,
            user_id=request.user_id
        )

        # Get chapter metadata
        chapter_meta = data_loader.get_chapter_metadata(surah_num)

        return {
            "session_id": session_id,
            "surah": surah_num,
            "surah_name": chapter_meta['name'],
            "verse_range": verse_nums,
            "total_verses": len(verse_nums),
            "chapter_context": chapter_context,
            "message": "Chapter context ready. Use /sessions/{session_id}/continue to read first verse.",
            "next_action": f"/sessions/{session_id}/continue"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/sessions/{session_id}/continue")
async def continue_reading(session_id: str) -> Dict[str, Any]:
    """
    Continue to next verse in session

    Args:
        session_id: Session UUID

    Returns:
        Verse analysis and progress
    """
    try:
        # Get session state
        try:
            state = session_manager.get_state(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if session complete
        if session_manager.is_complete(session_id):
            progress = session_manager.get_progress(session_id)
            return {
                "complete": True,
                "message": "Session complete! All verses have been read.",
                "progress": progress
            }

        # Get next verse to analyze
        next_verse = session_manager.get_next_verse(session_id)

        print(f"\n=== Analyzing verse {state['surah']}:{next_verse} ===")

        # Analyze verse
        analysis = verse_analyzer.analyze_verse(
            state['surah'],
            next_verse,
            session_id
        )

        # Get updated progress
        progress = session_manager.get_progress(session_id)

        return {
            "session_id": session_id,
            "verse": next_verse,
            "surah": state['surah'],
            "analysis": analysis['explanation'],
            "from_cache": analysis.get('from_cache', False),
            "tokens_used": analysis.get('tokens_used', 0),
            "mode": analysis.get('mode', 'unknown'),
            "progress": progress,
            "complete": progress['complete'],
            "next_action": f"/sessions/{session_id}/continue" if not progress['complete'] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/sessions/{session_id}/progress")
async def get_progress(session_id: str) -> Dict[str, Any]:
    """
    Get session progress

    Args:
        session_id: Session UUID

    Returns:
        Progress statistics
    """
    try:
        try:
            progress = session_manager.get_progress(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

        return progress

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/sessions/{session_id}/state")
async def get_session_state(session_id: str) -> Dict[str, Any]:
    """
    Get full session state (for debugging)

    Args:
        session_id: Session UUID

    Returns:
        Complete session state
    """
    try:
        try:
            state = session_manager.get_state(session_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

        return state

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics

    Returns:
        Cache stats
    """
    try:
        stats = cache_manager.get_cache_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.delete("/cache/clear")
async def clear_cache(cache_type: str = "all") -> Dict[str, Any]:
    """
    Clear cache (use with caution!)

    Args:
        cache_type: "chapters", "verses", "sessions", or "all"

    Returns:
        Success message
    """
    try:
        success = cache_manager.clear_cache(cache_type)

        if success:
            return {
                "success": True,
                "message": f"Cleared {cache_type} cache"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """
    Delete session

    Args:
        session_id: Session UUID

    Returns:
        Success message
    """
    try:
        success = cache_manager.delete_session(session_id)

        if success:
            return {
                "success": True,
                "message": f"Deleted session {session_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ===== Health Check =====

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
