import os

from backend.app.llm.adapter import StubLLM, get_llm


def test_stub_llm_basic_citation_and_excerpt():
    llm = StubLLM()
    prompt = "Explain photosynthesis"
    context = [
        {"title": "Chapter 1", "page": 2, "content": "Photosynthesis is the process by which plants convert light into chemical energy."},
        {"title": "Appendix", "page": 99, "text": "Light reactions occur in the thylakoid membranes."},
    ]

    out = llm.generate(prompt, context)
    # Should echo the prompt
    assert "Stub answer to: Explain photosynthesis" in out
    # Should contain deterministic citations
    assert "[Chapter 1:2]" in out
    assert "[Appendix:99]" in out
    # Should include excerpts from provided content
    assert "Photosynthesis is the process" in out
    assert "Light reactions occur" in out


def test_get_llm_env_default_and_override(tmp_path, monkeypatch):
    # default should be StubLLM
    monkeypatch.delenv("BACKEND_LLM_PROVIDER", raising=False)
    llm = get_llm()
    assert isinstance(llm, StubLLM)

    # override to unknown provider should fallback to stub
    monkeypatch.setenv("BACKEND_LLM_PROVIDER", "something_unknown")
    # Clear cached instance by reloading the factory module instance variable
    # Simpler: import a fresh get_llm via module reload - but here we just delete attr if present
    import importlib
    import backend.app.llm.adapter as adapter_mod

    # reset internal cache
    if hasattr(adapter_mod, "_llm_instance"):
        adapter_mod._llm_instance = None

    llm2 = adapter_mod.get_llm()
    assert isinstance(llm2, StubLLM)
