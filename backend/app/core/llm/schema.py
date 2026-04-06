from typing import List
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # system / user / assistant
    content: str

class ChatCompletionRequest(BaseModel):
    model_name: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    stream: bool = False