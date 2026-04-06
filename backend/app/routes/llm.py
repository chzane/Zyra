import re

from flask import Blueprint

from app.utils.request_validator import validate_json
from app.utils.response import success, error
from config.config_manager import get_config, save_config
from config.items.llm_config import APIModelInfo, APIProviderInfo


llm_dp = Blueprint("llm", __name__)

_PROVIDER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_TRANSPORT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$")
_MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")


def _validate_provider_id(value: str, field_name: str = "pid") -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    if not _PROVIDER_ID_PATTERN.fullmatch(text):
        raise ValueError(f"{field_name} contains invalid characters")
    return text


def _validate_transport(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("transport cannot be empty")
    if not _TRANSPORT_PATTERN.fullmatch(text):
        raise ValueError("transport contains invalid characters")
    return text


def _validate_model_name(value: str, field_name: str = "model_name") -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    if len(text) > 128:
        raise ValueError(f"{field_name} is too long")
    if any(ord(ch) < 32 for ch in text):
        raise ValueError(f"{field_name} contains control characters")
    return text


def _validate_model_id(value: str, field_name: str = "model_id") -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    if len(text) > 128:
        raise ValueError(f"{field_name} is too long")
    if any(ord(ch) < 32 for ch in text):
        raise ValueError(f"{field_name} contains control characters")
    if not _MODEL_ID_PATTERN.fullmatch(text):
        raise ValueError(f"{field_name} contains invalid characters")
    return text


def _validate_model_payload(payload: dict, field_name: str = "model") -> APIModelInfo:
    if not isinstance(payload, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    model_name = _validate_model_name(str(payload.get("model_name", "")), field_name=f"{field_name}.model_name")
    model_id = _validate_model_id(str(payload.get("model_id", "")), field_name=f"{field_name}.model_id")
    api_key = payload.get("api_key")
    if api_key is not None:
        api_key = str(api_key).strip()
        if not api_key:
            api_key = None
    return APIModelInfo(model_name=model_name, model_id=model_id, api_key=api_key)


@llm_dp.route("/providers", methods=["GET"])
def llmdp_list_providers():
    """
    List all configured business providers.
    """
    config = get_config()
    return success(data=[provider.to_dict() for provider in config.llm.providers])


@llm_dp.route("/providers", methods=["POST"])
@validate_json(required_fields=["provider"])
def llmdp_add_provider(req_json):
    """
    Add one business provider using APIProviderInfo schema.
    """
    config = get_config()

    provider_payload = req_json["provider"]
    if not isinstance(provider_payload, dict):
        return error(message="provider must be a JSON object", code=400)

    try:
        provider = APIProviderInfo.model_validate(provider_payload)
        provider.pid = _validate_provider_id(str(provider.pid or ""))
        if provider.name is not None:
            provider.name = provider.name.strip()
        provider.transport = _validate_transport(provider.transport)
        provider.models = [
            _validate_model_payload(model.model_dump(mode="python"), field_name="provider.models")
            for model in provider.models
        ]

        config.llm.add_provider(provider)
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Add provider failed: {exc}", code=500)

    return success(message="Provider created", data=provider.to_dict())


@llm_dp.route("/providers/<pid>", methods=["GET"])
def llmdp_get_provider(pid: str):
    """
    Get one business provider by pid.
    """
    config = get_config()

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        provider = config.llm.require_provider(pid=target_pid)
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Get provider failed: {exc}", code=500)

    return success(data=provider.to_dict())


@llm_dp.route("/providers/<pid>", methods=["PATCH"])
@validate_json(required_fields=["provider"])
def llmdp_update_provider(pid: str, req_json):
    """
    Update one business provider by pid.
    """
    config = get_config()

    provider_payload = req_json["provider"]
    if not isinstance(provider_payload, dict):
        return error(message="provider must be a JSON object", code=400)

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        patch_data = provider_payload.copy()

        if "pid" in patch_data:
            patch_data["pid"] = _validate_provider_id(str(patch_data["pid"]), field_name="provider.pid")
        if "transport" in patch_data:
            patch_data["transport"] = _validate_transport(str(patch_data["transport"]))
        if "models" in patch_data:
            if not isinstance(patch_data["models"], list):
                raise ValueError("provider.models must be a list")
            patch_data["models"] = [
                _validate_model_payload(model, field_name="provider.models").model_dump(mode="python")
                for model in patch_data["models"]
            ]
        if "name" in patch_data and patch_data["name"] is not None:
            patch_data["name"] = str(patch_data["name"]).strip()

        updated = config.llm.update_provider(pid=target_pid, provider_data=patch_data)
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Update provider failed: {exc}", code=500)

    return success(message="Provider updated", data=updated.to_dict())


@llm_dp.route("/providers/<pid>", methods=["DELETE"])
def llmdp_remove_provider(pid: str):
    """
    Remove one business provider by pid.
    """
    config = get_config()

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        removed = config.llm.remove_provider(target_pid)
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Delete provider failed: {exc}", code=500)

    return success(message="Provider deleted", data=removed.to_dict())


@llm_dp.route("/providers/<pid>/models", methods=["POST"])
@validate_json(required_fields=["model"])
def llmdp_add_model(pid: str, req_json):
    """
    Add one model to a business provider.
    """
    config = get_config()

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        model = _validate_model_payload(req_json["model"])
        provider = config.llm.add_model_to_provider(pid=target_pid, model=model)
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Add model failed: {exc}", code=500)

    return success(message="Model added", data=provider.to_dict())


@llm_dp.route("/providers/<pid>/models", methods=["PATCH"])
@validate_json(required_fields=["old_model_id", "model"])
def llmdp_update_model(pid: str, req_json):
    """
    Rename one model in a business provider.
    """
    config = get_config()

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        old_model_id = _validate_model_id(str(req_json["old_model_id"]), field_name="old_model_id")
        new_model = _validate_model_payload(req_json["model"])
        provider = config.llm.update_provider_model(
            pid=target_pid,
            old_model_id=old_model_id,
            new_model=new_model
        )
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Update model failed: {exc}", code=500)

    return success(message="Model updated", data=provider.to_dict())


@llm_dp.route("/providers/<pid>/models", methods=["DELETE"])
@validate_json(required_fields=["model_id"])
def llmdp_remove_model(pid: str, req_json):
    """
    Remove one model from a business provider.
    """
    config = get_config()

    try:
        target_pid = _validate_provider_id(pid, field_name="pid")
        model_id = _validate_model_id(str(req_json["model_id"]))
        provider = config.llm.remove_model_from_provider(pid=target_pid, model_id=model_id)
        save_config()
    except ValueError as exc:
        return error(message=str(exc), code=400)
    except Exception as exc:
        return error(message=f"Delete model failed: {exc}", code=500)

    return success(message="Model deleted", data=provider.to_dict())
