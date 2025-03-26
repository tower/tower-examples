from ollama import chat
from ollama import ChatResponse
from typing import Any


from core.actions import Action

class InferWithOllamaChat(Action):

    def __init__(
            self,
            actionname: str = None,
            *args,
            **kwargs):
        super().__init__(actionname)
        # consider setting up a Client attribute https://github.com/ollama/ollama-python

    def do(self, model, messages, *args:Any, **kwargs: Any):

        response: ChatResponse = chat(model=model, messages=messages)
 
        ret = response.message.content

        return ret

