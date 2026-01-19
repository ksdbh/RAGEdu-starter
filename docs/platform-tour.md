# Platform tour — EduRAG in plain language

<div class="hero-card">
  <div class="hero-inner">
    <p class="hero-eyebrow">Guided tour</p>
    <p class="hero-title">
      See how a PDF turns into an
      <span class="bubble"><span class="bubble-dot"></span>answer with citations</span>.
    </p>
    <p class="hero-tagline">
      This tour walks through the ingestion and query flows in plain language,
      so you can understand EduRAG even if you are new to RAG systems.
    </p>
  </div>
</div>

By the end you should understand what EduRAG does, how a document becomes an answer with citations, and where to look next in the docs.

## 1. The story in one paragraph

EduRAG ingests your course materials (slides, PDFs, syllabi), breaks them into small, searchable chunks, and stores them in a vector index. When someone asks a question, the backend finds the most relevant chunks, checks that they are good enough, and then asks an LLM to answer using only those chunks. The frontend shows the answer alongside citations so users can see exactly which pages were used.

## 2. What happens to a PDF?

Let’s follow a lecture PDF end to end.

<div class="step-grid">
  <div class="step-card">
    <div class="step-label">Step 1</div>
    <div class="step-title">Upload</div>
    <p>You place the PDF in a storage location (S3 or local) or point the
    ingest CLI at it.</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 2</div>
    <div class="step-title">Extract text</div>
    <p>A parser or Textract reads the PDF and emits text per page, giving us a
    clean text representation to work with.</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 3</div>
    <div class="step-title">Chunk and label</div>
    <p>EduRAG runs the text through a chunker that cleans whitespace, splits
    into smaller sections, and adds metadata like <code>course_id</code>,
    <code>page</code>, and a guessed <code>section</code> title.</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 4</div>
    <div class="step-title">Embed &amp; index</div>
    <p>Each chunk is converted into a numeric vector (an embedding) using a
    stub or real embedding model, then stored with metadata in OpenSearch so
    it can be retrieved by similarity later.</p>
  </div>
</div>

All of this logic is implemented in <code>backend/app/ingest.py</code>. See
[Ingestion](rag/ingestion.md) and [Chunking](rag/chunking.md) for more detail.

## 3. What happens when I ask a question?

Now imagine a student asks: “What topics are covered on Exam 1?”

<div class="step-grid">
  <div class="step-card">
    <div class="step-label">Step 1</div>
    <div class="step-title">Question arrives</div>
    <p>The frontend sends a POST request to <code>/rag/answer</code> with a JSON
    body like <code>{"query": "What topics are covered on Exam 1?", "top_k": 5}</code>.</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 2</div>
    <div class="step-title">Search for context</div>
    <p>A search client (stub or OpenSearch) finds the top-k chunks that best
    match the question. Each chunk has a score and metadata (title, page,
    snippet).</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 3</div>
    <div class="step-title">Guardrail check</div>
    <p>The
    <span class="bubble"><span class="bubble-dot"></span>guardrail</span>
    in <code>answer_query</code> looks at the highest score. If it is below a
    threshold (<code>min_similarity</code>), it <strong>does not</strong> call
    the LLM and instead returns a "need more sources" answer so the UI can
    prompt the user to add or refine content.</p>
  </div>
  <div class="step-card">
    <div class="step-label">Step 4</div>
    <div class="step-title">Prompt, LLM, and citations</div>
    <p>If scores are good, the backend constructs a grounded prompt (with a
    <code>Sources:</code> section), calls the LLM (stub or real), and returns an
    answer plus a list of citations with <code>{ title, page, snippet, score }</code>
    and a <code>metadata</code> object including <code>top_k</code>,
    <code>course_id</code>, and <code>confidence</code>.</p>
  </div>
</div>

See [RAG Overview](rag/overview.md) and [RAG Pipeline](rag.md) for the exact
behavior and contracts.

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
