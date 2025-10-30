#!/usr/bin/env python3
"""
Script to load test data and validate recommendations.
Fixes validation errors and tests the recommendation system.
"""

import requests
import json
import time
from typing import List, Dict, Any
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# ANSI Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str, emoji: str = "🎯"):
    """Print a styled header."""
    border = "=" * 100
    print(f"\n{Colors.BOLD}{Colors.HEADER}{border}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{emoji}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{border}{Colors.ENDC}\n")

def print_subheader(text: str):
    """Print a styled subheader."""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'─' * 100}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}📋 {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'─' * 100}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_progress_bar(current: int, total: int, prefix: str = "", length: int = 50):
    """Print a progress bar."""
    percent = f"{100 * (current / float(total)):.1f}"
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent}% ({current}/{total})', end='', flush=True)
    if current == total:
        print()  # New line on completion

def print_table(headers: List[str], rows: List[List[str]], col_widths: List[int] = None):
    """Print a formatted table."""
    if not col_widths:
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) + 2 for i in range(len(headers))]

    # Print header
    header_line = "│".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers)))
    border = "─" * (sum(col_widths) + len(headers) * 3 - 1)

    print(f"┌{border}┐")
    print(f"│{header_line}│")
    print(f"├{border}┤")

    # Print rows
    for row in rows:
        row_line = "│".join(f" {str(row[i]):<{col_widths[i]}} " for i in range(len(row)))
        print(f"│{row_line}│")

    print(f"└{border}┘")

def print_score_bar(label: str, score: float, max_width: int = 40):
    """Print a visual score bar."""
    filled = int(max_width * score)
    bar = '█' * filled + '░' * (max_width - filled)

    # Color based on score
    if score >= 0.8:
        color = Colors.OKGREEN
    elif score >= 0.6:
        color = Colors.WARNING
    else:
        color = Colors.FAIL

    print(f"  {label:<30} {color}|{bar}| {score:.3f}{Colors.ENDC}")

