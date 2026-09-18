import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPBearer

from app.dependencies import get_catalogue_service, get_current_user
from app.repositories.catalogue_repository import CatalogueRepository
from app.services.catalogue_service import CatalogueService
from app.settings import settings

bearer_scheme = HTTPBearer(scheme_name="bearerAuth", auto_error=False)

router = APIRouter(
    prefix="/v1",
    tags=["catalogue"],
    dependencies=[Depends(get_current_user), Security(bearer_scheme)],
)


def pagination(rows: list[dict], total: int, page: int, size: int, transform) -> dict:
    last_page = max(1, math.ceil(total / size))
    return {
        "data": [transform(row) for row in rows],
        "current_page": page,
        "from": (page - 1) * size + 1 if rows else None,
        "last_page": last_page,
        "per_page": size,
        "to": (page - 1) * size + len(rows) if rows else None,
        "total": total,
    }


def page_args(
    page: int = Query(1, ge=1),
    size: int = Query(settings.page_size, ge=1, le=settings.max_page_size),
) -> tuple[int, int]:
    return page, size


def movie(row: dict) -> dict:
    return {
        "title": row["title"],
        "uuid": row["uuid"],
        "createdAt": row.get("created_at"),
        "year": row.get("year"),
        "rated": row.get("rated"),
        "released": row.get("released"),
        "runtime": row.get("runtime"),
        "genre": row.get("genre"),
        "director": row.get("director"),
        "writer": row.get("writer"),
        "actors": row.get("actors"),
        "plot": row.get("plot"),
        "language": row.get("language"),
        "country": row.get("country"),
        "poster": row.get("poster"),
        "imdbID": row.get("imdb_id"),
        "dvd": row.get("dvd"),
    }


def rule(row: dict) -> dict:
    return {
        "title": row["title"],
        "uuid": row["uuid"],
        "value": row["value"],
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at"),
    }


def tracker(row: dict, repo: CatalogueRepository) -> dict:
    return {
        "title": row["title"],
        "uuid": row["uuid"],
        "createdAt": row.get("created_at"),
        "url": row["url"],
        "rss": row["rss"],
        "rules": [rule(item) for item in repo.tracker_rules(row["id"])],
    }


def torrent(row: dict) -> dict:
    return {
        "title": row["title"],
        "uuid": row["uuid"],
        "createdAt": row.get("created_at"),
        "uri": row["uri"],
        "tracker": row["tracker_title"],
        "movie": movie(row["movie"]) if row.get("movie") else None,
    }


@router.get("/movies")
def movies(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    page, size = args
    result = service.page("movies", page, size)
    return pagination(result["rows"], result["total"], page, size, movie)


@router.get("/movies/{movie_id}")
def movie_show(
    movie_id: str, service: Annotated[CatalogueService, Depends(get_catalogue_service)]
) -> dict:
    row = service.repository.by_uuid("movies", movie_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return movie(row)


@router.get("/trackers")
def trackers(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    page, size = args
    result = service.page("trackers", page, size)
    return pagination(
        result["rows"],
        result["total"],
        page,
        size,
        lambda row: tracker(row, service.repository),
    )


@router.get("/trackers/{tracker_id}")
def tracker_show(
    tracker_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    row = service.repository.by_uuid("trackers", tracker_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return tracker(row, service.repository)


@router.get("/trackers/{tracker_id}/rules")
def rules(
    tracker_id: str,
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    track = service.repository.by_uuid("trackers", tracker_id)
    if not track:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    page, size = args
    rows, total = service.repository.rules(track["id"], page, size)
    return pagination(rows, total, page, size, rule)


@router.get("/trackers/{tracker_id}/rules/{rule_id}")
def rule_show(
    tracker_id: str,
    rule_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    track = service.repository.by_uuid("trackers", tracker_id)
    if not track:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    rows, _ = service.repository.rules(track["id"], 1, 1, rule_id)
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return rule(rows[0])


@router.get("/torrents")
def torrents(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    page, size = args
    result = service.page("torrents", page, size)
    return pagination(
        result["rows"],
        result["total"],
        page,
        size,
        lambda row: torrent(service.repository.torrent_details(row)),
    )


@router.get("/torrents/{torrent_id}")
def torrent_show(
    torrent_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> dict:
    row = service.repository.by_uuid("torrents", torrent_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    with_movie = service.repository.torrent_details(row)
    return torrent(with_movie)
