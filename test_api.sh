#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

echo "========================================="
echo "Testing Hylancer AI Recommendation APIs"
echo "========================================="
echo ""

# Test 1: Create Freelancer Embedding
echo "1. Creating Freelancer Embedding..."
FREELANCER_RESPONSE=$(curl -s -X POST "$BASE_URL/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "freelancer_id": "123e4567-e89b-12d3-a456-426614174000",
    "bio": "I am a senior full-stack developer with over 8 years of experience building scalable web applications using modern JavaScript frameworks and cloud technologies. Expert in React, Node.js, and AWS with a passion for clean code and agile methodologies.",
    "past_projects": "E-commerce Platform: Built a scalable online marketplace using React, Node.js, and MongoDB. Real-time Chat Application: Developed WebSocket-based chat system with 10K concurrent users.",
    "skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "AWS", "Docker"],
    "success_rate": 0.92,
    "client_satisfaction": 0.95,
    "communication_score": 0.90,
    "hourly_rate": 75.00,
    "availability_status": "available",
    "location": "San Francisco, CA",
    "experience_level": 4,
    "total_projects": 15,
    "metadata": {
      "is_new_freelancer": false,
      "has_past_projects": true,
      "feedback_count": 12
    }
  }')

echo "$FREELANCER_RESPONSE" | python -m json.tool
echo ""

# Test 2: Create Project Embedding
echo "2. Creating Project Embedding..."
PROJECT_RESPONSE=$(curl -s -X POST "$BASE_URL/project_embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "223e4567-e89b-12d3-a456-426614174001",
    "title": "Build Real-time Collaboration Platform",
    "description": "We need an experienced full-stack developer to build a real-time collaboration platform similar to Figma or Miro. The platform should support multiple users working simultaneously on the same canvas with WebSocket technology. Key features include real-time updates, user authentication, drawing tools, and cloud storage integration. Must have experience with React, Node.js, WebSocket, and AWS deployment.",
    "required_skills": ["React", "Node.js", "WebSocket", "AWS", "TypeScript"],
    "budget": 8000.00,
    "required_experience_level": 4,
    "preferred_location": null,
    "status": "open",
    "metadata": {
      "is_generic_description": false,
      "skill_count": 5
    }
  }')

echo "$PROJECT_RESPONSE" | python -m json.tool
echo ""

# Test 3: Get Freelancer Recommendations for Project
echo "3. Getting Freelancer Recommendations for Project..."
RECOMMENDATIONS=$(curl -s -X POST "$BASE_URL/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "223e4567-e89b-12d3-a456-426614174001",
    "top_k": 10,
    "min_score": 0.3
  }')

echo "$RECOMMENDATIONS" | python -m json.tool
echo ""

# Test 4: Get Project Recommendations for Freelancer
echo "4. Getting Project Recommendations for Freelancer..."
PROJECT_RECS=$(curl -s -X POST "$BASE_URL/recommend_projects" \
  -H "Content-Type: application/json" \
  -d '{
    "freelancer_id": "123e4567-e89b-12d3-a456-426614174000",
    "top_k": 10,
    "min_score": 0.3
  }')

echo "$PROJECT_RECS" | python -m json.tool
echo ""

# Test 5: Check Metrics Again
echo "5. Checking Updated Metrics..."
curl -s "$BASE_URL/metrics" | python -m json.tool
echo ""

echo "========================================="
echo "Testing Complete!"
echo "========================================="
