"""
Ollama provider: talks to the local Ollama server via its HTTP API.
Ollama runs on the user's machine at http://localhost:11434 by default.
"""

import httpx
from app.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self._model = model
        self._base_url = base_url

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        raw_output = data["message"]["content"]
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)

        return raw_output, input_tokens, output_tokens
