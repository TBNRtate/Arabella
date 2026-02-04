"""Lightweight IPC channel for cross-service coordination."""
from __future__ import annotations

import json
from dataclasses import dataclass
from queue import SimpleQueue
from typing import Any, Optional


@dataclass
class Event:
    topic: str
    payload: dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._queue: SimpleQueue[Event] = SimpleQueue()

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        self._queue.put(Event(topic=topic, payload=payload))

    def poll(self) -> Optional[Event]:
        if self._queue.empty():
            return None
        return self._queue.get()

    def export_json(self, event: Event) -> str:
        return json.dumps({"topic": event.topic, "payload": event.payload})
