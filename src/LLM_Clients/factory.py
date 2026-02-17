
# src/llm_clients/factory.py
from typing import Literal

from src.core.config import get_settings

from .base import LLMClient
from .cohere import CohereClient
from .groq import GroqClient  # ← new import (remove xai if not needed)

ProviderType = Literal["cohere", "groq"]  # ← change to groq

def get_llm_client(provider: ProviderType = "groq") -> LLMClient:  # default to groq now
    settings = get_settings()

    if provider == "cohere":
        if not settings.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY missing")
        return CohereClient(api_key=settings.COHERE_API_KEY)

    elif provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing")
        return GroqClient(api_key=settings.GROQ_API_KEY)

    raise ValueError(f"Unsupported LLM provider: {provider}")