import json
from pathlib import Path
from flask import Blueprint, Response, stream_with_context
from app.utils.response import success, error
from app.utils.request_validator import validate_json
from app.core.llm.client import get_llm_client, LLMClient
from app.core.llm.schema import ChatCompletionRequest
from app.core.llm.task_router_client import TaskRouterClient
from config.config_manager import get_config
from config.items.llm_config import APIModelInfo, APIProviderInfo
from state.state_manager import get_state
from .utils.chat_utiles import _default_choice_message, _merge_stream_value, _normalize_choice_message, _api_data_from_response


chat_dp = Blueprint("chat", __name__)
config = get_config()
state = get_state()

task_router_client: TaskRouterClient = None
task_router_init_error = None
task_router_init_error_info = None


def _build_local_model_error_info(exc: Exception, phase: str, language: str | None = None):
    model_dir = config.local_model.model_dir
    model_dir_path = Path(model_dir).expanduser().resolve() if model_dir else None

    error_type = "local_model_error"
    if model_dir is None:
        error_type = "model_dir_not_configured"
    elif not model_dir_path.exists():
        error_type = "model_dir_not_found"
    elif isinstance(exc, FileNotFoundError):
        error_type = "model_not_found"
    elif isinstance(exc, ValueError):
        error_type = "invalid_input"
    elif phase == "load":
        error_type = "model_load_error"
    elif phase == "predict":
        error_type = "model_runtime_error"

    return {
        "type": error_type,
        "phase": phase,
        "language": language,
        "model_dir": str(model_dir_path) if model_dir_path else None,
        "detail": str(exc)
    }

try:
    preload_languages = [state.system.userlanguage] if state.system.userlanguage else None
    task_router_client = TaskRouterClient(
        model_dir=config.local_model.model_dir,
        preload_languages=preload_languages
    )
except Exception as e:
    task_router_init_error = str(e)

    task_router_init_error_info = _build_local_model_error_info(
        e,
        phase="load",
        language=state.system.userlanguage
    )


@chat_dp.route("/completions", methods=["POST"])
@validate_json(required_fields=["model_name", "messages"])
def chatdp_completions(req_json):
    """
    Get completions for a message with LLM model
    
    :return: JSON response
    :return_code: 200
    :return_msg: "OK"
    :return_data: Response from the model
    """
   
    chat_completion_request = {
        "model_name": req_json["model_name"],
        "messages": req_json["messages"],
        "temperature": req_json.get("temperature", 0.7),
        "stream": req_json.get("stream", False)
    }
    
    resolved: tuple[APIProviderInfo, APIModelInfo] | None = config.llm.resolve_provider_model(
        chat_completion_request["model_name"]
    )
    if resolved is None:
        return error(message="Provider not found", code=400)
    model_provider, resolved_model = resolved
    effective_api_key = resolved_model.api_key or model_provider.api_key
    if not effective_api_key:
        return error(message=f"Provider api_key is empty: {model_provider.pid}", code=400)
    chat_completion_request["model_name"] = resolved_model.model_id
    
    try:
        chat_client: LLMClient = get_llm_client(model_provider.transport, effective_api_key, model_provider.api_base)
    except ValueError as e:
        return error(message=str(e), code=400)
    except Exception as e:
        return error(message=f"Create chat client failed: {e}", code=400)

    if chat_client is None:
        return error(message="Create chat client failed", code=400)
    
    resp, is_success, msg = chat_client.chat(ChatCompletionRequest(**chat_completion_request))
    
    if chat_completion_request["stream"]:
        if not is_success:
            return error(message=msg, code=400)

        def event_stream():
            choices_state = {}
            for chunk in resp:
                if chunk.choices:
                    for choice in chunk.choices:
                        idx = choice.index
                        if idx not in choices_state:
                            choices_state[idx] = _default_choice_message()
                        delta = choice.delta
                        if delta:
                            delta_dict = delta.model_dump() if hasattr(delta, "model_dump") else {}
                            choices_state[idx] = _merge_stream_value(choices_state[idx], delta_dict)

                ordered_choices = [_normalize_choice_message(choices_state[index]) for index in sorted(choices_state.keys())]
                payload = {
                    "code": 200,
                    "msg": "success",
                    "data": _api_data_from_response(chunk, ordered_choices),
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    if is_success:
        api_response = _api_data_from_response(
            resp,
            [choice.message.model_dump() for choice in resp.choices] if resp.choices else []
        )
        return success(data=api_response)
    else:
        return error(message=msg, code=400)
        
@chat_dp.route("/task_route", methods=["POST"])
@validate_json(required_fields=["input"])
def chatdp_route(req_json):
    """
    Route a message to a specific model
    
    :return: JSON response
    :return_code: 200
    :return_msg: "OK"
    :return_data: Response from the model
    """
    
    if not config.local_model.enabled:
        return error(
            message="Task router is disabled by config.local_model.enabled",
            code=400,
            data={"type": "local_model_disabled"}
        )

    if task_router_init_error:
        return error(
            message=f"Task router unavailable: {task_router_init_error}",
            code=400,
            data=task_router_init_error_info
        )

    text = str(req_json["input"]).strip()
    if not text:
        return error(message="input cannot be empty", code=400)

    language = state.system.userlanguage
    try:
        result = task_router_client.route(text=text, language=language)
    except FileNotFoundError as e:
        return error(
            message=f"Task route model not found: {e}",
            code=400,
            data=_build_local_model_error_info(e, phase="load", language=language)
        )
    except ValueError as e:
        return error(
            message=f"Task route invalid input: {e}",
            code=400,
            data=_build_local_model_error_info(e, phase="predict", language=language)
        )
    except Exception as e:
        return error(
            message=f"Task route prediction failed: {e}",
            code=400,
            data=_build_local_model_error_info(e, phase="predict", language=language)
        )

    return success(data=result)
