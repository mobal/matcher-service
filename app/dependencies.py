from typing import Annotated

from fastapi import Depends, Request

from app.clients.omdb_client import OMDbClient
from app.clients.rss_client import RSSClient
from app.exceptions import InvalidCredentialsException
from app.models.response.auth import UserClaims
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.torrent_repository import TorrentRepository
from app.security import decode_token
from app.services.catalogue_service import CatalogueService
from app.services.mail_service import MailService
from app.services.movie_service import MovieService
from app.services.search_service import SearchService
from app.services.statistics_service import StatisticsService


def get_current_user(request: Request) -> UserClaims:
    scheme, _, raw_token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not raw_token:
        raise InvalidCredentialsException("Not authenticated")
    try:
        return decode_token(raw_token)
    except (KeyError, TypeError, ValueError):
        raise InvalidCredentialsException("Not authenticated")


def get_catalogue_repository() -> CatalogueRepository:
    return CatalogueRepository()


def get_movie_repository() -> MovieRepository:
    return MovieRepository()


def get_statistics_repository() -> StatisticsRepository:
    return StatisticsRepository()


def get_torrent_repository() -> TorrentRepository:
    return TorrentRepository()


def get_omdb_client() -> OMDbClient:
    return OMDbClient()


def get_rss_client() -> RSSClient:
    return RSSClient()


def get_mail_service() -> MailService:
    return MailService()


def get_catalogue_service(
    repository: Annotated[CatalogueRepository, Depends(get_catalogue_repository)],
) -> CatalogueService:
    return CatalogueService(repository)


def get_movie_service(
    repository: Annotated[MovieRepository, Depends(get_movie_repository)],
    client: Annotated[OMDbClient, Depends(get_omdb_client)],
) -> MovieService:
    return MovieService(repository, client)


def get_search_service(
    rss: Annotated[RSSClient, Depends(get_rss_client)],
    movies: Annotated[MovieService, Depends(get_movie_service)],
    torrents: Annotated[TorrentRepository, Depends(get_torrent_repository)],
    catalogue: Annotated[CatalogueRepository, Depends(get_catalogue_repository)],
    mail: Annotated[MailService, Depends(get_mail_service)],
) -> SearchService:
    return SearchService(rss, movies, torrents, catalogue, mail)


def get_statistics_service(
    repository: Annotated[StatisticsRepository, Depends(get_statistics_repository)],
    mail: Annotated[MailService, Depends(get_mail_service)],
) -> StatisticsService:
    return StatisticsService(repository, mail)


CurrentUser = Annotated[UserClaims, Depends(get_current_user)]
