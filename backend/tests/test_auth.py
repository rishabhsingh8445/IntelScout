import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.config import settings
from src.dependencies import get_current_user


def test_auth_requires_token_or_dev_mode():
    request = Request({"type": "http", "headers": []})

    # Save original values
    orig_env = settings.ENVIRONMENT
    orig_dev_header = settings.AUTH_ALLOW_DEV_HEADER
    try:
        # In production without credentials, should raise 401
        settings.ENVIRONMENT = "production"
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(request=request, credentials=None, x_user_id=None)
        assert exc_info.value.status_code == 401

        # In development without dev header allowed, should raise 401
        settings.ENVIRONMENT = "development"
        settings.AUTH_ALLOW_DEV_HEADER = False
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(request=request, credentials=None, x_user_id="user_123")
        assert exc_info.value.status_code == 401

        # In development with dev header explicitly allowed
        settings.ENVIRONMENT = "development"
        settings.AUTH_ALLOW_DEV_HEADER = True
        user_id = get_current_user(request=request, credentials=None, x_user_id="user_123")
        assert user_id == "user_123"
    finally:
        settings.ENVIRONMENT = orig_env
        settings.AUTH_ALLOW_DEV_HEADER = orig_dev_header

