"""Client wrapper for Letta archival memory."""
from __future__ import annotations

import requests


class LettaClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint.rstrip("/")

    def archival_memory_search(self, query: str) -> dict:
        response = requests.post(f"{self.endpoint}/search", json={"query": query})
        response.raise_for_status()
        return response.json()

    def core_memory_update(self, payload: dict) -> dict:
        response = requests.post(f"{self.endpoint}/core", json=payload)
        response.raise_for_status()
        return response.json()
