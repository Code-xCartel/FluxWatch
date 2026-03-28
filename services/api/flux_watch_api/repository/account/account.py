from fastapi import Depends

from flux_watch_api.core.base_repository import Repository


class AccountRepository:
    def __init__(self, repo: Repository = Depends()):
        self.repo = repo

    def get_self(self):
        return self.repo.session_account
