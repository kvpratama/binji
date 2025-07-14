"""Define the configurable parameters for the agent."""

from typing import Annotated, Literal
from pydantic import BaseModel, Field
import os


class Configuration(BaseModel):
    """The configuration for the agent."""

    thread_id: str = Field(
        ...,  # Use ellipsis (...) to mark the field as required
        description="The thread ID to use for the agent's interactions.",
    )

    disposal_country: Annotated[
        Literal[
            "South Korea",
            "United States",
            "Canada",
            "China",
            "Taiwan",
            "United Kingdom",
            "Japan",
            "Indonesia",
            "Singapore",
        ],
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="South Korea",
        description="A string representing the country in which the waste disposal is taking place. This value determines which waste sorting rules, categories, and disposal guidelines should be applied.",
    )

    visual_model: Annotated[
        Literal[
            "gemma-3-12b-it",
            "gemma-3-27b-it",
            "gemini-2.5-flash-lite-preview-06-17",
        ],
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="gemma-3-27b-it",
        description="The name of the visual model to use for the agent's image processing. "
        "Should be in the form: provider/model-name.",
    )

    llm_model_general: Annotated[
        Literal[
            "gemma-3-12b-it",
            "gemma-3-27b-it",
            "gemini-2.5-flash-lite-preview-06-17",
            "gemini-2.5-flash",
        ],
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="gemini-2.5-flash-lite-preview-06-17",
        description="The name of the language model to use for general purposes."
        "Should be in the form: provider/model-name.",
    )

    llm_model_specialized: Annotated[
        Literal[
            "gemma-3-12b-it",
            "gemma-3-27b-it",
            "gemini-2.5-flash-lite-preview-06-17",
            "gemini-2.5-flash",
        ],
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="gemini-2.5-flash",
        description="The name of the language model to use for specialized purposes. "
        "Should be in the form: provider/model-name.",
    )
