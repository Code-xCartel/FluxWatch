from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request

from flux_watch_api.managers.auth.auth_manager import AuthManager
from flux_watch_api.models.account import AccountCreate, AccountSession
from flux_watch_api.models.response_schema import MessageResponse

auth_router = APIRouter()


@auth_router.post("/sign-up", tags=["sign-up"], status_code=status.HTTP_201_CREATED)
def sign_up(account: AccountCreate, auth_manager: AuthManager = Depends()):
    auth_manager.create_new(
        name=account.name,
        email=account.email,
        password=account.password,
    )
    ## send email for account activation
    return MessageResponse(msg="Account created successfully")


@auth_router.post(
    "/sign-in", tags=["sign-in"], status_code=status.HTTP_200_OK, response_model=AccountSession
)
def sign_in(request: Request, auth_manager: AuthManager = Depends()):
    return auth_manager.authenticate_and_save(
        auth_header=request.headers.get("Authorization", None)
    )
