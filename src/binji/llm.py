from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(model_name: str):
    """Initializes and returns a ChatGoogleGenerativeAI instance."""
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        max_tokens=None,
        timeout=60,
        max_retries=2,
    )
