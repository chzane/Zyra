from openai import OpenAI
from ..base_client import LLMClient
from ..schema import ChatCompletionRequest


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, api_baseurl: str):
        super().__init__(api_key, api_baseurl)
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=api_baseurl,
        )

    def chat(self, request: ChatCompletionRequest):
        """
        Chat with OpenAI model
        
        :param request: ChatCompletionRequest
        :return: Response from the model
        :return: str
        """
                
        resp = self.client.chat.completions.create(
            model=request.model_name,
            messages=self.convert_messages_to_dicts(request.messages),
            temperature=request.temperature,
            stream=request.stream,
        )
        return resp
