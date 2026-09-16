from typing import Any

import httpx2 as httpx

from app.settings import settings


class OMDbClient:
    def get_movie(
        self, title: str, year: int | None, media_type: str | None
    ) -> dict[str, Any] | None:
        if not settings.omdb_api_key:
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
        response = httpx.get(
            settings.omdb_api_url, params=params, timeout=settings.http_timeout_seconds
        )
        response.raise_for_status()
        data = response.json()
        return None if data.get("Response") == "False" else data
