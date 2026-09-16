from contextlib import closing
from datetime import UTC, datetime

from app.connection import connection


class StatisticsRepository:
    def between(self, start: datetime, end: datetime) -> list[dict]:
        start_utc = start.astimezone(UTC)
        end_utc = end.astimezone(UTC)
        with closing(connection()) as db:
            rows = db.execute(
                """
                SELECT id, uuid, title, uri, tracker_id, movie_id, created_at
                FROM torrents
                WHERE deleted_at IS NULL AND created_at BETWEEN ? AND ?
                ORDER BY id DESC
                """,
                (start_utc.isoformat(), end_utc.isoformat()),
            ).fetchall()
        return [dict(row) for row in rows]
