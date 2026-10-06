"""Verify Clerk session JWTs for API authentication."""
from __future__ import annotations

import logging
import time
from typing import Any

import jwt
from jwt import PyJWKClient

from ..config import settings

logger = logging.getLogger(__name__)

_jwk_client: PyJWKClient | None = None
_jwks_url_loaded: str | None = None


def _get_jwk_client() -> PyJWKClient | None:
    global _jwk_client, _jwks_url_loaded
    jwks_url = settings.clerk_jwks_url
    if not jwks_url:
        return None
    if _jwk_client is None or _jwks_url_loaded != jwks_url:
        _jwk_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
        _jwks_url_loaded = jwks_url
    return _jwk_client


def verify_clerk_token(token: str) -> dict[str, Any]:
    if not token:
        raise ValueError("Missing token")
    client = _get_jwk_client()
    if client is None:
        raise ValueError("Clerk JWKS is not configured")
    signing_key = client.get_signing_key_from_jwt(token)
    decode_options = {"verify_aud": bool(settings.CLERK_JWT_AUDIENCE)}
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.CLERK_JWT_AUDIENCE or None,
        issuer=settings.CLERK_JWT_ISSUER or None,
        options=decode_options,
    )
    if payload.get("exp") and payload["exp"] < time.time():
        raise ValueError("Token expired")
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise ValueError("Invalid token subject")
    return payload


async def verify_clerk_secret_key_configured() -> bool:
    """Optional sanity check that Clerk secret is present (no network call)."""
    return bool(settings.CLERK_SECRET_KEY)
