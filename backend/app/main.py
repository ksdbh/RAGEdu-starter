import logging
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .auth import get_current_user, get_current_user_optional, require_role, User

logger = logging.getLogger("app.main")

app = FastAPI(title="RAGEdu API (scaffold)")

# Allow CORS for local dev (frontend dev server). In production tighten this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/whoami")
async def whoami(user: User = Depends(get_current_user)):
    """Return the authenticated user's information. Requires a valid token."""
    return {"sub": user.sub, "username": user.username, "email": user.email, "role": user.role}


@app.get("/protected/auth")
async def protected_auth(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.username}, you are authenticated as {user.role}"}


@app.get("/protected/student")
async def protected_student(user: User = Depends(require_role("student"))):
    return {"message": f"Welcome student {user.username}!"}


@app.get("/protected/professor")
async def protected_professor(user: User = Depends(require_role("professor"))):
    return {"message": f"Welcome professor {user.username}!"}


# Example endpoint which allows optional authentication and shows different views
@app.get("/greeting")
async def greeting(user: User | None = Depends(get_current_user_optional)):
    if not user:
        return {"message": "Hello anonymous visitor! Please login to access more features."}
    if user.role == "student":
        return {"message": f"Hey student {user.username} — check your assignments."}
    if user.role == "professor":
        return {"message": f"Hello professor {user.username} — manage your course here."}
    return {"message": f"Hello {user.username} ({user.role})"}
