# Add a local course

A local course is created when you ingest a text PDF with its course ID:

```sh
# From repository root, activated backend environment
python -m backend.app.ingest path/to/lecture.pdf --course CS101
```

Start the API with `RAGEDU_MODE=local`; reload home to select the course and ask a keyword-based question. Index more PDFs under the same ID to extend the corpus. Reimporting identical bytes is idempotent; changed bytes form a new document. The local index does not yet manage versions/deletions or enforce student access rights.

See [Local PDF → course search](local-course-search.md) for index paths, parsing limits, real citations, and errors. The separate `CourseSyllabusStore`/quest helpers are not involved in this flow.
