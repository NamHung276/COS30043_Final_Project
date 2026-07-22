"""
schemas/game.py — Pydantic models for game-related API responses.

These models normalise data from RAWG and CheapShark into
consistent shapes that Vue components can rely on.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Platform(BaseModel):
    id: int
    name: str
    slug: str


class Genre(BaseModel):
    id: int
    name: str
    slug: str


class Developer(BaseModel):
    id: int
    name: str
    slug: str


class Publisher(BaseModel):
    id: int
    name: str
    slug: str


class Store(BaseModel):
    id: int
    name: str
    slug: str
    url: Optional[str] = None


class Screenshot(BaseModel):
    id: int
    image: str
    width: Optional[int] = None
    height: Optional[int] = None


class Trailer(BaseModel):
    id: int
    name: str
    preview: Optional[str] = None
    data: Optional[Dict[str, Any]] = None  # RAWG returns {480, max} quality URLs


class Deal(BaseModel):
    """A single deal from CheapShark for a game."""

    deal_id: str = Field(alias="dealID")
    store_id: str = Field(alias="storeID")
    store_name: Optional[str] = None
    sale_price: str = Field(alias="salePrice")
    normal_price: str = Field(alias="normalPrice")
    savings: str
    metacritic_score: Optional[str] = Field(default=None, alias="metacriticScore")
    deal_rating: Optional[str] = Field(default=None, alias="dealRating")
    thumb: Optional[str] = None
    game_name: Optional[str] = Field(default=None, alias="title")
    is_on_sale: Optional[str] = Field(default=None, alias="isOnSale")
    steam_app_id: Optional[str] = Field(default=None, alias="steamAppID")

    model_config = {"populate_by_name": True}


class GameSummary(BaseModel):
    """Lightweight game card — used in lists and search results."""

    id: int
    name: str
    slug: str
    background_image: Optional[str] = None
    released: Optional[str] = None
    metacritic: Optional[int] = None
    rating: Optional[float] = None
    ratings_count: Optional[int] = None
    genres: List[Genre] = []
    platforms: List[Dict[str, Any]] = []
    tags: List[Dict[str, Any]] = []
    short_screenshots: List[Dict[str, Any]] = []


class GameDetail(BaseModel):
    """
    Aggregated game detail — combines RAWG + CheapShark into one response.
    This is what GET /api/games/{id} returns.
    """

    # ── RAWG Fields ──────────────────────────────────────────────────────────────
    id: int
    name: str
    slug: str
    description_raw: Optional[str] = None
    background_image: Optional[str] = None
    background_image_additional: Optional[str] = None
    released: Optional[str] = None
    tba: Optional[bool] = None
    metacritic: Optional[int] = None
    metacritic_url: Optional[str] = None
    rating: Optional[float] = None
    rating_top: Optional[int] = None
    ratings_count: Optional[int] = None
    playtime: Optional[int] = None
    website: Optional[str] = None

    genres: List[Genre] = []
    platforms: List[Dict[str, Any]] = []
    developers: List[Developer] = []
    publishers: List[Publisher] = []
    stores: List[Dict[str, Any]] = []
    tags: List[Dict[str, Any]] = []

    # ── Aggregated Media ─────────────────────────────────────────────────────────
    screenshots: List[Screenshot] = []
    trailers: List[Trailer] = []

    # ── CheapShark Deals ─────────────────────────────────────────────────────────
    deals: List[Deal] = []
    cheapest_deal_price: Optional[str] = None
    cheapest_deal_store: Optional[str] = None

    # ── Meta ─────────────────────────────────────────────────────────────────────
    rawg_url: Optional[str] = None
    aggregated_at: Optional[str] = None  # ISO timestamp of when data was fetched
