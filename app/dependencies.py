from typing import Annotated, Any

from fastapi import Depends, Request

from app.exceptions import InvalidCredentialsException
from app.repositories import CatalogueRepository
from app.security import decode_token
from app.services import CatalogueService


def get_current_user(request: Request) -> dict[str, Any]:
    scheme, _, raw_token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not raw_token:
        raise InvalidCredentialsException("Not authenticated")
    try:
        return decode_token(raw_token)
    except (KeyError, TypeError, ValueError):
        raise InvalidCredentialsException("Not authenticated")


def get_catalogue_service() -> CatalogueService:
    return CatalogueService(CatalogueRepository())


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]
