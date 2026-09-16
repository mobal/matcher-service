# Matcher Service Laravel → FastAPI Migration Checklist

This checklist describes the current Python implementation and the remaining
production hardening work.

## Completed

### Application structure

- [x] FastAPI application with `/api` route prefix.
- [x] Router → service → repository layering.
- [x] Dedicated OMDb and RSS clients using `httpx2`.
- [x] Pydantic settings and environment-based configuration.
- [x] Health endpoint, structured errors, CORS, gzip, and correlation IDs.
- [x] Alembic-managed schema migrations with no import-time seeding.

### Persistence and authentication

- [x] SQLite catalogue schema for trackers, rules, movies, and torrents.
- [x] UUIDs, timestamps, soft deletion, foreign keys, indexes, and uniqueness constraints.
- [x] Auth-service JWT validation for issuer, audience, signature, and expiration claims.
- [x] Authentication remains external; Matcher Service does not persist credentials or issue tokens.

### Catalogue API

- [x] Movie, torrent, tracker, and tracker-rule list/detail endpoints.
- [x] Authentication on all `/api/v1/*` endpoints.
- [x] Pagination, newest-first ordering, soft-delete filtering, 404 handling,
  camelCase fields, and nested tracker/movie/rule responses.
- [x] OpenAPI documentation through FastAPI.

### Workflows and integrations

- [x] RSS retrieval and defused XML parsing.
- [x] Torrent title normalization, metadata extraction, rule matching, and deduplication.
- [x] OMDb lookup and movie caching by title/year hash.
- [x] Statistics grouping for daily, weekly, monthly, and yearly periods.
- [x] Configurable SMTP notifications.
- [x] CLI entry points for migration, search, and statistics workflows.
- [x] Docker Compose WireMock, database initialization, and Newman execution.

## Test strategy

- [x] Unit tests under `tests/unit/clients/`, `repositories/`, and `services/`.
- [x] Unit tests mock database and external boundaries.
- [x] Integration tests under `tests/integration/routers/` use FastAPI's
  synchronous `TestClient` and isolated SQLite data.
- [x] Newman E2E tests remain Docker-only and outside pytest.
- [x] External OMDb and RSS behavior is declared in `mocks/external/mappings/`.
- [x] Unit and integration tests run independently.
- [x] Unit coverage target: 90%.
- [x] Integration router coverage target: 90%.

Current validation baseline:

- `pytest tests/unit` — 46 tests passed.
- `pytest tests/integration` — 21 tests passed.
- Unit coverage is configured for the client, repository, and service layers.
- Integration coverage: 98% for routers.

## Delivery and documentation

- [x] Ruff formatting and linting.
- [x] `ty` type checking.
- [x] Bandit security scanning configuration.
- [x] GitHub Actions workflow for build, test, and Docker/Newman jobs.
- [x] Postman collection and environment files.
- [x] Docker Compose E2E stack with disposable seeded data.
- [x] Environment and local-development documentation.

## Remaining production work

- [x] Replace the explicit SQLite schema initializer with versioned Alembic migrations.
- [ ] Make production administrator provisioning environment-driven.
- [x] Validate the GitHub Actions Docker/Newman workflow against the current
  repository-specific Compose and Postman names before the first release.

## Source compatibility

The implementation preserves the Laravel API paths, authentication claim names,
pagination contract, response field names, soft-delete behavior, and nested
catalogue relationships. Background workflows remain available through the
Python CLI and services, while deployment scheduling is intentionally external.
