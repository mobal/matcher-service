from unittest.mock import MagicMock, patch

from app.models.response.catalogue import CatalogueRow
from app.repositories.catalogue_repository import CatalogueRepository


class TestCatalogueRepository:
    def test_page_returns_rows_and_total(
        self, catalogue_repository: CatalogueRepository, database_connection
    ) -> None:
        total_result = MagicMock()
        total_result.fetchone.return_value = (2,)
        rows_result = MagicMock()
        rows_result.fetchall.return_value = [{"id": 1, "title": "Movie"}]
        database_connection.execute.side_effect = [total_result, rows_result]
        with patch(
            "app.repositories.catalogue_repository.connection", database_connection
        ):
            result, total = catalogue_repository.page("movies", 2, 10)

        assert result == [CatalogueRow(id=1, title="Movie")]
        assert total == 2
        assert database_connection.execute.call_count == 2

    def test_rejects_unsupported_resource(
        self, catalogue_repository: CatalogueRepository
    ) -> None:
        try:
            catalogue_repository.page("unknown", 1, 10)
        except KeyError:
            pass
        else:
            raise AssertionError("unsupported resource was accepted")

    def test_by_uuid_returns_row_and_rejects_unknown_table(
        self, catalogue_repository: CatalogueRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchone.return_value = {"uuid": "u"}
        with patch(
            "app.repositories.catalogue_repository.connection", database_connection
        ):
            assert catalogue_repository.by_uuid("movies", "u") == CatalogueRow(uuid="u")

        try:
            catalogue_repository.by_uuid("users", "u")
        except ValueError:
            pass
        else:
            raise AssertionError("unsupported table was accepted")

    def test_rules_and_tracker_rules(
        self, catalogue_repository: CatalogueRepository, database_connection
    ) -> None:
        total = MagicMock()
        total.fetchone.return_value = (1,)
        rows = MagicMock()
        rows.fetchall.return_value = [{"id": 1, "tracker_id": 2}]
        database_connection.execute.side_effect = [total, rows, rows]
        with patch(
            "app.repositories.catalogue_repository.connection", database_connection
        ):
            rules = catalogue_repository.rules(2, 1, 10, "rule")
            tracker_rules = catalogue_repository.tracker_rules(2)

        assert rules == ([CatalogueRow(id=1, tracker_id=2)], 1)
        assert tracker_rules == [CatalogueRow(id=1, tracker_id=2)]

    def test_torrent_details_adds_related_objects(
        self, catalogue_repository: CatalogueRepository, database_connection
    ) -> None:
        tracker = MagicMock()
        tracker.fetchone.return_value = {"title": "Tracker"}
        movie = MagicMock()
        movie.fetchone.return_value = {"id": 3, "title": "Movie"}
        database_connection.execute.side_effect = [tracker, movie]
        with patch(
            "app.repositories.catalogue_repository.connection", database_connection
        ):
            result = catalogue_repository.torrent_details(
                CatalogueRow(tracker_id=1, movie_id=3)
            )

        assert result.tracker_title == "Tracker"
        assert result.movie == CatalogueRow(id=3, title="Movie")
