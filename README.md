# Matcher Service API

FastAPI port of the original Laravel torrent catalogue API. The application is
organized as routers → services → repositories, with outbound integrations in
`app/clients/`.

## Local development

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

```shell
uv sync
cp .env.example .env
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

## Adding new functionality

Follow the application layers in this order:

1. Add or update the database schema in a new Alembic migration.
2. Apply the migration locally with `uv run alembic upgrade head`.
3. Add request and response contracts under `app/models/request/` and
   `app/models/response/`.
4. Add the persistence operations to the appropriate repository in
   `app/repositories/`.
5. Add the business rules to a service in `app/services/`.
6. Register the repository and service in `app/dependencies.py`.
7. Add or update the endpoint in `app/routers/`.
8. Add unit tests for repositories and services, then integration tests for
   the HTTP behavior. Update the Postman collection when the public API
   changes.
9. Run `make format`, `make lint`, `make ty`, and `make test`.

For a schema change, create the migration with:

```shell
uv run alembic revision -m "describe the schema change"
uv run alembic upgrade head
```

Write and review the migration operations before committing them. This
project does not configure SQLAlchemy metadata for autogeneration. Alembic
uses `alembic/script.py.mako` when creating new migration files, so keep that
template in the repository.

### Inserting catalogue records

Insert records in parent-to-child order so foreign-key references already
exist:

1. `trackers`
2. `rules` for an existing tracker
3. `movies`
4. `torrents` referencing an existing tracker and, optionally, movie

Use the repository or service layer for application data writes rather than
writing directly to SQLite. Run migrations before inserting data, and provide
all required fields, including UUIDs and timestamps. To add another entity,
insert its independent records first, then insert records that reference
them.

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

## Docker local runtime

To run the API in Docker with SQLite mounted at `./data`:

```shell
mkdir -p data
cp .env.example .env
docker compose -f docker-compose.local.yml up --build
```

The API is available at `http://127.0.0.1:8080`. Schedule the search task on the Docker host with:

```cron
0 * * * * cd /path/to/matcher-service && docker compose -f docker-compose.local.yml run --rm --no-deps app uv run --no-dev python -m app.cli search
```

The CLI runs Alembic migrations before the task. Stop the API with:

```shell
docker compose -f docker-compose.local.yml down
```

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
