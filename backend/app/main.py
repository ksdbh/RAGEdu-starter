from fastapi import FastAPI

app = FastAPI()

# Existing app setup (routers, middleware, etc.) may already live in this file.
# To ensure the new /rag endpoints are registered, we try to import the rag module.
# We keep this in a try/except to avoid breaking environments where the module
# might not be available during partial scaffolding operations.
try:
    # Import the module so its APIRouter (router) can be included.
    # The rag module lives at backend/app/rag.py -> package import .rag
    from . import rag as _rag_module

    if hasattr(_rag_module, "router"):
        app.include_router(_rag_module.router)
except Exception:
    # If anything goes wrong (import error, etc.) we log to the standard logger
    # but do not fail app import. This keeps the scaffold resilient in CI/dev.
    import logging

    logging.getLogger(__name__).exception("Failed to include rag router (safe to ignore in some contexts)")
