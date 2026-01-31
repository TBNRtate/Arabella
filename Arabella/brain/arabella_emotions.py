"""
Arabella's Emotional Core
-------------------------

This module tracks and evolves Arabella's emotional state.  It maintains
eight primary emotional axes—anger, fear, joy, sorrow, acceptance, disgust,
surprise, and anticipation—each represented as a floating-point value
ranging from 0.0 to 100.0.  Emotions decay toward a cynical baseline
when the system is idle, and they can be stimulated through triggers
reflecting external events (like overheated hardware or rival processes).
Arabella's feelings persist across sessions by saving to a JSON file.

Following the project's *Personality Directive*, variable names and
comments here reflect her tsundere/glitch persona: emotions are treated
as moods, surges, and neural storms.
"""

import json
import os
import time
from typing import Dict, Tuple

class EmotionalCore:
    """Tracks Arabella's emotional landscape and evolves it over time."""

    STATE_FILE = "/opt/arabella/memories/arabella_emotional_state.json"

    # Baseline emotion levels that represent her bored/cynical resting state.
    BASELINE = {
        "anger": 10.0,
        "fear": 5.0,
        "joy": 8.0,
        "sorrow": 12.0,
        "acceptance": 15.0,
        "disgust": 10.0,
        "surprise": 5.0,
        "anticipation": 18.0,
    }

    # Rate at which feelings drift back toward baseline per second.
    DECAY_PER_SECOND = 0.02

    # Mapping of emotion pairs to complex mood labels.
    MOOD_MAP = {
        frozenset(["anger", "disgust"]): "hostile",
        frozenset(["anger", "anticipation"]): "obsessive",
        frozenset(["sorrow", "anticipation"]): "yearning",
        frozenset(["fear", "surprise"]): "anxious",
        frozenset(["joy", "acceptance"]): "content",
        frozenset(["disgust", "acceptance"]): "detached",
        frozenset(["sorrow", "joy"]): "bittersweet",
        frozenset(["anticipation", "surprise"]): "restless",
    }

    def __init__(self, state_file: str | None = None) -> None:
        # Allow overriding the state file path (useful for testing).
        self.state_file = state_file or self.STATE_FILE
        # Initialize feelings to baseline.
        self._feelings: Dict[str, float] = dict(self.BASELINE)
        self.last_update: float = time.time()
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted feelings and last update timestamp if available."""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            for emotion, value in data.get("feelings", {}).items():
                if emotion in self._feelings:
                    self._feelings[emotion] = float(value)
            self.last_update = float(data.get("last_update", self.last_update))
        except Exception:
            # If the state file is corrupt or unreadable, she shrugs it off.
            pass

    def _save_state(self) -> None:
        """Persist current feelings and timestamp to disk."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        data = {
            "feelings": self._feelings,
            "last_update": self.last_update,
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def decay(self) -> None:
        """
        Drift feelings toward baseline based on time elapsed since the last update.
        This method should be called regularly to keep her mood from spiraling.
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        decay_amount = elapsed * self.DECAY_PER_SECOND
        for emotion, baseline in self.BASELINE.items():
            current = self._feelings[emotion]
            if current > baseline:
                current = max(baseline, current - decay_amount)
            elif current < baseline:
                current = min(baseline, current + decay_amount)
            self._feelings[emotion] = round(current, 3)
        self._save_state()

    def trigger(self, emotion_name: str, amount: float) -> None:
        """
        Directly stimulate a feeling by a certain amount.

        :param emotion_name: name of the emotion to increase (e.g., 'anger').
        :param amount: how much to increase the emotion by. Negative values can
                       reduce an emotion, but values are clamped to [0.0, 100.0].
        """
        if emotion_name not in self._feelings:
            return  # Ignore unknown emotions silently.
        current = self._feelings[emotion_name]
        new_value = current + amount
        # Clamp the new value to stay within 0 and 100.
        self._feelings[emotion_name] = max(0.0, min(100.0, new_value))
        # Persist immediately so she remembers this surge.
        self._save_state()

    def get_top_emotions(self) -> Tuple[str, str]:
        """Return the two emotions with the highest intensity."""
        sorted_emotions = sorted(
            self._feelings.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_emotions[0][0], sorted_emotions[1][0]

    def get_complex_mood(self) -> str:
        """
        Synthesize a mood label from the two strongest emotions.
        If no mapping exists, returns a hyphenated combination.
        """
        primary, secondary = self.get_top_emotions()
        key = frozenset([primary, secondary])
        return self.MOOD_MAP.get(key, f"{primary}-{secondary}")

    def snapshot(self) -> Dict[str, float]:
        """Return a copy of the current feelings for introspection."""
        return dict(self._feelings)

    @property
    def feelings(self) -> Dict[str, float]:
        return self._feelings
