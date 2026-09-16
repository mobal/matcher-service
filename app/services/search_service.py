import re
from dataclasses import dataclass

from app.clients.rss_client import RSSClient
from app.repositories import CatalogueRepository
from app.repositories.torrent_repository import TorrentRepository
from app.services.mail_service import MailService
from app.services.movie_service import MovieService


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
        for tracker in self._trackers_with_rules():
            for title, uri in self._rss.fetch_items(tracker["rss"]):
                normalized = self.normalize_title(title)
                if not normalized or self._torrents.exists_by_title(normalized):
                    continue
                if not any(
                    self.matches_rule(normalized, item["value"])
                    for item in tracker["rules"]
                ):
                    continue
                torrent = self._torrents.create(
                    title=normalized, uri=uri, tracker_id=tracker["id"]
                )
                metadata = self.metadata(normalized)
                if metadata:
                    movie = self._movies.get_movie_info(
                        metadata.title, metadata.year, metadata.media_type
                    )
                    if movie:
                        self._torrents.attach_movie(torrent["id"], movie["id"])
                        self._mail.send(
                            subject=movie.get("title", metadata.title),
                            body=(
                                f"Movie: {movie.get('title', metadata.title)}\n"
                                f"Torrent: {normalized}\n"
                                f"URI: {uri}"
                            ),
                        )
                created += 1
        return created

    def _trackers_with_rules(self) -> list[dict]:
        trackers, _ = self._catalogue.page("trackers", 1, 10000)
        for tracker in trackers:
            tracker["rules"] = self._catalogue.tracker_rules(tracker["id"])
        return [tracker for tracker in trackers if tracker["rules"]]

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
        without_groups = re.sub(r"[\[\{\(].*?[\]\}\)]", "", title).strip()
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
