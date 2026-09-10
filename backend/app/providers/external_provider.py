"""
External provider: connects to Groq's API (hosted open-source models).
Groq offers a free tier with fast inference, used as our external comparison point.
"""

import os
from groq import AsyncGroq
from app.providers.base import LLMProvider


class ExternalProvider(LLMProvider):
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self._model = model
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self._client = AsyncGroq(api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_output = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return raw_output, input_tokens, output_tokens
