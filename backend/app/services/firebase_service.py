"""
services/firebase_service.py — Firebase Admin SDK integration.

Provides:
  - Firebase Admin initialisation (graceful no-op if service account not present)
  - verify_token(id_token) — decode and validate Firebase ID tokens
  - Firestore db accessor for backend-side reads (future use)

Design decision:
  The backend does NOT manage user data or replace Firestore.
  This service is used ONLY for:
    1. Verifying Firebase ID tokens on protected endpoints
    2. Optional admin-only Firestore queries in future features

  All user data (favorites, reviews, news) continues to live in Firestore
  and is accessed directly by the Vue frontend via the Firebase client SDK.
"""

from app.models.user import UserContext
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Firebase Admin SDK — loaded lazily so the app starts even without a service account
_firebase_app = None
_firebase_auth = None
_firestore_db = None
_init_attempted = False


def _init_firebase() -> bool:
    """
    Attempt to initialise Firebase Admin SDK.

    Returns True if successful, False if service account file is missing
    or if the SDK raises an error during initialisation.
    """
    global _firebase_app, _firebase_auth, _firestore_db, _init_attempted

    if _init_attempted:
        return _firebase_app is not None

    _init_attempted = True

    try:
        # pyrefly: ignore [missing-import]
        import firebase_admin
        # pyrefly: ignore [missing-import]
        from firebase_admin import credentials, auth, firestore
        from config import settings

        sa_path = settings.firebase_service_account_path

        if not os.path.isfile(sa_path):
            logger.warning(
                "Firebase service account not found at '%s'. Token verification is DISABLED. "
                "Download from: Firebase Console -> Project Settings -> Service Accounts",
                sa_path,
            )
            return False

        cred = credentials.Certificate(sa_path)

        # Avoid re-initialising if already done (e.g., hot-reload)
        if not firebase_admin._apps:
            _firebase_app = firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })
        else:
            _firebase_app = firebase_admin.get_app()

        _firebase_auth = auth
        _firestore_db = firestore.client()

        logger.info(
            "Firebase Admin SDK initialised for project '%s'",
            settings.firebase_project_id,
        )
        return True

    except ImportError:
        logger.error(
            "firebase-admin package not installed. Run: pip install firebase-admin"
        )
        return False
    except Exception as exc:
        logger.error("Failed to initialise Firebase Admin SDK: %s", exc)
        return False


async def verify_token(id_token: str) -> Optional["UserContext"]:
    """
    Verify a Firebase ID token and return a UserContext.

    Args:
        id_token: Raw Firebase ID token string from the Authorization header.

    Returns:
        UserContext if the token is valid, None if verification fails.
        Returns None (not raises) so callers can decide how to handle it.
    """
    from app.models.user import UserContext

    if not _init_firebase():
        logger.warning(
            "Firebase Admin not initialised — cannot verify token. "
            "Returning None (unauthenticated)."
        )
        return None

    try:
        if _firebase_auth is None:
            logger.error("Firebase auth unexpectedly None after successful init.")
            return None
        decoded = _firebase_auth.verify_id_token(id_token)
        return UserContext.from_decoded_token(decoded)
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        return None


def get_firestore():
    """
    Return the Firestore client (for admin-side operations).

    Returns None if Firebase Admin is not initialised.
    Use this sparingly — Vue handles all user-facing Firestore operations.
    """
    _init_firebase()
    return _firestore_db


def is_firebase_ready() -> bool:
    """Check whether Firebase Admin SDK has been successfully initialised."""
    return _init_firebase()
