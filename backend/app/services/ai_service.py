"""
services/ai_service.py — AI / Chatbot service stub.

This module is intentionally empty. It is a placeholder for future
AI integration (e.g., OpenAI GPT, Google Gemini).

When implementing the chatbot feature:
  1. Add your AI SDK to requirements.txt
  2. Add API keys to .env and config.py
  3. Implement the functions below
  4. Wire up chatbot/router.py to call this service

See also: chatbot/README.md for architecture notes.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Stub Functions ─────────────────────────────────────────────────────────────

async def chat(
    message: str,
    conversation_history: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Process a chat message and return an AI response.

    NOT IMPLEMENTED — returns a stub response.

    Args:
        message:              The user's chat message.
        conversation_history: Prior messages for multi-turn context.
        user_context:         Optional user data (favorites, genres, etc.)
                              for personalised recommendations.

    Returns:
        Dict with keys: response (str), sources (list), intent (str)
    """
    logger.info("AI chat requested but not yet implemented.")
    return {
        "response": (
            "The GameHub AI assistant is coming soon! "
            "This feature is currently under development."
        ),
        "sources": [],
        "intent": "not_implemented",
    }


async def get_game_recommendations(
    user_favorites: Optional[List[int]] = None,
    user_genres: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Generate personalised game recommendations.

    NOT IMPLEMENTED — returns empty list.

    Future implementation will:
      1. Analyse user's favorite game genres from Firestore
      2. Call RAWG for games matching those genres
      3. Optionally rank using an AI model
    """
    logger.info("Recommendations requested but not yet implemented.")
    return []
