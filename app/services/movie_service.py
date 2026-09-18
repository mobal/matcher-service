import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from app.clients.omdb_client import OMDbClient
from app.models.request.movie import MovieCreateRequest, MovieLookupRequest
from app.models.response.catalogue import CatalogueRow
from app.repositories.movie_repository import MovieRepository


class MovieService:
    def __init__(self, repository: MovieRepository, client: OMDbClient) -> None:
        self._repository = repository
        self._client = client

    @staticmethod
    def movie_hash(title: str, year: int | None) -> str:
        value = f"{title}+{year}" if year is not None else title

        return hashlib.sha1(value.encode(), usedforsecurity=False).hexdigest()

    def get_movie_info(self, request: MovieLookupRequest) -> CatalogueRow | None:
        movie_hash = self.movie_hash(request.title, request.year)
        cached = self._repository.get_by_hash(movie_hash)
        if cached:
            return cached

        data = self._client.get_movie(request)
        if not data:
            return None
        now = datetime.now(UTC).isoformat()
        movie = MovieCreateRequest(
            uuid=uuid4().hex,
            title=data.title or request.title,
            year=data.year,
            rated=data.rated,
            released=self._date(data.released),
            runtime=data.runtime,
            genre=data.genre,
            director=data.director,
            writer=data.writer,
            actors=data.actors,
            plot=data.plot,
            language=data.language,
            country=data.country,
            awards=data.awards,
            poster=data.poster,
            metascore=data.metascore,
            imdb_rating=data.imdb_rating,
            imdb_votes=data.imdb_votes,
            imdb_id=data.imdb_id,
            type=data.media_type,
            dvd=self._date(data.dvd),
            box_office=data.box_office,
            production=data.production,
            website=data.website,
            response=data.response,
            hash=movie_hash,
            created_at=now,
            updated_at=now,
        )

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
