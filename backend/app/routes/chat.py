import json
from flask import Blueprint, Response, stream_with_context
from app.utils.response import success, error
from app.utils.request_validator import validate_json
from app.core.llm.client import get_llm_client, LLMClient
from app.core.llm.schema import ChatCompletionRequest
from config.config_manager import get_config
from config.items.llm_config import APIModelInfo, APIProviderInfo
from .utils.chat_utiles import _default_choice_message, _merge_stream_value, _normalize_choice_message, _api_data_from_response


chat_dp = Blueprint("chat", __name__)
config = get_config()


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
