"""Vector DB wrapper for retrieving contextual memory."""
from __future__ import annotations

from typing import Any


class ChromaClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def query(self, text: str) -> dict[str, Any]:
        # Placeholder for actual vector search.
        return {"query": text, "results": []}
