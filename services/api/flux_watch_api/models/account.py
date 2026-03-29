import datetime
import re
from uuid import UUID

from pydantic import Field, field_validator

from flux_watch_api.models.base import APIModel

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class Email(APIModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()

        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address")

        return v


class Password(APIModel):
    password: str = Field(..., min_length=8, max_length=64)


class AccountCreate(Email, Password):
    name: str


class Account(APIModel):
    id: UUID
    name: str
    principal: str
    is_active: bool
    is_locked: bool
    failed_login_attempts: int


class AccountSessionMinimal(APIModel):
    access_token: str
    ttl: datetime.datetime


class AccountSession(AccountSessionMinimal):
    account: Account


class ApiKey(APIModel):
    created_at: datetime.datetime
    last_used_at: datetime.datetime | None
    is_active: bool


class Sessions(APIModel):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    ttl: datetime.datetime | None


class SessionsResponse(APIModel):
    sessions: list[Sessions]
