# app/services/generation_service.py
from loguru import logger
from typing import Dict, List, Optional

from app.schemas.generation import (
    GenerateProjectDescriptionRequest,
    GenerateProjectDescriptionResponse,
    GenerateBioDescriptionRequest,
    GenerateBioDescriptionResponse,
    GenerateBioFromResumeRequest,
    GenerateBioFromResumeResponse,
    ParsedResumeData,
    KnowYourWorthRequest,
    KnowYourWorthResponse,
    WorthBreakdown,
    MarketInsights,
    GenerateProjectFromTextRequest,
    GenerateProjectFromTextResponse,
)
from app.core.llm_client import generate_text
from app.clients.project_service_client import ProjectServiceClient
from app.core.config import get_settings


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

    async def generate_bio_from_resume(
        self,
        request: GenerateBioFromResumeRequest
    ) -> GenerateBioFromResumeResponse:
        """
        Generate a professional bio by parsing a resume and using extracted data.

        This method:
        1. Parses the resume text to extract structured data
        2. Uses the extracted data to generate a professional bio

        Args:
            request: Contains the resume text

        Returns:
            GenerateBioFromResumeResponse with bio, headline, rate, level, and parsed data
        """
        logger.info("Starting bio generation from resume")

        try:
            # Step 1: Parse the resume to extract structured data
            logger.info("Parsing resume to extract structured data")
            parsed_data = await self._parse_resume(request.resume_text)

            # Step 2: Create a bio generation request from parsed data
            bio_request = GenerateBioDescriptionRequest(
                name=parsed_data.name,
                title=parsed_data.title,
                skills=parsed_data.skills,
                years_of_experience=parsed_data.years_of_experience,
                top_achievements=parsed_data.top_achievements,
                personality_traits=parsed_data.personality_traits or []
            )

            # Step 3: Generate bio using the existing method
            logger.info("Generating bio from parsed data")
            bio_response = await self.generate_bio_description(bio_request)

            # Step 4: Combine results
            result = GenerateBioFromResumeResponse(
                bio=bio_response.bio,
                headline=bio_response.headline,
                suggested_hourly_rate=bio_response.suggested_hourly_rate,
                experience_level=bio_response.experience_level,
                parsed_data=parsed_data
            )

            logger.info("Successfully generated bio from resume")
            return result

        except Exception as e:
            logger.exception(f"Error generating bio from resume: {e}")
            raise

    async def _parse_resume(self, resume_text: str) -> ParsedResumeData:
        """
        Parse a resume text to extract structured data using LLM.

        Args:
            resume_text: The raw resume text

        Returns:
            ParsedResumeData with extracted information
        """
        logger.info("Parsing resume with LLM")

        prompt = f"""You are an expert resume parser. Extract structured information from the following resume.

Resume Text:
{resume_text}

Please extract and provide the following information in a structured format:
1. Full name of the person
2. Current or most recent professional title/role
3. Technical skills (list 5-15 skills)
4. Total years of professional experience (estimate if not explicitly stated)
5. Top 3-5 achievements or accomplishments
6. Personality traits or soft skills (3-5 traits like "team-player", "problem-solver", etc.)

Format your response EXACTLY as follows:
NAME: [full name]
TITLE: [professional title]
SKILLS: [skill1, skill2, skill3, ...]
YEARS: [number only]
ACHIEVEMENTS:
- [achievement 1]
- [achievement 2]
- [achievement 3]
TRAITS: [trait1, trait2, trait3, ...]

IMPORTANT:
- For YEARS, provide only a number (e.g., 5, not "5 years")
- List skills separated by commas
- List achievements one per line with a dash
- List traits separated by commas"""

        try:
            response_text = await generate_text(prompt)
            parsed_data = self._parse_resume_response(response_text)
            logger.info(f"Successfully parsed resume for: {parsed_data.name}")
            return parsed_data

        except Exception as e:
            logger.exception(f"Error parsing resume: {e}")
            raise ValueError(f"Failed to parse resume: {str(e)}")

    def _parse_resume_response(self, response_text: str) -> ParsedResumeData:
        """
        Parse the LLM response for resume extraction.

        Args:
            response_text: The LLM's response

        Returns:
            ParsedResumeData object
        """
        lines = response_text.strip().split("\n")

        name = "Unknown"
        title = "Professional"
        skills = []
        years = 3
        achievements = []
        traits = []

        current_field = None

        for line in lines:
            line = line.strip()

            if line.startswith("NAME:"):
                name = line.replace("NAME:", "").strip()
                current_field = "name"
            elif line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_field = "title"
            elif line.startswith("SKILLS:"):
                skills_str = line.replace("SKILLS:", "").strip()
                skills = [s.strip() for s in skills_str.split(",") if s.strip()]
                current_field = "skills"
            elif line.startswith("YEARS:"):
                try:
                    years_str = line.replace("YEARS:", "").strip()
                    # Extract just the number
                    years = int(''.join(filter(str.isdigit, years_str)) or "3")
                    years = max(0, min(50, years))  # Clamp between 0-50
                except:
                    years = 3
                current_field = "years"
            elif line.startswith("ACHIEVEMENTS:"):
                current_field = "achievements"
            elif line.startswith("TRAITS:"):
                traits_str = line.replace("TRAITS:", "").strip()
                traits = [t.strip() for t in traits_str.split(",") if t.strip()]
                current_field = "traits"
            elif current_field == "achievements" and line.startswith("-"):
                achievement = line.lstrip("- ").strip()
                if achievement:
                    achievements.append(achievement)

        # Validate and set defaults
        if not name or name == "Unknown":
            name = "Professional"
        if not title:
            title = "Experienced Professional"
        if not skills:
            skills = ["Communication", "Problem Solving", "Teamwork"]
        if not achievements:
            achievements = ["Successfully delivered projects on time", "Collaborated with cross-functional teams"]
        if not traits:
            traits = ["professional", "dedicated", "team-player"]

        return ParsedResumeData(
            name=name,
            title=title,
            skills=skills[:15],  # Limit to 15 skills
            years_of_experience=years,
            top_achievements=achievements[:5],  # Limit to 5 achievements
            personality_traits=traits[:5]  # Limit to 5 traits
        )

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

    async def calculate_freelancer_worth(
        self,
        request: KnowYourWorthRequest
    ) -> KnowYourWorthResponse:
        """
        Calculate freelancer worth in Indian market context.

        This method:
        1. Calculates base rate based on experience and specialization
        2. Applies multipliers for skills, location, education, certifications, portfolio
        3. Provides market insights using AI
        4. Gives personalized recommendations

        Args:
            request: KnowYourWorthRequest with freelancer details

        Returns:
            KnowYourWorthResponse with worth calculation and insights
        """
        logger.info(f"Calculating worth for: {request.name or 'a freelancer'}")

        # Step 1: Calculate base rate (INR per hour)
        base_rate = self._calculate_base_rate(
            request.years_of_experience,
            request.specialization
        )

        # Step 2: Calculate multipliers
        experience_multiplier = self._calculate_experience_multiplier(request.years_of_experience)
        skill_premium = self._calculate_skill_premium(request.skills)
        location_adjustment = self._calculate_location_adjustment(request.city)
        education_bonus = self._calculate_education_bonus(request.education_level)
        certification_bonus = self._calculate_certification_bonus(request.certifications)
        portfolio_bonus = self._calculate_portfolio_bonus(request.portfolio_projects)
        reputation_bonus = self._calculate_reputation_bonus(request.client_reviews_average)

        # Step 3: Calculate final hourly rate
        hourly_rate_inr = (
            base_rate *
            (1 + experience_multiplier) *
            (1 + skill_premium) *
            (1 + location_adjustment) +
            education_bonus +
            certification_bonus +
            portfolio_bonus +
            reputation_bonus
        )

        # Round to nearest 50
        hourly_rate_inr = round(hourly_rate_inr / 50) * 50

        # Convert to USD (approximate rate: 1 USD = 83 INR)
        hourly_rate_usd = round(hourly_rate_inr / 83, 2)

        # Calculate earning potential
        monthly_potential = hourly_rate_inr * 160  # 160 hours/month
        annual_potential = monthly_potential * 12

        # Step 4: Create worth breakdown
        worth_breakdown = WorthBreakdown(
            base_rate=base_rate,
            experience_multiplier=experience_multiplier,
            skill_premium=skill_premium,
            location_adjustment=location_adjustment,
            education_bonus=education_bonus,
            certification_bonus=certification_bonus,
            portfolio_bonus=portfolio_bonus,
            reputation_bonus=reputation_bonus
        )

        # Step 5: Generate market insights using LLM
        market_insights = await self._generate_market_insights(request, hourly_rate_inr)

        # Step 6: Generate comparison message
        comparison_message = self._generate_comparison_message(
            request.years_of_experience,
            hourly_rate_inr,
            request.city
        )

        # Step 7: Generate recommendations
        recommendations = await self._generate_recommendations(request, hourly_rate_inr)

        logger.info(f"Calculated worth for {request.name or 'a freelancer'}: ₹{hourly_rate_inr}/hr")

        return KnowYourWorthResponse(
            estimated_hourly_rate_inr=hourly_rate_inr,
            estimated_hourly_rate_usd=hourly_rate_usd,
            monthly_earning_potential_inr=monthly_potential,
            annual_earning_potential_inr=annual_potential,
            worth_breakdown=worth_breakdown,
            market_insights=market_insights,
            comparison_message=comparison_message,
            recommendations=recommendations
        )

    def _calculate_base_rate(self, years_of_experience: int, specialization: str) -> float:
        """Calculate base hourly rate in INR based on experience and specialization."""
        # Base rates for different specializations in India (INR/hour)
        specialization_rates = {
            "data science": 800,
            "machine learning": 850,
            "ai": 900,
            "blockchain": 950,
            "full-stack": 700,
            "backend": 650,
            "frontend": 600,
            "mobile": 650,
            "devops": 750,
            "cloud": 750,
            "cybersecurity": 850,
            "ui/ux": 550,
            "graphic design": 450,
            "content writing": 350,
            "digital marketing": 500,
            "default": 600
        }

        # Find matching specialization (case-insensitive, partial match)
        spec_lower = specialization.lower()
        base_rate = specialization_rates["default"]

        for key, rate in specialization_rates.items():
            if key in spec_lower or spec_lower in key:
                base_rate = rate
                break

        # Adjust for experience (0-2 years get lower base)
        if years_of_experience < 1:
            base_rate *= 0.5
        elif years_of_experience < 2:
            base_rate *= 0.7

        return base_rate

    def _calculate_experience_multiplier(self, years: int) -> float:
        """Calculate experience multiplier (0.0 to 1.0+)."""
        if years < 1:
            return 0.0
        elif years < 2:
            return 0.1
        elif years < 3:
            return 0.2
        elif years < 5:
            return 0.3
        elif years < 7:
            return 0.45
        elif years < 10:
            return 0.6
        else:
            return 0.8 + min((years - 10) * 0.05, 0.5)

    def _calculate_skill_premium(self, skills: list) -> float:
        """Calculate skill premium based on demand (0.0 to 0.5)."""
        # High-demand skills in Indian market
        premium_skills = {
            "react", "node.js", "python", "aws", "docker", "kubernetes",
            "typescript", "golang", "rust", "machine learning", "ai",
            "tensorflow", "pytorch", "blockchain", "solidity", "flutter",
            "react native", "next.js", "graphql", "mongodb", "postgresql",
            "redis", "kafka", "microservices", "system design"
        }

        skill_count = sum(1 for skill in skills if skill.lower() in premium_skills)
        return min(skill_count * 0.05, 0.5)

    def _calculate_location_adjustment(self, city: str) -> float:
        """Calculate location-based adjustment for Indian cities (-0.2 to 0.3)."""
        city_lower = city.lower()

        # Tier 1 cities (higher rates)
        tier1 = ["bangalore", "bengaluru", "mumbai", "delhi", "ncr", "gurgaon", "noida", "hyderabad", "pune"]
        # Tier 2 cities (moderate rates)
        tier2 = ["chennai", "kolkata", "ahmedabad", "jaipur", "chandigarh", "kochi", "indore"]

        if any(t1 in city_lower for t1 in tier1):
            return 0.2
        elif any(t2 in city_lower for t2 in tier2):
            return 0.05
        else:
            return -0.1  # Tier 3 cities

    def _calculate_education_bonus(self, education: str) -> float:
        """Calculate education bonus in INR/hour."""
        education_lower = education.lower()

        if "phd" in education_lower or "doctorate" in education_lower:
            return 150
        elif "master" in education_lower or "msc" in education_lower or "mtech" in education_lower:
            return 100
        elif "bachelor" in education_lower or "btech" in education_lower or "bsc" in education_lower:
            return 50
        else:
            return 0

    def _calculate_certification_bonus(self, certifications: list) -> float:
        """Calculate certification bonus in INR/hour."""
        if not certifications:
            return 0

        # Bonus per certification, capped at 5
        cert_count = min(len(certifications), 5)
        return cert_count * 50

    def _calculate_portfolio_bonus(self, projects: int) -> float:
        """Calculate portfolio bonus in INR/hour."""
        if projects == 0:
            return 0
        elif projects < 5:
            return 25
        elif projects < 10:
            return 50
        elif projects < 20:
            return 75
        else:
            return 100

    def _calculate_reputation_bonus(self, rating: float) -> float:
        """Calculate reputation bonus based on client reviews in INR/hour."""
        if rating == 0:
            return 0
        elif rating >= 4.8:
            return 100
        elif rating >= 4.5:
            return 75
        elif rating >= 4.0:
            return 50
        elif rating >= 3.5:
            return 25
        else:
            return 0

    async def _generate_market_insights(
        self,
        request: KnowYourWorthRequest,
        hourly_rate: float
    ) -> MarketInsights:
        """Generate market insights using LLM."""
        logger.info("Generating market insights with AI")

        # Determine tier
        if request.years_of_experience < 2:
            tier = "Entry-Level"
        elif request.years_of_experience < 5:
            tier = "Mid-Level"
        elif request.years_of_experience < 10:
            tier = "Senior"
        else:
            tier = "Expert"

        # Build prompt for LLM
        skills_str = ", ".join(request.skills)
        certs_str = ", ".join(request.certifications) if request.certifications else "None"

        prompt = f"""You are an expert freelance market analyst for India. Analyze this freelancer profile and provide insights.

Freelancer Profile:
- Specialization: {request.specialization}
- Years of Experience: {request.years_of_experience}
- Skills: {skills_str}
- City: {request.city}
- Education: {request.education_level}
- Certifications: {certs_str}
- Portfolio Projects: {request.portfolio_projects}
- Client Rating: {request.client_reviews_average}/5.0
- Estimated Hourly Rate: ₹{hourly_rate}

Provide insights in this EXACT format:

POSITION: [market position as percentile, e.g., "Top 30%", "Top 50%", etc.]
DEMAND: [demand level: "Low", "Medium", "High", or "Very High"]
ADVANTAGES:
- [competitive advantage 1]
- [competitive advantage 2]
- [competitive advantage 3]
IMPROVEMENTS:
- [improvement suggestion 1]
- [improvement suggestion 2]
- [improvement suggestion 3]

Keep each point concise (max 15 words). Focus on Indian freelance market context."""

        try:
            response_text = await generate_text(prompt)
            insights_data = self._parse_market_insights_response(response_text)

            return MarketInsights(
                tier=tier,
                market_position=insights_data["position"],
                demand_level=insights_data["demand"],
                competitive_advantage=insights_data["advantages"],
                improvement_suggestions=insights_data["improvements"]
            )

        except Exception as e:
            logger.exception(f"Error generating market insights: {e}")
            # Return fallback insights
            return MarketInsights(
                tier=tier,
                market_position="Top 50%",
                demand_level="Medium",
                competitive_advantage=[
                    f"Strong foundation in {request.specialization}",
                    f"Located in {request.city}",
                    "Good skill diversity"
                ],
                improvement_suggestions=[
                    "Build more portfolio projects",
                    "Obtain industry certifications",
                    "Improve client ratings"
                ]
            )

    def _parse_market_insights_response(self, response_text: str) -> dict:
        """Parse LLM response for market insights."""
        lines = response_text.strip().split("\n")

        position = "Top 50%"
        demand = "Medium"
        advantages = []
        improvements = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("POSITION:"):
                position = line.replace("POSITION:", "").strip()
            elif line.startswith("DEMAND:"):
                demand = line.replace("DEMAND:", "").strip()
            elif line.startswith("ADVANTAGES:"):
                current_section = "advantages"
            elif line.startswith("IMPROVEMENTS:"):
                current_section = "improvements"
            elif line.startswith("-") and current_section:
                item = line.lstrip("- ").strip()
                if item:
                    if current_section == "advantages":
                        advantages.append(item)
                    elif current_section == "improvements":
                        improvements.append(item)

        # Ensure at least some content
        if not advantages:
            advantages = ["Good technical skills", "Relevant experience", "Market presence"]
        if not improvements:
            improvements = ["Expand skill set", "Build portfolio", "Get certifications"]

        return {
            "position": position,
            "demand": demand,
            "advantages": advantages[:5],
            "improvements": improvements[:5]
        }

    def _generate_comparison_message(
        self,
        years_of_experience: int,
        hourly_rate: float,
        city: str
    ) -> str:
        """Generate comparison message for the freelancer."""
        # Average rates by experience in India
        if years_of_experience < 2:
            avg_low = 300
            avg_high = 600
            category = "entry-level"
        elif years_of_experience < 5:
            avg_low = 600
            avg_high = 1000
            category = "mid-level"
        elif years_of_experience < 10:
            avg_low = 1000
            avg_high = 1800
            category = "senior"
        else:
            avg_low = 1500
            avg_high = 2500
            category = "expert"

        avg_rate = (avg_low + avg_high) / 2

        if hourly_rate > avg_high:
            position = "above"
            percentage = round(((hourly_rate - avg_rate) / avg_rate) * 100)
            message = f"Your rate of ₹{hourly_rate:.0f}/hr is {percentage}% above the average for {category} freelancers in {city} (₹{avg_low}-₹{avg_high}/hr)."
        elif hourly_rate < avg_low:
            position = "below"
            percentage = round(((avg_rate - hourly_rate) / avg_rate) * 100)
            message = f"Your rate of ₹{hourly_rate:.0f}/hr is {percentage}% below the average for {category} freelancers in {city} (₹{avg_low}-₹{avg_high}/hr)."
        else:
            message = f"Your rate of ₹{hourly_rate:.0f}/hr is within the average range for {category} freelancers in {city} (₹{avg_low}-₹{avg_high}/hr)."

        return message

    async def _generate_recommendations(
        self,
        request: KnowYourWorthRequest,
        hourly_rate: float
    ) -> list:
        """Generate personalized recommendations using LLM."""
        logger.info("Generating personalized recommendations")

        skills_str = ", ".join(request.skills)
        certs_str = ", ".join(request.certifications) if request.certifications else "None"

        prompt = f"""You are a career advisor for Indian freelancers. Provide actionable recommendations to increase earning potential.

Profile:
- Specialization: {request.specialization}
- Experience: {request.years_of_experience} years
- Skills: {skills_str}
- City: {request.city}
- Certifications: {certs_str}
- Portfolio: {request.portfolio_projects} projects
- Rating: {request.client_reviews_average}/5.0
- Current Rate: ₹{hourly_rate}/hr

Provide 5 specific, actionable recommendations to increase their worth. Format as:

RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]
- [recommendation 3]
- [recommendation 4]
- [recommendation 5]

Each recommendation should be:
1. Specific and actionable
2. Relevant to Indian market
3. Max 20 words
4. Focus on skills, certifications, or market positioning"""

        try:
            response_text = await generate_text(prompt)
            recommendations = self._parse_recommendations_response(response_text)
            return recommendations

        except Exception as e:
            logger.exception(f"Error generating recommendations: {e}")
            # Return fallback recommendations
            return [
                "Build a strong portfolio with 3-5 showcase projects",
                "Obtain relevant certifications (AWS, Google Cloud, or domain-specific)",
                "Improve English communication skills for international clients",
                "Specialize in high-demand technologies (AI, Cloud, Blockchain)",
                "Request client testimonials to boost your reputation"
            ]

    def _parse_recommendations_response(self, response_text: str) -> list:
        """Parse LLM response for recommendations."""
        lines = response_text.strip().split("\n")
        recommendations = []

        for line in lines:
            line = line.strip()
            if line.startswith("-"):
                rec = line.lstrip("- ").strip()
                if rec:
                    recommendations.append(rec)

        # Ensure at least 3 recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                "Expand your skill set with in-demand technologies",
                "Build a professional online presence",
                "Network with other freelancers and clients"
            ])

        return recommendations[:5]

    async def generate_project_from_text(
        self,
        request: GenerateProjectFromTextRequest,
        jwt_token: Optional[str] = None
    ) -> GenerateProjectFromTextResponse:
        """
        Generate complete project description from brief text.

        This method:
        1. Fetches available categories and subcategories from Project Service
        2. Uses AI to map the brief text to best matching category/subcategory
        3. Generates complete project description with title, description, and skills

        Args:
            request: GenerateProjectFromTextRequest with brief description
            jwt_token: Optional JWT token for authenticating with Project Service

        Returns:
            GenerateProjectFromTextResponse with complete project details
        """
        logger.info("Generating project from brief text")

        settings = get_settings()

        # Step 1: Fetch categories from Project Service
        try:
            project_client = ProjectServiceClient(settings.PROJECT_SERVICE_URL, jwt_token=jwt_token)
            categories_dict = await project_client.get_categories_and_subcategories()
            logger.info(f"Fetched {len(categories_dict)} categories from Project Service")
        except Exception as e:
            logger.error(f"Failed to fetch categories from Project Service: {e}")
            # Fallback to default categories if service is unavailable
            categories_dict = {
                "IT And Development": ["Python Developer", "Java Developer", "Web Development"],
                "Design": ["Logo Design", "Web Design", "UI/UX Design"],
                "Writing": ["Content Writing", "Technical Writing", "Copywriting"]
            }
            logger.warning("Using fallback categories")

        # Step 2: Build AI prompt to select category/subcategory and generate project details
        categories_text = "\n".join([
            f"- {category}: {', '.join(subcategories)}"
            for category, subcategories in categories_dict.items()
        ])

        prompt = f"""You are a project classification and description expert for a freelance marketplace.

Given the client's brief description, you need to:
1. Select the MOST APPROPRIATE category and subcategory from the available options
2. Generate a professional project title
3. Write a detailed project description (200-400 words)
4. Suggest relevant skills needed

Client's Brief Description:
"{request.brief_description}"

Available Categories and Subcategories:
{categories_text}

Budget: {"₹" + str(request.budget) if request.budget else "Not specified"}
Budget Type: {request.budget_type}
Deadline: {request.deadline if request.deadline else "Not specified"}

IMPORTANT: You MUST select a category and subcategory from the list above. Use the EXACT names as provided.

Provide your response in this EXACT format:

CATEGORY: [exact category name from the list]
SUBCATEGORY: [exact subcategory name from the list]
TITLE: [professional project title, max 80 characters]
DESCRIPTION: [detailed project description, 200-400 words, include project goals, deliverables, technical requirements, and success criteria]
SKILLS: [skill1, skill2, skill3, skill4, skill5]
DURATION: [estimated duration like "2-3 months", "4-6 weeks"]
COMPLEXITY: [beginner, intermediate, or expert]"""

        try:
            response_text = await generate_text(prompt)
            result = self._parse_project_from_text_response(response_text, categories_dict)
            logger.info(f"Successfully generated project: {result.category} -> {result.sub_category}")
            return result

        except Exception as e:
            logger.exception(f"Error generating project from text: {e}")
            # Return a basic fallback response
            return self._get_fallback_project_from_text_response(request, categories_dict)

    def _parse_project_from_text_response(
        self,
        response_text: str,
        categories_dict: Dict[str, List[str]]
    ) -> GenerateProjectFromTextResponse:
        """Parse LLM response for project generation from text."""
        lines = response_text.strip().split("\n")

        category = ""
        sub_category = ""
        title = ""
        description = ""
        skills = []
        duration = ""
        complexity = ""

        current_field = None
        description_lines = []

        for line in lines:
            line = line.strip()

            if line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
                current_field = "category"
            elif line.startswith("SUBCATEGORY:"):
                sub_category = line.replace("SUBCATEGORY:", "").strip()
                current_field = "subcategory"
            elif line.startswith("TITLE:"):
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

        # Validate category exists
        if category not in categories_dict:
            logger.warning(f"AI selected invalid category: {category}")
            # Try to find closest match or use first category
            category = list(categories_dict.keys())[0]

        # Validate subcategory exists under category
        if sub_category not in categories_dict.get(category, []):
            logger.warning(f"AI selected invalid subcategory: {sub_category} for category: {category}")
            # Use first subcategory of the category
            sub_category = categories_dict[category][0] if categories_dict[category] else "General"

        # Fallback values
        if not title:
            title = "Professional Project Request"
        if not description:
            description = "Looking for a professional to help with this project. Please review the requirements and provide your proposal."
        if not skills:
            skills = ["Communication", "Problem Solving"]

        return GenerateProjectFromTextResponse(
            category=category,
            sub_category=sub_category,
            title=title[:100],
            description=description,
            suggested_skills=skills[:10],
            estimated_duration=duration if duration else None,
            complexity_level=complexity if complexity in ["beginner", "intermediate", "expert"] else None
        )

    def _get_fallback_project_from_text_response(
        self,
        request: GenerateProjectFromTextRequest,
        categories_dict: Dict[str, List[str]]
    ) -> GenerateProjectFromTextResponse:
        """Return a fallback response if AI generation fails."""
        # Use first available category and subcategory
        first_category = list(categories_dict.keys())[0] if categories_dict else "General"
        first_subcategory = categories_dict[first_category][0] if categories_dict.get(first_category) else "General Services"

        return GenerateProjectFromTextResponse(
            category=first_category,
            sub_category=first_subcategory,
            title="Project Request",
            description=request.brief_description,
            suggested_skills=["Communication", "Problem Solving", "Attention to Detail"],
            estimated_duration="1-2 months",
            complexity_level="intermediate"
        )
