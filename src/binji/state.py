from operator import add
from typing import List, Annotated
from langgraph.graph import MessagesState


class GraphState(MessagesState):
    image_path: str
    max_size: int
    question: str
    research: Annotated[List[str], add]
    final_answer: str


class GraphStateInput(MessagesState):
    image_path: str
    max_size: int


class GraphStateOutput(MessagesState):
    final_answer: str
