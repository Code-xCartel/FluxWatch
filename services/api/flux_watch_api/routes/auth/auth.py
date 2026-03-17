from fastapi import APIRouter, BackgroundTasks, Depends
from starlette import status
from starlette.requests import Request

from flux_watch_api.core.config import AppConfig
from flux_watch_api.managers.auth.auth_manager import AuthManager
from flux_watch_api.models.account import AccountCreate, AccountSession
from flux_watch_api.models.response_schema import MessageResponse
from flux_watch_api.services.email_service import EmailService

auth_router = APIRouter()


@auth_router.post("/sign-up", tags=["sign-up"], status_code=status.HTTP_201_CREATED)
def sign_up(
    account: AccountCreate,
    background_tasks: BackgroundTasks,
    auth_manager: AuthManager = Depends(),
    email_service: EmailService = Depends(),
    config: AppConfig = Depends(),
):
    token = auth_manager.create_new(
        name=account.name,
        email=account.email,
        password=account.password,
    )

    background_tasks.add_task(
        lambda: email_service.send_email(
            to_emails=account.email,
            subject="Activate Your Account",
            template_path="templates/email_verification.html",
            name=account.name,
            platform_link=config.PLATFORM_LINK,
            token=token,
        )
    )

    return MessageResponse(msg="Account created successfully")


@auth_router.post(
    "/sign-in", tags=["sign-in"], status_code=status.HTTP_200_OK, response_model=AccountSession
)
def sign_in(request: Request, auth_manager: AuthManager = Depends()):
    return auth_manager.authenticate_and_save(
        auth_header=request.headers.get("Authorization", None)
    )


@auth_router.post("/activate", tags=["activate"], status_code=status.HTTP_200_OK)
def activate(request: Request, auth_manager: AuthManager = Depends()):
    auth_manager.activate_account(request.headers.get("Authorization", None))
    return MessageResponse(msg="Account activated successfully")
