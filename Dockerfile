FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends --yes curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests
COPY README.md ./README.md
RUN uv sync --frozen --no-dev

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=12 \
    CMD curl -fsS http://localhost:8080/health || exit 1

CMD ["uv", "run", "--no-dev", "uvicorn", "app.api_handler:app", "--host", "0.0.0.0", "--port", "8080"]
