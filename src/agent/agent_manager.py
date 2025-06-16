import os
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

from .wrapper import MDWrapper, JSONWrapper
from .openai_provider import OpenAIProvider, OpenAIEmbeddingProvider


class AgentManager:
    def __init__(self, strategy: str | None = None, model: str = 'gpt-4.1-nano') -> None:
        match strategy:
            case "md":
                self.strategy = MDWrapper()
            case "json":
                self.strategy = JSONWrapper()
            case _:
                self.strategy = JSONWrapper()
        self.model = model

    async def _get_provider(self, **kwargs: Any) -> OpenAIProvider:
        api_key = kwargs.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
        if api_key:
            return OpenAIProvider(api_key=api_key)
        model = kwargs.get("model", self.model)

        return OpenAIProvider(model=model)

    async def run(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Run the agent with the given prompt and generation arguments.
        """
        provider = await self._get_provider(**kwargs)
        return await self.strategy(prompt, provider, **kwargs)


class EmbeddingManager:
    def __init__(self, model: str = "text-embedding-3-small") -> None:
        self._model = model

    async def _get_embedding_provider(
            self, **kwargs: Any
    ) -> OpenAIEmbeddingProvider:
        api_key = kwargs.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
        if api_key:
            return OpenAIEmbeddingProvider(api_key=api_key)
        model = kwargs.get("embedding_model", self._model)

        return OpenAIEmbeddingProvider(embedding_model=model)

    async def embed(self, text: str, **kwargs: Any) -> list[float]:
        """
        Get the embedding for the given text.
        """
        provider = await self._get_embedding_provider(**kwargs)
        return await provider.embed(text)
