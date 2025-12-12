# app/security/dependencies.py
from typing import Optional
from fastapi import Header, HTTPException, status
from loguru import logger

from app.security.token_util import TokenUtil
from app.security.models import UserDetails


async def get_current_user(
    authorization: Optional[str] = Header(None, description="JWT token in format: Bearer <token>")
) -> Optional[UserDetails]:
    """
    FastAPI dependency to extract and decode JWT token from Authorization header.

    This dependency is OPTIONAL - it returns None if no token is provided.
    Use this for endpoints that support both authenticated and unauthenticated access.

    Args:
        authorization: Authorization header value

    Returns:
        UserDetails if token is valid, None if no token provided

    Raises:
        HTTPException: 401 if token is invalid or cannot be decoded
    """
    if not authorization:
        return None

    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization[7:]  # Remove "Bearer " prefix
        else:
            token = authorization

        # Decode token and extract user details
        user_details = TokenUtil.decode_token(token)
        logger.info(f"Authenticated user: {user_details.email} (ID: {user_details.user_id})")
        return user_details

    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_authenticated_user(
    authorization: Optional[str] = Header(None, description="JWT token in format: Bearer <token>")
) -> UserDetails:
    """
    FastAPI dependency to require authentication.

    This dependency is REQUIRED - it raises 401 if no token is provided.
    Use this for endpoints that require authentication.

    Args:
        authorization: Authorization header value

    Returns:
        UserDetails object

    Raises:
        HTTPException: 401 if no token provided or token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_details = await get_current_user(authorization)
    if not user_details:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_details


def require_roles(*required_roles: str):
    """
    Factory function to create a role-checking dependency.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: UserDetails = Depends(require_roles("Admin"))
        ):
            ...

    Args:
        required_roles: One or more role names required

    Returns:
        Dependency function that checks roles
    """
    async def role_checker(
        user: UserDetails = Header(alias="Authorization", default=None)
    ) -> UserDetails:
        # First authenticate the user
        authenticated_user = await require_authenticated_user(user)

        # Check if user has any of the required roles
        user_roles = set(authenticated_user.roles)
        required_roles_set = set(required_roles)

        if not user_roles.intersection(required_roles_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role(s): {', '.join(required_roles)}"
            )

        return authenticated_user

    return role_checker
