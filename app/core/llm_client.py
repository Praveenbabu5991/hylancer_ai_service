# app/core/llm_client.py - Implements a get_llm() function for different LLM providers.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Bedrock
from langchain_core.language_models.llms import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
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

async def get_llm() -> BaseLLM:
    settings = get_settings()
    if settings.LLM_PROVIDER == "gemini":
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

async def generate_text(prompt: str) -> str:
    llm = await get_llm()
    if isinstance(llm, MockLLM):
        return llm._call(prompt)
    else:
        # For actual LLMs, use invoke or a chain
        # For simplicity, directly calling invoke for now
        return llm.invoke(prompt)