# Fixed test data for hylancers
HYLANCERS = [
  {
    "hylancer_id": "b321c112-47f5-4a8b-b393-91a6b25ad7a1",
    "bio": "Full-stack developer specializing in high-performance APIs and cloud-native applications. Skilled in Go, Python, and AWS services. Passionate about building scalable and maintainable systems that handle millions of requests.",
    "past_projects": "Built a scalable microservice architecture for fintech transactions. Developed REST and GraphQL APIs for enterprise apps.",
    "skills": ["Go", "Python", "AWS", "Docker", "Kubernetes", "PostgreSQL"],
    "success_rate": 0.97,
    "client_satisfaction": 0.93,
    "communication_score": 0.96,
    "hourly_rate": 85,
    "availability_status": "available",
    "location": "Remote",
    "experience_level": 5,
    "total_projects": 22,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 40
    }
  },
  {
    "hylancer_id": "a145d224-12b3-46ef-8dc1-219af82ad9e1",
    "bio": "Frontend engineer passionate about creating interactive and accessible user interfaces. Strong background in React and TypeScript. Love crafting pixel-perfect designs that provide excellent user experiences.",
    "past_projects": "Redesigned a SaaS dashboard with advanced state management. Built a component library used across multiple teams.",
    "skills": ["React", "TypeScript", "Next.js", "Redux", "CSS", "Figma"],
    "success_rate": 0.93,
    "client_satisfaction": 0.91,
    "communication_score": 0.95,
    "hourly_rate": 70,
    "availability_status": "busy",
    "location": "Berlin, Germany",
    "experience_level": 3,
    "total_projects": 18,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 30
    }
  },
  {
    "hylancer_id": "9f231122-78cd-40af-b9a2-83e4ad26d4b2",
    "bio": "Backend developer with expertise in data-intensive applications and distributed systems. Adept in Python, Java, and Redis. Experienced in building high-throughput systems that process millions of events per day.",
    "past_projects": "Created an ETL pipeline for analytics. Designed scalable job schedulers and caching layers.",
    "skills": ["Python", "Java", "Redis", "Kafka", "PostgreSQL", "Docker"],
    "success_rate": 0.96,
    "client_satisfaction": 0.94,
    "communication_score": 0.9,
    "hourly_rate": 80,
    "availability_status": "available",
    "location": "Toronto, Canada",
    "experience_level": 5,
    "total_projects": 25,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 50
    }
  },
  {
    "hylancer_id": "6e712f34-0e93-41c2-b91c-15ab9df41a52",
    "bio": "Software engineer focused on DevOps and CI/CD automation. Experienced with AWS, Docker, and Terraform. Specialized in infrastructure as code and building reliable deployment pipelines.",
    "past_projects": "Set up CI/CD pipelines for a multi-region deployment. Automated infrastructure provisioning using Terraform.",
    "skills": ["AWS", "Terraform", "Docker", "Jenkins", "Python", "Bash"],
    "success_rate": 0.94,
    "client_satisfaction": 0.9,
    "communication_score": 0.97,
    "hourly_rate": 78,
    "availability_status": "available",
    "location": "Austin, USA",
    "experience_level": 4,
    "total_projects": 20,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 33
    }
  },
  {
    "hylancer_id": "a512c941-53d9-4b42-a36a-9f9349a18d77",
    "bio": "Mobile developer building performant iOS and Android apps using Flutter and Swift. Focused on creating smooth user experiences with native performance and cross-platform capabilities.",
    "past_projects": "Built a cross-platform fitness app with real-time sync. Integrated payment and analytics modules.",
    "skills": ["Flutter", "Dart", "Swift", "Firebase", "REST APIs", "Git"],
    "success_rate": 0.92,
    "client_satisfaction": 0.88,
    "communication_score": 0.94,
    "hourly_rate": 65,
    "availability_status": "busy",
    "location": "Remote",
    "experience_level": 3,
    "total_projects": 14,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 20
    }
  },
  {
    "hylancer_id": "4e313ac2-bb2e-4032-b99a-843f001ff872",
    "bio": "Machine learning engineer specializing in NLP and recommendation systems. Proficient in Python, TensorFlow, and PyTorch. Experienced in deploying ML models at scale using cloud infrastructure.",
    "past_projects": "Developed a sentiment analysis model for social data. Built a recommendation engine for e-commerce personalization.",
    "skills": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "SQL", "AWS"],
    "success_rate": 0.98,
    "client_satisfaction": 0.95,
    "communication_score": 0.92,
    "hourly_rate": 90,
    "availability_status": "available",
    "location": "London, UK",
    "experience_level": 5,
    "total_projects": 27,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 45
    }
  },
  {
    "hylancer_id": "3a45b212-7db5-4a01-8e19-33b6fa3cc9b1",
    "bio": "Backend-focused software developer with strong experience in Node.js, Express, and MongoDB. Passionate about building RESTful APIs and microservices with clean architecture patterns.",
    "past_projects": "Developed REST APIs for logistics management. Built authentication and billing systems from scratch.",
    "skills": ["Node.js", "Express", "MongoDB", "Redis", "AWS", "TypeScript"],
    "success_rate": 0.9,
    "client_satisfaction": 0.89,
    "communication_score": 0.91,
    "hourly_rate": 68,
    "availability_status": "available",
    "location": "Remote",
    "experience_level": 3,
    "total_projects": 16,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 28
    }
  },
  {
    "hylancer_id": "5b812a13-4472-48e7-9e17-36e8c1135f11",
    "bio": "Data engineer experienced in building and maintaining large-scale data pipelines with Spark and Airflow. Specialized in real-time streaming and batch processing workloads.",
    "past_projects": "Created a real-time streaming pipeline for IoT analytics. Optimized data warehouse queries by 40%.",
    "skills": ["Python", "Spark", "Airflow", "SQL", "AWS", "Docker"],
    "success_rate": 0.95,
    "client_satisfaction": 0.9,
    "communication_score": 0.96,
    "hourly_rate": 82,
    "availability_status": "available",
    "location": "Singapore",
    "experience_level": 4,
    "total_projects": 21,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 37
    }
  },
  {
    "hylancer_id": "df412ac2-cc72-43a2-9b8f-412f6fa21b31",
    "bio": "Full-stack developer with a focus on performance and maintainability. Experienced in Vue.js, Laravel, and MySQL. Love building clean, well-documented code that teams can easily work with.",
    "past_projects": "Developed an HR management tool with role-based access. Integrated RESTful services with frontend dashboards.",
    "skills": ["Vue.js", "Laravel", "MySQL", "PHP", "JavaScript", "Docker"],
    "success_rate": 0.91,
    "client_satisfaction": 0.89,
    "communication_score": 0.94,
    "hourly_rate": 72,
    "availability_status": "busy",
    "location": "Warsaw, Poland",
    "experience_level": 3,
    "total_projects": 17,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 24
    }
  },
  {
    "hylancer_id": "cb623a19-61f7-44a2-832a-1e9c8e918ef0",
    "bio": "Software architect with a focus on scalability and system design. Skilled in microservices, event-driven systems, and cloud infrastructure. Over 15 years of experience leading complex technical projects.",
    "past_projects": "Led a migration from monolith to microservices. Designed event-driven architecture for a logistics platform.",
    "skills": ["Java", "Spring Boot", "Kafka", "Kubernetes", "AWS", "PostgreSQL"],
    "success_rate": 0.99,
    "client_satisfaction": 0.97,
    "communication_score": 0.95,
    "hourly_rate": 100,
    "availability_status": "available",
    "location": "San Francisco, USA",
    "experience_level": 5,  # FIXED: Changed from 6 to 5 (max allowed)
    "total_projects": 35,
    "metadata": {
      "is_new_hylancer": False,
      "has_past_projects": True,
      "feedback_count": 60
    }
  }
]

