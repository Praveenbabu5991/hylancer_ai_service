# app/agents/recommendation_agent.py - Agent for recommending freelancers and projects.

from typing import List, Dict, Any
from app.core.llm_client import generate_text
from app.core.vector_client import get_or_create_collection
from app.utils.prompts import recommend_hylancer_prompt, recommend_project_prompt
from app.core.config import get_settings

async def recommend_hylancer_agent(query: str, top_k: int) -> Dict[str, Any]:
    settings = get_settings()
    if settings.LLM_PROVIDER == "mock":
        # Mocked response for development
        return {"recommendations": [f"Mock Hylancer 1 for '{query}'", f"Mock Hylancer 2 for '{query}'"]}

    # In a real scenario, you would use the vector store to find relevant freelancers
    # For now, we'll just use the LLM to generate a list based on the prompt
    # This part needs actual vector search implementation
    # freelancer_collection = get_or_create_collection("freelancers")
    # search_results = freelancer_collection.query(query_texts=[query], n_results=top_k)

    prompt = recommend_hylancer_prompt(query, top_k)
    response_text = await generate_text(prompt)
    # Assuming the LLM returns a comma-separated list
    recommendations = [r.strip() for r in response_text.split(',') if r.strip()]
    return {"recommendations": recommendations}

async def recommend_project_agent(query: str, top_k: int) -> Dict[str, Any]:
    settings = get_settings()
    if settings.LLM_PROVIDER == "mock":
        # Mocked response for development
        return {"recommendations": [f"Mock Project A for '{query}'", f"Mock Project B for '{query}'"]}

    # Similar to hylancer recommendation, this would involve vector search
    # project_collection = get_or_create_collection("projects")
    # search_results = project_collection.query(query_texts=[query], n_results=top_k)

    prompt = recommend_project_prompt(query, top_k)
    response_text = await generate_text(prompt)
    # Assuming the LLM returns a comma-separated list
    recommendations = [r.strip() for r in response_text.split(',') if r.strip()]
    return {"recommendations": recommendations}
