# Backend endpoints

Current implementation: `backend/app/main.py`. Updated October 30, 2026.

| Method/path | Behavior |
| --- | --- |
| `GET /health` | Always `{"status":"ok"}`; caller-independent. |
| `GET /whoami` | Token-derived mock identity; missing/invalid credentials return 401. |
| `GET /protected/student` | Requires student role; 403 for another valid role. |
| `GET /protected/professor` | Requires professor role; 403 for another valid role. |
| `GET /protected/auth` | Any valid mock identity. |
| `GET /greeting` | Anonymous or token-derived role greeting. |
| `GET /rag/status` | Explicit local/demo mode and indexed course counts. |
| `POST /rag/answer` | Simulated demo or course-filtered keyword/source-excerpt response. See [Q&A contract](rag-api.md). |
| `POST /quiz/generate` | Prototype questions based on `query`; `num_questions` is clamped to 1..20. No actual course retrieval. |
| `POST /quiz/submit` | Requires string `quiz_id`, string `user_id`, nonempty `results`; counts client-supplied `correct` flags. Does not persist scores. |

Local mock tokens include `student_token`, `prof_token`, and `mock:alice|professor`. Cognito verification is a placeholder. The study and quiz endpoints do not enforce course authorization. There is no upload/document-serving/course-management HTTP API; use the [local ingestion CLI](../guides/local-course-search.md) for the current offline path.
