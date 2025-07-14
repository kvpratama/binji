from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)


@tool
def search_tavily(query: str):
    """
    Research tool to search the web for information and format the results.

    Args:
        query (str): The search query.

    Returns:
        str: The formatted search documents.
    """
    logger.info("Entered search_tavily function.")
    try:
        # time.sleep(15) # to prevent rate limit

        # Search
        tavily_search = TavilySearch(max_results=3)
        search_docs = tavily_search.invoke(query)
        logger.info(f"Retrieved {len(search_docs)} documents from Tavily.")

        # Format
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
                for doc in search_docs["results"]
            ]
        )
        logger.info("Formatted search documents.")
        return formatted_search_docs
    except Exception as e:
        logger.error(f"Exception in search_tavily: {e}")
        raise


def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text


@tool
def search_google(query: str):
    """
    Research tool to search the web for information using Google Search.

    Args:
        query (str): The search query.

    Returns:
        str: The formatted search documents.
    """
    logger.info("Entered search_google function.")
    try:
        # Configure the client
        client = genai.Client()

        # Define the grounding tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Configure generation settings
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        # Make the request
        response = client.models.generate_content(
               model="gemini-2.5-flash-lite-preview-06-17",
            contents=query,
            config=config,
        )
        return add_citations(response)
    except Exception as e:
        logger.error(f"Exception in search_google: {e}")
        return ""
