# app/integrations/base_client.py - Reusable async API client for internal services.

import httpx
import asyncio
from loguru import logger
from typing import Optional, Dict, Any

class BaseClient:
    def __init__(self, base_url: str, service_name: str):
        if not base_url:
            raise ValueError(f"Base URL for {service_name} cannot be empty.")
        self.base_url = base_url
        self.service_name = service_name
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def _request(self, method: str, url: str, retries: int = 2, backoff_factor: float = 0.5, **kwargs) -> httpx.Response:
        for attempt in range(retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()  # Raise an exception for 4xx/5xx responses
                logger.info(f"[{self.service_name}] {method} {url} successful (Attempt {attempt + 1})")
                return response
            except httpx.TimeoutException as e:
                logger.warning(f"[{self.service_name}] Timeout during {method} {url} (Attempt {attempt + 1}/{retries + 1}): {e}")
            except httpx.HTTPStatusError as e:
                logger.error(f"[{self.service_name}] HTTP error during {method} {url} (Attempt {attempt + 1}/{retries + 1}): {e.response.status_code} - {e.response.text}")
                if attempt == retries:
                    raise
            except httpx.RequestError as e:
                logger.error(f"[{self.service_name}] Request error during {method} {url} (Attempt {attempt + 1}/{retries + 1}): {e}")
                if attempt == retries:
                    raise
            except Exception as e:
                logger.error(f"[{self.service_name}] Unexpected error during {method} {url} (Attempt {attempt + 1}/{retries + 1}): {e}")
                if attempt == retries:
                    raise

            if attempt < retries:
                delay = backoff_factor * (2 ** attempt)
                logger.info(f"[{self.service_name}] Retrying {method} {url} in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
        raise Exception(f"[{self.service_name}] Failed to complete {method} {url} after {retries + 1} attempts.")

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        return await self._request("POST", path, json=json)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
