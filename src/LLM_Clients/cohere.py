
# src/llm_clients/cohere.py
from typing import List, Any, AsyncGenerator, Optional

from litellm import acompletion

from .base import LLMClient, LLMMessage, LLMResponse


class CohereClient(LLMClient):
    def __init__(self, api_key: str | None = None):
        if not api_key:
            raise ValueError("Cohere API key is required")
        self.api_key = api_key

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        if stream:
            # LiteLLM supports streaming – we can yield chunks
            async def stream_generator():
                async for chunk in await acompletion(
                    model=f"cohere/{model}",
                    messages=messages,
                    api_key=self.api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs,
                ):
                    # LiteLLM chunk format: usually delta.content
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta

            return stream_generator()

        # Non-streaming path
        response = await acompletion(
            model=f"cohere/{model}",
            messages=messages,
            api_key=self.api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs,
        )

        # LiteLLM normalizes Cohere → content is str or list of blocks
        content = response.choices[0].message.content
        if isinstance(content, list):
            content = "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )

        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                "total_tokens": getattr(response.usage, "total_tokens", 0),
            }

        return LLMResponse(
            content=content,
            usage=usage,
            raw_response=response,
        )