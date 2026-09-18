import logging

import httpx2 as httpx

from app.models.request.movie import MovieLookupRequest
from app.models.response.movie import OMDbMovieResponse
from app.settings import settings

logger = logging.getLogger(__name__)


class OMDbClient:
    def get_movie(self, request: MovieLookupRequest) -> OMDbMovieResponse | None:
        if not settings.omdb_api_key:
            logger.warning("OMDb lookup skipped because no API key is configured")
            return None

        params: dict[str, str | int] = {
            "apikey": settings.omdb_api_key,
            "plot": "full",
            "r": "json",
            "t": request.title,
        }

        if request.year is not None:
            params["y"] = request.year
        if request.media_type:
            params["type"] = request.media_type

        logger.info("Looking up movie metadata for %r", request.title)
        response = httpx.get(
            settings.omdb_api_url, params=params, timeout=settings.http_timeout_seconds
        )
        response.raise_for_status()
        movie = OMDbMovieResponse.model_validate(response.json())
        if movie.response == "False":
            logger.info("OMDb returned no metadata for %r", request.title)
            return None

        logger.info("OMDb metadata found for %r", request.title)
        return movie
