# app/core/llm_client.py - Implements a get_llm() function for different LLM providers and embedding models.

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.llms import Bedrock
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.language_models.llms import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from langchain_core.embeddings import Embeddings # Import Embeddings base class
from typing import Any, List, Optional

from app.core.config import get_settings

class MockLLM(BaseLLM):
    """A mock LLM for testing and development."""

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        # Simply echoes the prompt for now
        generations = [[BaseMessage(content=f"Mock response for: {p}")] for p in prompts]
        return LLMResult(generations=generations)

    async def _agenerate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        return self._generate(prompts, stop, **kwargs)

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        return f"Mock response for: {prompt}"

class MockEmbeddings(Embeddings):
    """A mock Embeddings model for testing and development."""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Return dummy embeddings of size 1536
        return [[float(i % 1536) for i in range(1536)] for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        # Return a dummy embedding of size 1536
        return [float(i % 1536) for i in range(1536)]

async def get_llm() -> BaseLLM:
    settings = get_settings()
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set for OpenAI provider.")
        return ChatOpenAI(model="gpt-4o-mini", openai_api_key=settings.OPENAI_API_KEY, temperature=0.7)
    elif settings.LLM_PROVIDER == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set for Gemini provider.")
        return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=settings.GOOGLE_API_KEY)
    elif settings.LLM_PROVIDER == "bedrock":
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials not set for Bedrock provider.")
        return Bedrock(
            credentials_profile_name="default", # Assumes AWS CLI config or env vars
            region_name=settings.AWS_REGION,
            model_id="anthropic.claude-v2"
        )
    elif settings.LLM_PROVIDER == "mock":
        return MockLLM()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {settings.LLM_PROVIDER}")

async def get_embedding_model() -> Embeddings:
    settings = get_settings()
    if settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set for OpenAI provider.")
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            dimensions=settings.EMBEDDING_DIMENSIONS
        )
    elif settings.LLM_PROVIDER == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set for Gemini provider.")
        return GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )
    elif settings.LLM_PROVIDER == "bedrock":
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials not set for Bedrock provider.")
        return BedrockEmbeddings(
            credentials_profile_name="default",
            region_name=settings.AWS_REGION,
            model_id="amazon.titan-embed-text-v1"
        )
    elif settings.LLM_PROVIDER == "mock":
        return MockEmbeddings()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER for embeddings: {settings.LLM_PROVIDER}")

async def get_embedding(text: str) -> List[float]:
    embedding_model = await get_embedding_model()
    return embedding_model.embed_query(text)

async def generate_text(prompt: str) -> str:
    llm = await get_llm()
    if isinstance(llm, MockLLM):
        return llm._call(prompt)
    else:
        # For actual LLMs, use invoke or a chain
        # For simplicity, directly calling invoke for now
        response = llm.invoke(prompt)
        # Handle both string responses and AIMessage objects
        if isinstance(response, str):
            return response
        elif hasattr(response, 'content'):
            # AIMessage or similar object
            return response.content
        else:
            # Fallback to string conversion
            return str(response)
