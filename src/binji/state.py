from typing import List, Dict
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


# Define the state type with annotations
class GraphState(MessagesState):
    image_path: str
    description: str
    max_size: int
    final_result: str


class GraphStateInput(MessagesState):
    image_path: str
    max_size: int


class GraphStateOutput(MessagesState):
    final_result: str
