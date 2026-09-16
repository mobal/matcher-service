import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.logging_config import configure_logging
from app.middleware import CorrelationIdMiddleware
from app.routers.catalogue import router as catalogue_router
from app.settings import settings

configure_logging(getattr(settings, "log_level", "INFO"))

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Matcher Service API",
    summary="Torrent catalogue and matching service",
    description=(
        "Authenticated catalogue endpoints and background workflows for "
        "trackers, rules, torrents, movies, and statistics. Authentication "
        "tokens are issued by the external auth-service."
    ),
    version=settings.app_version,
    debug=settings.debug,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Matcher Service Team"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {
            "name": "system",
            "description": "Service health and operational endpoints.",
        },
        {
            "name": "catalogue",
            "description": "Read-only movies, torrents, trackers, and rules.",
        },
    ],
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(catalogue_router, prefix="/api")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _: Request, error: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status": 422,
            "error": "Validation Error",
            "errors": jsonable_encoder(error.errors()),
        },
    )


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, error: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"status": error.status_code, "error": error.detail},
        headers=error.headers,
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, error: Exception) -> JSONResponse:
    detail = (
        f"{type(error).__name__}: {error}"
        if settings.debug
        else "Internal Server Error"
    )
    logger.error(
        "Unhandled application error",
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(status_code=500, content={"status": 500, "error": detail})


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.api_handler:app", host="127.0.0.1", port=8080, reload=settings.debug
    )
