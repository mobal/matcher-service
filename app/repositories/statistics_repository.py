from contextlib import closing
from datetime import UTC, datetime

from app.connection import connection
from app.models.response.statistics import StatisticsTorrent


class StatisticsRepository:
    def between(self, start: datetime, end: datetime) -> list[StatisticsTorrent]:
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

        return [StatisticsTorrent.model_validate(dict(row)) for row in rows]
