from pydantic import BaseModel, ConfigDict


class TorrentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    uri: str
    tracker_id: int
    movie_id: int | None = None
