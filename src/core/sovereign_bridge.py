"""Cognitive router that merges Sense-Packets with VAD state."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from src.core.config import AppConfig
from src.core.event_bus import EventBus
from src.memory.vad_engine import VadEngine
from src.models.deepseek_llm import DeepSeekLLM
from src.models.personaplex_tts import PersonaPlexTTS, VoiceControl


logger = logging.getLogger("arabella.sovereign_bridge")


@dataclass
class SensePacket:
    packet_id: str
    payload: dict[str, Any]
    interaction_mode: str = "text_chat"


class SovereignBridge:
    def __init__(self, config: AppConfig, event_bus: EventBus) -> None:
        self.config = config
        self.event_bus = event_bus
        self.vad_engine = VadEngine(database_path="data/vad_history.sqlite")
        self.llm = DeepSeekLLM(model_path="models/deepseek.gguf")
        self.tts = PersonaPlexTTS(endpoint=self.config.services.personaplex_endpoint)

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

    def route_response(self, sense_packet: SensePacket, prompt: str) -> dict[str, Any]:
        if sense_packet.interaction_mode == "duplex_voice":
            system_prompt = (
                "MODE: VOICE CALL. Keep responses under 2 sentences. "
                "No markdown. No code blocks. Be conversational."
            )
            response = self.llm.generate(f"{system_prompt}\n{prompt}")
            control = VoiceControl(pitch=1.0, speed=1.0, tone="neutral")
            self.tts.synthesize(response.content, control)
            return {"mode": "duplex_voice", "routed_to": "PersonaPlexTTS"}

        system_prompt = "MODE: TEXT CHAT. formatting allowed. Full detail."
        response = self.llm.generate(f"{system_prompt}\n{prompt}")
        return {"mode": "text_chat", "text": response.content, "thought": response.thought}
