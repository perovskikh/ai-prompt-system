# src/middleware/jwt_auth.py
"""
JWT Authentication Service for AI Prompt System v2.0.0

Provides JWT token-based authentication with:
- Token generation and validation
- Refresh token mechanism
- Token revocation support
- Role-based access control (RBAC)
"""

import os
import time
import hashlib
import hmac
import json
from typing import Optional, Dict, List, Any
from functools import wraps
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str  # Subject (user/project ID)
    role: str  # Role: admin, developer, user
    permissions: List[str]
    tier_access: List[str]  # Which tiers can be accessed
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    refresh_id: str  # Refresh token ID for revocation


class JWTService:
    """JWT authentication service."""

    def __init__(self, secret_key: str = None):
        # Use environment secret or generate from machine ID
        self.secret_key = secret_key or os.getenv(
            "JWT_SECRET",
            hashlib.sha256(str(os.uname()).encode()).hexdigest()[:32]
        )
        self.algorithm = "HS256"
        self.default_expiry = 3600  # 1 hour
        self.refresh_expiry = 604800  # 7 days

        # Token revocation list (in production, use Redis)
        self._revoked_tokens: set = set()
        self._refresh_tokens: Dict[str, Dict] = {}

    def generate_token(
        self,
        subject: str,
        role: str = "user",
        permissions: List[str] = None,
        tier_access: List[str] = None,
        expiry: int = None
    ) -> str:
        """Generate a JWT token."""
        now = int(time.time())
        exp = now + (expiry or self.default_expiry)

        # Generate refresh token ID
        refresh_id = hashlib.sha256(
            f"{subject}{now}{self.secret_key}".encode()
        ).hexdigest()[:16]

        payload = {
            "sub": subject,
            "role": role,
            "permissions": permissions or ["read"],
            "tier_access": tier_access or ["universal"],
            "exp": exp,
            "iat": now,
            "refresh_id": refresh_id
        }

        # Store refresh token
        self._refresh_tokens[refresh_id] = {
            "sub": subject,
            "role": role,
            "expires": now + self.refresh_expiry
        }

        # Create JWT (simplified - in production use pyjwt)
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_b64 = self._base64url_encode(json.dumps(header))
        payload_b64 = self._base64url_encode(json.dumps(payload))
        signature = self._sign(f"{header_b64}.{payload_b64}")

        return f"{header_b64}.{payload_b64}.{signature}"

    def generate_refresh_token(self, refresh_id: str) -> Optional[str]:
        """Generate a new access token from refresh token."""
        refresh_data = self._refresh_tokens.get(refresh_id)
        if not refresh_data:
            return None

        # Check if refresh token expired
        if refresh_data["expires"] < int(time.time()):
            del self._refresh_tokens[refresh_id]
            return None

        return self.generate_token(
            subject=refresh_data["sub"],
            role=refresh_data["role"]
        )

    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """Validate JWT token and return payload."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature = parts

            # Verify signature
            expected_sig = self._sign(f"{header_b64}.{payload_b64}")
            if not hmac.compare_digest(signature, expected_sig):
                logger.warning("Invalid token signature")
                return None

            # Decode payload
            payload = json.loads(self._base64url_decode(payload_b64))

            # Check expiration
            if payload["exp"] < int(time.time()):
                logger.warning("Token expired")
                return None

            # Check revocation
            if token in self._revoked_tokens:
                logger.warning("Token revoked")
                return None

            return TokenPayload(
                sub=payload["sub"],
                role=payload["role"],
                permissions=payload.get("permissions", []),
                tier_access=payload.get("tier_access", []),
                exp=payload["exp"],
                iat=payload["iat"],
                refresh_id=payload.get("refresh_id", "")
            )

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        self._revoked_tokens.add(token)
        return True

    def revoke_refresh_token(self, refresh_id: str) -> bool:
        """Revoke a refresh token."""
        if refresh_id in self._refresh_tokens:
            del self._refresh_tokens[refresh_id]
            return True
        return False

    def check_tier_access(self, payload: TokenPayload, tier: str) -> bool:
        """Check if token has access to specific tier."""
        if payload.role == "admin":
            return True
        return tier in payload.tier_access

    def check_permission(self, payload: TokenPayload, permission: str) -> bool:
        """Check if token has specific permission."""
        if payload.role == "admin":
            return True
        return permission in payload.permissions

    def _base64url_encode(self, data: str) -> str:
        """Base64URL encode."""
        import base64
        return base64.urlsafe_b64encode(
            data.encode()
        ).decode().rstrip("=")

    def _base64url_decode(self, data: str) -> str:
        """Base64URL decode."""
        import base64
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data).decode()

    def _sign(self, data: str) -> str:
        """HMAC-SHA256 sign."""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()


# Default roles configuration
DEFAULT_ROLES = {
    "admin": {
        "permissions": ["*"],
        "tier_access": ["core", "universal", "mpv_stage", "projects"],
        "rate_limit": 1000
    },
    "developer": {
        "permissions": ["read_prompts", "run_prompt", "write_prompts"],
        "tier_access": ["universal", "mpv_stage", "projects"],
        "rate_limit": 500
    },
    "user": {
        "permissions": ["read_prompts", "run_prompt"],
        "tier_access": ["universal"],
        "rate_limit": 100
    }
}


def require_auth(role: str = None, permission: str = None, tier: str = None):
    """Decorator for requiring authentication."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In FastMCP, auth is handled differently
            # This is a placeholder for the auth logic
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global JWT service instance
_jwt_service: Optional[JWTService] = None


def get_jwt_service() -> JWTService:
    """Get or create global JWT service."""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTService()
    return _jwt_service
