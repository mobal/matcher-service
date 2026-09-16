from collections.abc import Iterator
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient

from app.connection import connection
from app.migrations import upgrade
from app.settings import settings


@pytest.fixture
def database(tmp_path: Path) -> Iterator[str]:
    original_database_path = settings.database_path
    original_auth_secret = settings.auth_jwt_secret
    settings.database_path = tmp_path / "integration.sqlite3"
    settings.auth_jwt_secret = "integration-secret-that-is-at-least-32-bytes"
    try:
        upgrade()
        seed_database()
        yield str(uuid4())
    finally:
        settings.database_path = original_database_path
        settings.auth_jwt_secret = original_auth_secret


@pytest.fixture
def client(database: str) -> Iterator[TestClient]:
    from app.api_handler import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(database: str) -> dict[str, str]:
    claims = {
        "sub": database,
        "iss": settings.auth_jwt_issuer,
        "aud": settings.auth_jwt_audience,
        "iat": 1,
        "exp": 4102444800,
        "jti": "integration-token",
        "scope": "posts:write tokens:revoke users:read users:write",
    }
    token = jwt.encode(claims, settings.auth_jwt_secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def seed_database() -> None:
    now = datetime.now(UTC).isoformat()
    with closing(connection()) as db:
        tracker_id = db.execute(
            "INSERT INTO trackers(uuid,title,url,rss,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (
                str(uuid4()),
                "Example Tracker",
                "https://tracker.test",
                "https://tracker.test/rss",
                now,
                now,
            ),
        ).lastrowid
        movie_id = db.execute(
            "INSERT INTO movies(uuid,title,year,created_at,updated_at) VALUES(?,?,?,?,?)",
            (str(uuid4()), "Example Movie", "2025", now, now),
        ).lastrowid
        db.execute(
            "INSERT INTO rules(uuid,tracker_id,title,value,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (str(uuid4()), tracker_id, "1080p", "1080p,BluRay", now, now),
        )
        db.execute(
            "INSERT INTO torrents(uuid,title,uri,tracker_id,movie_id,created_at) VALUES(?,?,?,?,?,?)",
            (
                str(uuid4()),
                "Example Movie 1080p",
                "magnet:?xt=example",
                tracker_id,
                movie_id,
                now,
            ),
        )
