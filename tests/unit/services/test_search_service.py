from typing import cast
from unittest.mock import Mock

from app.models.request.movie import MovieLookupRequest
from app.models.response.catalogue import CatalogueRow
from app.services.search_service import SearchService


class TestSearchService:
    def test_search_skips_duplicate_and_unmatched_items(
        self, search_service: SearchService
    ) -> None:
        rss = cast(Mock, search_service._rss)
        torrents = cast(Mock, search_service._torrents)
        catalogue = cast(Mock, search_service._catalogue)
        tracker = CatalogueRow(
            id=1,
            title="Tracker",
            rss="https://tracker.test/rss",
            rules=[CatalogueRow(value="1080p")],
        )
        catalogue.page.return_value = ([tracker], 1)
        catalogue.tracker_rules.return_value = tracker.rules
        rss.fetch_items.return_value = [
            ("[group] Movie 1080p", "duplicate-uri"),
            ("[group] Movie 720p", "unmatched-uri"),
        ]
        torrents.exists_by_title.side_effect = [True, False]

        assert search_service.search() == 0
        torrents.create.assert_not_called()

    def test_search_creates_torrent_and_attaches_movie(
        self, search_service: SearchService
    ) -> None:
        rss = cast(Mock, search_service._rss)
        torrents = cast(Mock, search_service._torrents)
        catalogue = cast(Mock, search_service._catalogue)
        movies = cast(Mock, search_service._movies)
        mail = cast(Mock, search_service._mail)
        tracker = CatalogueRow(
            id=7,
            title="Tracker",
            rss="https://tracker.test/rss",
            rules=[CatalogueRow(value="1080p")],
        )
        catalogue.page.return_value = ([tracker], 1)
        catalogue.tracker_rules.return_value = tracker.rules
        rss.fetch_items.return_value = [("Movie.2025.1080p", "magnet")]
        torrents.exists_by_title.return_value = False
        torrents.create.return_value = CatalogueRow(id=8)
        movies.get_movie_info.return_value = CatalogueRow(id=9, title="Movie")

        assert search_service.search() == 1
        torrents.create.assert_called_once()
        movies.get_movie_info.assert_called_once_with(
            MovieLookupRequest(title="Movie", year=2025, media_type="movie")
        )
        torrents.attach_movie.assert_called_once_with(8, 9)
        mail.send.assert_called_once()

    def test_search_ignores_trackers_without_rules(
        self, search_service: SearchService
    ) -> None:
        catalogue = cast(Mock, search_service._catalogue)
        catalogue.page.return_value = ([CatalogueRow(id=1, title="Empty")], 1)
        catalogue.tracker_rules.return_value = []

        assert search_service.search() == 0
        cast(Mock, search_service._rss).fetch_items.assert_not_called()

    def test_metadata_parses_movie_release_name(
        self, search_service: SearchService
    ) -> None:
        metadata = search_service.metadata("The.Movie.2025.1080p.BluRay")
        assert metadata is not None
        assert metadata.title == "The Movie"
        assert metadata.year == 2025
        assert metadata.media_type == "movie"

    def test_metadata_parses_series_release_name(
        self, search_service: SearchService
    ) -> None:
        metadata = search_service.metadata("The.Show.S02E03.1080p")
        assert metadata is not None
        assert metadata.title == "The Show"
        assert metadata.year is None
        assert metadata.media_type == "series"

    def test_metadata_returns_none_for_non_release_title(
        self, search_service: SearchService
    ) -> None:
        assert search_service.metadata("Unstructured torrent title") is None

    def test_rule_matching_preserves_rule_order(
        self, search_service: SearchService
    ) -> None:
        assert search_service.matches_rule(
            "Movie.1080p.BluRay.x265", "1080p,BluRay,x265"
        )
        assert not search_service.matches_rule("Movie.BluRay.1080p", "1080p,BluRay")

    def test_rule_matching_ignores_empty_rule_parts(
        self, search_service: SearchService
    ) -> None:
        assert search_service.matches_rule("Movie.1080p", ",1080p,,")

    def test_normalize_title_removes_bracketed_metadata(
        self, search_service: SearchService
    ) -> None:
        assert (
            search_service.normalize_title("Movie Name [Group] 1080p")
            == "Movie.Name.1080p"
        )

    def test_normalize_title_returns_empty_for_brackets_only(
        self, search_service: SearchService
    ) -> None:
        assert search_service.normalize_title("[release-group]") == ""
