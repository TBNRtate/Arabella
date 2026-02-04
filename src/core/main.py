"""Arabella core entry point."""
from __future__ import annotations

import asyncio
import logging

from src.core.config import load_config
from src.core.event_bus import EventBus
from src.core.sovereign_bridge import SovereignBridge


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arabella.core")


async def main() -> None:
    config = load_config()
    bus = EventBus()
    bridge = SovereignBridge(config=config, event_bus=bus)

    logger.info("Starting SovereignBridge loop")
    await bridge.run()


if __name__ == "__main__":
    asyncio.run(main())
