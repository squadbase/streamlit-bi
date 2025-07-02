from typing import Annotated

from langchain_core.messages import AIMessage, MessageLikeRepresentation
from langgraph.graph.message import Messages, add_messages

from .utils import ExtendedBaseModel


# State
class DataAgentState(ExtendedBaseModel):
    messages: Annotated[Messages, add_messages]

    def get_last_message(self) -> MessageLikeRepresentation:
        if isinstance(self.messages, list):
            if len(self.messages) == 0:
                raise ValueError("No messages found in state: {self}")
            return self.messages[-1]
        else:
            return self.messages

    def get_last_ai_message(self) -> AIMessage:
        last_message = self.get_last_message()
        if isinstance(last_message, AIMessage):
            return last_message

        raise ValueError(f"Expected AIMessage, but got {type(last_message)}")