# Fixed test data for projects
PROJECTS = [
  {
    "project_id": "a912c76e-3d54-47f1-88a9-42b89db77f1a",
    "title": "Build a SaaS analytics dashboard",
    "description": "We need a full-stack developer to create a SaaS platform with analytics dashboards, subscription management, and API integrations. Prior experience with data visualization tools is preferred. The platform should support multiple user roles and real-time data updates.",
    "required_skills": ["React", "Node.js", "MongoDB", "AWS"],
    "budget": 18000,
    "required_experience_level": 4,
    "preferred_location": "Remote",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "cf6d471b-25b3-4cc7-97e3-bd81e21b0d42",
    "title": "Develop a mobile banking app",
    "description": "Seeking a mobile developer to build a secure and user-friendly banking app with transaction history, notifications, and biometric login. Experience with Flutter or React Native required. Must implement strong security practices and comply with financial regulations.",
    "required_skills": ["Flutter", "Dart", "Firebase", "REST APIs"],
    "budget": 25000,
    "required_experience_level": 5,
    "preferred_location": "Remote",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "dc8311a2-fb22-46b2-b3a8-3f582fc87e21",
    "title": "Create an AI-powered recommendation system",
    "description": "Looking for a machine learning engineer to design and implement a recommendation engine for an e-commerce store. Experience with TensorFlow or PyTorch is a must. The system should handle personalized product recommendations based on user behavior and purchase history.",
    "required_skills": ["Python", "TensorFlow", "scikit-learn", "AWS"],
    "budget": 22000,
    "required_experience_level": 5,
    "preferred_location": "London, UK",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "e352aa77-5c81-46df-b9ef-1199e2d2126a",
    "title": "Redesign an existing corporate website",
    "description": "We need a frontend developer to redesign our corporate site for better performance, accessibility, and SEO. Must have strong React and Tailwind CSS experience. The site should be mobile-responsive and achieve 90+ Lighthouse scores.",
    "required_skills": ["React", "Next.js", "Tailwind CSS", "SEO"],
    "budget": 9000,
    "required_experience_level": 3,
    "preferred_location": "Remote",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "f931ca55-8b22-4b5e-bb23-f7e7af61a9e4",
    "title": "Develop a healthcare appointment system",
    "description": "Looking for a backend developer to build a REST API for appointment booking, patient management, and notifications. Experience with Node.js and PostgreSQL is essential. Must implement HIPAA-compliant security measures.",
    "required_skills": ["Node.js", "Express", "PostgreSQL", "Docker"],
    "budget": 14000,
    "required_experience_level": 4,
    "preferred_location": "Toronto, Canada",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "b4c32b11-6a21-4422-9335-cc92c8c77211",
    "title": "Build a microservices-based logistics platform",
    "description": "Seeking an experienced software architect to lead development of a scalable logistics system using microservices and message queues. Should have expertise in event-driven architecture and distributed systems. The platform will handle real-time tracking and route optimization.",
    "required_skills": ["Java", "Spring Boot", "Kafka", "Kubernetes"],
    "budget": 30000,
    "required_experience_level": 5,  # FIXED: Changed from 6 to 5
    "preferred_location": "San Francisco, USA",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "a712f633-225c-4a41-88cb-df1e2d664fe9",
    "title": "Create an educational video streaming platform",
    "description": "We're hiring a full-stack engineer to develop a streaming platform with real-time chat, user profiles, and course management features. Experience with WebSockets and video streaming protocols required. Platform should support thousands of concurrent users.",
    "required_skills": ["React", "Node.js", "WebSockets", "AWS"],
    "budget": 20000,
    "required_experience_level": 4,
    "preferred_location": "Remote",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "db25f111-118a-422c-b5a1-cb6227e8c932",
    "title": "Automate data pipelines for analytics",
    "description": "Need a data engineer to create automated data pipelines for real-time analytics dashboards using Airflow and Spark. Should handle ETL processes for large datasets and provide data quality monitoring. Experience with AWS or GCP required.",
    "required_skills": ["Python", "Airflow", "Spark", "SQL"],
    "budget": 16000,
    "required_experience_level": 5,
    "preferred_location": "Singapore",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "f5d1c823-8c22-48a3-9a99-11c22e5f6113",
    "title": "Develop an internal CRM tool",
    "description": "We need a web developer to build an internal CRM system with user authentication, analytics, and admin controls. The system should manage customer interactions, sales pipeline, and reporting. Experience with Vue.js and Laravel required.",  # FIXED: Extended to 150+ chars
    "required_skills": ["Vue.js", "Laravel", "MySQL", "Docker"],
    "budget": 13000,
    "required_experience_level": 3,
    "preferred_location": "Warsaw, Poland",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  },
  {
    "project_id": "c992f2a1-441b-4b91-a218-7a3111a2eaa1",
    "title": "Integrate AI chatbot into existing web platform",
    "description": "We're seeking an AI developer to integrate a conversational chatbot using OpenAI API into our customer support platform. Should implement natural language understanding, context management, and seamless handoff to human agents when needed.",
    "required_skills": ["Python", "FastAPI", "OpenAI API", "React"],
    "budget": 17000,
    "required_experience_level": 4,
    "preferred_location": "Remote",
    "status": "open",
    "metadata": {
      "is_generic_description": False,
      "skill_count": 4
    }
  }
]


