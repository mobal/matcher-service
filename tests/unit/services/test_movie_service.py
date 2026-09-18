from typing import cast
from unittest.mock import Mock

from app.models.request.movie import MovieLookupRequest
from app.models.response.catalogue import CatalogueRow
from app.models.response.movie import OMDbMovieResponse
from app.services.movie_service import MovieService


class TestMovieService:
    def test_returns_cached_movie_without_calling_client(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = CatalogueRow(title="Cached")
        client = cast(Mock, movie_service._client)

        result = movie_service.get_movie_info(
            MovieLookupRequest(title="Movie", year=2025, media_type="movie")
        )
        assert result == CatalogueRow(title="Cached")
        client.get_movie.assert_not_called()

    def test_creates_movie_from_client_response(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = None
        repository.create.return_value = CatalogueRow(title="Movie")
        client = cast(Mock, movie_service._client)
        client.get_movie.return_value = OMDbMovieResponse(
            title="Movie", released="01 Jan 2025"
        )
        result = movie_service.get_movie_info(
            MovieLookupRequest(title="Movie", year=2025, media_type="movie")
        )

        assert result == CatalogueRow(title="Movie")
        repository.create.assert_called_once()

    def test_returns_none_when_client_has_no_data(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = None
        client = cast(Mock, movie_service._client)
        client.get_movie.return_value = None

        assert movie_service.get_movie_info(MovieLookupRequest(title="Movie")) is None

    def test_date_handles_missing_and_invalid_values(self) -> None:
        assert MovieService._date(None) is None
        assert MovieService._date("N/A") is None
        assert MovieService._date("invalid") is None

    def test_movie_hash_distinguishes_missing_year(self) -> None:
        assert MovieService.movie_hash("Movie", None) != MovieService.movie_hash(
            "Movie", 2025
        )
