from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .security.clerk_auth import verify_clerk_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    x_user_id: str | None = Header(default=None, alias="x-user-id"),
) -> str:
    if credentials and credentials.credentials:
        try:
            payload = verify_clerk_token(credentials.credentials)
            return payload["sub"]
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

    if settings.AUTH_ALLOW_DEV_HEADER and settings.ENVIRONMENT == "development" and x_user_id:
        return x_user_id

    raise HTTPException(status_code=401, detail="Authentication required")
