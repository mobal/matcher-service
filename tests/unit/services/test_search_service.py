from app.services.search_service import SearchService


class TestSearchService:
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
