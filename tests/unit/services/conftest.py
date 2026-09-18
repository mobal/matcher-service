from unittest.mock import Mock

import pytest

from app.clients.omdb_client import OMDbClient
from app.clients.rss_client import RSSClient
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.torrent_repository import TorrentRepository
from app.services.catalogue_service import CatalogueService
from app.services.mail_service import MailService
from app.services.movie_service import MovieService
from app.services.search_service import SearchService
from app.services.statistics_service import StatisticsService


@pytest.fixture
def catalogue_service() -> CatalogueService:
    return CatalogueService(Mock(spec=CatalogueRepository))


@pytest.fixture
def mail_service() -> MailService:
    return MailService()


@pytest.fixture
def movie_service() -> MovieService:
    return MovieService(Mock(spec=MovieRepository), Mock(spec=OMDbClient))


@pytest.fixture
def search_service() -> SearchService:
    return SearchService(
        Mock(spec=RSSClient),
        Mock(spec=MovieService),
        Mock(spec=TorrentRepository),
        Mock(spec=CatalogueRepository),
        Mock(spec=MailService),
    )


@pytest.fixture
def statistics_service() -> StatisticsService:
    return StatisticsService(Mock(spec=StatisticsRepository), Mock(spec=MailService))
