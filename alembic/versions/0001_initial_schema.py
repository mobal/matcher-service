"""Create the matcher catalogue schema."""

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL UNIQUE, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, email_verified_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT)"
    )
    op.execute(
        "CREATE TABLE trackers (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL UNIQUE, title TEXT NOT NULL UNIQUE, url TEXT NOT NULL, rss TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT)"
    )
    op.execute(
        "CREATE TABLE rules (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL UNIQUE, tracker_id INTEGER NOT NULL REFERENCES trackers(id), title TEXT NOT NULL, value TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT)"
    )
    op.execute(
        "CREATE TABLE movies (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL UNIQUE, title TEXT NOT NULL, year TEXT, rated TEXT, released TEXT, runtime TEXT, genre TEXT, director TEXT, writer TEXT, actors TEXT, plot TEXT, language TEXT, country TEXT, awards TEXT, poster TEXT, metascore TEXT, imdb_rating TEXT, imdb_votes TEXT, imdb_id TEXT, type TEXT, dvd TEXT, box_office TEXT, production TEXT, website TEXT, response TEXT, hash TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT)"
    )
    op.execute(
        "CREATE TABLE torrents (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL UNIQUE, title TEXT NOT NULL UNIQUE, uri TEXT NOT NULL, tracker_id INTEGER NOT NULL REFERENCES trackers(id), movie_id INTEGER REFERENCES movies(id), created_at TEXT NOT NULL, deleted_at TEXT)"
    )
    op.execute(
        "CREATE TABLE revoked_tokens (jti TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)"
    )
    for statement in (
        "CREATE INDEX idx_trackers_title_uuid ON trackers(title, uuid)",
        "CREATE INDEX idx_rules_title_uuid ON rules(title, uuid)",
        "CREATE INDEX idx_torrents_title_uuid ON torrents(title, uuid)",
        "CREATE INDEX idx_movies_hash_uuid ON movies(hash, uuid)",
        "CREATE INDEX idx_rules_tracker_id ON rules(tracker_id)",
        "CREATE INDEX idx_torrents_tracker_id ON torrents(tracker_id)",
        "CREATE INDEX idx_torrents_movie_id ON torrents(movie_id)",
    ):
        op.execute(statement)


def downgrade() -> None:
    for table in ("revoked_tokens", "torrents", "movies", "rules", "trackers", "users"):
        op.execute(f"DROP TABLE {table}")
