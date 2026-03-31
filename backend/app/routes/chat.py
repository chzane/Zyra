from flask import Blueprint, jsonify, request
from app.utils.response import success, error
from app.core.llm.client import get_llm_client, LLMClient
from app.core.llm.schema import ChatCompletionRequest

chat_dp = Blueprint("chat", __name__)

llm: LLMClient = get_llm_client("openai", "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", "https://openrouter.ai/api/v1")

@chat_dp.route("/chat", methods=["POST"])
def chatdp_chat():
    """
    Chat with LLM model
    
    :return: JSON response
    :return_code: 200
    :return_msg: "OK"
    :return_data: Response from the model
    """
   
    req_json = request.json
    if not req_json:
        return error(message="Request body is empty")
    
    resp = llm.chat(ChatCompletionRequest(**req_json))
    content = resp.choices[0].message.content
    
    return success(data=content)
