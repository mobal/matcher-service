from pydantic import BaseModel, ConfigDict


class MovieLookupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    year: int | None = None
    media_type: str | None = None


class MovieCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uuid: str
    title: str
    year: str | None = None
    rated: str | None = None
    released: str | None = None
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
    dvd: str | None = None
    box_office: str | None = None
    production: str | None = None
    website: str | None = None
    response: str | None = None
    hash: str
    created_at: str
    updated_at: str
