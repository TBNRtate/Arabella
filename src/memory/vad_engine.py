"""SQLite-backed VAD engine with decay logic."""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VadState:
    valence: float
    arousal: float
    dominance: float
    updated_at: str


class VadEngine:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vad_state (
                    id INTEGER PRIMARY KEY,
                    valence REAL NOT NULL,
                    arousal REAL NOT NULL,
                    dominance REAL NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get_state(self) -> VadState:
        with sqlite3.connect(self.database_path) as conn:
            row = conn.execute(
                "SELECT valence, arousal, dominance, updated_at FROM vad_state ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row:
            return VadState(*row)
        return VadState(valence=0.0, arousal=0.0, dominance=0.0, updated_at=self._now())

    def update_state(self, valence: float, arousal: float, dominance: float) -> VadState:
        state = VadState(valence=valence, arousal=arousal, dominance=dominance, updated_at=self._now())
        with sqlite3.connect(self.database_path) as conn:
            conn.execute(
                "INSERT INTO vad_state (valence, arousal, dominance, updated_at) VALUES (?, ?, ?, ?)",
                (state.valence, state.arousal, state.dominance, state.updated_at),
            )
            conn.commit()
        return state

    def decay(self, hours: float, decay_rate: float = 0.1) -> VadState:
        state = self.get_state()
        factor = max(0.0, 1.0 - decay_rate * hours)
        return self.update_state(
            valence=state.valence * factor,
            arousal=state.arousal * factor,
            dominance=state.dominance * factor,
        )

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
