import datetime
from uuid import UUID

from flux_watch_api.models.base import APIModel


class AccountLogin(APIModel):
    email: str
    password: str


class AccountCreate(AccountLogin):
    name: str


class Account(APIModel):
    id: UUID
    name: str
    principal: str
    is_active: bool
    is_locked: bool
    failed_login_attempts: int


class AccountSession(APIModel):
    session_token: str
    ttl: datetime.datetime
    account: Account
