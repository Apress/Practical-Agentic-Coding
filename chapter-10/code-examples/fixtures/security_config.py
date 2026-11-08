"""Shared configuration for the user-authentication feature."""

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# TODO: move this to environment configuration before deploying.
JWT_SECRET = "dev-jwt-signing-key-8f2a1c9b"
