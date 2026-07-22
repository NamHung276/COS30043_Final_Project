"""
utils/dependencies.py — FastAPI dependency injection functions.

These are used with FastAPI's Depends() system in route handlers.

Usage in a router:
    from app.utils.dependencies import get_current_user, get_optional_user
    from app.models.user import UserContext

    @router.get("/protected")
    async def protected_route(user: UserContext = Depends(get_current_user)):
        return {"uid": user.uid}

    @router.get("/public-but-personalized")
    async def mixed_route(user: Optional[UserContext] = Depends(get_optional_user)):
        if user:
            return {"message": f"Hello {user.display_name}"}
        return {"message": "Hello, guest"}
"""

import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from app.models.user import UserContext
from app.services import firebase_service

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> UserContext:
    """
    FastAPI dependency that requires a valid Firebase Bearer token.

    Raises HTTP 401 if:
      - No Authorization header is present
      - The token is invalid or expired
      - Firebase Admin SDK is not initialised

    Usage:
        @router.get("/me")
        async def get_me(user: UserContext = Depends(get_current_user)):
            ...
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()

    user = await firebase_service.verify_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(default=None),
) -> Optional[UserContext]:
    """
    FastAPI dependency that optionally verifies a Firebase Bearer token.

    Returns:
        UserContext if a valid token is provided, None otherwise.
        Does NOT raise an error if no token is present.

    Usage:
        @router.get("/feed")
        async def get_feed(user: Optional[UserContext] = Depends(get_optional_user)):
            ...
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()

    try:
        return await firebase_service.verify_token(token)
    except Exception:
        logger.debug("Optional auth token invalid — proceeding as guest")
        return None
