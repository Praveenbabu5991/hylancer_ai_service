# app/clients/project_service_client.py
"""Client for interacting with the Hylancer Project Service."""

import httpx
from typing import Dict, List, Optional
from loguru import logger


class ProjectServiceClient:
    """Async client for Hylancer Project Service."""

    def __init__(self, base_url: str, jwt_token: Optional[str] = None):
        """
        Initialize the Project Service client.

        Args:
            base_url: Base URL of the project service
            jwt_token: Optional JWT authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        return headers

    async def get_categories_and_subcategories(self) -> Dict[str, List[str]]:
        """
        Fetch all categories and their subcategories from the project service.

        Returns:
            Dictionary mapping category names to lists of subcategories
        """
        url = f"{self.base_url}/api/projects/categories-and-subcategories"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                # Extract categories from response
                if 'data' in data and 'categories_And_Subcategories' in data['data']:
                    return data['data']['categories_And_Subcategories']

                logger.warning(f"Unexpected response format: {data}")
                return {}

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching categories: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            raise
