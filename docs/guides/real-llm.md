# Guide: Wire a real LLM provider

This guide will describe how to replace the stub LLM with a real provider
(OpenAI, Bedrock, etc.), including:

- Selecting a model and configuring credentials.
- Updating the LLM adapter and environment variables.
- Validating prompts and responses with existing tests.
- Guardrail considerations when moving from stubs to real models.

For now, see `backend/app/llm/adapter.py` and the RAG docs for how the stub
provider is used.
