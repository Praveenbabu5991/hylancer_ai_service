# app/security/token_util.py
import jwt
from typing import Optional
from loguru import logger
from uuid import UUID

from app.security.models import UserDetails


class TokenUtil:
    """
    Utility class for decoding JWT tokens.
    Mirrors the TokenUtil from Project Management Service.

    Note: This implementation only DECODES tokens without verification,
    matching the behavior of the Project Management Service.
    In production with API Gateway, token verification is handled by the gateway.
    """

    @staticmethod
    def decode_token(token: str) -> UserDetails:
        """
        Decode JWT token and extract user details.

        IMPORTANT: This does NOT verify the token signature or expiration.
        It only decodes the payload to extract user information.

        Args:
            token: JWT token string (without "Bearer " prefix)

        Returns:
            UserDetails object with user information

        Raises:
            jwt.DecodeError: If token cannot be decoded
            ValueError: If required claims are missing
        """
        try:
            # Decode without verification (matching Project Management Service behavior)
            # In production, API Gateway validates the token
            decoded = jwt.decode(token, options={"verify_signature": False})

            logger.info(f"Decoded JWT claims: {decoded.keys()}")

            return TokenUtil._extract_user_details(decoded)

        except jwt.DecodeError as e:
            logger.error(f"Failed to decode JWT token: {e}")
            raise
        except Exception as e:
            logger.error(f"Error extracting user details from token: {e}")
            raise

    @staticmethod
    def _extract_user_details(decoded: dict) -> UserDetails:
        """
        Extract user details from decoded JWT claims.

        Expected claims (matching AWS Cognito token structure):
        - sub: User ID (UUID)
        - email: User email
        - name: User name
        - cognito:groups: User roles/groups

        Args:
            decoded: Decoded JWT payload dictionary

        Returns:
            UserDetails object

        Raises:
            ValueError: If required claims are missing
        """
        try:
            # Extract user ID from 'sub' claim
            user_id_str = decoded.get("sub")
            if not user_id_str:
                raise ValueError("Missing 'sub' claim in JWT token")

            user_id = UUID(user_id_str)

            # Extract email
            email = decoded.get("email")
            if not email:
                raise ValueError("Missing 'email' claim in JWT token")

            # Extract name
            name = decoded.get("name", "")

            # Extract roles from cognito:groups
            roles = decoded.get("cognito:groups", [])
            if not isinstance(roles, list):
                roles = [roles] if roles else []

            user_details = UserDetails(
                user_id=user_id,
                email=email,
                name=name,
                roles=roles
            )

            logger.info(f"Extracted user details: user_id={user_id}, email={email}, roles={roles}")
            return user_details

        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Error parsing user details: {e}")
            raise ValueError(f"Invalid token claims: {e}")
