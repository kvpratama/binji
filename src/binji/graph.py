from langgraph.graph import START, StateGraph, END
from binji.state import GraphState, GraphStateInput, GraphStateOutput
from binji.nodes import (
    preprocess_image,
    image_question,
    tavily_research_assistant,
    generate_answer,
    disposal_guide,
)
from binji.configuration import Configuration

# Build the graph
builder = StateGraph(
    GraphState,
    input=GraphStateInput,
    output=GraphStateOutput,
    config_schema=Configuration,
)

builder.add_node("preprocess_image", preprocess_image)
builder.add_node("image_question", image_question)
builder.add_node("tavily_research_assistant", tavily_research_assistant)
builder.add_node("generate_answer", generate_answer)
builder.add_node("disposal_guide", disposal_guide)

builder.add_edge(START, "preprocess_image")
builder.add_edge("preprocess_image", "image_question")
builder.add_edge("image_question", "tavily_research_assistant")
builder.add_edge("image_question", "disposal_guide")
builder.add_edge("tavily_research_assistant", "generate_answer")
builder.add_edge("disposal_guide", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile()
