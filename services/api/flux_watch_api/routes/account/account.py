from fastapi import APIRouter, Depends
from starlette import status

from flux_watch_api.models.account import Account
from flux_watch_api.repository.account.account import AccountRepository

accounts_router = APIRouter()


@accounts_router.get("/self", tags=["self"], status_code=status.HTTP_200_OK, response_model=Account)
def get_self(account_repo: AccountRepository = Depends()):
    return account_repo.get_self()
