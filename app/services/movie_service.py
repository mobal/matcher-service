import hashlib
from datetime import UTC, datetime
from typing import Any

from app.clients.omdb_client import OMDbClient
from app.repositories.movie_repository import MovieRepository


class MovieService:
    def __init__(self, repository: MovieRepository, client: OMDbClient) -> None:
        self._repository = repository
        self._client = client

    @staticmethod
    def movie_hash(title: str, year: int | None) -> str:
        value = f"{title}+{year}" if year is not None else title
        return hashlib.sha1(value.encode(), usedforsecurity=False).hexdigest()

    def get_movie_info(
        self, title: str, year: int | None, media_type: str | None
    ) -> dict[str, Any] | None:
        movie_hash = self.movie_hash(title, year)
        cached = self._repository.get_by_hash(movie_hash)
        if cached:
            return cached
        data = self._client.get_movie(title, year, media_type)
        if not data:
            return None
        now = datetime.now(UTC).isoformat()
        movie = {
            "uuid": __import__("uuid").uuid4().hex,
            "title": data.get("Title", title),
            "year": data.get("Year"),
            "rated": data.get("Rated"),
            "released": self._date(data.get("Released")),
            "runtime": data.get("Runtime"),
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "writer": data.get("Writer"),
            "actors": data.get("Actors"),
            "plot": data.get("Plot"),
            "language": data.get("Language"),
            "country": data.get("Country"),
            "awards": data.get("Awards"),
            "poster": data.get("Poster"),
            "metascore": data.get("Metascore"),
            "imdb_rating": data.get("imdbRating"),
            "imdb_votes": data.get("imdbVotes"),
            "imdb_id": data.get("imdbID"),
            "type": data.get("Type"),
            "dvd": self._date(data.get("DVD")),
            "box_office": data.get("BoxOffice"),
            "production": data.get("Production"),
            "website": data.get("Website"),
            "response": data.get("Response"),
            "hash": movie_hash,
            "created_at": now,
            "updated_at": now,
        }
        return self._repository.create(movie)

    @staticmethod
    def _date(value: str | None) -> str | None:
        if not value or value == "N/A":
            return None
        try:
            return (
                datetime.strptime(value, "%d %b %Y")
                .replace(tzinfo=UTC)
                .date()
                .isoformat()
            )
        except ValueError:
            return None
