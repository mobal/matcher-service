import httpx2 as httpx
from defusedxml import ElementTree

from app.settings import settings


class RSSClient:
    def fetch_items(self, url: str) -> list[tuple[str, str]]:
        response = httpx.get(url, timeout=settings.http_timeout_seconds)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        return [
            (item.findtext("title", default=""), item.findtext("link", default=""))
            for item in root.findall(".//item")
        ]
