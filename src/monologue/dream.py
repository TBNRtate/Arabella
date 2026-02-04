"""Random intent generator using VAD state."""
from __future__ import annotations

import random

from src.memory.vad_engine import VadState


class Dreamer:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)

    def propose_task(self, vad_state: VadState) -> str:
        if vad_state.arousal > 0.5:
            return "Audit system performance and prioritize cooling optimizations."
        if vad_state.valence < -0.2:
            return "Review error logs and apply stability patches."
        return "Optimize resource allocation for idle services."
