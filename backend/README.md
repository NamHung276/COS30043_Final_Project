# GameHub — FastAPI Backend

A modular FastAPI service layer for the GameHub Vue 3 application.

## Architecture

```
Vue 3 Frontend
      ↓
FastAPI Backend (port 8000)
      ↓
Firebase Admin SDK + External APIs
      ↓
Firestore / RAWG / CheapShark / NewsAPI
```

## Features

- **API Proxy** — hides API keys from the browser
- **Server-side Caching** — in-memory TTL cache for expensive calls
- **Aggregated Endpoints** — `GET /api/games/{id}` returns RAWG + CheapShark combined
- **News Aggregation** — merges NewsAPI + NewsData.io into one normalised feed
- **Firebase Auth Verification** — optional Bearer token verification via Admin SDK
- **Rate Limiting** — 60 requests/min per IP (in-memory)
- **Request Logging** — every request logged with method, path, status, duration
- **Swagger UI** — auto-generated at `http://localhost:8000/docs`
- **AI/Chatbot stub** — architecture ready at `chatbot/` for future integration

## Quick Start

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Create a Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. (Optional) Firebase Admin SDK

Download a service account key from:
**Firebase Console → Project Settings → Service Accounts → Generate new private key**

Save the downloaded JSON as:
```
backend/firebase-service-account.json
```

> If this file is not present, the backend runs without token verification.
> All public endpoints still work. Protected endpoints return a 503 with a clear message.

### 6. Run the Server

```bash
# From the backend/ directory
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API Base**: `http://localhost:8000/api`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/health`

## Project Structure

```
backend/
├── main.py                        # FastAPI app entry point
├── config.py                      # Settings via python-dotenv
├── requirements.txt
├── .env                           # Real secrets (git-ignored)
├── .env.example                   # Template
├── firebase-service-account.json  # Firebase Admin key (git-ignored)
├── README.md
│
├── app/
│   ├── routers/
│   │   ├── health.py              # GET /api/health
│   │   ├── games.py               # GET /api/games, /api/games/{id}
│   │   ├── deals.py               # GET /api/deals
│   │   ├── news.py                # GET /api/news
│   │   ├── free_games.py          # GET /api/free-games
│   │   └── chatbot.py             # Stub — not implemented
│   │
│   ├── services/
│   │   ├── rawg_service.py        # RAWG API calls
│   │   ├── cheapshark_service.py  # CheapShark API calls
│   │   ├── news_service.py        # NewsAPI + NewsData.io
│   │   ├── free_games_service.py  # FreeToGame API calls
│   │   ├── firebase_service.py    # Firebase Admin SDK
│   │   └── ai_service.py          # AI stub (not implemented)
│   │
│   ├── schemas/
│   │   ├── common.py              # PaginatedResponse, ErrorResponse
│   │   ├── game.py                # GameSummary, GameDetail, Deal
│   │   └── news.py                # NewsArticle, NewsResponse
│   │
│   ├── cache/
│   │   └── memory_cache.py        # In-memory TTL cache
│   │
│   ├── middleware/
│   │   ├── logging_middleware.py  # Request logging
│   │   └── rate_limit.py          # IP-based rate limiter
│   │
│   ├── models/
│   │   └── user.py                # UserContext (auth)
│   │
│   └── utils/
│       ├── helpers.py             # Shared utility functions
│       └── dependencies.py        # FastAPI dependency injection
│
├── chatbot/
│   └── README.md                  # Future AI chatbot placeholder
│
└── tests/
    └── test_health.py             # Basic health endpoint test
```

## API Endpoints

| Method | Path | Description | Cache TTL |
|--------|------|-------------|-----------|
| GET | `/api/health` | Liveness check | None |
| GET | `/api/games` | RAWG game list | 5 min |
| GET | `/api/games/search` | Search games | 5 min |
| GET | `/api/games/{id}` | Aggregated game detail | 10 min |
| GET | `/api/games/{id}/screenshots` | Game screenshots | 10 min |
| GET | `/api/games/{id}/trailers` | Game trailers | 10 min |
| GET | `/api/deals` | CheapShark deals | 15 min |
| GET | `/api/deals/stores` | Store list | 1 hour |
| GET | `/api/news` | Merged gaming news | 10 min |
| GET | `/api/free-games` | FreeToGame list | 30 min |
| GET | `/api/free-games/{id}` | FreeToGame detail | 30 min |
| POST | `/api/chatbot/chat` | AI chat (stub) | N/A |

## Vue Migration Guide

See the [gradual migration plan](../src/services/README.md) for how to redirect Vue API calls to the backend one endpoint at a time.

**Short version**: Update `src/services/api.js` to point to `http://localhost:8000` for each endpoint after verifying it works.

## Running Tests

```bash
cd backend
pytest tests/ -v
```
