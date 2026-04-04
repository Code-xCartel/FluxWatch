from fastapi import HTTPException
from starlette import status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Record not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsError(HTTPException):
    def __init__(self, detail: str = "Record already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class TooManyRequestsError(HTTPException):
    def __init__(self, detail: str = "Too many requests made"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ServerError(HTTPException):
    def __init__(self, detail: str = "An internal server error occurred"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
