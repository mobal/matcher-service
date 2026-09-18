import logging

import httpx2 as httpx
from defusedxml import ElementTree

from app.settings import settings

logger = logging.getLogger(__name__)


class RSSClient:
    def fetch_items(self, url: str) -> list[tuple[str, str]]:
        logger.info("Fetching RSS feed: %s", url)

        response = httpx.get(url, timeout=settings.http_timeout_seconds)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        items = [
            (item.findtext("title", default=""), item.findtext("link", default=""))
            for item in root.findall(".//item")
        ]

        logger.info("Fetched %d RSS item(s) from %s", len(items), url)
        return items
