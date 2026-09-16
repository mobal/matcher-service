# Matcher Service API

FastAPI port of the original Laravel torrent catalogue API. The application is
organized as routers → services → repositories, with outbound integrations in
`app/clients/`.

## Local development

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

```shell
uv sync
cp .env.example .env.local
uv run uvicorn app.api_handler:app --reload
```

Configuration comes from environment variables. Set a production-strength
`AUTH_JWT_SECRET`, matching `AUTH_JWT_ISSUER` and `AUTH_JWT_AUDIENCE`, and a writable `DATABASE_PATH` outside local development. The
schema is managed by Alembic; importing the FastAPI application does not initialize or seed a database.

```shell
uv run alembic upgrade head
uv run python -m app.cli search
uv run python -m app.cli statistics --type daily
```

## API

- Authenticated catalogue endpoints under `/api/v1`: movies, torrents,
  trackers, and tracker rules.
- `GET /health`

Use `/docs` for the generated OpenAPI contract. Catalogue responses preserve
the Laravel-compatible pagination shape and camelCase response fields.

## Tests

Unit and integration tests are separate:

```shell
DEBUG=false uv run pytest tests/unit
DEBUG=false uv run pytest tests/integration
```

Unit tests mock database and external boundaries and cover clients, services,
repositories. Integration tests use the synchronous FastAPI
`TestClient` with isolated SQLite data and exercise the routers. The test tree
mirrors the application layout under `tests/unit/` and `tests/integration/`.

The `Makefile` provides formatting, linting, security, type-checking, and a
combined `make test` target.

## Docker and Newman E2E

The Compose stack starts a declarative WireMock external-API stub, initializes
disposable SQLite data, starts the API, and runs the Postman collection through
Newman:

```shell
docker compose up --build --abort-on-container-exit --exit-code-from newman newman
docker compose down -v --remove-orphans
```

The collection and environment are in `postman/`; WireMock mappings are in
`mocks/external/mappings/`. Newman tests are Docker E2E tests, not pytest tests.

## GitHub Actions

The workflow is in `.github/workflows/`. It installs dependencies from
`uv.lock`, runs security and lint checks, executes tests, and runs the Docker /
Newman job separately.

## Project layout

```text
app/
├── clients/       # OMDb and RSS HTTP clients
├── repositories/  # SQLite persistence
├── routers/       # FastAPI HTTP endpoints
├── services/      # Application and workflow logic
├── api_handler.py
├── cli.py
├── connection.py
├── migrations.py
├── alembic.ini
├── alembic/
├── models.py
├── security.py
└── settings.py

tests/
├── unit/
│   ├── clients/
│   ├── repositories/
│   └── services/
└── integration/
    └── routers/
```

## Migration notes

The Python implementation preserves the Laravel catalogue routes, soft-delete filtering, UUIDs, pagination, and nested catalogue responses. Authentication is delegated to the external auth service; Matcher Service validates its JWT issuer, audience, signature, and expiration. Alembic owns schema versioning; administrator provisioning and token issuance remain external concerns.
