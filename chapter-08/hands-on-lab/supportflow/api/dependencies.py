"""FastAPI dependencies for SupportFlow."""

import os
from typing import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from database.connection import get_db

# API Key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Valid API keys (in production, store in database or environment)
VALID_API_KEYS = {
    os.getenv("API_KEY", "demo-key-12345"),  # Default demo key
}


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key from request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


def get_database() -> Generator[Session, None, None]:
    """
    Get database session dependency.

    Yields database session and ensures cleanup.
    """
    yield from get_db()
