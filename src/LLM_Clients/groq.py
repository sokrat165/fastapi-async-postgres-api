# src/llm_clients/groq.py
from typing import List, Any, AsyncGenerator, Optional

from litellm import acompletion
from src.core.config import settings
from .base import LLMClient, LLMMessage, LLMResponse

class GroqClient(LLMClient):
    def __init__(self, api_key: str=settings.GROQ_API_KEY , base_url:str=settings.GROQ_API_BASE_URL ):
        if not api_key:
            raise ValueError("Groq API key is required")
        self.api_key = api_key
        self.base_url = base_url

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        # LiteLLM uses "groq/" prefix for routing
        litellm_model = f"groq/{model}"

        if stream:
            async def stream_generator():
                async for chunk in await acompletion(
                    model=litellm_model,
                    messages=messages,
                    api_key=self.api_key,
                    api_base=self.base_url,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs,
                ):
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta.content or ""
                        if delta:
                            yield delta

            return stream_generator()

        response = await acompletion(
            model=litellm_model,
            messages=messages,
            api_key=self.api_key,
            api_base=self.base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs,
        )

        content = ""
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content

        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0,
            }

        return LLMResponse(
            content=content.strip(),
            usage=usage,
            raw_response=response,
        )