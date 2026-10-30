# Course Q&A API

`GET /rag/status` reports explicit `demo` or `local` mode. Local mode lists indexed course IDs/document/passage counts and identifies `retrieval: "keyword"`, `generation: "source_excerpts"`.

`POST /rag/answer` accepts:

```json
{"query": "What does Dijkstra require?", "course_id": "CS101", "top_k": 5}
```

Use exactly one of `query` or its older `question` alias. Text is nonempty and at most 1000 characters; `top_k` is a strict integer 1..20 (default 5). `course_id` is required in local mode and scopes all retrieval. There is no `max_tokens` generation option in this endpoint.

The response contains `answer`, `citations`, and `metadata`. Local results quote actual matching passages with title/source/page/snippet/document_id/chunk_id/course_id/section/score. Metadata identifies the mode, retrieval/generation type, selected course, top_k, score, and `ok`/`insufficient_evidence` status. Keyword scores are not answer-correctness probabilities.

No matches or missing corpus: insufficient evidence and no citations. Corrupt index or invalid runtime configuration: HTTP 503, not fake sources. Demo mode deliberately uses sample contexts and a simulated answer. No model/API calls occur in either mode.

These study endpoints are local-development endpoints without course authorization. See the [local search guide](../guides/local-course-search.md) for complete storage and security boundaries, and the [handoff](../changelog.md) for verification.
