"""Cognitive router that merges Sense-Packets with VAD state."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from src.core.config import AppConfig
from src.core.event_bus import EventBus
from src.memory.vad_engine import VadEngine


logger = logging.getLogger("arabella.sovereign_bridge")


@dataclass
class SensePacket:
    packet_id: str
    payload: dict[str, Any]


class SovereignBridge:
    def __init__(self, config: AppConfig, event_bus: EventBus) -> None:
        self.config = config
        self.event_bus = event_bus
        self.vad_engine = VadEngine(database_path="data/vad_history.sqlite")

    async def run(self) -> None:
        while True:
            event = self.event_bus.poll()
            if event:
                logger.info("Received event %s", event.topic)
            await asyncio.sleep(0.1)

    def merge_vad(self, sense_packet: SensePacket) -> dict[str, Any]:
        vad_state = self.vad_engine.get_state()
        merged = dict(sense_packet.payload)
        merged["vad"] = vad_state
        return merged
