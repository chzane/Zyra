from openai import OpenAI, AuthenticationError, APIError
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
        :return: dict
        :return_code: 200
        :return_msg: "OK"
        """
                
        try:
            resp = self.client.chat.completions.create(
                model=request.model_name,
                messages=self._convert_messages_to_dicts(request.messages),
                temperature=request.temperature,
                stream=request.stream,
            )
            return resp, True, "OK"

        except AuthenticationError:
            return None, False, "OpenAI API authentication error"

        except APIError as e:
            return None, False, f"OpenAI API error: {e}"

        except Exception as e:
            return None, False, f"Unexpected error: {e}"
