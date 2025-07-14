# from langgraph.constants import Send
import os
import logging
import time
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from binji.state import GraphState
from PIL import Image
from binji.llm import get_llm
from binji.configuration import Configuration
from binji.tools import search_tavily
import base64
from langgraph.config import get_stream_writer
from typing import Dict, List, Literal
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
from pydantic import BaseModel, Field
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


def preprocess_image(state: GraphState, config: Configuration):
    logger.info(f"Resizing image: {state.get('image_path', '<missing>')}")
    stream_writer = get_stream_writer()

    try:
        stream_writer({"custom_key": "Processing the image..."})
        if "image_path" not in state:
            raise KeyError("'image_path' key not found in state.")
        if "max_size" not in state:
            raise KeyError("'max_size' key not found in state.")

        image = Image.open(state["image_path"])
        original_width, original_height = image.size
        if original_width == 0 or original_height == 0:
            raise ValueError("Image has zero width or height.")

        # Determine scale factor
        if original_width > original_height:
            scale = state["max_size"] / float(original_width)
        else:
            scale = state["max_size"] / float(original_height)

        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_image.save(state["image_path"])

        logger.info(f"Resized image: {state['image_path']}")
        return {"image_path": state["image_path"]}
    except Exception as e:
        logger.error(f"Exception in preprocess_image: {e}", exc_info=True)
        if stream_writer:
            stream_writer(
                {
                    "custom_key": f"Unknown error during image processing. Please try again."
                }
            )
        return {"image_path": None, "error": str(e)}


def process_image_with_llm(
    *,
    state: GraphState,
    log_message: str,
    stream_message: str,
    prompt: str,
    model_name: str,
    postprocess_fn=None,
):
    logger.info(f"{log_message}: {state.get('image_path', '<missing>')}")
    stream_writer = get_stream_writer()
    try:
        stream_writer({"custom_key": stream_message})
        if "image_path" not in state:
            raise KeyError("'image_path' key not found in state.")
        llm = get_llm(model_name=model_name)

        with open(state["image_path"], "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        human_message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{encoded_image}",
                },
            ]
        )

        response = llm.invoke([human_message])
        parsed = response.content
        if postprocess_fn:
            return postprocess_fn(parsed, stream_writer)
        return parsed
    except Exception as e:
        logger.error(f"Exception in process_image_with_llm: {e}", exc_info=True)
        if stream_writer:
            stream_writer(
                {
                    "custom_key": f"Unknown error during image processing. Please try again."
                }
            )
        return {"error": str(e)}


def image_question(state: GraphState, config: Configuration):
    def postprocess(parsed, stream_writer):
        try:
            logger.info(f"Question: {parsed}")
            stream_writer({"custom_key": f"Image processed successfully..."})
            return {"question": parsed}
        except Exception as e:
            logger.error(f"Exception in describe_image postprocess: {e}", exc_info=True)
            if stream_writer:
                stream_writer({"custom_key": f"Error: {str(e)}"})
            return {"question": "", "error": str(e)}

    try:
        prompt = os.path.join("prompts", "imageq_prompt.txt")
        with open(prompt, "r") as f:
            prompt = f.read()
        prompt = prompt.format(
            disposal_country=config["configurable"]["disposal_country"]
        )
        return process_image_with_llm(
            state=state,
            log_message="Describe image",
            stream_message="Analyzing image...",
            prompt=prompt,
            model_name=config["configurable"]["visual_model"],
            postprocess_fn=postprocess,
        )
    except Exception as e:
        logger.error(f"Exception in describe_image: {e}", exc_info=True)
        stream_writer = get_stream_writer()
        if stream_writer:
            stream_writer(
                {
                    "custom_key": f"Unknown error during image analysis. Please try again."
                }
            )
        return {"question": "", "error": str(e)}


def tavily_research_assistant(state: GraphState, config: Configuration):
    try:
        logger.info("Tavily research assistant")
        stream_writer = get_stream_writer()
        stream_writer({"custom_key": "Researching disposal information..."})

        system_prompt = os.path.join("prompts", "research_prompt.txt")
        with open(system_prompt, "r") as f:
            system_prompt = f.read()
        system_message = SystemMessage(
            content=system_prompt.format(
                disposal_country=config["configurable"]["disposal_country"]
            )
        )
        human_message = HumanMessage(content=state["question"])

        llm = get_llm(model_name=config["configurable"]["llm_model_specialized"])
        agent_executor = create_react_agent(
            llm, [search_tavily], prompt=system_message, name="tavily_research_agent"
        )
        agent_response = agent_executor.invoke({"messages": [human_message]})
        tavily_research = agent_response["messages"][-1].content

        logger.info(f"Tavily research: {tavily_research}")
        return {"tavily_research": tavily_research}
    except Exception as e:
        logger.error(f"Exception in tavily_research_assistant: {e}", exc_info=True)
        stream_writer = get_stream_writer()
        if stream_writer:
            stream_writer(
                {"custom_key": f"Unknown error during researching. Please try again."}
            )
        return {"tavily_research": "", "error": str(e)}


def generate_answer(state: GraphState, config: Configuration):
    try:
        logger.info("Generate answer")
        stream_writer = get_stream_writer()
        stream_writer({"custom_key": "Generating answer..."})

        system_prompt = os.path.join("prompts", "answer_prompt.txt")
        with open(system_prompt, "r") as f:
            system_prompt = f.read()
        system_message = SystemMessage(content=system_prompt)

        context_message = AIMessage(
            content=state["tavily_research"], name="tavily_research"
        )
        human_message = HumanMessage(content=state["question"])

        llm = get_llm(model_name=config["configurable"]["llm_model_general"])
        response = llm.invoke([system_message, context_message, human_message])
        answer = response.content

        logger.info(f"Answer: {answer}")
        return {"final_answer": answer}
    except Exception as e:
        logger.error(f"Exception in generate_answer: {e}", exc_info=True)
        stream_writer = get_stream_writer()
        if stream_writer:
            stream_writer(
                {
                    "custom_key": f"Unknown error during answer generation. Please try again."
                }
            )
        return {"final_answer": "", "error": str(e)}
