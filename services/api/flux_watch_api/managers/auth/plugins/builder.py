from flux_watch_api.core.base_repository import Repository
from flux_watch_api.managers.auth.plugins.resident_plugin import ResidentPlugin
from flux_watch_api.managers.auth.plugins.token_plugin import TokenPlugin
from flux_watch_api.models.auth import Scheme
from flux_watch_api.utils.auth import AuthUtils


def build_plugins(repo: Repository, auth_utils: AuthUtils):
    return {
        Scheme.RESIDENT: ResidentPlugin(repo=repo, auth_utils=auth_utils),
        Scheme.TOKEN: TokenPlugin(repo=repo, auth_utils=auth_utils),
    }
