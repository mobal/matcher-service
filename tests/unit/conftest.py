import pytest

from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.torrent_repository import TorrentRepository


@pytest.fixture
def catalogue_repository() -> CatalogueRepository:
    return CatalogueRepository()


@pytest.fixture
def movie_repository() -> MovieRepository:
    return MovieRepository()


@pytest.fixture
def statistics_repository() -> StatisticsRepository:
    return StatisticsRepository()


@pytest.fixture
def torrent_repository() -> TorrentRepository:
    return TorrentRepository()
