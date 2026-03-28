_auth_token = None


def set_token(token: str):
    global _auth_token
    _auth_token = token


def get_token():
    return _auth_token
