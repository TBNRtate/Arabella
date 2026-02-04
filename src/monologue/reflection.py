"""Idle-time reflection daemon."""
from __future__ import annotations

import time

from src.core.event_bus import EventBus
from src.memory.letta_client import LettaClient


class ReflectionDaemon:
    def __init__(self, event_bus: EventBus, letta: LettaClient) -> None:
        self.event_bus = event_bus
        self.letta = letta
        self.last_interaction = time.monotonic()

    def touch(self) -> None:
        self.last_interaction = time.monotonic()

    def maybe_reflect(self) -> None:
        if time.monotonic() - self.last_interaction < 20 * 60:
            return
        memory = self.letta.archival_memory_search("Identify a forgotten promise to the root user")
        self.event_bus.publish("reflection", {"memory": memory})
        self.last_interaction = time.monotonic()
