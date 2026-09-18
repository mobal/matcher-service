from datetime import UTC, datetime
from unittest.mock import patch

from app.models.response.statistics import StatisticsTorrent
from app.repositories.statistics_repository import StatisticsRepository


class TestStatisticsRepository:
    def test_between_converts_rows_to_dicts(
        self, statistics_repository: StatisticsRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchall.return_value = [
            {
                "id": 1,
                "title": "Movie",
                "created_at": "2025-01-01T00:00:00+00:00",
            }
        ]
        with patch(
            "app.repositories.statistics_repository.connection", database_connection
        ):
            result = statistics_repository.between(
                datetime(2025, 1, 1, tzinfo=UTC), datetime(2025, 1, 2, tzinfo=UTC)
            )

        assert result == [
            StatisticsTorrent(
                id=1, title="Movie", created_at="2025-01-01T00:00:00+00:00"
            )
        ]
        assert database_connection.execute.called
