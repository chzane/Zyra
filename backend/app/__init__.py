from flask import Flask


def create_app():
    app = Flask(__name__)

    from .routes.system import system_dp

    app.register_blueprint(system_dp, url_prefix="/system")

    return app
