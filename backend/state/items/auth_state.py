from config.base_config import ZyraBaseState


class AuthState(ZyraBaseState):
    auth_token: str = ""
