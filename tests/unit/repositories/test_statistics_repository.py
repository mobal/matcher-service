from datetime import UTC, datetime
from unittest.mock import patch

from app.repositories.statistics_repository import StatisticsRepository


class TestStatisticsRepository:
    def test_between_converts_rows_to_dicts(
        self, statistics_repository: StatisticsRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchall.return_value = [
            {"id": 1, "title": "Movie"}
        ]
        with patch(
            "app.repositories.statistics_repository.connection", database_connection
        ):
            result = statistics_repository.between(
                datetime(2025, 1, 1, tzinfo=UTC), datetime(2025, 1, 2, tzinfo=UTC)
            )

        assert result == [{"id": 1, "title": "Movie"}]
        assert database_connection.execute.called
