from unittest.mock import patch

from app.models.request.torrent import TorrentCreateRequest
from app.models.response.catalogue import CatalogueRow
from app.repositories.torrent_repository import TorrentRepository


class TestTorrentRepository:
    def test_exists_by_title_returns_boolean(
        self, torrent_repository: TorrentRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.fetchone.return_value = (1,)
        with patch(
            "app.repositories.torrent_repository.connection", database_connection
        ):
            assert torrent_repository.exists_by_title("Movie")

    def test_attach_movie_updates_relation(
        self, torrent_repository: TorrentRepository, database_connection
    ) -> None:
        with patch(
            "app.repositories.torrent_repository.connection", database_connection
        ):
            torrent_repository.attach_movie(4, 8)

        database_connection.execute.assert_called_once_with(
            "UPDATE torrents SET movie_id=? WHERE id=?", (8, 4)
        )

    def test_create_inserts_and_returns_torrent(
        self, torrent_repository: TorrentRepository, database_connection
    ) -> None:
        database_connection.execute.return_value.lastrowid = 2
        database_connection.execute.return_value.fetchone.return_value = {
            "id": 2,
            "title": "Movie",
        }
        with patch(
            "app.repositories.torrent_repository.connection", database_connection
        ):
            result = torrent_repository.create(
                TorrentCreateRequest(title="Movie", uri="magnet", tracker_id=1)
            )

        assert result == CatalogueRow(id=2, title="Movie")
