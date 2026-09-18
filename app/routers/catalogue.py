import math
from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPBearer

from app.dependencies import get_catalogue_service, get_current_user
from app.models.response.catalogue import (
    CatalogueRow,
    MovieResponse,
    Pagination,
    RuleResponse,
    TorrentResponse,
    TrackerResponse,
)
from app.repositories.catalogue_repository import CatalogueRepository
from app.services.catalogue_service import CatalogueService
from app.settings import settings

bearer_scheme = HTTPBearer(scheme_name="bearerAuth", auto_error=False)

router = APIRouter(
    prefix="/v1",
    tags=["catalogue"],
    dependencies=[Depends(get_current_user), Security(bearer_scheme)],
)


def pagination(
    rows: list[CatalogueRow],
    total: int,
    page: int,
    size: int,
    transform: Callable[[CatalogueRow], object],
) -> Pagination:
    last_page = max(1, math.ceil(total / size))
    return Pagination(
        data=[transform(row) for row in rows],
        current_page=page,
        from_=(page - 1) * size + 1 if rows else None,
        last_page=last_page,
        per_page=size,
        to=(page - 1) * size + len(rows) if rows else None,
        total=total,
    )


def page_args(
    page: int = Query(1, ge=1),
    size: int = Query(settings.page_size, ge=1, le=settings.max_page_size),
) -> tuple[int, int]:
    return page, size


def movie(row: CatalogueRow) -> MovieResponse:
    return MovieResponse.model_validate(row)


def rule(row: CatalogueRow) -> RuleResponse:
    return RuleResponse(
        title=row.title or "",
        uuid=row.uuid or "",
        value=row.value or "",
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def tracker(row: CatalogueRow, repo: CatalogueRepository) -> TrackerResponse:
    return TrackerResponse(
        title=row.title or "",
        uuid=row.uuid or "",
        created_at=row.created_at,
        url=row.url or "",
        rss=row.rss or "",
        rules=[rule(item) for item in repo.tracker_rules(row.id or 0)],
    )


def torrent(row: CatalogueRow) -> TorrentResponse:
    return TorrentResponse(
        title=row.title or "",
        uuid=row.uuid or "",
        created_at=row.created_at,
        uri=row.uri or "",
        tracker=row.tracker_title or "",
        movie=movie(row.movie) if row.movie else None,
    )


@router.get("/movies", response_model=Pagination)
def movies(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> Pagination:
    page, size = args
    result = service.page("movies", page, size)
    return pagination(result.rows, result.total, page, size, movie)


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def movie_show(
    movie_id: str, service: Annotated[CatalogueService, Depends(get_catalogue_service)]
) -> MovieResponse:
    row = service.repository.by_uuid("movies", movie_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return movie(row)


@router.get("/trackers", response_model=Pagination)
def trackers(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> Pagination:
    page, size = args
    result = service.page("trackers", page, size)
    return pagination(
        result.rows,
        result.total,
        page,
        size,
        lambda row: tracker(row, service.repository),
    )


@router.get("/trackers/{tracker_id}", response_model=TrackerResponse)
def tracker_show(
    tracker_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> TrackerResponse:
    row = service.repository.by_uuid("trackers", tracker_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return tracker(row, service.repository)


@router.get("/trackers/{tracker_id}/rules", response_model=Pagination)
def rules(
    tracker_id: str,
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> Pagination:
    track = service.repository.by_uuid("trackers", tracker_id)
    if not track:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    page, size = args
    rows, total = service.repository.rules(track.id or 0, page, size)
    return pagination(rows, total, page, size, rule)


@router.get("/trackers/{tracker_id}/rules/{rule_id}", response_model=RuleResponse)
def rule_show(
    tracker_id: str,
    rule_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> RuleResponse:
    track = service.repository.by_uuid("trackers", tracker_id)
    if not track:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    rows, _ = service.repository.rules(track.id or 0, 1, 1, rule_id)
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return rule(rows[0])


@router.get("/torrents", response_model=Pagination)
def torrents(
    args: Annotated[tuple[int, int], Depends(page_args)],
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> Pagination:
    page, size = args
    result = service.page("torrents", page, size)
    return pagination(
        result.rows,
        result.total,
        page,
        size,
        lambda row: torrent(service.repository.torrent_details(row)),
    )


@router.get("/torrents/{torrent_id}", response_model=TorrentResponse)
def torrent_show(
    torrent_id: str,
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> TorrentResponse:
    row = service.repository.by_uuid("torrents", torrent_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    with_movie = service.repository.torrent_details(row)
    return torrent(with_movie)
