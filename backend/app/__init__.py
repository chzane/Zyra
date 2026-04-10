from flask import Flask, request
from werkzeug.exceptions import BadRequest
from .core.auth import get_token
from .utils.response import success, error


def create_app():
    app = Flask(__name__)

    from .routes.system import system_dp
    from .routes.chat import chat_dp
    from .routes.llm import llm_dp

    app.register_blueprint(system_dp, url_prefix="/system")
    app.register_blueprint(chat_dp, url_prefix="/chat")
    app.register_blueprint(llm_dp, url_prefix="/llm")

    # register_error_handlers(app)
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

def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def bad_request(_):
        return error(code=400, message="Invalid JSON body. Please check JSON syntax."), 400
    
    @app.errorhandler(404)
    def not_found(e):
        """
        Handle 404 error.
        """
        print(f"[ERROR 404] {e}")
        
        return error(code=404, message="Not Found"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """
        Handle 500 error.
        """
        print(f"[ERROR 500] {e}")
        
        return error(code=500, message="Internal Server Error"), 500
    
    @app.errorhandler(Exception)
    def default_error_handler(e):
        """
        Handle default error.
        """
        print(f"[ERROR DEFAULT] {e}")
        
        return error(code=500, message="An unexpected error occurred"), 500
