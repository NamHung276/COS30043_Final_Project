"""
main.py — FastAPI application entry point for the GameHub backend.

Registers all routers, configures CORS, middleware, logging, and global
exception handlers. Run with:

    uvicorn main:app --reload --port 8000
"""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from pythonjsonlogger import json as jsonlogger

from config import settings
from app.routers import health, games, deals, news, free_games, chatbot, payments, paypal, coingecko
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


# ── Logging Setup ──────────────────────────────────────────────────────────────

def setup_logging() -> None:
    """Configure structured JSON logging for the application."""
    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        handler.setFormatter(formatter)
        log_level = logging.INFO
    else:
        # Human-readable format in development
        formatter = logging.Formatter(
            "%(asctime)s  [%(levelname)-8s]  %(name)s - %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        log_level = logging.DEBUG

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "firebase_admin", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(__name__)


# ── Startup / Shutdown (lifespan) ──────────────────────────────────────────────

_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events using the modern lifespan pattern."""
    # --- startup ---
    logger.info(
        "GameHub API starting",
        extra={
            "version": settings.app_version,
            "env": settings.app_env,
            "port": settings.app_port,
            "cors_origins": settings.cors_origins_list,
        },
    )
    logger.info("Swagger UI available at: http://localhost:%s/docs", settings.app_port)
    yield
    # --- shutdown ---
    uptime = round(time.time() - _start_time, 1)
    logger.info("GameHub API shutting down after %.1fs uptime", uptime)


# ── FastAPI App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GameHub API",
    description=(
        "FastAPI service layer for the GameHub Vue 3 application. "
        "Proxies external gaming APIs, aggregates data, and provides "
        "server-side caching and security."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "GameHub Team",
        "url": "https://github.com/NamHung276/COS30043_Final_Project",
    },
)


# ── Middleware ─────────────────────────────────────────────────────────────────
# Order matters: middleware is applied in reverse registration order.
# CORS must be outermost so preflight requests are handled before rate limiting.

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# ── Routers ────────────────────────────────────────────────────────────────────

API_PREFIX = "/api"

app.include_router(health.router,      prefix=API_PREFIX, tags=["Health"])
app.include_router(games.router,       prefix=API_PREFIX, tags=["Games"])
app.include_router(deals.router,       prefix=API_PREFIX, tags=["Deals"])
app.include_router(news.router,        prefix=API_PREFIX, tags=["News"])
app.include_router(free_games.router,  prefix=API_PREFIX, tags=["Free Games"])
app.include_router(chatbot.router,     prefix=API_PREFIX, tags=["Chatbot (Stub)"])
app.include_router(payments.router,    prefix=API_PREFIX + "/payments", tags=["Payments"])
app.include_router(paypal.router,      prefix=API_PREFIX + "/paypal", tags=["PayPal Checkout"])
app.include_router(coingecko.router,   prefix=API_PREFIX + "/crypto", tags=["Crypto (CoinGecko)"])


# ── Global Exception Handlers ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any unhandled exception — returns a structured error response."""
    logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
            "error_type": type(exc).__name__,
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.is_development else "An unexpected error occurred.",
            "path": request.url.path,
        },
    )


# ── Root Redirect ──────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to Swagger docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
