# Chatbot — Future AI Integration

This directory is reserved for the GameHub AI chatbot and recommendation engine.

## Planned Architecture

```
chatbot/
├── __init__.py
├── README.md                  ← This file
├── router.py                  ← FastAPI router (stub is at app/routers/chatbot.py)
├── conversation_manager.py    ← Multi-turn context handling
├── intent_classifier.py       ← Classify user intent (search, recommend, info)
└── prompts/
    ├── system_prompt.txt      ← Base system prompt
    └── game_expert.txt        ← Domain-specific gaming knowledge prompt
```

## Planned Capabilities

### Phase A — Game Information Q&A
- Answer questions about game genres, platforms, release dates
- Pull live data from RAWG via `rawg_service.py`
- Example: "What are the best RPGs released in 2024?"

### Phase B — Personalised Recommendations
- Read user's favorites and review history from Firestore (via firebase_service)
- Generate recommendations based on genre preferences
- Example: "I loved Elden Ring, what should I play next?"

### Phase C — Deal Alerts
- Notify users when a wishlisted game goes on sale
- Integrate with CheapShark via `cheapshark_service.py`

## Implementation Steps

1. Choose an AI provider:
   - **OpenAI** (`pip install openai`) — add `OPENAI_API_KEY` to `.env`
   - **Google Gemini** (`pip install google-generativeai`) — add `GEMINI_API_KEY` to `.env`

2. Add the key to `config.py`:
   ```python
   openai_api_key: str = Field(default="", description="OpenAI API key")
   ```

3. Implement `app/services/ai_service.py`:
   - The stub functions are already in place — just fill them in.

4. Add conversation history storage:
   - Option A: In-memory (resets on restart, fine for demos)
   - Option B: Firestore collection `chatSessions/{uid}/messages`

5. Update `app/routers/chatbot.py` to remove the stub comments.

## Current Status

🚧 **Not implemented.** The router is registered and returns placeholder responses.
All stubs are in `app/services/ai_service.py` and `app/routers/chatbot.py`.
