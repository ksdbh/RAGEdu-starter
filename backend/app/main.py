from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict

from .llm.adapter import get_llm

app = FastAPI(title="RAGEdu API")


@app.get("/health")
def health():
    return {"status": "ok"}


class RAGRequest(BaseModel):
    prompt: str
    # context is a list of arbitrary dicts (e.g. {"title": ..., "page": ..., "content": ...})
    context: Optional[List[Dict]] = None


@app.post("/rag/answer")
def rag_answer(req: RAGRequest):
    """Return an answer produced by the configured LLM provider.

    This endpoint delegates to the LLM adapter factory get_llm(). The default
    provider is the local StubLLM which is safe to run in development.
    """
    llm = get_llm()
    try:
        ans = llm.generate(req.prompt, req.context)
    except Exception as e:
        # Surface LLM errors as 500 so the frontend / tests can handle them.
        raise HTTPException(status_code=500, detail=str(e))
    return {"answer": ans}


# Lightweight runner hint for local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
