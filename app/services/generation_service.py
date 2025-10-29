# app/services/generation_service.py
from loguru import logger

from app.schemas.generation import (
    GenerateProjectDescriptionRequest,
    GenerateProjectDescriptionResponse,
    GenerateBioDescriptionRequest,
    GenerateBioDescriptionResponse,
)
from app.core.llm_client import generate_text


class GenerationService:
    """Service for AI-powered content generation."""

    async def generate_project_description(
        self,
        request: GenerateProjectDescriptionRequest
    ) -> GenerateProjectDescriptionResponse:
        """
        Generate a professional project description using AI.

        This uses the LLM to create:
        - Compelling project title
        - Detailed description
        - Suggested skills
        - Estimated duration
        - Complexity level
        """
        logger.info(f"Generating project description for category: {request.category}")

        # Build the prompt for the LLM
        prompt = self._build_project_prompt(request)

        # Generate using the LLM
        try:
            response_text = await generate_text(prompt)

            # Parse the response
            result = self._parse_project_response(response_text, request)

            logger.info("Successfully generated project description")
            return result

        except Exception as e:
            logger.exception(f"Error generating project description: {e}")
            # Return a fallback response
            return self._get_fallback_project_response(request)

    async def generate_bio_description(
        self,
        request: GenerateBioDescriptionRequest
    ) -> GenerateBioDescriptionResponse:
        """
        Generate a professional bio description for a hylancer using AI.

        This uses the LLM to create:
        - Professional bio
        - Compelling headline
        - Suggested hourly rate
        - Experience level (1-5)
        """
        logger.info(f"Generating bio description for: {request.name}")

        # Build the prompt for the LLM
        prompt = self._build_bio_prompt(request)

        # Generate using the LLM
        try:
            response_text = await generate_text(prompt)

            # Parse the response
            result = self._parse_bio_response(response_text, request)

            logger.info("Successfully generated bio description")
            return result

        except Exception as e:
            logger.exception(f"Error generating bio description: {e}")
            # Return a fallback response
            return self._get_fallback_bio_response(request)

    def _build_project_prompt(self, request: GenerateProjectDescriptionRequest) -> str:
        """Build prompt for project description generation."""
        skills_str = ", ".join(request.required_skills)
        deadline_str = f" with deadline {request.deadline}" if request.deadline else ""

        prompt = f"""You are a professional project description writer for a freelance marketplace.

Generate a compelling project description with the following details:

Category: {request.category}
Sub-category: {request.sub_category}
Required Skills: {skills_str}
Budget Type: {request.budget_type}
Budget: ${request.budget:,.2f}{deadline_str}

Please provide:
1. A catchy project title (max 80 characters)
2. A detailed project description (200-400 words) that includes:
   - Project overview and goals
   - Key deliverables
   - Technical requirements
   - Success criteria
3. List of suggested skills (5-8 skills)
4. Estimated duration (e.g., "2-3 months", "4-6 weeks")
5. Complexity level: "beginner", "intermediate", or "expert"

Format your response as:
TITLE: [project title]
DESCRIPTION: [detailed description]
SKILLS: [skill1, skill2, skill3, ...]
DURATION: [estimated duration]
COMPLEXITY: [complexity level]"""

        return prompt

    def _build_bio_prompt(self, request: GenerateBioDescriptionRequest) -> str:
        """Build prompt for bio description generation."""
        skills_str = ", ".join(request.skills)
        achievements_str = "\n".join([f"- {a}" for a in request.top_achievements]) if request.top_achievements else "N/A"
        traits_str = ", ".join(request.personality_traits) if request.personality_traits else "N/A"

        prompt = f"""You are a professional profile writer for freelancers.

Generate a compelling professional bio and headline with the following details:

Name: {request.name}
Title: {request.title}
Skills: {skills_str}
Years of Experience: {request.years_of_experience}
Top Achievements:
{achievements_str}
Personality Traits: {traits_str}

Please provide:
1. A professional bio (150-250 words) that:
   - Highlights expertise and experience
   - Showcases achievements
   - Demonstrates value proposition
   - Has a professional yet approachable tone
2. A compelling headline (max 120 characters)
3. Suggested hourly rate (USD, based on skills and experience)
4. Experience level (1=Entry, 2=Junior, 3=Mid-level, 4=Senior, 5=Expert)

Format your response as:
BIO: [professional bio]
HEADLINE: [headline]
RATE: [hourly rate as number]
LEVEL: [experience level as number 1-5]"""

        return prompt

    def _parse_project_response(
        self,
        response_text: str,
        request: GenerateProjectDescriptionRequest
    ) -> GenerateProjectDescriptionResponse:
        """Parse LLM response for project description."""
        lines = response_text.strip().split("\n")

        title = ""
        description = ""
        skills = []
        duration = ""
        complexity = "intermediate"

        current_field = None
        description_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_field = "title"
            elif line.startswith("DESCRIPTION:"):
                description_lines.append(line.replace("DESCRIPTION:", "").strip())
                current_field = "description"
            elif line.startswith("SKILLS:"):
                skills_str = line.replace("SKILLS:", "").strip()
                skills = [s.strip() for s in skills_str.split(",")]
                current_field = "skills"
            elif line.startswith("DURATION:"):
                duration = line.replace("DURATION:", "").strip()
                current_field = "duration"
            elif line.startswith("COMPLEXITY:"):
                complexity = line.replace("COMPLEXITY:", "").strip().lower()
                current_field = "complexity"
            elif current_field == "description" and line:
                description_lines.append(line)

        description = " ".join(description_lines).strip()

        # Fallback values
        if not title:
            title = f"{request.category} {request.sub_category} Project"
        if not description:
            description = f"Looking for an experienced professional to work on a {request.category} project. Required skills: {', '.join(request.required_skills)}."
        if not skills:
            skills = request.required_skills
        if not duration:
            duration = "1-3 months"
        if complexity not in ["beginner", "intermediate", "expert"]:
            complexity = "intermediate"

        return GenerateProjectDescriptionResponse(
            title=title[:100],
            description=description,
            suggested_skills=skills[:10],
            estimated_duration=duration,
            complexity_level=complexity
        )

    def _parse_bio_response(
        self,
        response_text: str,
        request: GenerateBioDescriptionRequest
    ) -> GenerateBioDescriptionResponse:
        """Parse LLM response for bio description."""
        lines = response_text.strip().split("\n")

        bio = ""
        headline = ""
        rate = 50.0
        level = 3

        current_field = None
        bio_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("BIO:"):
                bio_lines.append(line.replace("BIO:", "").strip())
                current_field = "bio"
            elif line.startswith("HEADLINE:"):
                headline = line.replace("HEADLINE:", "").strip()
                current_field = "headline"
            elif line.startswith("RATE:"):
                try:
                    rate_str = line.replace("RATE:", "").strip().replace("$", "").replace(",", "")
                    rate = float(rate_str)
                except:
                    rate = 50.0
                current_field = "rate"
            elif line.startswith("LEVEL:"):
                try:
                    level = int(line.replace("LEVEL:", "").strip())
                    level = max(1, min(5, level))  # Clamp between 1-5
                except:
                    level = 3
                current_field = "level"
            elif current_field == "bio" and line:
                bio_lines.append(line)

        bio = " ".join(bio_lines).strip()

        # Fallback values
        if not bio:
            bio = f"{request.name} is a {request.title} with {request.years_of_experience} years of experience specializing in {', '.join(request.skills[:3])}."
        if not headline:
            headline = f"{request.title} | {' • '.join(request.skills[:3])}"

        return GenerateBioDescriptionResponse(
            bio=bio,
            headline=headline[:120],
            suggested_hourly_rate=rate,
            experience_level=level
        )

    def _get_fallback_project_response(
        self,
        request: GenerateProjectDescriptionRequest
    ) -> GenerateProjectDescriptionResponse:
        """Return a fallback response if generation fails."""
        return GenerateProjectDescriptionResponse(
            title=f"{request.category} {request.sub_category} Project",
            description=f"We are looking for an experienced professional to work on a {request.category} project in the {request.sub_category} domain. "
                       f"The ideal candidate should have expertise in {', '.join(request.required_skills[:3])}. "
                       f"Budget: ${request.budget:,.2f} ({request.budget_type}).",
            suggested_skills=request.required_skills,
            estimated_duration="1-3 months",
            complexity_level="intermediate"
        )

    def _get_fallback_bio_response(
        self,
        request: GenerateBioDescriptionRequest
    ) -> GenerateBioDescriptionResponse:
        """Return a fallback response if generation fails."""
        # Estimate hourly rate based on experience
        base_rate = 30
        rate = base_rate + (request.years_of_experience * 5)

        # Calculate experience level
        if request.years_of_experience < 2:
            level = 1
        elif request.years_of_experience < 4:
            level = 2
        elif request.years_of_experience < 7:
            level = 3
        elif request.years_of_experience < 10:
            level = 4
        else:
            level = 5

        return GenerateBioDescriptionResponse(
            bio=f"{request.name} is a {request.title} with {request.years_of_experience} years of professional experience. "
                f"Specialized in {', '.join(request.skills[:3])}, with a proven track record of delivering high-quality results.",
            headline=f"{request.title} | {' • '.join(request.skills[:3])}",
            suggested_hourly_rate=float(rate),
            experience_level=level
        )
