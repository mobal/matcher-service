import logging
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.settings import settings

logger = logging.getLogger(__name__)


def decode_token(token: str) -> dict[str, Any]:
    if not settings.auth_jwt_secret:
        logger.error("JWT verification requested without configured signing secret")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Auth JWT verification is not configured",
        )
    try:
        return jwt.decode(
            token,
            settings.auth_jwt_secret,
            algorithms=["HS256"],
            issuer=settings.auth_jwt_issuer,
            audience=settings.auth_jwt_audience,
        )
    except jwt.PyJWTError as error:
        logger.warning("JWT validation failed: %s", type(error).__name__)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
