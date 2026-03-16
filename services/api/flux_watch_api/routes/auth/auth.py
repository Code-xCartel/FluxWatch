from fastapi import APIRouter, Depends
from starlette import status

from flux_watch_api.models.account import AccountCreate, AccountLogin, AccountSession
from flux_watch_api.models.response_schema import MessageResponse
from flux_watch_api.repository.auth.auth import AuthRepository

auth_router = APIRouter()


@auth_router.post("/sign-up", tags=["sign-up"], status_code=status.HTTP_201_CREATED)
def sign_up(account: AccountCreate, auth_repo: AuthRepository = Depends()):
    auth_repo.create_account(account)
    return MessageResponse(msg="Account created successfully")


@auth_router.post(
    "/sign-in", tags=["sign-in"], status_code=status.HTTP_200_OK, response_model=AccountSession
)
def sign_in(account: AccountLogin, auth_repo: AuthRepository = Depends()):
    return auth_repo.authenticate_account(account)
