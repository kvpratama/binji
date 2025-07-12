from langgraph.graph import START, StateGraph, END
from binji.state import GraphState, GraphStateInput, GraphStateOutput
from binji.nodes import preprocess_image, describe_image
from binji.configuration import Configuration

# Build the graph
builder = StateGraph(
    GraphState,
    input=GraphStateInput,
    output=GraphStateOutput,
    config_schema=Configuration,
)

builder.add_node("preprocess_image", preprocess_image)
builder.add_node("describe_image", describe_image)

builder.add_edge(START, "preprocess_image")
builder.add_edge("preprocess_image", "describe_image")
builder.add_edge("describe_image", END)

graph = builder.compile()
