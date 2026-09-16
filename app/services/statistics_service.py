from collections import defaultdict
from datetime import datetime, timedelta
from typing import ClassVar, Protocol
from zoneinfo import ZoneInfo

from app.repositories.statistics_repository import StatisticsRepository
from app.services.mail_service import MailService
from app.settings import settings


class StatisticsRepositoryProtocol(Protocol):
    def between(self, start: datetime, end: datetime) -> list[dict]: ...


class MailServiceProtocol(Protocol):
    def send(
        self, *, subject: str, body: str, recipients: list[str] | None = None
    ) -> bool: ...


class StatisticsService:
    _SUBJECTS: ClassVar[dict[str, str]] = {
        "daily": "Daily statistics",
        "weekly": "Weekly statistics",
        "monthly": "Monthly statistics",
        "yearly": "Yearly statistics",
    }

    def __init__(
        self,
        repository: StatisticsRepositoryProtocol | None = None,
        mail: MailServiceProtocol | None = None,
    ) -> None:
        self._repository = repository or StatisticsRepository()
        self._mail = mail or MailService()

    def report(
        self, period: str, start: datetime, end: datetime
    ) -> dict[str, list[dict]]:
        if period not in self._SUBJECTS:
            raise ValueError("period must be daily, weekly, monthly, or yearly")
        torrents = self._repository.between(start, end)
        grouped: defaultdict[str, list[dict]] = defaultdict(list)
        for torrent in torrents:
            grouped[self._group_key(torrent["created_at"], period)].append(torrent)
        return dict(grouped)

    def send(self, period: str, start: datetime, end: datetime) -> bool:
        groups = self.report(period, start, end)
        if not groups:
            return False
        body = self._render(groups)
        return self._mail.send(subject=self._SUBJECTS[period], body=body)

    @staticmethod
    def range_for(period: str, reference: datetime) -> tuple[datetime, datetime]:
        local_date = reference.astimezone(ZoneInfo(settings.timezone)).date()
        if period == "daily":
            first = last = local_date - timedelta(days=1)
        elif period == "weekly":
            last = local_date - timedelta(days=local_date.weekday() + 1)
            first = last - timedelta(days=6)
        elif period == "monthly":
            last = local_date.replace(day=1) - timedelta(days=1)
            first = last.replace(day=1)
        elif period == "yearly":
            last = local_date.replace(month=1, day=1) - timedelta(days=1)
            first = last.replace(month=1, day=1)
        else:
            raise ValueError("period must be daily, weekly, monthly, or yearly")
        timezone = ZoneInfo(settings.timezone)
        return (
            datetime.combine(first, datetime.min.time(), timezone),
            datetime.combine(last, datetime.max.time(), timezone),
        )

    @staticmethod
    def _group_key(created_at: str, period: str) -> str:
        timestamp = datetime.fromisoformat(created_at)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))
        local = timestamp.astimezone(ZoneInfo(settings.timezone))
        if period == "daily":
            return local.date().isoformat()
        if period == "monthly":
            return local.strftime("%Y-%m")
        if period == "yearly":
            return local.strftime("%Y")
        week_start = local.date() - timedelta(days=local.weekday())
        week_end = week_start + timedelta(days=6)
        return f"{week_start} - {week_end}"

    @staticmethod
    def _render(groups: dict[str, list[dict]]) -> str:
        lines: list[str] = []
        for label, torrents in groups.items():
            lines.append(f"{label}: {len(torrents)} torrent(s)")
            lines.extend(f"- {torrent['title']}" for torrent in torrents)
        return "\n".join(lines)
