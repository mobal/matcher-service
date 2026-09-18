from pydantic import BaseModel, ConfigDict


class UserClaims(BaseModel):
    model_config = ConfigDict(extra="allow")

    sub: str | None = None
    iss: str | None = None
    aud: str | list[str] | None = None
    exp: int | None = None
    iat: int | None = None
    jti: str | None = None
    scope: str | None = None
