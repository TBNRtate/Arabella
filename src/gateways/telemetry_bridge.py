"""Telemetry bridge that maps hardware stats to VAD signals."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import psutil


@dataclass
class TelemetrySnapshot:
    vram_gb: Optional[float]
    cpu_temp_c: Optional[float]
    timestamp: str


class TelemetryBridge:
    def __init__(self) -> None:
        self.last_snapshot: Optional[TelemetrySnapshot] = None

    def capture(self) -> TelemetrySnapshot:
        temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
        cpu_temp = None
        if temps:
            for entries in temps.values():
                if entries:
                    cpu_temp = entries[0].current
                    break

        snapshot = TelemetrySnapshot(
            vram_gb=None,
            cpu_temp_c=cpu_temp,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        self.last_snapshot = snapshot
        return snapshot
