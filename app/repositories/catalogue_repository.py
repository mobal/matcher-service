from contextlib import closing
from typing import Any, ClassVar

from app.connection import connection


class CatalogueRepository:
    _LIST_QUERIES: ClassVar[dict[str, str]] = {
        "movies": "SELECT * FROM movies WHERE deleted_at IS NULL ORDER BY created_at DESC",
        "trackers": "SELECT * FROM trackers WHERE deleted_at IS NULL ORDER BY created_at DESC",
        "torrents": "SELECT t.*, tr.title AS tracker_title FROM torrents t JOIN trackers tr ON tr.id=t.tracker_id AND tr.deleted_at IS NULL WHERE t.deleted_at IS NULL ORDER BY t.created_at DESC",
    }

    def page(self, resource: str, page: int, size: int) -> tuple[list[dict], int]:
        query = self._LIST_QUERIES[resource]
        with closing(connection()) as db:
            total = db.execute(f"SELECT COUNT(*) FROM ({query})").fetchone()[0]
            rows = db.execute(
                f"{query} LIMIT ? OFFSET ?", (size, (page - 1) * size)
            ).fetchall()

        return [dict(row) for row in rows], total

    def by_uuid(self, table: str, value: str) -> dict | None:
        if table not in {"movies", "trackers", "torrents"}:
            raise ValueError(f"Unsupported table: {table}")
        with closing(connection()) as db:
            row = db.execute(
                f"SELECT * FROM {table} WHERE uuid=? AND deleted_at IS NULL", (value,)
            ).fetchone()

        return dict(row) if row else None

    def rules(
        self, tracker_id: int, page: int, size: int, rule_uuid: str | None = None
    ) -> tuple[list[dict], int]:
        where = "tracker_id=? AND deleted_at IS NULL"
        args: list[Any] = [tracker_id]
        if rule_uuid:
            where += " AND uuid=?"
            args.append(rule_uuid)
        with closing(connection()) as db:
            total = db.execute(
                f"SELECT COUNT(*) FROM rules WHERE {where}", args
            ).fetchone()[0]
            rows = db.execute(
                f"SELECT * FROM rules WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*args, size, (page - 1) * size],
            ).fetchall()

        return [dict(row) for row in rows], total

    def tracker_rules(self, tracker_id: int) -> list[dict]:
        with closing(connection()) as db:
            rows = db.execute(
                "SELECT * FROM rules WHERE tracker_id=? AND deleted_at IS NULL ORDER BY created_at DESC",
                (tracker_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    def torrent_details(self, row: dict) -> dict:
        with closing(connection()) as db:
            tracker = db.execute(
                "SELECT title FROM trackers WHERE id=? AND deleted_at IS NULL",
                (row["tracker_id"],),
            ).fetchone()
            movie = db.execute(
                "SELECT * FROM movies WHERE id=? AND deleted_at IS NULL",
                (row.get("movie_id"),),
            ).fetchone()

        return {
            **row,
            "tracker_title": tracker["title"] if tracker else None,
            "movie": dict(movie) if movie else None,
        }
