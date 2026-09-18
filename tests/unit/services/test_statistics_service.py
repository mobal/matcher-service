from datetime import UTC, datetime
from typing import cast
from unittest.mock import Mock

import pytest

from app.models.response.statistics import StatisticsTorrent
from app.services.statistics_service import StatisticsService


class TestStatisticsService:
    def test_report_rejects_unknown_period(
        self, statistics_service: StatisticsService
    ) -> None:
        service = statistics_service
        start = datetime.now(UTC)
        end = datetime.now(UTC)

        with pytest.raises(ValueError):
            service.report("hourly", start, end)

    def test_range_for_supports_all_periods_and_rejects_unknown(self) -> None:

        reference = datetime(2025, 3, 15, tzinfo=UTC)
        for period in ("daily", "weekly", "monthly", "yearly"):
            start, end = StatisticsService.range_for(period, reference)
            assert start < end

        invalid_period = "hourly"

        with pytest.raises(ValueError):
            StatisticsService.range_for(invalid_period, reference)

    def test_report_groups_week_month_and_year(
        self, statistics_service: StatisticsService
    ) -> None:
        repository = cast(Mock, statistics_service._repository)
        repository.between.return_value = [
            StatisticsTorrent(title="A", created_at="2025-01-06T12:00:00+00:00")
        ]

        service = statistics_service
        start = datetime.now(UTC)
        end = datetime.now(UTC)

        weekly = service.report("weekly", start, end)
        monthly = service.report("monthly", start, end)
        yearly = service.report("yearly", start, end)

        assert weekly
        assert monthly
        assert yearly

    def test_report_groups_torrents_in_configured_timezone(
        self, statistics_service: StatisticsService
    ) -> None:
        repository = cast(Mock, statistics_service._repository)
        repository.between.return_value = [
            StatisticsTorrent(
                title="Before midnight", created_at="2025-01-01T23:30:00+00:00"
            ),
            StatisticsTorrent(
                title="After midnight", created_at="2025-01-02T00:30:00+00:00"
            ),
        ]

        report = statistics_service.report(
            "daily", datetime(2025, 1, 1, tzinfo=UTC), datetime(2025, 1, 3, tzinfo=UTC)
        )
        assert list(report) == ["2025-01-02"]
        assert [torrent.title for torrent in report["2025-01-02"]] == [
            "Before midnight",
            "After midnight",
        ]

    def test_range_for_monthly_returns_previous_local_month(
        self,
    ) -> None:
        from app.settings import settings

        original_timezone = settings.timezone
        settings.timezone = "Europe/Budapest"
        try:
            start, end = StatisticsService.range_for(
                "monthly", datetime(2025, 3, 15, tzinfo=UTC)
            )

        finally:
            settings.timezone = original_timezone

        assert start.isoformat().startswith("2025-02-01T00:00:00")
        assert end.isoformat().startswith("2025-02-28T23:59:59")

    def test_send_does_not_mail_empty_report(
        self, statistics_service: StatisticsService
    ) -> None:
        repository = cast(Mock, statistics_service._repository)
        repository.between.return_value = []
        mail = cast(Mock, statistics_service._mail)

        result = statistics_service.send(
            "daily", datetime(2025, 1, 1, tzinfo=UTC), datetime(2025, 1, 2, tzinfo=UTC)
        )

        assert not result
        mail.send.assert_not_called()

    def test_send_renders_non_empty_report(
        self, statistics_service: StatisticsService
    ) -> None:
        repository = cast(Mock, statistics_service._repository)
        repository.between.return_value = [
            StatisticsTorrent(title="Demo", created_at="2025-01-01T12:00:00+00:00")
        ]
        mail = cast(Mock, statistics_service._mail)
        mail.send.return_value = True

        result = statistics_service.send(
            "daily", datetime(2025, 1, 1, tzinfo=UTC), datetime(2025, 1, 2, tzinfo=UTC)
        )

        assert result
        mail.send.assert_called_once()
        message = mail.send.call_args.kwargs
        assert message["subject"] == "Daily statistics"
        assert "Demo" in message["body"]