def load_hylancer_embeddings():
    """Load all hylancer embeddings."""
    print_header("LOADING HYLANCER EMBEDDINGS", "👨‍💻")

    success_count = 0
    error_count = 0
    total = len(HYLANCERS)

    for idx, hylancer in enumerate(HYLANCERS, 1):
        hylancer_id = hylancer["hylancer_id"]
        name_info = f"{hylancer.get('location', 'Unknown')} | {hylancer.get('hourly_rate', 0)}/hr"

        print_progress_bar(idx - 1, total, prefix="Progress")

        try:
            response = requests.post(
                f"{BASE_URL}/hylancer_embeddings",
                json=hylancer,
                timeout=30
            )

            if response.status_code == 201:
                print_success(f"Loaded hylancer {idx}/{total}: {name_info}")
                success_count += 1
            else:
                print_error(f"Failed hylancer {idx}/{total}: {response.status_code}")
                error_count += 1

        except Exception as e:
            print_error(f"Exception for hylancer {idx}/{total}: {str(e)[:80]}...")
            error_count += 1

        time.sleep(0.5)  # Avoid rate limiting

    print_progress_bar(total, total, prefix="Progress")

    # Summary table
    print("\n")
    print_table(
        ["Status", "Count", "Percentage"],
        [
            [f"{Colors.OKGREEN}✅ Success{Colors.ENDC}", str(success_count), f"{100*success_count/total:.1f}%"],
            [f"{Colors.FAIL}❌ Errors{Colors.ENDC}", str(error_count), f"{100*error_count/total:.1f}%"],
            ["📊 Total", str(total), "100%"]
        ]
    )

    return success_count, error_count


