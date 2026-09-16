import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any

CORRELATION_ID_HEADER = "x-correlation-id"
correlation_id: ContextVar[str] = ContextVar(CORRELATION_ID_HEADER, default="")


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
        correlation_id.set(value)

        async def send_with_correlation(message: dict) -> None:
            if message["type"] == "http.response.start":
                message = dict(message)
                message["headers"] = [
                    *message.get("headers", []),
                    (CORRELATION_ID_HEADER.encode(), value.encode()),
                ]
            await send(message)

        await self.app(scope, receive, send_with_correlation)
