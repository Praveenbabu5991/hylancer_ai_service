# app/agents/generation_agent.py - Agent for generating project descriptions and bios.

from typing import List, Dict, Any
from app.core.llm_client import generate_text
from app.utils.prompts import generate_project_description_prompt, generate_bio_prompt
from app.core.config import get_settings

async def generate_project_description_agent(project_title: str, keywords: List[str], length: str) -> Dict[str, Any]:
    settings = get_settings()
    if settings.LLM_PROVIDER == "mock":
        # Mocked response for development
        return {"description": f"Mock {length} description for project '{project_title}' with keywords {', '.join(keywords)}."}

    prompt = generate_project_description_prompt(project_title, keywords, length)
    description = await generate_text(prompt)
    return {"description": description}

async def generate_bio_agent(freelancer_skills: List[str], experience_level: str, tone: str) -> Dict[str, Any]:
    settings = get_settings()
    if settings.LLM_PROVIDER == "mock":
        # Mocked response for development
        return {"bio": f"Mock {tone} bio for an {experience_level} freelancer with skills {', '.join(freelancer_skills)}."}

    prompt = generate_bio_prompt(freelancer_skills, experience_level, tone)
    bio = await generate_text(prompt)
    return {"bio": bio}
