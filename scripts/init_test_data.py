from datetime import UTC, datetime
from contextlib import closing
from uuid import uuid4

from app.connection import connection
from app.migrations import upgrade


def main() -> None:
    upgrade()
    now = datetime.now(UTC).isoformat()
    with closing(connection()) as db:
        tracker = db.execute("SELECT id FROM trackers WHERE title=?", ("Demo Tracker",)).fetchone()
        tracker_id = tracker["id"] if tracker else db.execute(
            "INSERT INTO trackers(uuid,title,url,rss,created_at,updated_at) VALUES(?,?,?,?,?,?) RETURNING id",
            (str(uuid4()), "Demo Tracker", "http://wiremock:8080", "http://wiremock:8080/rss/demo", now, now),
        ).fetchone()[0]
        movie = db.execute("SELECT id FROM movies WHERE title=?", ("Demo Movie",)).fetchone()
        movie_id = movie["id"] if movie else db.execute(
            "INSERT INTO movies(uuid,title,year,created_at,updated_at) VALUES(?,?,?,?,?) RETURNING id",
            (str(uuid4()), "Demo Movie", "2025", now, now),
        ).fetchone()[0]
        db.execute(
            "INSERT OR IGNORE INTO rules(uuid,tracker_id,title,value,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (str(uuid4()), tracker_id, "1080p BluRay", "1080p,BluRay", now, now),
        )
        db.execute(
            "INSERT OR IGNORE INTO torrents(uuid,title,uri,tracker_id,movie_id,created_at) VALUES(?,?,?,?,?,?)",
            (str(uuid4()), "Demo.Movie.2025.1080p.BluRay", "magnet:?xt=demo", tracker_id, movie_id, now),
        )
    print("Initialized SQLite database with Newman test data")


if __name__ == "__main__":
    main()
