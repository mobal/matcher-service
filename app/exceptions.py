from typing import Any

from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(
        self, detail: Any = "The provided credentials do not match our records"
    ):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: Any = "Not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ConflictException(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status.HTTP_409_CONFLICT, detail)
