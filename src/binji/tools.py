from langchain_tavily import TavilySearch
from langchain_core.tools import tool
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
