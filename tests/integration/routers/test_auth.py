from datetime import UTC, datetime

import jwt
from fastapi import status
from fastapi.testclient import TestClient

from app.settings import settings


class TestExternalAuth:
    def test_catalogue_requires_a_bearer_token(self, client: TestClient) -> None:
        response = client.get("/api/v1/movies")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_catalogue_rejects_an_invalid_token(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/movies", headers={"Authorization": "Bearer invalid"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_catalogue_rejects_an_expired_token(self, client: TestClient) -> None:
        token = jwt.encode(
            {
                "sub": "external-user",
                "iss": settings.auth_jwt_issuer,
                "aud": settings.auth_jwt_audience,
                "exp": int(datetime.now(UTC).timestamp()) - 1,
            },
            settings.auth_jwt_secret,
            algorithm="HS256",
        )

        response = client.get(
            "/api/v1/movies", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_catalogue_accepts_auth_service_token(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/api/v1/movies", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
