import argparse
from datetime import UTC, datetime

from app.clients.omdb_client import OMDbClient
from app.clients.rss_client import RSSClient
from app.migrations import upgrade
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.torrent_repository import TorrentRepository
from app.services.mail_service import MailService
from app.services.movie_service import MovieService
from app.services.search_service import SearchService
from app.services.statistics_service import StatisticsService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="matcher-service")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="create or update the application schema")
    commands.add_parser("search", help="fetch tracker RSS feeds and save torrents")
    statistics = commands.add_parser("statistics", help="send torrent statistics")
    statistics.add_argument(
        "--type",
        choices=("daily", "weekly", "monthly", "yearly"),
        default="daily",
    )

    return parser


def run_search() -> int:
    service = SearchService(
        RSSClient(),
        MovieService(MovieRepository(), OMDbClient()),
        TorrentRepository(),
        CatalogueRepository(),
        MailService(),
    )

    return service.search()


def run_statistics(period: str) -> bool:
    start, end = StatisticsService.range_for(period, datetime.now(UTC))

    return StatisticsService().send(period, start, end)


def main() -> None:
    arguments = build_parser().parse_args()
    upgrade()
    if arguments.command == "migrate":
        print("Database schema is ready")
    elif arguments.command == "search":
        print(f"Created {run_search()} torrent(s)")
    else:
        sent = run_statistics(arguments.type)
        print("Statistics email sent" if sent else "No statistics to send")