def load_project_embeddings():
    """Load all project embeddings."""
    print_header("LOADING PROJECT EMBEDDINGS", "📁")

    success_count = 0
    error_count = 0
    total = len(PROJECTS)

    for idx, project in enumerate(PROJECTS, 1):
        project_id = project["project_id"]
        project_info = f"{project['title'][:50]}... | ${project['budget']:,}"

        print_progress_bar(idx - 1, total, prefix="Progress")

        try:
            response = requests.post(
                f"{BASE_URL}/project_embeddings",
                json=project,
                timeout=30
            )

            if response.status_code == 201:
                print_success(f"Loaded project {idx}/{total}: {project_info}")
                success_count += 1
            else:
                print_error(f"Failed project {idx}/{total}: {response.status_code}")
                error_count += 1

        except Exception as e:
            print_error(f"Exception for project {idx}/{total}: {str(e)[:80]}...")
            error_count += 1

        time.sleep(0.5)  # Avoid rate limiting

    print_progress_bar(total, total, prefix="Progress")

    # Summary table
    print("\n")
    print_table(
        ["Status", "Count", "Percentage"],
        [
            [f"{Colors.OKGREEN}✅ Success{Colors.ENDC}", str(success_count), f"{100*success_count/total:.1f}%"],
            [f"{Colors.FAIL}❌ Errors{Colors.ENDC}", str(error_count), f"{100*error_count/total:.1f}%"],
            ["📊 Total", str(total), "100%"]
        ]
    )

    return success_count, error_count


