"""
models/user.py — Internal user context model (not a Firestore model).

UserContext is populated by the get_current_user dependency after
verifying a Firebase ID token. It is passed to route handlers that
require authentication.
"""

from typing import Optional
from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """
    Represents an authenticated Firebase user.
    Created from the decoded Firebase ID token by firebase_service.verify_token().
    """

    uid: str = Field(description="Firebase user UID")
    email: Optional[str] = Field(default=None, description="User's email address")
    email_verified: bool = Field(default=False)
    display_name: Optional[str] = Field(default=None)
    picture: Optional[str] = Field(default=None, description="Profile picture URL")
    provider: Optional[str] = Field(
        default=None,
        description="Auth provider (e.g., 'google.com', 'password')",
    )
    is_admin: bool = Field(
        default=False,
        description="True if the user has admin custom claims",
    )

    @classmethod
    def from_decoded_token(cls, decoded: dict) -> "UserContext":
        """
        Build a UserContext from a Firebase decoded ID token dict.

        Args:
            decoded: The dict returned by firebase_admin.auth.verify_id_token()
        """
        return cls(
            uid=decoded.get("uid", ""),
            email=decoded.get("email"),
            email_verified=decoded.get("email_verified", False),
            display_name=decoded.get("name"),
            picture=decoded.get("picture"),
            provider=decoded.get("firebase", {}).get("sign_in_provider"),
            is_admin=decoded.get("admin", False),
        )
