from flask import Blueprint

from app.core.model_download import create_download_task
from app.utils.request_validator import validate_json
from app.utils.response import success, error


model_dp = Blueprint("model", __name__)


@model_dp.route("/download_tasks", methods=["POST"])
@validate_json(required_fields=["model_id", "target_folder"])
def modeldp_create_download_task(req_json):
    """
    Create a HuggingFace model download task.

    Example:
    - model_id: "Qwen/Qwen3.5-8b"
    - target_folder: "qwen_models"
    """
    model_id = str(req_json["model_id"]).strip()
    target_folder = str(req_json["target_folder"]).strip()

    try:
        task = create_download_task(model_id=model_id, target_folder=target_folder)
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Create download task failed: {exc}", code=500)

    return success(message="Download task created", data=task)
