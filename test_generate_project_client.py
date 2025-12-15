#!/usr/bin/env python3
"""
Client script to call AI Service generate_project_from_text endpoint.
This demonstrates how the UI should call the AI Service with JWT authentication.
"""

import requests
import json
import sys


class AIServiceClient:
    """Client for Hylancer AI Service"""

    def __init__(self, base_url: str, jwt_token: str):
        """
        Initialize AI Service client.

        Args:
            base_url: Base URL of AI Service (e.g., http://localhost:8000)
            jwt_token: JWT token from user authentication
        """
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token

    def _get_headers(self):
        """Get request headers with JWT authentication."""
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }

    def generate_project_from_text(
        self,
        brief_description: str,
        budget: float = None,
        budget_type: str = "Fixed-Price",
        deadline: str = None
    ):
        """
        Generate complete project description from brief text.

        Args:
            brief_description: Client's brief description of what they need
            budget: Optional project budget
            budget_type: "Fixed-Price" or "Hourly"
            deadline: Optional deadline in YYYY-MM-DD format

        Returns:
            dict: Generated project details including category, title, description, etc.

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v1/generate_project_from_text"

        payload = {
            "brief_description": brief_description
        }

        if budget is not None:
            payload["budget"] = budget
        if budget_type:
            payload["budget_type"] = budget_type
        if deadline:
            payload["deadline"] = deadline

        print(f"📤 Calling AI Service: {url}")
        print(f"🔑 Using JWT token: {self.jwt_token[:30]}...")
        print(f"📝 Request payload: {json.dumps(payload, indent=2)}\n")

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )

            print(f"📥 Response status: {response.status_code}")

            # Raise exception for HTTP errors
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            print(f"Response: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            raise


def main():
    """Example usage of AI Service client"""

    # Configuration
    AI_SERVICE_URL = "http://localhost:8000"

    # JWT Token - In real UI, this comes from user's authentication
    # The UI should get this from the user's login session
    JWT_TOKEN = "eyJraWQiOiJtOU1JQTBSTnZhbnBVajlkQUlwZDAzYkdVbHpDcEp6ZTNqXC9JQkltTlRkdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiMTkzYmRhYS03MDAxLTcwNTMtODllYi03NmEyNTVhM2ZmNWYiLCJjb2duaXRvOmdyb3VwcyI6WyJDbGllbnQiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aC0xLmFtYXpvbmF3cy5jb21cL2FwLXNvdXRoLTFfNVRwSnhhZWpGIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjpmYWxzZSwiY29nbml0bzp1c2VybmFtZSI6ImIxOTNiZGFhLTcwMDEtNzA1My04OWViLTc2YTI1NWEzZmY1ZiIsImN1c3RvbTpSb2xlIjoiQ0xJRU5UIiwib3JpZ2luX2p0aSI6ImMyMTRhMTkzLTJmZGEtNDBmOC04N2M0LWQ5Njk0MzFlYTViZiIsImF1ZCI6InA3b2xjMGRqZTU1aHFtdHQ3ZWRtODd2bDAiLCJldmVudF9pZCI6IjNkZjU4YmE0LThjNGQtNDEwYi04MWI1LWIzNWI1MGM1OTk1OSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzY1NTIyMDY5LCJuYW1lIjoiUmF0aGkgVmlqYXkiLCJwaG9uZV9udW1iZXIiOiIrOTE0MzQ1NDU0NTMyIiwiZXhwIjoxNzY1NjA4NDY5LCJpYXQiOjE3NjU1MjIwNjksImp0aSI6ImI5NjYzZjNmLTgzYmYtNDU4ZS04MWIzLWI2M2I4N2IzMzY3NSIsImVtYWlsIjoiZmVmaWIzMjYyN0BkZWxhZWIuY29tIn0.arHNOPs_lNPFNU1rXeVTvuwB_yxTKYHFyMhbJRb4wbKdPJeH0RSyABtBkTSl2JiymQ6sJFG_Q_DLS9iTGXettbUr0InJ6bzrObVgvBlGBQ0T8slP4IQD3jKWVdglWtO-RYusxk0223lh2-KN1wbaJk0ex9jgizO1e8JNLceFhknxZCL-XxFcZVq2dEOPRxS8ZAbYYEn8h97d2UaPZVvkQ9tGnIHBPZ4-mgxRdc11zCtnO_q4-nl5Deq5TpK0o27fRWAjZXi6OlUqBN4P5hKSclemgdEKZ8i-4xRtlxUliVbzIR7h4_oOpaRCxfpHCO8SMyuwAvDQVEvYpl5S4WqAVg"

    print("=" * 80)
    print("AI Service Client - Generate Project from Text")
    print("=" * 80)
    print()

    # Initialize client
    client = AIServiceClient(AI_SERVICE_URL, JWT_TOKEN)

    # Example 1: Restaurant mobile app
    print("📱 Example 1: Restaurant Mobile App")
    print("-" * 80)
    try:
        result = client.generate_project_from_text(
            brief_description="I need a mobile app for my restaurant with online ordering and delivery tracking",
            budget=50000,
            budget_type="Fixed-Price",
            deadline="2026-03-31"
        )

        print("✅ SUCCESS!\n")
        print(f"Category: {result.get('category')}")
        print(f"Sub-Category: {result.get('sub_category')}")
        print(f"Title: {result.get('title')}")
        print(f"\nDescription:")
        print(result.get('description'))
        print(f"\nSuggested Skills: {', '.join(result.get('suggested_skills', []))}")
        print(f"Estimated Duration: {result.get('estimated_duration')}")
        print(f"Complexity Level: {result.get('complexity_level')}")

    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print()

    # Example 2: E-commerce website
    print("🛒 Example 2: E-commerce Website")
    print("-" * 80)
    try:
        result = client.generate_project_from_text(
            brief_description="Build an e-commerce website to sell handmade jewelry online",
            budget=80000,
            budget_type="Fixed-Price"
        )

        print("✅ SUCCESS!\n")
        print(f"Category: {result.get('category')}")
        print(f"Sub-Category: {result.get('sub_category')}")
        print(f"Title: {result.get('title')}")
        print(f"\nSuggested Skills: {', '.join(result.get('suggested_skills', []))}")

    except Exception as e:
        print(f"❌ Failed: {e}")

    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


# Example usage for integration in UI framework
def example_react_integration():
    """
    Example of how to integrate this in a React/Next.js frontend.

    In your frontend code, you would make a similar API call:
    """
    example_code = """
    // React/Next.js Example

    const generateProject = async (briefDescription, budget, userToken) => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/generate_project_from_text', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userToken}`,  // JWT from user session
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            brief_description: briefDescription,
            budget: budget,
            budget_type: 'Fixed-Price'
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

      } catch (error) {
        console.error('Error generating project:', error);
        throw error;
      }
    };

    // Usage in React component
    const handleGenerateProject = async () => {
      const userToken = getUserTokenFromSession(); // Get from auth context/session
      const result = await generateProject(
        "I need a mobile app for my restaurant",
        50000,
        userToken
      );

      console.log('Generated project:', result);
      // Update UI with result.category, result.title, result.description, etc.
    };
    """
    return example_code


def example_angular_integration():
    """
    Example of how to integrate this in an Angular frontend.
    """
    example_code = """
    // Angular Example (TypeScript)

    import { HttpClient, HttpHeaders } from '@angular/common/http';
    import { Injectable } from '@angular/core';
    import { Observable } from 'rxjs';

    @Injectable({
      providedIn: 'root'
    })
    export class AIServiceClient {
      private baseUrl = 'http://localhost:8000';

      constructor(private http: HttpClient) {}

      generateProjectFromText(
        briefDescription: string,
        budget: number,
        userToken: string
      ): Observable<any> {
        const headers = new HttpHeaders({
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        });

        const payload = {
          brief_description: briefDescription,
          budget: budget,
          budget_type: 'Fixed-Price'
        };

        return this.http.post(
          `${this.baseUrl}/api/v1/generate_project_from_text`,
          payload,
          { headers }
        );
      }
    }

    // Usage in component
    export class ProjectFormComponent {
      constructor(private aiService: AIServiceClient) {}

      async onGenerateProject() {
        const userToken = this.authService.getToken(); // Get from auth service

        this.aiService.generateProjectFromText(
          'I need a mobile app for my restaurant',
          50000,
          userToken
        ).subscribe({
          next: (result) => {
            console.log('Generated project:', result);
            // Update component with result
          },
          error: (error) => {
            console.error('Error:', error);
          }
        });
      }
    }
    """
    return example_code


if __name__ == "__main__":
    main()

    # Uncomment to see frontend integration examples
    # print("\n" + "=" * 80)
    # print("React/Next.js Integration Example:")
    # print("=" * 80)
    # print(example_react_integration())
    #
    # print("\n" + "=" * 80)
    # print("Angular Integration Example:")
    # print("=" * 80)
    # print(example_angular_integration())
