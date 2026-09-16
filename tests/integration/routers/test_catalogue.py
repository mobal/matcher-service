from contextlib import closing
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.connection import connection


class TestCatalogueApi:
    def test_missing_tracker_detail_returns_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        assert (
            client.get("/api/v1/trackers/missing", headers=auth_headers).status_code
            == 404
        )

    def test_rule_collection_and_missing_rule_return_expected_statuses(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        tracker = client.get("/api/v1/trackers", headers=auth_headers).json()["data"][0]

        rules = client.get(
            f"/api/v1/trackers/{tracker['uuid']}/rules", headers=auth_headers
        )
        missing_tracker = client.get(
            "/api/v1/trackers/missing/rules", headers=auth_headers
        )
        missing_rule = client.get(
            f"/api/v1/trackers/{tracker['uuid']}/rules/missing", headers=auth_headers
        )
        assert rules.status_code == 200
        assert missing_tracker.status_code == 404
        assert missing_rule.status_code == 404

    def test_missing_torrent_detail_returns_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        assert (
            client.get("/api/v1/torrents/missing", headers=auth_headers).status_code
            == 404
        )

    def test_movies_are_paginated_and_protected(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/api/v1/movies?page=1&size=10", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["data"][0]["title"] == "Example Movie"
        assert body["data"][0]["imdbID"] is None

    def test_tracker_includes_rules(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/api/v1/trackers", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["data"][0]["rules"][0]["title"] == "1080p"

    def test_torrent_includes_tracker_and_movie(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        item = client.get("/api/v1/torrents", headers=auth_headers).json()["data"][0]

        assert item["tracker"] == "Example Tracker"
        assert item["movie"]["title"] == "Example Movie"

    def test_missing_resource_returns_not_found(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/api/v1/movies/does-not-exist", headers=auth_headers)

        assert response.status_code == 404

    def test_details_return_resources(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        movies = client.get("/api/v1/movies", headers=auth_headers).json()["data"]
        trackers = client.get("/api/v1/trackers", headers=auth_headers).json()["data"]
        torrents = client.get("/api/v1/torrents", headers=auth_headers).json()["data"]
        movie = client.get(f"/api/v1/movies/{movies[0]['uuid']}", headers=auth_headers)
        tracker = client.get(
            f"/api/v1/trackers/{trackers[0]['uuid']}", headers=auth_headers
        )
        torrent = client.get(
            f"/api/v1/torrents/{torrents[0]['uuid']}", headers=auth_headers
        )
        rule_uuid = tracker.json()["rules"][0]["uuid"]
        rule = client.get(
            f"/api/v1/trackers/{trackers[0]['uuid']}/rules/{rule_uuid}",
            headers=auth_headers,
        )

        assert all(
            response.status_code == 200 for response in (movie, tracker, torrent, rule)
        )

    def test_rejects_invalid_pagination(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/api/v1/movies?page=0&size=101", headers=auth_headers)

        assert response.status_code == 422

    def test_soft_deleted_movies_are_filtered(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        with closing(connection()) as db:
            db.execute(
                "UPDATE movies SET deleted_at=?", (datetime.now(UTC).isoformat(),)
            )

        response = client.get("/api/v1/movies", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_empty_page_has_null_bounds(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        body = client.get("/api/v1/movies?page=2&size=1", headers=auth_headers).json()

        assert body["data"] == []
        assert body["from"] is None
        assert body["to"] is None

    def test_rule_routes_reject_unknown_tracker(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get(
            "/api/v1/trackers/unknown-tracker/rules", headers=auth_headers
        )

        assert response.status_code == 404

    def test_movie_detail_requires_authentication(self, client: TestClient) -> None:
        response = client.get("/api/v1/movies/unknown-movie")

        assert response.status_code == 401
