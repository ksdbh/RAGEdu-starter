import os
from typing import List, Dict, Optional, Protocol


class LLMProvider(Protocol):
    """Minimal interface for LLM providers used by the RAG API.

    Implementations must provide a synchronous generate method that accepts a
    prompt string and an optional list of context blocks and returns a string
    reply. The exact shape of context blocks is intentionally flexible (dicts)
    to keep the scaffold simple and testable.
    """

    def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        ...


class StubLLM:
    """A deterministic, local stub LLM useful for testing and local dev.

    Behavior:
    - Returns an answer that echoes the prompt.
    - Produces deterministic citations for each context block in the form
      [title:page]. If a context block lacks title/page those fields are
      replaced with 'unknown' or '?'.
    - Includes short excerpts from each context block (first 120 chars)
      so responses are inspectable in tests.
    """

    def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        ctx = context or []
        # Build deterministic citation tokens [title:page]
        citations = []
        excerpts = []
        for i, block in enumerate(ctx):
            title = str(block.get("title") or "unknown")
            page = str(block.get("page") if block.get("page") is not None else "?")
            citations.append(f"[{title}:{page}]")

            content = block.get("content") or block.get("text") or ""
            # deterministic excerpt length
            excerpt = content.replace("\n", " ")[:120]
            excerpts.append(f"- {title} (page {page}): {excerpt}")

        citation_str = ", ".join(citations) if citations else ""
        excerpt_str = "\n".join(excerpts) if excerpts else ""

        # Deterministic answer form
        answer_parts = [f"Stub answer to: {prompt}"]
        if citation_str:
            answer_parts.append(f"Citations: {citation_str}")
        if excerpt_str:
            answer_parts.append("Context excerpts:\n" + excerpt_str)

        return "\n\n".join(answer_parts)


class BedrockLLM:
    """Skeleton class for an AWS Bedrock-backed LLM provider.

    This is intentionally a minimal placeholder: it defines the same public
    generate() signature as other providers but does not make any real network
    calls. When integrating with Bedrock you should expand this class to
    accept credentials/clients, handle retries, timeouts and streaming, and
    map Bedrock responses to the common generate(...) return value.
    """

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        # TODO: accept and configure a real Bedrock client (boto3 / botocore / aws-sdk).
        # Keep model_id/region so callers can pass env-specific config later.
        self.model_id = model_id or os.environ.get("BEDROCK_MODEL_ID")
        self.region = region or os.environ.get("AWS_REGION")

    def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Generate a response using Bedrock.

        TODO: Implement actual Bedrock invocations. For now raise NotImplementedError
        so the scaffold remains safe unless someone intentionally wires Bedrock.
        """
        raise NotImplementedError("BedrockLLM.generate is not implemented in the scaffold")


# Factory

_llm_instance: Optional[LLMProvider] = None


def get_llm() -> LLMProvider:
    """Return a configured LLM provider instance.

    Configuration is selected via the BACKEND_LLM_PROVIDER environment variable:
      - "stub" (default): returns StubLLM
      - "bedrock": returns BedrockLLM (skeleton – NotImplementedError on generate)

    The function caches a single provider instance for the process lifetime to
    avoid expensive re-initialization.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    provider = os.environ.get("BACKEND_LLM_PROVIDER", "stub").lower()
    if provider == "bedrock":
        _llm_instance = BedrockLLM()
    else:
        _llm_instance = StubLLM()
    return _llm_instance
