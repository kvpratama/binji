from langgraph.graph import START, StateGraph, END
from binji.state import GraphState, GraphStateInput, GraphStateOutput
from binji.nodes import preprocess_image, describe_image, generate_question, tavily_research_assistant
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
builder.add_node("generate_question", generate_question)
builder.add_node("tavily_research_assistant", tavily_research_assistant)

builder.add_edge(START, "preprocess_image")
builder.add_edge("preprocess_image", "describe_image")
builder.add_edge("describe_image", "generate_question")
builder.add_edge("generate_question", "tavily_research_assistant")
builder.add_edge("tavily_research_assistant", END)

graph = builder.compile()
