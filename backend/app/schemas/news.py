"""
schemas/news.py — Pydantic models for gaming news API responses.

Normalises articles from both NewsAPI and NewsData.io into a
single consistent shape so Vue components only deal with one format.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NewsSource(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class NewsArticle(BaseModel):
    """
    A normalised news article.

    Both NewsAPI and NewsData.io articles are mapped into this shape.
    The *provider* field indicates the original source.
    """

    article_id: Optional[str] = Field(default=None, description="Unique article identifier")
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    url_to_image: Optional[str] = Field(default=None, description="Thumbnail image URL")
    published_at: Optional[str] = Field(default=None, description="ISO 8601 publication date")
    source: Optional[NewsSource] = None
    author: Optional[str] = None
    category: Optional[str] = None
    provider: str = Field(description="'newsapi' or 'newsdata'")


class NewsResponse(BaseModel):
    """Response envelope for the /api/news endpoint."""

    articles: List[NewsArticle]
    total_results: int
    sources: List[str] = Field(description="API sources that contributed to this response")
    fetched_at: Optional[str] = None
# Schemas package
