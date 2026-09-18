from contextlib import closing

from app.connection import connection
from app.models.request.torrent import TorrentCreateRequest
from app.models.response.catalogue import CatalogueRow


class TorrentRepository:
    def exists_by_title(self, title: str) -> bool:
        with closing(connection()) as db:
            return (
                db.execute(
                    "SELECT 1 FROM torrents WHERE title=? AND deleted_at IS NULL",
                    (title,),
                ).fetchone()
                is not None
            )

    def create(self, request: TorrentCreateRequest) -> CatalogueRow:
        from datetime import UTC, datetime
        from uuid import uuid4

        with closing(connection()) as db:
            torrent_id = db.execute(
                "INSERT INTO torrents(uuid,title,uri,tracker_id,movie_id,created_at) VALUES(?,?,?,?,?,?)",
                (
                    str(uuid4()),
                    request.title,
                    request.uri,
                    request.tracker_id,
                    request.movie_id,
                    datetime.now(UTC).isoformat(),
                ),
            ).lastrowid
            row = db.execute(
                "SELECT * FROM torrents WHERE id=?", (torrent_id,)
            ).fetchone()

        return CatalogueRow.model_validate(dict(row))

    def attach_movie(self, torrent_id: int, movie_id: int) -> None:
        with closing(connection()) as db:
            db.execute(
                "UPDATE torrents SET movie_id=? WHERE id=?", (movie_id, torrent_id)
            )
