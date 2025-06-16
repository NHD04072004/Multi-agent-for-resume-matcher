from typing import Any, Dict
from abc import ABC, abstractmethod


class Provider(ABC):
    """
    Abstract base class for providers.
    """

    @abstractmethod
    async def __call__(self, prompt: str, **generation_args: Any) -> str: ...


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...


class Strategy(ABC):
    @abstractmethod
    async def __call__(
            self, prompt: str, provider: Provider, **generation_args: Any
    ) -> Dict[str, Any]:
        """
        Abstract method which should be used to define the strategy for generating a response from LLM.

        Args:
            prompt (str): The input prompt for the provider.
            provider (Provider): The provider instance to use for generation.
            **generation_args (Any): Additional arguments for generation.

        Returns:
            Dict[str, Any]: The generated response and any additional information.
        """
        ...
