# backend/app/rag.py
from __future__ import annotations

from typing import Any, Dict, Protocol


class OpenSearchClientInterface(Protocol):
    """
    Minimal interface expected by tests for an OpenSearch client.

    Implementations should provide:
      - index(index: str, document: Dict[str, Any]) -> Any
      - search(index: str, body: Dict[str, Any]) -> Dict[str, Any]
    """

    def index(self, index: str, document: Dict[str, Any]) -> Any: ...
    def search(self, index: str, body: Dict[str, Any]) -> Dict[str, Any]: ...