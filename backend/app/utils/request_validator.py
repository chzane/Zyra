from functools import wraps
from flask import request
from app.utils.response import error


def validate_json(required_fields=None, arg_name="req_json"):
    """
    Validate JSON request body and extract required fields.
    
    :param required_fields: List of required fields in the JSON body
    :param arg_name: Name of the argument to store the JSON data in the view function
    :return: Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            req_json = request.get_json(silent=True)
            if req_json is None:
                raw_body = request.get_data(as_text=True)
                if not raw_body or not raw_body.strip():
                    return error(message="Request body is empty", code=400)
                return error(message="Invalid JSON body. Please check JSON syntax.", code=400)

            if not isinstance(req_json, dict):
                return error(message="Request body must be a JSON object", code=400)

            if required_fields:
                missing_fields = [field for field in required_fields if field not in req_json]
                if missing_fields:
                    return error(message=f"Required parameters are missing: {', '.join(missing_fields)}", code=400)

            kwargs[arg_name] = req_json
            return func(*args, **kwargs)

        return wrapper

    return decorator
