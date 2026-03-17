import base64
import uuid
from datetime import datetime, timedelta

import bcrypt

from flux_watch_api.models.account import AccountSession
from flux_watch_api.schema import AccountORM, AccountSessionORM


class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def validate_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def make_ttl(ttl_days: float | None) -> datetime:
        return datetime.now() + timedelta(days=ttl_days or 1)

    @staticmethod
    def make_token(_id: uuid.UUID, account: AccountORM) -> str:
        _token = f"{_id}:{account.principal}"
        return base64.b64encode(_token.encode()).decode()

    def make_session(self, account: AccountORM, ttl_days: float | None = None) -> AccountSessionORM:
        return AccountSessionORM(
            account_id=account.id,
            ttl=self.make_ttl(ttl_days),
            account=account,
        )

    def enrich_session(self, session: AccountSessionORM) -> AccountSession:
        access_token = self.make_token(_id=session.id, account=session.account)
        session_data = {
            "access_token": access_token,
            "ttl": session.ttl,
            "account": session.account,
        }
        account_session = AccountSession.model_validate(session_data)

        return account_session
