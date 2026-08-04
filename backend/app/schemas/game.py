"""
schemas/game.py — Pydantic models for game-related API responses.

These models normalise data from RAWG and CheapShark into
consistent shapes that Vue components can rely on.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


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

    id: Union[int, str]
    name: str
    slug: str
    background_image: Optional[str] = None
    released: Optional[str] = None
    metacritic: Optional[int] = None
    rating: Optional[float] = None
    ratings_count: Optional[int] = None
    genres: Optional[List[Genre]] = []
    platforms: Optional[List[Dict[str, Any]]] = []
    tags: Optional[List[Dict[str, Any]]] = []
    short_screenshots: Optional[List[Dict[str, Any]]] = []


class UnifiedPrice(BaseModel):
    currency: str = "USD"
    initial: float = 0.0
    final: float = 0.0
    discount_percent: int = 0
    store_name: Optional[str] = None
    url: Optional[str] = None
    source: str

class UnifiedHistoricalLow(BaseModel):
    amount: float = 0.0
    store_name: str
    date: str
    url: Optional[str] = None
    source: str

class UnifiedPlayers(BaseModel):
    live: int = 0
    peak_24h: int = 0
    peak_all_time: int = 0
    source: str = "SteamCharts"

class UnifiedTrailer(BaseModel):
    url: str
    poster: Optional[str] = None
    is_youtube_fallback: bool = False

class UnifiedGameDetail(BaseModel):
    """
    Unified game detail — gracefully merged from RAWG, Steam, ITAD, CheapShark, etc.
    This is what GET /api/games/{id} returns to the frontend.
    """

    id: Union[int, str]
    title: str
    slug: str
    description: str
    hero_image: Optional[str] = None
    cover_image: Optional[str] = None

    # Meta
    released: Optional[str] = None
    metacritic: Optional[int] = None
    website: Optional[str] = None
    esrb_rating: Optional[Dict[str, Any]] = None
    
    # Collections
    screenshots: List[str] = []
    genres: List[str] = []
    developers: List[str] = []
    publishers: List[str] = []
    platforms: List[str] = []
    
    # Enrichment from Steam
    languages: List[str] = []
    categories: List[str] = []
    achievements_total: int = 0
    
    # Fallback-Prioritized Blocks
    price: Optional[UnifiedPrice] = None
    historical_low: Optional[UnifiedHistoricalLow] = None
    players: Optional[UnifiedPlayers] = None
    trailer: Optional[UnifiedTrailer] = None
    
    # Extra data arrays
    store_deals: List[Dict[str, Any]] = []
    bundles: List[Dict[str, Any]] = []
    
    # Metadata
    rawg_url: Optional[str] = None
    steam_url: Optional[str] = None
    aggregated_at: str
