from abc import ABC, abstractmethod
from typing import List, Dict
from .schema import ChatCompletionRequest, ChatMessage


class LLMClient(ABC):
    def __init__(self, api_key: str, api_baseurl: str | None = None) -> None:
        self.api_key = api_key
        self.api_baseurl = api_baseurl

        super().__init__()
    
    @abstractmethod
    def chat(self, request: ChatCompletionRequest):
        """
        Chat with LLM model
        
        :param messages: List of messages to send to the model
        :param model_name: Name of the model to use
        :param temperature: Temperature for the model
        :param stream: Whether to stream the response
        :return: Response from the model
        :return: str
        """
        
        pass
    
    def _convert_messages_to_dicts(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        Convert List[ChatMessage] to List[Dict[str, str]]
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]
