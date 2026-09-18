from contextlib import closing

from app.connection import connection
from app.models.request.movie import MovieCreateRequest
from app.models.response.catalogue import CatalogueRow


class MovieRepository:
    def get_by_hash(self, movie_hash: str) -> CatalogueRow | None:
        with closing(connection()) as db:
            row = db.execute(
                "SELECT * FROM movies WHERE hash=? AND deleted_at IS NULL",
                (movie_hash,),
            ).fetchone()

        return CatalogueRow.model_validate(dict(row)) if row else None

    def create(self, data: MovieCreateRequest) -> CatalogueRow:
        values_by_column = data.model_dump(exclude_none=True)
        columns = ",".join(values_by_column)
        values = list(values_by_column.values())
        placeholders = ",".join("?" for _ in values)
        with closing(connection()) as db:
            movie_id = db.execute(
                f"INSERT INTO movies({columns}) VALUES({placeholders})", values
            ).lastrowid
            row = db.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()

        return CatalogueRow.model_validate(dict(row))
