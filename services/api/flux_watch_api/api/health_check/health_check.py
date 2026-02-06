from fastapi import APIRouter
from starlette import status

health_check_router = APIRouter()


@health_check_router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "OK"}
