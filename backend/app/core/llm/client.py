from .providers.openai_provider import OpenAIClient
from .base_client import LLMClient


def get_llm_client(provider_name: str, api_key: str, api_baseurl: str) -> LLMClient:
    if provider_name == "openai":
        return OpenAIClient(api_key, api_baseurl)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
