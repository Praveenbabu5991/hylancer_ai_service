# app/utils/prompts.py - Defines prompt templates for AI agents.

from typing import List

def recommend_hylancer_prompt(query: str, top_k: int) -> str:
    return f"""You are an AI assistant that recommends freelancers based on a user query.
Given the following query, recommend {top_k} freelancers. Focus on skills, experience, and relevance.
Query: {query}

Provide the recommendations as a comma-separated list of freelancer names or IDs.
"""

def recommend_project_prompt(query: str, top_k: int) -> str:
    return f"""You are an AI assistant that recommends projects based on a user query.
Given the following query, recommend {top_k} projects. Focus on project type, required skills, and budget.
Query: {query}

Provide the recommendations as a comma-separated list of project titles or IDs.
"""

def generate_project_description_prompt(project_title: str, keywords: List[str], length: str) -> str:
    keywords_str = ", ".join(keywords)
    return f"""You are an AI assistant that generates project descriptions.
Generate a {length} project description for a project titled "{project_title}".
Include the following keywords: {keywords_str}.

The description should be engaging and clearly outline the project's goals and scope.
"""

def generate_bio_prompt(freelancer_skills: List[str], experience_level: str, tone: str) -> str:
    skills_str = ", ".join(freelancer_skills)
    return f"""You are an AI assistant that generates professional freelancer bios.
Generate a {tone} bio for a freelancer with an {experience_level} experience level.
Highlight the following skills: {skills_str}.

The bio should be concise, impactful, and suitable for a professional profile.
"""
