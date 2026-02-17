

# src/llm_clients/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional


class LLMMessage(Dict[str, str]):
    """Standard OpenAI-compatible message format."""
    role: str
    content: str


class LLMResponse:
    """Unified response object returned by all LLM clients."""
    def __init__(
        self,
        content: str,
        usage: Optional[Dict[str, int]] = None,
        raw_response: Any = None,
    ):
        self.content = content.strip()
        self.usage = usage or {}
        self.raw_response = raw_response


class LLMClient(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """
        Core method: send messages and get response.
        - Non-streaming: returns LLMResponse
        - Streaming: returns AsyncGenerator yielding text chunks
        """
        pass

    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Convenience wrapper for streaming mode.
        Most clients should override only if they need custom chunk handling.
        """
        result = await self.chat_completion(
            messages=messages,
            model=model,
            stream=True,
            **kwargs
        )
        if not isinstance(result, AsyncGenerator):
            raise RuntimeError("Streaming requested but non-streaming response received")
        async for chunk in result:
            yield chunk