def test_recommendation(project_id: str, project_title: str):
    """Test hylancer recommendations for a specific project."""
    print_subheader(f"TESTING: {project_title}")

    print_info(f"Project ID: {project_id}")

    try:
        response = requests.post(
            f"{BASE_URL}/recommend_hylancer",
            json={"project_id": project_id, "top_k": 5},
            timeout=30
        )

        if response.status_code != 200:
            print_error(f"API Error {response.status_code}: {response.text}")
            return None

        data = response.json()
        results = data.get("results", [])

        if not results:
            print_warning("No recommendations returned")
            return None

        print_success(f"Returned {len(results)} recommendations")

        # Find project info for reference
        project_info = next((p for p in PROJECTS if p["project_id"] == project_id), None)
        if project_info:
            skills_str = ', '.join(project_info['required_skills'])
            print(f"\n{Colors.BOLD}Required Skills:{Colors.ENDC} {Colors.OKCYAN}{skills_str}{Colors.ENDC}")
            print(f"{Colors.BOLD}Budget:{Colors.ENDC} {Colors.OKCYAN}${project_info['budget']:,}{Colors.ENDC}")
            print(f"{Colors.BOLD}Experience Level:{Colors.ENDC} {Colors.OKCYAN}{project_info['required_experience_level']}/5{Colors.ENDC}\n")

        # Create recommendations table
        print(f"\n{Colors.BOLD}{'='*100}{Colors.ENDC}")

        for i, rec in enumerate(results, 1):
            hylancer_id = rec["hylancer_id"]
            score = rec['score']
            confidence = rec['metadata']['confidence']

            # Find hylancer info
            hylancer_info = next((h for h in HYLANCERS if h["hylancer_id"] == hylancer_id), None)

            # Rank indicator with color
            if i == 1:
                rank_str = f"{Colors.OKGREEN}🥇 #{i}{Colors.ENDC}"
            elif i == 2:
                rank_str = f"{Colors.WARNING}🥈 #{i}{Colors.ENDC}"
            elif i == 3:
                rank_str = f"{Colors.FAIL}🥉 #{i}{Colors.ENDC}"
            else:
                rank_str = f"   #{i}"

            # Confidence badge
            if confidence == 'high':
                conf_badge = f"{Colors.OKGREEN}●{Colors.ENDC} HIGH"
            elif confidence == 'medium':
                conf_badge = f"{Colors.WARNING}●{Colors.ENDC} MEDIUM"
            else:
                conf_badge = f"{Colors.FAIL}●{Colors.ENDC} LOW"

            print(f"\n{rank_str} {Colors.BOLD}Score: {score:.3f}{Colors.ENDC} | Confidence: {conf_badge}")

            if hylancer_info:
                location = hylancer_info.get('location', 'Unknown')
                rate = hylancer_info.get('hourly_rate', 0)
                print(f"    📍 {location} | 💰 ${rate}/hr")

            # Show score components with visual bars
            comp = rec["components"]
            print(f"\n    {Colors.BOLD}Score Breakdown:{Colors.ENDC}")
            print_score_bar("Bio Similarity", comp['bio_similarity'])
            print_score_bar("Past Projects", comp['past_project_similarity'])
            print_score_bar("Skill Overlap", comp['skill_overlap'])
            print_score_bar("Success Rate", comp['success_rate'])
            print_score_bar("Client Satisfaction", comp['client_satisfaction'])
            print_score_bar("Communication", comp['communication_score'])

            # Show matched skills
            matched = rec['metadata']['matched_skills']
            if matched:
                skills_display = f"{Colors.OKGREEN}{'  •  '.join(matched)}{Colors.ENDC}"
                print(f"\n    {Colors.BOLD}✓ Matched Skills ({len(matched)}):{Colors.ENDC} {skills_display}")
            else:
                print(f"\n    {Colors.WARNING}⚠ No matched skills{Colors.ENDC}")

            # Show reason
            print(f"\n    {Colors.BOLD}💡 Why this match:{Colors.ENDC}")
            reason_lines = rec['reason'][:200].split('. ')
            for line in reason_lines[:2]:
                if line.strip():
                    print(f"       • {line.strip()}")

            print(f"\n{Colors.BOLD}{'─'*100}{Colors.ENDC}")

        return results

    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def validate_semantic_search():
    """Validate that semantic search is working correctly."""
    print_header("SEMANTIC SEARCH VALIDATION", "🔍")

    test_cases = [
        {
            "project_id": "dc8311a2-fb22-46b2-b3a8-3f582fc87e21",
            "title": "AI-powered recommendation system",
            "expected_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
            "expected_hylancer": "4e313ac2-bb2e-4032-b99a-843f001ff872"  # ML engineer
        },
        {
            "project_id": "b4c32b11-6a21-4422-9335-cc92c8c77211",
            "title": "Microservices logistics platform",
            "expected_skills": ["Java", "Spring Boot", "Kafka", "Kubernetes"],
            "expected_hylancer": "cb623a19-61f7-44a2-832a-1e9c8e918ef0"  # Software architect
        },
        {
            "project_id": "cf6d471b-25b3-4cc7-97e3-bd81e21b0d42",
            "title": "Mobile banking app",
            "expected_skills": ["Flutter", "Dart", "Firebase"],
            "expected_hylancer": "a512c941-53d9-4b42-a36a-9f9349a18d77"  # Mobile developer
        },
        {
            "project_id": "db25f111-118a-422c-b5a1-cb6227e8c932",
            "title": "Data pipelines for analytics",
            "expected_skills": ["Python", "Airflow", "Spark"],
            "expected_hylancer": "5b812a13-4472-48e7-9e17-36e8c1135f11"  # Data engineer
        }
    ]

    validation_results = []

    for test_case in test_cases:
        results = test_recommendation(test_case["project_id"], test_case["title"])

        if not results:
            validation_results.append({
                "test": test_case["title"],
                "passed": False,
                "reason": "No recommendations returned"
            })
            continue

        # Check if expected hylancer is in top 3
        top_3_ids = [r["hylancer_id"] for r in results[:3]]
        expected_in_top_3 = test_case["expected_hylancer"] in top_3_ids

        # Check skill overlap in top result
        top_matched_skills = set(results[0]["metadata"]["matched_skills"])
        expected_skills = set(test_case["expected_skills"])
        skill_overlap = len(top_matched_skills.intersection(expected_skills))

        # Check scores are reasonable
        top_score = results[0]["score"]
        scores_descending = all(results[i]["score"] >= results[i+1]["score"] for i in range(len(results)-1))

        passed = expected_in_top_3 and skill_overlap >= 2 and top_score >= 0.5 and scores_descending

        validation_results.append({
            "test": test_case["title"],
            "passed": passed,
            "expected_in_top_3": expected_in_top_3,
            "skill_overlap": skill_overlap,
            "top_score": top_score,
            "scores_descending": scores_descending
        })

    # Print validation summary
    print_header("VALIDATION SUMMARY", "📊")

    # Calculate overall accuracy
    passed = sum(1 for r in validation_results if r["passed"])
    total = len(validation_results)
    accuracy = (passed / total * 100) if total > 0 else 0

    # Print overall accuracy meter
    print(f"\n{Colors.BOLD}Overall Accuracy:{Colors.ENDC}")
    print_score_bar(f"{passed}/{total} tests passed", accuracy / 100, max_width=60)

    # Create detailed results table
    print("\n")
    table_rows = []
    for result in validation_results:
        status_icon = f"{Colors.OKGREEN}✅{Colors.ENDC}" if result["passed"] else f"{Colors.FAIL}❌{Colors.ENDC}"
        test_name = result['test'][:40]

        metrics = []
        if result.get('expected_in_top_3') is not None:
            metrics.append(f"Top3: {'Yes' if result['expected_in_top_3'] else 'No'}")
        if result.get('skill_overlap') is not None:
            metrics.append(f"Skills: {result['skill_overlap']}")
        if result.get('top_score') is not None:
            metrics.append(f"Score: {result['top_score']:.3f}")

        metrics_str = ' | '.join(metrics) if metrics else "N/A"

        table_rows.append([status_icon, test_name, metrics_str])

    print_table(
        ["Status", "Test Case", "Metrics"],
        table_rows,
        col_widths=[10, 45, 40]
    )

    # Print final summary box
    print(f"\n{Colors.BOLD}{'='*100}{Colors.ENDC}")
    if accuracy == 100:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 PERFECT SCORE! All tests passed! 🎉{Colors.ENDC}")
    elif accuracy >= 75:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ GREAT! Most tests passed ({passed}/{total}){Colors.ENDC}")
    elif accuracy >= 50:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  NEEDS IMPROVEMENT: {passed}/{total} tests passed{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ FAILED: Only {passed}/{total} tests passed{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*100}{Colors.ENDC}\n")

    return validation_results


def main():
    """Main execution function."""
    start_time = datetime.now()

    print_header("HYLANCER RECOMMENDATION SYSTEM", "🚀")
    print(f"{Colors.BOLD}Data Loader & Validation Suite{Colors.ENDC}")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    h_success, h_errors = load_hylancer_embeddings()
    p_success, p_errors = load_project_embeddings()

    # Show loading summary
    total_loaded = h_success + p_success
    total_errors = h_errors + p_errors

    print_subheader("Data Loading Summary")

    if total_errors > 0:
        print_warning(f"Some embeddings failed to load ({total_errors} errors)")
        print_info("Continuing with validation using available data...")
    else:
        print_success(f"All embeddings loaded successfully! ({total_loaded} items)")

    # Wait for embeddings to be processed
    print_info("Waiting 3 seconds for embeddings to be processed...")
    for i in range(3, 0, -1):
        print(f"  {i}...", end='\r', flush=True)
        time.sleep(1)
    print("  ✓   ")

    # Validate recommendations
    validation_results = validate_semantic_search()

    # Calculate total execution time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Final summary
    print_header("EXECUTION COMPLETE", "🏁")

    print_table(
        ["Metric", "Value"],
        [
            ["Hylancers Loaded", f"{h_success}/{h_success + h_errors}"],
            ["Projects Loaded", f"{p_success}/{p_success + p_errors}"],
            ["Tests Passed", f"{sum(1 for r in validation_results if r['passed'])}/{len(validation_results)}"],
            ["Total Duration", f"{duration:.2f} seconds"],
            ["Status", f"{Colors.OKGREEN}SUCCESS{Colors.ENDC}" if total_errors == 0 and all(r['passed'] for r in validation_results) else f"{Colors.WARNING}COMPLETED WITH WARNINGS{Colors.ENDC}"]
        ],
        col_widths=[25, 60]
    )

    print(f"\n{Colors.BOLD}Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
