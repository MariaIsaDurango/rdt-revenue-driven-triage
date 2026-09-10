"""
Common interface all LLM providers must implement.
This abstraction lets the API call any provider the same way,
regardless of whether it's local (Ollama) or external.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class LLMProvider(ABC):
    """Base class every provider (Ollama, external) must inherit from."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int, int]:
        """
        Sends prompts to the LLM and returns the raw response.

        Returns:
            raw_output: the raw text response from the model (expected to contain JSON)
            input_tokens: number of tokens consumed by the prompt
            output_tokens: number of tokens consumed by the response
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the model being used, e.g. 'llama3.2:3b'."""
        raise NotImplementedError
