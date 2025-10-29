import httpx
import asyncio
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Example Freelancer Embedding Request Body (for POST /api/v1/embeddings)
# application/json
# {
#   "freelancer_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
#   "bio": "Experienced Python developer with expertise in FastAPI and machine learning. Passionate about building scalable and efficient AI solutions.",
#   "past_projects": "Developed a recommendation engine for an e-commerce platform. Built a real-time data processing pipeline using Apache Kafka. Created a sentiment analysis API.",
#   "skills": [
#     "Python",
#     "FastAPI",
#     "Machine Learning",
#     "Docker",
#     "SQL",
#     "AWS"
#   ],
#   "success_rate": 0.98,
#   "client_satisfaction": 0.95,
#   "communication_score": 0.97,
#   "hourly_rate": 85.0,
#   "availability_status": "available",
#   "location": "Remote",
#   "experience_level": 5,
#   "total_projects": 20,
#   "metadata": {
#     "is_new_freelancer": false,
#     "has_past_projects": true,
#     "feedback_count": 30
#   }
# }

async def ingest_freelancer_data():
    print("Ingesting sample freelancer data...")
    freelancers = [
        {
            "freelancer_id": str(uuid.uuid4()),
            "bio": "Experienced Python developer with expertise in FastAPI and machine learning. Passionate about building scalable and efficient AI solutions.",
            "past_projects": "Developed a recommendation engine for an e-commerce platform. Built a real-time data processing pipeline using Apache Kafka. Created a sentiment analysis API.",
            "skills": ["Python", "FastAPI", "Machine Learning", "Docker", "SQL", "AWS"],
            "success_rate": 0.98,
            "client_satisfaction": 0.95,
            "communication_score": 0.97,
            "hourly_rate": 85.0,
            "availability_status": "available",
            "location": "Remote",
            "experience_level": 5,
            "total_projects": 20,
            "metadata": {
                "is_new_freelancer": False,
                "has_past_projects": True,
                "feedback_count": 30
            }
        },
        {
            "freelancer_id": str(uuid.uuid4()),
            "bio": "Full-stack JavaScript developer with a focus on React and Node.js. Enjoys creating intuitive user interfaces and robust backend systems.",
            "past_projects": "Built a customer relationship management (CRM) system. Developed a progressive web application (PWA) for a local business. Contributed to an open-source UI library.",
            "skills": ["JavaScript", "React", "Node.js", "MongoDB", "TypeScript", "GraphQL"],
            "success_rate": 0.92,
            "client_satisfaction": 0.90,
            "communication_score": 0.93,
            "hourly_rate": 70.0,
            "availability_status": "busy",
            "location": "New York, USA",
            "experience_level": 4,
            "total_projects": 12,
            "metadata": {
                "is_new_freelancer": False,
                "has_past_projects": True,
                "feedback_count": 18
            }
        },
        {
            "freelancer_id": str(uuid.uuid4()),
            "bio": "Data Scientist with a strong background in statistical modeling and data visualization. Experienced in using Python for data analysis and building predictive models.",
            "past_projects": "Analyzed customer churn for a telecommunications company. Developed a fraud detection system for a financial institution. Created interactive dashboards using Tableau.",
            "skills": ["Python", "R", "Pandas", "NumPy", "Scikit-learn", "Tableau", "SQL"],
            "success_rate": 0.96,
            "client_satisfaction": 0.94,
            "communication_score": 0.96,
            "hourly_rate": 90.0,
            "availability_status": "available",
            "location": "London, UK",
            "experience_level": 5,
            "total_projects": 15,
            "metadata": {
                "is_new_freelancer": False,
                "has_past_projects": True,
                "feedback_count": 22
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        for freelancer in freelancers:
            try:
                response = await client.post(f"{BASE_URL}/embeddings", json=freelancer)
                response.raise_for_status()
                print(f"Successfully ingested freelancer: {freelancer['freelancer_id']}")
            except httpx.HTTPStatusError as e:
                print(f"Error ingesting freelancer {freelancer['freelancer_id']}: {e.response.text}")
            except Exception as e:
                print(f"An unexpected error occurred for freelancer {freelancer['freelancer_id']}: {e}")

# Example Project Embedding Request Body (for POST /api/v1/project_embeddings)
# application/json
# {
#   "project_id": "11111111-2222-3333-4444-555555555501",
#   "title": "Build a scalable AI-powered recommendation system",
#   "description": "We need an experienced AI engineer to design and implement a recommendation system for our new e-commerce platform. The system should be scalable, efficient, and integrate with our existing data infrastructure. Experience with collaborative filtering and deep learning models is a plus.",
#   "required_skills": [
#     "Machine Learning",
#     "Python",
#     "TensorFlow",
#     "AWS",
#     "Data Engineering"
#   ],
#   "budget": 25000.0,
#   "required_experience_level": 5,
#   "preferred_location": "Remote",
#   "status": "open",
#   "metadata": {
#     "is_generic_description": false,
#     "skill_count": 5
#   }
# }

async def ingest_project_data():
    print("Ingesting sample project data...")
    projects = [
        {
            "project_id": str(uuid.uuid4()),
            "title": "Build a scalable AI-powered recommendation system",
            "description": "We need an experienced AI engineer to design and implement a recommendation system for our new e-commerce platform. The system should be scalable, efficient, and integrate with our existing data infrastructure. Experience with collaborative filtering and deep learning models is a plus.",
            "required_skills": ["Machine Learning", "Python", "TensorFlow", "AWS", "Data Engineering"],
            "budget": 25000.0,
            "required_experience_level": 5,
            "preferred_location": "Remote",
            "status": "open",
            "metadata": {
                "is_generic_description": False,
                "skill_count": 5
            }
        },
        {
            "project_id": str(uuid.uuid4()),
            "title": "Develop a modern full-stack web application",
            "description": "Looking for a talented full-stack developer to build a responsive web application for managing customer interactions. The application should feature a user-friendly interface, secure authentication, and a robust backend API. Technologies: React, Node.js, PostgreSQL.",
            "required_skills": ["React", "Node.js", "PostgreSQL", "TypeScript", "RESTful APIs"],
            "budget": 18000.0,
            "required_experience_level": 4,
            "preferred_location": "Any",
            "status": "open",
            "metadata": {
                "is_generic_description": False,
                "skill_count": 5
            }
        },
        {
            "project_id": str(uuid.uuid4()),
            "title": "Data analysis and visualization for marketing campaigns",
            "description": "We require a data scientist to analyze the performance of our recent marketing campaigns. The task involves cleaning and processing large datasets, performing statistical analysis, and creating insightful visualizations to identify key trends and areas for improvement.",
            "required_skills": ["Data Analysis", "Python", "Pandas", "Matplotlib", "SQL", "Tableau"],
            "budget": 12000.0,
            "required_experience_level": 4,
            "preferred_location": "Remote",
            "status": "open",
            "metadata": {
                "is_generic_description": False,
                "skill_count": 6
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        for project in projects:
            try:
                response = await client.post(f"{BASE_URL}/project_embeddings", json=project)
                response.raise_for_status()
                print(f"Successfully ingested project: {project['project_id']}")
            except httpx.HTTPStatusError as e:
                print(f"Error ingesting project {project['project_id']}: {e.response.text}")
            except Exception as e:
                print(f"An unexpected error occurred for project {project['project_id']}: {e}")

async def main():
    await ingest_freelancer_data()
    await ingest_project_data()
    print("Sample data ingestion complete.")

if __name__ == "__main__":
    asyncio.run(main())
