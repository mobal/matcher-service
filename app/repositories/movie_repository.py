from contextlib import closing
from typing import Any

from app.connection import connection


class MovieRepository:
    def get_by_hash(self, movie_hash: str) -> dict[str, Any] | None:
        with closing(connection()) as db:
            row = db.execute(
                "SELECT * FROM movies WHERE hash=? AND deleted_at IS NULL",
                (movie_hash,),
            ).fetchone()
        return dict(row) if row else None

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        columns = ",".join(data)
        values = list(data.values())
        placeholders = ",".join("?" for _ in values)
        with closing(connection()) as db:
            movie_id = db.execute(
                f"INSERT INTO movies({columns}) VALUES({placeholders})", values
            ).lastrowid
            row = db.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
        return dict(row)
