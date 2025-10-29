# app/utils/scoring.py - Utility functions for recommendation scoring

from typing import List, Dict, Tuple
from app.core.config import get_settings

settings = get_settings()


def calculate_jaccard_similarity(set_a: List[str], set_b: List[str]) -> float:
    """
    Calculate Jaccard similarity between two sets of skills.

    Jaccard similarity = |intersection| / |union|

    Args:
        set_a: First set of skills
        set_b: Second set of skills

    Returns:
        Float between 0 and 1 representing similarity
    """
    if not set_a or not set_b:
        return 0.0

    # Convert to sets and normalize (lowercase)
    set_a_normalized = {skill.lower().strip() for skill in set_a}
    set_b_normalized = {skill.lower().strip() for skill in set_b}

    intersection = len(set_a_normalized & set_b_normalized)
    union = len(set_a_normalized | set_b_normalized)

    if union == 0:
        return 0.0

    return intersection / union


def get_matched_skills(set_a: List[str], set_b: List[str]) -> List[str]:
    """
    Get the list of matched skills between two sets.

    Args:
        set_a: First set of skills
        set_b: Second set of skills

    Returns:
        List of matched skills
    """
    set_a_normalized = {skill.lower().strip(): skill for skill in set_a}
    set_b_normalized = {skill.lower().strip() for skill in set_b}

    matched = []
    for skill_lower in set_b_normalized:
        if skill_lower in set_a_normalized:
            matched.append(set_a_normalized[skill_lower])

    return matched


def calculate_confidence_level(score: float) -> str:
    """
    Determine confidence level based on score.

    Args:
        score: Recommendation score between 0 and 1

    Returns:
        String: "high", "medium", or "low"
    """
    if score >= settings.HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    elif score >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    else:
        return "low"


def adjust_freelancer_weights(
    has_past_projects: bool,
    feedback_count: int
) -> Dict[str, float]:
    """
    Dynamically adjust weights for freelancer recommendation based on data availability.

    According to PRD:
    - If no past projects: increase bio_similarity and skill_overlap
    - If low feedback: reduce metric weights, increase semantic weights

    Args:
        has_past_projects: Whether freelancer has past projects
        feedback_count: Number of feedback received

    Returns:
        Dictionary of adjusted weights
    """
    weights = {
        "bio_similarity": settings.FREELANCER_BIO_SIMILARITY_WEIGHT,
        "past_project_similarity": settings.FREELANCER_PAST_PROJECT_SIMILARITY_WEIGHT,
        "skill_overlap": settings.FREELANCER_SKILL_OVERLAP_WEIGHT,
        "success_rate": settings.FREELANCER_SUCCESS_RATE_WEIGHT,
        "client_satisfaction": settings.FREELANCER_CLIENT_SATISFACTION_WEIGHT,
        "communication_score": settings.FREELANCER_COMMUNICATION_SCORE_WEIGHT,
    }

    if not settings.WEIGHT_ADJUSTMENTS_ENABLED:
        return weights

    # Adjust for no past projects
    if not has_past_projects:
        weights["bio_similarity"] = 0.30  # +10%
        weights["past_project_similarity"] = 0.0  # -20%
        weights["skill_overlap"] = 0.30  # +10%

    # Adjust for low feedback
    if feedback_count < settings.LOW_FEEDBACK_THRESHOLD:
        # Reduce metric weights
        weights["success_rate"] = 0.05  # -10%
        weights["client_satisfaction"] = 0.05  # -10%
        weights["communication_score"] = 0.05  # -5%

        # Redistribute to semantic weights
        if has_past_projects:
            weights["bio_similarity"] += 0.10
            weights["skill_overlap"] += 0.10
            weights["past_project_similarity"] += 0.05
        else:
            # If no past projects, distribute to bio and skill only
            weights["bio_similarity"] += 0.125
            weights["skill_overlap"] += 0.125

    return weights


def calculate_data_quality_score(
    bio_length: int,
    skills_count: int,
    has_past_projects: bool,
    total_projects: int,
    feedback_count: int
) -> float:
    """
    Calculate data quality score for a freelancer profile.

    Args:
        bio_length: Length of bio text
        skills_count: Number of skills
        has_past_projects: Whether has past project descriptions
        total_projects: Number of completed projects
        feedback_count: Number of feedback received

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0

    # Bio quality (30%)
    if bio_length >= 200:
        score += 0.30
    elif bio_length >= settings.MIN_BIO_LENGTH:
        score += 0.15

    # Skills completeness (20%)
    if skills_count >= 5:
        score += 0.20
    elif skills_count >= settings.MIN_SKILLS_COUNT:
        score += 0.10

    # Past projects (25%)
    if has_past_projects and total_projects >= 3:
        score += 0.25
    elif has_past_projects and total_projects >= 1:
        score += 0.15
    elif has_past_projects:
        score += 0.10

    # Feedback (25%)
    if feedback_count >= 10:
        score += 0.25
    elif feedback_count >= 5:
        score += 0.15
    elif feedback_count >= 1:
        score += 0.10

    return min(1.0, score)


def calculate_project_data_quality_score(
    title_length: int,
    description_length: int,
    skills_count: int
) -> float:
    """
    Calculate data quality score for a project.

    Args:
        title_length: Length of project title
        description_length: Length of project description
        skills_count: Number of required skills

    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0

    # Title quality (20%)
    if title_length >= 30:
        score += 0.20
    elif title_length >= 10:
        score += 0.10

    # Description quality (60%)
    if description_length >= 300:
        score += 0.60
    elif description_length >= settings.MIN_PROJECT_DESCRIPTION_LENGTH:
        score += 0.30

    # Skills completeness (20%)
    if skills_count >= 3:
        score += 0.20
    elif skills_count >= settings.MIN_PROJECT_SKILLS_COUNT:
        score += 0.10

    return min(1.0, score)


