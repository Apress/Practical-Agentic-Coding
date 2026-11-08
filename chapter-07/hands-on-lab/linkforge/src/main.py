"""
LinkForge - URL Shortener Microservice
Main FastAPI application entry point.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .database import close_db, get_db, init_db
from .schemas import (
    HealthResponse,
    LinkCreate,
    LinkResponse,
    AnalyticsResponse,
)
from .shortener import ShorteningService
from .analytics import AnalyticsService
from .cache import RedisCache
from .ratelimit import DailyRateLimiter, get_rate_limiter

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management.

    Startup fails fast: if the database cannot be initialized, the
    process refuses to start instead of serving requests that can only
    fail once they reach the data layer.
    """
    try:
        await init_db()
    except Exception:
        logger.critical(
            "Database initialization failed; aborting startup", exc_info=True
        )
        raise
    logger.info("Database initialized successfully")

    yield

    await close_db()
    logger.info("Database connections closed; application shut down")


app = FastAPI(
    title="LinkForge",
    description="A URL shortening microservice with real-time analytics",
    version="1.0.0",
    lifespan=lifespan,
)


# Dependency injection helpers
async def get_shortening_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ShorteningService:
    """Get the shortening service with dependencies."""
    cache = await RedisCache.get_instance()
    analytics = AnalyticsService(cache, db=db)
    return ShorteningService(db, cache, analytics)


async def enforce_daily_limit(
    request: Request,
    limiter: Annotated[DailyRateLimiter, Depends(get_rate_limiter)],
) -> None:
    """
    Enforce the free-tier daily quota on shortening requests.

    Raises:
        HTTPException: 429 once the caller's daily quota is spent
    """
    if not await limiter.allow(limiter.identify(request)):
        raise HTTPException(
            status_code=429,
            detail=(
                f"Daily limit of {limiter.limit} shortening requests "
                "exceeded; quota resets at midnight UTC"
            ),
        )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint for load balancers and monitoring.

    Returns:
        HealthResponse: Current health status
    """
    return HealthResponse(status="healthy", version="1.0.0")


@app.post(
    "/api/v1/links",
    response_model=LinkResponse,
    status_code=201,
    tags=["Links"],
    dependencies=[Depends(enforce_daily_limit)],
)
async def create_short_url(
    request: LinkCreate,
    service: Annotated[ShorteningService, Depends(get_shortening_service)],
    user_id: int = 1,  # TODO: Implement proper authentication (init_db seeds user 1)
) -> LinkResponse:
    """
    Create a shortened URL.

    Args:
        request: The URL to shorten, with optional custom code and expiry
        service: Shortening service (injected)
        user_id: Authenticated user ID

    Returns:
        LinkResponse: The created short link details

    Raises:
        HTTPException: 400 if the URL or custom code is invalid,
            429 if the daily rate limit is exceeded
    """
    try:
        link = await service.create_short_url(
            original_url=request.original_url,
            user_id=user_id,
            custom_code=request.custom_code,
            expires_in_days=request.expires_in_days,
        )
        return LinkResponse(
            short_code=link.short_code,
            original_url=link.original_url,
            created_at=link.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/api/v1/links/{short_code}",
    response_model=LinkResponse,
    tags=["Links"],
)
async def get_link(
    short_code: str,
    service: Annotated[ShorteningService, Depends(get_shortening_service)],
) -> LinkResponse:
    """
    Get details of a shortened URL.

    Args:
        short_code: The short code to look up
        service: Shortening service (injected)

    Returns:
        LinkResponse: The link details

    Raises:
        HTTPException: If link not found
    """
    link = await service.get_link(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return LinkResponse(
        short_code=link.short_code,
        original_url=link.original_url,
        created_at=link.created_at,
    )


@app.get("/{short_code}", tags=["Redirect"])
async def redirect_to_url(
    short_code: str,
    request: Request,
    service: Annotated[ShorteningService, Depends(get_shortening_service)],
) -> RedirectResponse:
    """
    Redirect to the original URL and log analytics.

    Args:
        short_code: The short code to redirect
        request: FastAPI request object for analytics
        service: Shortening service (injected)

    Returns:
        RedirectResponse: HTTP redirect to original URL

    Raises:
        HTTPException: If link not found or expired
    """
    link = await service.get_link(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Log click asynchronously
    await service.log_click(
        short_code=short_code,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return RedirectResponse(url=link.original_url, status_code=307)


@app.get(
    "/api/v1/links/{short_code}/analytics",
    response_model=AnalyticsResponse,
    tags=["Analytics"],
)
async def get_analytics(
    short_code: str,
    service: Annotated[ShorteningService, Depends(get_shortening_service)],
) -> AnalyticsResponse:
    """
    Get analytics for a shortened URL.

    Args:
        short_code: The short code to get analytics for
        service: Shortening service (injected)

    Returns:
        AnalyticsResponse: Click statistics

    Raises:
        HTTPException: If link not found
    """
    link = await service.get_link(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    analytics = await service.get_analytics(short_code)
    return analytics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
