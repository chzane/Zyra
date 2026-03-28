from flask import Flask, request
from .core.auth import get_token
from .utils.response import success, error


def create_app():
    app = Flask(__name__)

    from .routes.system import system_dp

    app.register_blueprint(system_dp, url_prefix="/system")

    register_auth(app)

    return app


def register_auth(app):

    @app.before_request
    def check_token():
        """
        Check token in request headers
        """
        token = request.headers.get("X-Token")
        if not token or token != get_token():
            return error(code=401, message="Unauthorized"), 401
