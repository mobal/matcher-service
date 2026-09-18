from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class OMDbMovieResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    title: str | None = Field(
        default=None, validation_alias=AliasChoices("Title", "title")
    )
    year: str | None = Field(
        default=None, validation_alias=AliasChoices("Year", "year")
    )
    rated: str | None = Field(
        default=None, validation_alias=AliasChoices("Rated", "rated")
    )
    released: str | None = Field(
        default=None, validation_alias=AliasChoices("Released", "released")
    )
    runtime: str | None = Field(
        default=None, validation_alias=AliasChoices("Runtime", "runtime")
    )
    genre: str | None = Field(
        default=None, validation_alias=AliasChoices("Genre", "genre")
    )
    director: str | None = Field(
        default=None, validation_alias=AliasChoices("Director", "director")
    )
    writer: str | None = Field(
        default=None, validation_alias=AliasChoices("Writer", "writer")
    )
    actors: str | None = Field(
        default=None, validation_alias=AliasChoices("Actors", "actors")
    )
    plot: str | None = Field(
        default=None, validation_alias=AliasChoices("Plot", "plot")
    )
    language: str | None = Field(
        default=None, validation_alias=AliasChoices("Language", "language")
    )
    country: str | None = Field(
        default=None, validation_alias=AliasChoices("Country", "country")
    )
    awards: str | None = Field(
        default=None, validation_alias=AliasChoices("Awards", "awards")
    )
    poster: str | None = Field(
        default=None, validation_alias=AliasChoices("Poster", "poster")
    )
    metascore: str | None = Field(
        default=None, validation_alias=AliasChoices("Metascore", "metascore")
    )
    imdb_rating: str | None = Field(
        default=None, validation_alias=AliasChoices("imdbRating", "imdb_rating")
    )
    imdb_votes: str | None = Field(
        default=None, validation_alias=AliasChoices("imdbVotes", "imdb_votes")
    )
    imdb_id: str | None = Field(
        default=None, validation_alias=AliasChoices("imdbID", "imdb_id")
    )
    media_type: str | None = Field(
        default=None, validation_alias=AliasChoices("Type", "type")
    )
    dvd: str | None = Field(default=None, validation_alias=AliasChoices("DVD", "dvd"))
    box_office: str | None = Field(
        default=None, validation_alias=AliasChoices("BoxOffice", "box_office")
    )
    production: str | None = Field(
        default=None, validation_alias=AliasChoices("Production", "production")
    )
    website: str | None = Field(
        default=None, validation_alias=AliasChoices("Website", "website")
    )
    response: str | None = Field(
        default=None, validation_alias=AliasChoices("Response", "response")
    )
