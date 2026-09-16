import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any

CORRELATION_ID_HEADER = "x-correlation-id"
correlation_id: ContextVar[str] = ContextVar(CORRELATION_ID_HEADER, default="")
logger = logging.getLogger(__name__)


class CorrelationIdMiddleware:
    """Pure ASGI correlation middleware, avoiding BaseHTTPMiddleware overhead."""

    def __init__(self, app: Callable[..., Awaitable[Any]]) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        value = headers.get(CORRELATION_ID_HEADER.encode(), b"").decode() or str(
            uuid.uuid4()
        )
        correlation_token = correlation_id.set(value)
        started_at = time.perf_counter()
        response_status = 500

        async def send_with_correlation(message: dict) -> None:
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 500)
                message = dict(message)
                message["headers"] = [
                    *message.get("headers", []),
                    (CORRELATION_ID_HEADER.encode(), value.encode()),
                ]
            await send(message)

        try:
            await self.app(scope, receive, send_with_correlation)
        finally:
            logger.info(
                "%s %s %s %.3fs",
                scope.get("method", ""),
                scope.get("path", ""),
                response_status,
                time.perf_counter() - started_at,
                extra={"correlation_id": value},
            )
            correlation_id.reset(correlation_token)
