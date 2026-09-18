from datetime import datetime

from pydantic import BaseModel, ConfigDict, RootModel


class StatisticsTorrent(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int | None = None
    uuid: str | None = None
    title: str
    uri: str | None = None
    tracker_id: int | None = None
    movie_id: int | None = None
    created_at: datetime


class StatisticsReport(RootModel[dict[str, list[StatisticsTorrent]]]):
    def __bool__(self) -> bool:
        return bool(self.root)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, label: str) -> list[StatisticsTorrent]:
        return self.root[label]
