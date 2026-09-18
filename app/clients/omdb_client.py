import logging
from typing import Any

import httpx2 as httpx

from app.settings import settings

logger = logging.getLogger(__name__)


class OMDbClient:
    def get_movie(
        self, title: str, year: int | None, media_type: str | None
    ) -> dict[str, Any] | None:
        if not settings.omdb_api_key:
            logger.warning("OMDb lookup skipped because no API key is configured")
            return None

        params: dict[str, str | int] = {
            "apikey": settings.omdb_api_key,
            "plot": "full",
            "r": "json",
            "t": title,
        }

        if year is not None:
            params["y"] = year
        if media_type:
            params["type"] = media_type

        logger.info("Looking up movie metadata for %r", title)
        response = httpx.get(
            settings.omdb_api_url, params=params, timeout=settings.http_timeout_seconds
        )
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "False":
            logger.info("OMDb returned no metadata for %r", title)
            return None

        logger.info("OMDb metadata found for %r", title)
        return data
