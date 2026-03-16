import base64
import uuid
from datetime import datetime, timedelta

import bcrypt

from flux_watch_api.schema import AccountORM, AccountSessionORM

DEFAULT_TTL = 24 * 60 * 60 * 1000  # one day in ms


class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def validate_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def make_ttl(ttl_days: int | None) -> datetime:
        return datetime.now() + timedelta(days=ttl_days or 1)

    @staticmethod
    def make_token(_id: uuid.UUID, account: AccountORM) -> str:
        _token = f"{_id}:{account.principal}"
        return base64.b64encode(_token.encode()).decode()

    def make_session(self, account: AccountORM, ttl_days: int | None = None) -> AccountSessionORM:
        _id = uuid.uuid4()

        return AccountSessionORM(
            id=_id,
            account_id=account.id,
            session_token=self.make_token(_id, account),
            ttl=self.make_ttl(ttl_days),
            account=account,
        )
