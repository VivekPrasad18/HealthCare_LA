"""
Thin LLM wrapper. Returns a LangChain BaseChatModel based on the configured provider.
Calling code uses: llm.invoke([HumanMessage(content="...")]) or llm.predict(prompt).
"""

from __future__ import annotations
from functools import lru_cache
from typing import Any

from langchain_core.language_models import BaseChatModel

from app.utils.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info(f"Using Google Gemini: {model}")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
            convert_system_message_to_human=True,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        logger.info(f"Using OpenAI: {model}")
        return ChatOpenAI(
            model=model,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        logger.info(f"Using Anthropic: {model}")
        return ChatAnthropic(
            model=model,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.2,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def extract_text(response: Any) -> str:
    """
    Safely extract plain text from an LLM response.
    Handles both simple string content and structured list content
    (e.g. newer Gemini models that return [{'type':'text','text':'...'}]).
    """
    content = response.content if hasattr(response, "content") else response

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()

    return str(content).strip()
