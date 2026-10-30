"""Keep request logs isolated from developer files for every API test."""
import pytest


@pytest.fixture(autouse=True)
def isolated_request_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("RAGEDU_MODE", "demo")
    from backend.app import main
    monkeypatch.setattr(main, "LOG_PATH", tmp_path / "app.json")
