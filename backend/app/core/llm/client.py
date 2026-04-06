from .providers.openai_provider import OpenAIClient
from .base_client import LLMClient


def get_llm_client(transport: str, api_key: str, api_baseurl: str) -> LLMClient:
    transport_name = (transport or "").strip().lower()
    if transport_name == "openai":
        return OpenAIClient(api_key, api_baseurl)
    raise ValueError(f"Unsupported LLM transport: {transport}")
