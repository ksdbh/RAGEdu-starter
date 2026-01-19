# Platform tour — EduRAG in plain language

This page is a guided tour of EduRAG for people who are new to the platform and to RAG-style systems.

By the end you should understand what EduRAG does, how a document becomes an answer with citations, and where to look next in the docs.

## 1. The story in one paragraph

EduRAG ingests your course materials (slides, PDFs, syllabi), breaks them into small, searchable chunks, and stores them in a vector index. When someone asks a question, the backend finds the most relevant chunks, checks that they are good enough, and then asks an LLM to answer using only those chunks. The frontend shows the answer alongside citations so users can see exactly which pages were used.

## 2. What happens to a PDF?

Let’s follow a lecture PDF end to end.

1. **Upload**
   - You place the PDF in a storage location (S3 or local) or point the ingest CLI at it.
2. **Extract text**
   - A parser or Textract reads the PDF and emits text per page.
3. **Chunk and label**
   - EduRAG runs the text through a chunker that:
     - Cleans up whitespace.
     - Splits pages into smaller sections.
     - Adds metadata like `course_id`, `page`, and a guessed `section` title.
4. **Embed**
   - Each chunk is converted into a numeric vector (an embedding) using a stub or real embedding model.
5. **Index**
   - Vectors and metadata are stored in OpenSearch so they can be retrieved by similarity later.

All of this logic is implemented in `backend/app/ingest.py`. See [Ingestion](rag/ingestion.md) and [Chunking](rag/chunking.md) for more detail.

## 3. What happens when I ask a question?

Now imagine a student asks: “What topics are covered on Exam 1?”

1. **Question arrives**
   - The frontend sends a POST request to `/rag/answer` with a JSON body like:

     ```json
     {
       "query": "What topics are covered on Exam 1?",
       "top_k": 5
     }
     ```

2. **Search for context**
   - A search client (stub or OpenSearch) finds the top-k chunks that best match the question.
   - Each chunk has a score and metadata (title, page, snippet).

3. **Guardrail check**
   - The RAG helper (`answer_query` in `backend/app/rag.py`) looks at the highest score.
   - If it is below a threshold (`min_similarity`), it **does not** call the LLM.
   - Instead, it returns a “need more sources” answer so the UI can prompt the user to add or refine content.

4. **Prompt building**
   - If the scores are good, the backend constructs a prompt that contains:
     - A short instruction.
     - Bullet points of the retrieved snippets.
     - The question.
     - A `Sources:` cue so the LLM knows to respect the retrieved context.

5. **LLM call**
   - In local dev, a deterministic stub LLM returns a test-friendly answer.
   - In production you can replace this with a real provider (OpenAI/Bedrock) behind the same interface.

6. **Answer and citations**
   - The backend returns:
     - An `answer` string that starts with `"ANSWER based on"`.
     - A list of `citations` with `{ title, page, snippet, score }`.
     - A small `metadata` object with `top_k`, `course_id`, and `confidence`.

See [RAG Overview](rag/overview.md) and [RAG Pipeline](rag.md) for the exact behavior and contracts.

## 4. How different people use EduRAG

=== "Students"

- Open the frontend.
- Ask questions about lectures, assignments, or the syllabus.
- Skim the citations to see which slides or pages the answer came from.

=== "Instructors"

- Decide which course materials to ingest.
- Use the ingest CLI or a future upload UI to feed PDFs/slides into the system.
- Generate practice questions or quizzes with `/quiz/generate`.

=== "Platform engineers"

- Treat this repo as a scaffold:
  - Backend: `backend/app/*` for routes, RAG logic, auth, and DB.
  - Frontend: `frontend/` for the minimal UI.
  - Infra: `infra/terraform` and Docker Compose files for a local / AWS-like stack.
- Swap stub components for real services carefully, guided by the tests.

=== "Ops / SRE"

- Monitor `/health` for liveness.
- Track RAG answer rates, error codes, and latency.
- Use the docs under `Operations`, `Security`, and `Environments` to plan out observability and IAM.

## 5. Where to go next

If you are **evaluating** EduRAG:

- Skim [Architecture](architecture.md) for the big picture.
- Look at [Getting Started](getting-started.md) to see how easy it is to run locally.

If you are **building on** EduRAG:

- Dive into [RAG Overview](rag/overview.md) and [RAG Pipeline](rag.md).
- Read [Backend endpoints](backend.md) to understand the API surface.
- Review [Testing](testing.md) so you know what behavior is guaranteed by the test suite.

If you are **operating** EduRAG:

- Start with [Environments](environments.md) and [Deployment](deployment.md).
- Then see [Operations](ops.md), [Monitoring](operations/monitoring.md), and [Runbooks](operations/runbooks.md).

---

!!! info "Where to edit"
    Source: `docs/platform-tour.md`  
    Related: `docs/index.md`, `docs/architecture.md`, `docs/rag/overview.md`
