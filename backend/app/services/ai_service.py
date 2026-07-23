"""
services/ai_service.py — AI / Chatbot service implementation using Google Gemini.
"""

import logging
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
client = None
if settings.gemini_api_key:
    client = genai.Client(api_key=settings.gemini_api_key)
else:
    logger.warning("GEMINI_API_KEY is not set. Chatbot will not function correctly.")

# System instructions to give the bot its persona
SYSTEM_INSTRUCTION = (
    "You are the GameHub AI Assistant, a helpful and knowledgeable gaming expert. "
    "Your role is to help users discover new games, track deals, and stay updated on gaming news. "
    "Do NOT use marketing fluff or hyperbolic claims like 'The Ultimate Gaming Platform' or "
    "'World's #1 Gaming Hub'. Focus on providing factual, helpful, and objective information. "
    "If a user asks about non-gaming topics, politely guide the conversation back to video games."
)


async def chat(
    message: str,
    conversation_history: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Process a chat message and return an AI response using Google Gemini.
    """
    if not client:
        return {
            "response": "I'm sorry, my AI backend is not configured yet. (Missing GEMINI_API_KEY).",
            "sources": [],
            "intent": "error",
        }

    try:
        # Convert our history format to Gemini's format
        gemini_history: List[Any] = []
        if conversation_history:
            for msg in conversation_history:
                # Map 'assistant' to 'model' for Gemini
                role = "model" if msg.get("role") == "assistant" else "user"
                gemini_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))]
                    )
                )

        chat_session = client.chats.create(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
            history=gemini_history
        )
        
        response = chat_session.send_message(message)

        return {
            "response": response.text,
            "sources": [],
            "intent": "general_chat",
        }
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return {
            "response": "I'm having trouble connecting to my brain right now. Please try again later.",
            "sources": [],
            "intent": "error",
        }


async def get_game_recommendations(
    user_favorites: Optional[List[int]] = None,
    user_genres: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Generate personalised game recommendations.
    Currently returns an empty list, to be implemented in a future phase.
    """
    logger.info("Recommendations requested but not yet implemented.")
    return []
