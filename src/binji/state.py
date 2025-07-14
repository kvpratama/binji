from typing import List, Dict
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


# Define the state type with annotations
class GraphState(MessagesState):
    image_path: str
    max_size: int
    question: str
    tavily_research: str
    google_research: str
    disposal_guide: str
    final_answer: str


class GraphStateInput(MessagesState):
    image_path: str
    max_size: int


class GraphStateOutput(MessagesState):
    final_answer: str
