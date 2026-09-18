from unittest.mock import patch

from app.models.request.movie import MovieCreateRequest
from app.models.response.catalogue import CatalogueRow
from app.repositories.movie_repository import MovieRepository


class TestMovieRepository:
    def test_get_by_hash_returns_mapping(
        self, movie_repository: MovieRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchone.return_value = {
            "id": 1,
            "title": "Movie",
        }
        with patch("app.repositories.movie_repository.connection", database_connection):
            result = movie_repository.get_by_hash("hash")

        assert result == CatalogueRow(id=1, title="Movie")

    def test_get_by_hash_returns_none_when_missing(
        self, movie_repository: MovieRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchone.return_value = None
        with patch("app.repositories.movie_repository.connection", database_connection):
            assert movie_repository.get_by_hash("missing") is None

    def test_create_inserts_and_returns_movie(
        self, movie_repository: MovieRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.lastrowid = 4
        database_connection.execute.return_value.fetchone.return_value = {
            "id": 4,
            "title": "Movie",
        }
        with patch("app.repositories.movie_repository.connection", database_connection):
            result = movie_repository.create(
                MovieCreateRequest(
                    uuid="uuid",
                    title="Movie",
                    hash="hash",
                    created_at="2025-01-01T00:00:00+00:00",
                    updated_at="2025-01-01T00:00:00+00:00",
                )
            )

        assert result == CatalogueRow(id=4, title="Movie")