def is_generic_project_description(description: str) -> bool:
    """
    Detect if a project description is generic/template-based.

    Args:
        description: Project description text

    Returns:
        Boolean indicating if description is generic
    """
    # Simple heuristic: check length and common generic phrases
    generic_phrases = [
        "need a developer",
        "looking for someone",
        "hire a freelancer",
        "simple project",
        "easy task",
        "quick job"
    ]

    description_lower = description.lower()

    # Check if description is too short
    if len(description) < 50:
        return True

    # Check if contains generic phrases
    generic_count = sum(1 for phrase in generic_phrases if phrase in description_lower)
    if generic_count >= 2:
        return True

    return False


def calculate_budget_fit(
    freelancer_hourly_rate: float,
    project_budget: float,
    estimated_hours: int = 40
) -> str:
    """
    Calculate how well the project budget fits the freelancer's rate.

    Args:
        freelancer_hourly_rate: Freelancer's hourly rate
        project_budget: Total project budget
        estimated_hours: Estimated project hours (default 40)

    Returns:
        String: "excellent", "good", or "fair"
    """
    estimated_freelancer_cost = freelancer_hourly_rate * estimated_hours

    if project_budget >= estimated_freelancer_cost * 1.5:
        return "excellent"
    elif project_budget >= estimated_freelancer_cost:
        return "good"
    else:
        return "fair"


def generate_freelancer_recommendation_reason(
    bio_similarity: float,
    past_project_similarity: float,
    skill_overlap: float,
    matched_skills: List[str],
    total_projects: int,
    client_satisfaction: float,
    communication_score: float,
    is_new_freelancer: bool
) -> str:
    """
    Generate a human-readable reason for freelancer recommendation.

    Args:
        Various scoring components and metadata

    Returns:
        String explaining why this freelancer was recommended
    """
    reasons = []

    # Skills match
    if skill_overlap >= 0.8:
        reasons.append(f"Excellent skill match with {len(matched_skills)} matching skills")
    elif skill_overlap >= 0.6:
        reasons.append(f"Strong skill alignment ({', '.join(matched_skills[:3])})")

    # Experience
    if past_project_similarity >= 0.7 and total_projects >= 5:
        reasons.append(f"{total_projects} similar past projects")
    elif past_project_similarity >= 0.6:
        reasons.append("Relevant past experience")

    # Bio match
    if bio_similarity >= 0.8:
        reasons.append("Profile expertise closely matches project needs")

    # Reputation
    if client_satisfaction >= 0.9:
        reasons.append(f"Outstanding client satisfaction ({client_satisfaction:.1%})")
    elif client_satisfaction >= 0.8:
        reasons.append(f"High client satisfaction ({client_satisfaction:.1%})")

    if communication_score >= 0.9:
        reasons.append("Excellent communication")

    # New talent
    if is_new_freelancer:
        reasons.append("Rising talent with strong potential")

    if reasons:
        return ". ".join(reasons) + "."
    else:
        return "Profile matches project requirements."


def generate_project_recommendation_reason(
    project_similarity: float,
    skill_overlap: float,
    matched_skills: List[str],
    budget_fit: str
) -> str:
    """
    Generate a human-readable reason for project recommendation.

    Args:
        Various scoring components and metadata

    Returns:
        String explaining why this project was recommended
    """
    reasons = []

    # Past work alignment
    if project_similarity >= 0.85:
        reasons.append("Excellent match - your past work aligns perfectly with requirements")
    elif project_similarity >= 0.7:
        reasons.append("Strong alignment with your experience")

    # Skills
    if skill_overlap >= 0.9:
        reasons.append(f"All required skills matched ({', '.join(matched_skills)})")
    elif skill_overlap >= 0.7:
        reasons.append(f"Most required skills matched")

    # Budget
    if budget_fit == "excellent":
        reasons.append("Budget well above your rate")
    elif budget_fit == "good":
        reasons.append("Budget fits your rate")

    if reasons:
        return ". ".join(reasons) + "."
    else:
        return "Project matches your expertise."
