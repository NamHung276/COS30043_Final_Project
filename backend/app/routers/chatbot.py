"""
routers/chatbot.py — AI chatbot endpoints.

This router provides endpoints to interact with the GameHub AI assistant.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response Schemas ─────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous conversation turns for multi-turn context",
    )


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    intent: Optional[str] = None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/chatbot/chat",
    response_model=ChatResponse,
    summary="Chat with GameHub AI",
    description=(
        "Interact with the GameHub AI assistant. "
        "Provides gaming knowledge, game discovery, and general help."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await ai_service.chat(
        message=request.message,
        conversation_history=[m.model_dump() for m in (request.history or [])],
    )
    return ChatResponse(**result)


@router.get(
    "/chatbot/recommendations",
    summary="Game recommendations (stub)",
    description=(
        "**Not yet implemented.** Will return personalised game recommendations "
        "based on the user's favorites and genre preferences."
    ),
)
async def get_recommendations():
    recommendations = await ai_service.get_game_recommendations()
    return {
        "recommendations": recommendations,
        "message": "AI recommendations are coming soon.",
    }
