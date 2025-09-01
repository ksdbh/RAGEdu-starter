import os
import logging
from typing import Dict, Optional, List, Callable

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger("auth")

security = HTTPBearer(auto_error=False)


class User(BaseModel):
    sub: str
    username: str
    email: Optional[str] = None
    role: str
    roles: List[str] = []


class CognitoClientInterface:
    """Minimal interface for a Cognito verification client.

    Implementations should provide verify_token(token) -> dict-like user info
    or raise an HTTPException(401) on invalid tokens.
    """

    def verify_token(self, token: str) -> Dict[str, str]:
        raise NotImplementedError()


class MockCognitoClient(CognitoClientInterface):
    """A lightweight mock client for local development.

    Behavior (deliberately simple for scaffolding/testability):
    - token "student_token" -> role: student
    - token "prof_token" -> role: professor
    - token "admin_token" -> role: professor (alias)
    - otherwise raise HTTPException(401)
    """

    def verify_token(self, token: str) -> Dict[str, str]:
        logger.debug("Mock verify_token called with token=%s", token)
        if not token:
            raise HTTPException(status_code=401, detail="Missing auth token")

        if token == "student_token":
            return {
                "sub": "mock-student-1",
                "username": "student1",
                "email": "student1@example.com",
                "role": "student",
            }
        if token == "prof_token" or token == "admin_token":
            return {
                "sub": "mock-prof-1",
                "username": "prof1",
                "email": "prof1@example.com",
                "role": "professor",
            }

        # simple acceptance: if token startswith "mock:" treat as student with name after colon
        if token.startswith("mock:"):
            _, name_role = token.split(":", 1)
            parts = name_role.split("|")
            username = parts[0]
            role = parts[1] if len(parts) > 1 else "student"
            return {"sub": f"mock-{username}", "username": username, "email": f"{username}@example.com", "role": role}

        raise HTTPException(status_code=401, detail="Invalid token (mock)")


class RealCognitoClient(CognitoClientInterface):
    """Skeleton for a real Cognito client.

    This is intentionally a minimal placeholder: a full implementation would
    fetch JWKS, verify JWT signature/claims and map Cognito groups -> roles.
    For now it raises NotImplementedError unless you wire it to a production
    library.
    """

    def __init__(self, user_pool_id: Optional[str] = None, region: Optional[str] = None):
        # In a complete implementation you would load keys/jwks and cache them.
        self.user_pool_id = user_pool_id
        self.region = region
        logger.info("RealCognitoClient initialized user_pool=%s region=%s", user_pool_id, region)

    def verify_token(self, token: str) -> Dict[str, str]:
        raise HTTPException(status_code=501, detail="Real Cognito verification is not configured in this scaffold")


# Factory for selecting client based on environment

_cognito_client: Optional[CognitoClientInterface] = None


def get_cognito_client() -> CognitoClientInterface:
    global _cognito_client
    if _cognito_client is not None:
        return _cognito_client

    # If environment indicates Cognito is configured, instantiate real client
    user_pool = os.environ.get("COGNITO_USER_POOL_ID")
    region = os.environ.get("AWS_REGION")
    if user_pool:
        logger.info("Cognito user pool configured; using RealCognitoClient")
        _cognito_client = RealCognitoClient(user_pool_id=user_pool, region=region)
    else:
        logger.info("No Cognito configuration found; using MockCognitoClient for local dev")
        _cognito_client = MockCognitoClient()
    return _cognito_client


# FastAPI dependency helpers

def _extract_token(creds: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
    if not creds:
        return None
    # creds.credentials contains the token portion after "Bearer"
    return creds.credentials


def get_current_user(creds: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Require a valid token and return a User model. Raises 401 if not valid."""
    token = _extract_token(creds)
    client = get_cognito_client()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    info = client.verify_token(token)
    role = info.get("role") or "student"
    roles = [role]
    return User(sub=info.get("sub", ""), username=info.get("username", ""), email=info.get("email"), role=role, roles=roles)


def get_current_user_optional(creds: HTTPAuthorizationCredentials = Security(security)) -> Optional[User]:
    """Optional current user: returns None when there's no token instead of raising."""
    token = _extract_token(creds)
    if not token:
        return None
    client = get_cognito_client()
    try:
        info = client.verify_token(token)
    except HTTPException:
        return None
    role = info.get("role") or "student"
    roles = [role]
    return User(sub=info.get("sub", ""), username=info.get("username", ""), email=info.get("email"), role=role, roles=roles)


def require_role(role: str) -> Callable:
    """Return a dependency that enforces the given role on the current user.

    Example usage in FastAPI route:
        @app.get("/foo")
        def foo(current_user: User = Depends(require_role("professor"))):
            ...
    """

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return current_user

    return _dependency
