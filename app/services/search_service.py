import logging
import re
from dataclasses import dataclass

from app.clients.rss_client import RSSClient
from app.models.request.movie import MovieLookupRequest
from app.models.request.torrent import TorrentCreateRequest
from app.models.response.catalogue import CatalogueRow
from app.repositories.catalogue_repository import CatalogueRepository
from app.repositories.torrent_repository import TorrentRepository
from app.services.mail_service import MailService
from app.services.movie_service import MovieService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TorrentMetadata:
    title: str
    year: int | None
    media_type: str


class SearchService:
    def __init__(
        self,
        rss: RSSClient,
        movies: MovieService,
        torrents: TorrentRepository,
        catalogue: CatalogueRepository,
        mail: MailService | None = None,
    ) -> None:
        self._rss = rss
        self._movies = movies
        self._torrents = torrents
        self._catalogue = catalogue
        self._mail = mail or MailService()

    def search(self) -> int:
        created = 0
        logger.info("Starting torrent search")
        for tracker in self._trackers_with_rules():
            logger.info("Processing tracker %s", tracker.title)
            for title, uri in self._rss.fetch_items(tracker.rss or ""):
                created += self._process_item(tracker, title, uri)
        logger.info("Torrent search completed; created %d torrent(s)", created)

        return created

    def _process_item(self, tracker: CatalogueRow, title: str, uri: str) -> int:
        normalized = self.normalize_title(title)
        if not normalized or self._torrents.exists_by_title(normalized):
            return 0
        if not any(
            self.matches_rule(normalized, item.value or "") for item in tracker.rules
        ):
            return 0

        torrent = self._torrents.create(
            TorrentCreateRequest(title=normalized, uri=uri, tracker_id=tracker.id or 0)
        )
        metadata = self.metadata(normalized)
        if metadata:
            self._attach_movie(torrent.id or 0, metadata, normalized, uri)

        return 1

    def _attach_movie(
        self, torrent_id: int, metadata: TorrentMetadata, title: str, uri: str
    ) -> None:
        movie = self._movies.get_movie_info(
            MovieLookupRequest(
                title=metadata.title,
                year=metadata.year,
                media_type=metadata.media_type,
            )
        )
        if not movie:
            return

        self._torrents.attach_movie(torrent_id, movie.id or 0)
        self._mail.send(
            subject=movie.title or metadata.title,
            body=(
                f"Movie: {movie.title or metadata.title}\nTorrent: {title}\nURI: {uri}"
            ),
        )

    def _trackers_with_rules(self) -> list[CatalogueRow]:
        trackers, _ = self._catalogue.page("trackers", 1, 10000)
        for tracker in trackers:
            tracker.rules = self._catalogue.tracker_rules(tracker.id or 0)

        return [tracker for tracker in trackers if tracker.rules]

    @staticmethod
    def metadata(title: str) -> TorrentMetadata | None:
        match = re.match(
            r"(.*?)\.(\d{4}|S\d{2}(?:E\d{2})?)\.(.*)", title, re.IGNORECASE
        )
        if not match:
            return None
        release = match.group(2)

        return TorrentMetadata(
            title=match.group(1).replace(".", " "),
            year=int(release) if release.isdigit() else None,
            media_type="series" if release.lower().startswith("s") else "movie",
        )

    @staticmethod
    def normalize_title(title: str) -> str:
        without_groups = re.sub(r"[\[\{\(][^\]\}\)]*[\]\}\)]", "", title).strip()

        return re.sub(r"\s+", " ", without_groups).replace(" ", ".")

    @staticmethod
    def matches_rule(title: str, rule: str) -> bool:
        remainder = title.lower()
        for part in re.split(r"[\s;,-]+", rule.lower()):
            if not part:
                continue
            position = remainder.find(part)
            if position < 0:
                return False
            remainder = remainder[position + len(part) :]

        return True
