"""Measure round-trip latency for Voice -> GPU1 -> GPU0 -> Voice."""
from __future__ import annotations

import time


def main() -> None:
    start = time.perf_counter()
    # Placeholder: integrate with audio gateway and sovereign bridge.
    time.sleep(0.01)
    end = time.perf_counter()
    print(f"Simulated RTT: {(end - start) * 1000:.2f} ms")


if __name__ == "__main__":
    main()
