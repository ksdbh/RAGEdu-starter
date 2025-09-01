from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RAGEdu API")

class Question(BaseModel):
    query: str
    course_id: str | None = None
    top_k: int = 5

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/rag/answer")
def rag_answer(q: Question):
    # TODO: wire OpenSearch retrieval + Bedrock LLM
    return {
        "answer": "This is a stub. Retrieval and LLM will be wired in subsequent PRs.",
        "citations": [],
        "metadata": {"top_k": q.top_k, "course_id": q.course_id}
    }
