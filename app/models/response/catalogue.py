from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CatalogueRow(APIModel):
    id: int | None = None
    uuid: str | None = None
    title: str | None = None
    value: str | None = None
    url: str | None = None
    rss: str | None = None
    uri: str | None = None
    tracker_id: int | None = None
    movie_id: int | None = None
    tracker_title: str | None = None
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
    awards: str | None = None
    poster: str | None = None
    metascore: str | None = None
    imdb_rating: str | None = None
    imdb_votes: str | None = None
    imdb_id: str | None = None
    type: str | None = None
    dvd: date | None = None
    box_office: str | None = None
    production: str | None = None
    website: str | None = None
    response: str | None = None
    hash: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    movie: "CatalogueRow | None" = None
    rules: list["CatalogueRow"] = Field(default_factory=list)


class CataloguePage(APIModel):
    rows: list[CatalogueRow]
    total: int
    page: int
    size: int


class MovieResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
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
    imdb_id: str | None = Field(default=None, serialization_alias="imdbID")
    dvd: date | None = None


class RuleResponse(APIModel):
    title: str
    uuid: str
    value: str
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    updated_at: datetime | None = Field(default=None, serialization_alias="updatedAt")


class TrackerResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    url: str
    rss: str
    rules: list[RuleResponse] = Field(default_factory=list)


class TorrentResponse(APIModel):
    title: str
    uuid: str
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    uri: str
    tracker: str
    movie: MovieResponse | None = None


class Pagination(APIModel):
    current_page: int
    data: list[object]
    from_: int | None = Field(default=None, serialization_alias="from")
    last_page: int
    per_page: int
    to: int | None = None
    total: int


class HealthResponse(APIModel):
    status: str
