# app/api/v1/endpoints/generate.py
from fastapi import APIRouter, HTTPException, status, Body, UploadFile, File
from loguru import logger

from app.services.generation_service import GenerationService
from app.schemas.generation import (
    GenerateProjectDescriptionRequest,
    GenerateProjectDescriptionResponse,
    GenerateBioDescriptionRequest,
    GenerateBioDescriptionResponse,
    GenerateBioFromResumeRequest,
    GenerateBioFromResumeResponse,
    KnowYourWorthRequest,
    KnowYourWorthResponse,
    GenerateProjectFromTextRequest,
    GenerateProjectFromTextResponse,
)
from app.utils.file_extractor import extract_text_from_file

router = APIRouter()


# ========== Dependency Injector ==========

async def get_generation_service() -> GenerationService:
    return GenerationService()


# ========== Generation Endpoints ==========

@router.post(
    "/generate_project_description",
    response_model=GenerateProjectDescriptionResponse,
    summary="Generate Project Description",
    description="Generate a professional project description using AI based on category, skills, and budget"
)
async def generate_project_description(
    request: GenerateProjectDescriptionRequest = Body(
        ...,
        example={
            "category": "Web Development",
            "sub_category": "Full-Stack",
            "required_skills": ["React", "Node.js", "PostgreSQL"],
            "budget_type": "Fixed-Price",
            "budget": 5000,
            "deadline": "2025-12-31"
        }
    )
):
    """
    Generate a project description using AI.

    This endpoint creates:
    - A compelling project title
    - Detailed project description
    - Suggested skills list
    - Estimated duration
    - Complexity level

    Example request:
    {
        "category": "Web Development",
        "sub_category": "Full-Stack",
        "required_skills": ["React", "Node.js", "PostgreSQL"],
        "budget_type": "Fixed-Price",
        "budget": 5000,
        "deadline": "2025-12-31"
    }
    """
    try:
        service = await get_generation_service()
        logger.info(f"Generating project description for category: {request.category}")
        response = await service.generate_project_description(request)
        return response
    except Exception as e:
        logger.exception(f"Error generating project description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate project description: {str(e)}"
        )


@router.post(
    "/generate_bio_description",
    response_model=GenerateBioDescriptionResponse,
    summary="Generate Hylancer Bio",
    description="Generate a professional bio description for a hylancer using AI"
)
async def generate_bio_description(
    request: GenerateBioDescriptionRequest = Body(
        ...,
        example={
            "name": "John Smith",
            "title": "Senior Full-Stack Developer",
            "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL"],
            "years_of_experience": 8,
            "top_achievements": [
                "Built a SaaS platform serving 10K users",
                "Led a team of 5 developers"
            ],
            "personality_traits": ["problem-solver", "team-player", "detail-oriented"]
        }
    )
):
    """
    Generate a professional bio for a hylancer using AI.

    This endpoint creates:
    - A professional bio (150-250 words)
    - A compelling headline
    - Suggested hourly rate
    - Experience level (1-5)

    Example request:
    {
        "name": "John Smith",
        "title": "Senior Full-Stack Developer",
        "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL"],
        "years_of_experience": 8,
        "top_achievements": [
            "Built a SaaS platform serving 10K users",
            "Led a team of 5 developers"
        ],
        "personality_traits": ["problem-solver", "team-player", "detail-oriented"]
    }
    """
    try:
        service = await get_generation_service()
        logger.info(f"Generating bio description for: {request.name}")
        response = await service.generate_bio_description(request)
        return response
    except Exception as e:
        logger.exception(f"Error generating bio description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate bio description: {str(e)}"
        )


@router.post(
    "/generate_bio_from_resume",
    response_model=GenerateBioFromResumeResponse,
    summary="Generate Bio from Resume File",
    description="Upload a resume file (PDF, DOCX, TXT) and generate a professional bio using AI"
)
async def generate_bio_from_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT format)")
):
    """
    Parse a resume file and generate a professional bio for a hylancer using AI.

    This endpoint:
    1. Accepts a resume file upload (PDF, DOCX, or TXT)
    2. Extracts text from the file
    3. Parses the resume to extract structured information (name, title, skills, experience, achievements)
    4. Generates a professional bio based on the extracted data
    5. Returns the bio along with the parsed data for transparency

    Creates:
    - A professional bio (150-250 words)
    - A compelling headline
    - Suggested hourly rate
    - Experience level (1-5)
    - Parsed resume data (name, title, skills, years of experience, achievements, traits)

    Supported file formats:
    - PDF (.pdf)
    - Microsoft Word (.docx, .doc)
    - Plain Text (.txt)

    File size limit: 10 MB
    """
    # Validate file size (10 MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

    try:
        # Read file content
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds 10 MB limit. File size: {len(file_content) / (1024 * 1024):.2f} MB"
            )

        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        logger.info(f"Processing resume file: {file.filename} ({len(file_content) / 1024:.2f} KB)")

        # Extract text from file
        try:
            resume_text = await extract_text_from_file(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except ImportError as e:
            logger.error(f"Missing required library: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: missing required file parsing library"
            )

        # Validate extracted text
        if len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extracted text is too short ({len(resume_text)} characters). Please ensure the resume has sufficient content."
            )

        logger.info(f"Extracted {len(resume_text)} characters from resume")

        # Create request object
        request = GenerateBioFromResumeRequest(resume_text=resume_text)

        # Generate bio from resume
        service = await get_generation_service()
        response = await service.generate_bio_from_resume(request)

        logger.info(f"Successfully generated bio from resume for: {response.parsed_data.name}")
        return response

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in bio generation from resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error generating bio from resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate bio from resume: {str(e)}"
        )
    finally:
        # Close the file
        await file.close()


