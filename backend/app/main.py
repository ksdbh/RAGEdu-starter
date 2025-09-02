from fastapi import FastAPI

# Ensure a stable top-level FastAPI app and a consistent /health endpoint.
# If another part of the file or project already defines `app`, keep it and
# attach the health route to the existing app. Otherwise create one.
try:
    app  # type: ignore[name-defined]
except NameError:
    app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}
