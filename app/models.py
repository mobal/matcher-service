from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MovieResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = None
    year: str | None = None
    rated: str | None = None
    released: date | None = None
    runtime: str | None = None
    genre: str | None = None
    director: str | None = None
    writer: str | None = None
    actors: str | None = None
    plot: str | None = None
    language: str | None = None
    country: str | None = None
    poster: str | None = None
    imdb_id: str | None = None
    dvd: date | None = None


class RuleResponse(APIModel):
    title: str
    uuid: str
    value: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TrackerResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = None
    url: str
    rss: str
    rules: list[RuleResponse] = Field(default_factory=list)


class TorrentResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = None
    uri: str
    tracker: str
    movie: MovieResponse | None = None


class Pagination(APIModel):
    current_page: int
    data: list[Any]
    from_: int | None = Field(default=None, serialization_alias="from")
    last_page: int
    per_page: int
    to: int | None = None
    total: int
