from unittest.mock import Mock, patch

from app.clients.omdb_client import OMDbClient
from app.clients.rss_client import RSSClient
from app.models.request.movie import MovieLookupRequest
from app.settings import Settings


class TestOMDbClient:
    def test_returns_none_without_api_key(self) -> None:
        client_settings = Settings(omdb_api_key=None)
        with patch("app.clients.omdb_client.settings", client_settings):
            result = OMDbClient().get_movie(
                MovieLookupRequest(title="Movie", year=2025, media_type="movie")
            )

        assert result is None

    def test_requests_movie_details(self) -> None:
        client_settings = Settings(omdb_api_key="key")
        response = Mock()
        response.json.return_value = {"Response": "True", "Title": "Movie"}
        with (
            patch("app.clients.omdb_client.settings", client_settings),
            patch(
                "app.clients.omdb_client.httpx.get", return_value=response
            ) as request,
        ):
            result = OMDbClient().get_movie(
                MovieLookupRequest(title="Movie", year=2025, media_type="movie")
            )

        request.assert_called_once()
        response.raise_for_status.assert_called_once_with()
        assert result is not None
        assert result.response == "True"
        assert result.title == "Movie"


class TestRSSClient:
    def test_parses_feed_items(self) -> None:
        response = Mock(
            content=b"<rss><channel><item><title>A</title><link>u</link></item></channel></rss>"
        )
        with patch("app.clients.rss_client.httpx.get", return_value=response):
            result = RSSClient().fetch_items("https://feed.test/rss")

        assert result == [("A", "u")]
        response.raise_for_status.assert_called_once_with()
