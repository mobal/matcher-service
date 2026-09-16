from typing import cast
from unittest.mock import Mock, patch

from app.services.movie_service import MovieService


class TestMovieService:
    def test_returns_cached_movie_without_calling_client(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = {"title": "Cached"}
        client = cast(Mock, movie_service._client)

        assert movie_service.get_movie_info("Movie", 2025, "movie") == {
            "title": "Cached"
        }
        client.get_movie.assert_not_called()

    def test_creates_movie_from_client_response(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = None
        repository.create.return_value = {"title": "Movie"}
        client = cast(Mock, movie_service._client)
        client.get_movie.return_value = {"Title": "Movie", "Released": "01 Jan 2025"}
        with patch("app.services.movie_service.datetime") as clock:
            clock.now.return_value.isoformat.return_value = "2025-01-01T00:00:00+00:00"
            result = movie_service.get_movie_info("Movie", 2025, "movie")

        assert result == {"title": "Movie"}
        repository.create.assert_called_once()

    def test_returns_none_when_client_has_no_data(
        self, movie_service: MovieService
    ) -> None:
        repository = cast(Mock, movie_service._repository)
        repository.get_by_hash.return_value = None
        client = cast(Mock, movie_service._client)
        client.get_movie.return_value = None

        assert movie_service.get_movie_info("Movie", None, None) is None

    def test_date_handles_missing_and_invalid_values(self) -> None:
        assert MovieService._date(None) is None
        assert MovieService._date("N/A") is None
        assert MovieService._date("invalid") is None