@router.post(
    "/know_your_worth",
    response_model=KnowYourWorthResponse,
    summary="Know Your Worth Calculator",
    description="Calculate freelancer worth in Indian market context with AI-powered insights"
)
async def know_your_worth(
    request: KnowYourWorthRequest = Body(
        ...,
        example={
            "skills": ["Python", "Django", "React", "AWS", "Docker", "PostgreSQL"],
            "years_of_experience": 5,
            "specialization": "Full-Stack Development",
            "city": "Bangalore",
            "education_level": "Bachelor's",
            "english_proficiency": "Fluent",
            "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional"],
            "portfolio_projects": 12
        }
    )
):
    """
    Calculate freelancer worth in Indian market context.

    This endpoint:
    1. Calculates estimated hourly rate based on multiple factors
    2. Considers Indian market dynamics (location, skills demand, etc.)
    3. Provides detailed breakdown of worth calculation
    4. Offers AI-powered market insights and positioning
    5. Gives personalized recommendations to increase earning potential

    Factors considered:
    - Years of experience and specialization
    - Skills (with premium for high-demand technologies)
    - Location (Tier 1, 2, 3 cities in India)
    - Education level (Bachelor's, Master's, PhD)
    - Professional certifications
    - Portfolio size and quality
    - Client reviews and reputation

    Returns:
    - Estimated hourly rate (INR and USD)
    - Monthly and annual earning potential
    - Detailed breakdown of calculation factors
    - Market insights (tier, position, demand level)
    - Competitive advantages
    - Personalized recommendations
    - Comparison with market average

    Example request:
    {
        "skills": ["Python", "Django", "React", "AWS"],
        "years_of_experience": 5,
        "specialization": "Full-Stack Development",
        "city": "Bangalore",
        "education_level": "Bachelor's",
        "english_proficiency": "Fluent",
        "certifications": ["AWS Certified", "Google Cloud Professional"],
        "portfolio_projects": 12
    }
    """
    try:
        service = await get_generation_service()
        logger.info(f"Calculating worth for: {request.name or 'a freelancer'}")
        response = await service.calculate_freelancer_worth(request)
        return response
    except Exception as e:
        logger.exception(f"Error calculating freelancer worth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate freelancer worth: {str(e)}"
        )


@router.post(
    "/generate_project_from_text",
    response_model=GenerateProjectFromTextResponse,
    summary="Generate Project Description from Brief Text",
    description="Generate complete project details (category, subcategory, title, description, skills) from client's brief text description"
)
async def generate_project_from_text(
    request: GenerateProjectFromTextRequest = Body(
        ...,
        example={
            "brief_description": "I need someone to build a mobile app for my restaurant with online ordering and delivery tracking",
            "budget": 50000,
            "budget_type": "Fixed-Price",
            "deadline": "2026-03-15"
        }
    )
):
    """
    Generate complete project description from brief text.

    This endpoint:
    1. Fetches available categories and subcategories from Project Service
    2. Uses AI to map the client's brief description to the most appropriate category/subcategory
    3. Generates a professional project title
    4. Creates a detailed project description (200-400 words)
    5. Suggests relevant skills required
    6. Estimates project duration and complexity

    Input:
    - brief_description: Client's brief text (e.g., "I need a mobile app for my restaurant")
    - budget (optional): Project budget
    - budget_type (optional): "Fixed-Price" or "Hourly"
    - deadline (optional): Project deadline

    Output:
    - category: Selected category from Project Service
    - sub_category: Selected subcategory from Project Service
    - title: Professional project title
    - description: Detailed project description
    - suggested_skills: List of relevant skills
    - estimated_duration: Estimated project duration
    - complexity_level: beginner/intermediate/expert

    Example request:
    {
        "brief_description": "Build a mobile app for restaurant",
        "budget": 50000,
        "deadline": "2026-03-15"
    }

    Example response:
    {
        "category": "IT And Development",
        "sub_category": "Mobile App Development",
        "title": "Restaurant Mobile App with Online Ordering & Delivery Tracking",
        "description": "We are seeking an experienced mobile app developer to create...",
        "suggested_skills": ["React Native", "Firebase", "Payment Gateway Integration", "Google Maps API"],
        "estimated_duration": "2-3 months",
        "complexity_level": "intermediate"
    }
    """
    try:
        service = await get_generation_service()
        logger.info(f"Generating project from text: {request.brief_description[:50]}...")
        response = await service.generate_project_from_text(request)
        return response
    except Exception as e:
        logger.exception(f"Error generating project from text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate project description: {str(e)}"
        )
