"""Configuration loader for Arabella core."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class HardwareConfig:
    gpu0_uuid: str
    gpu1_uuid: str
    gpu0_pci: str
    gpu1_pci: str


@dataclass(frozen=True)
class ServiceConfig:
    letta_endpoint: str
    openclaw_endpoint: str
    personaplex_endpoint: str


@dataclass(frozen=True)
class AppConfig:
    root_user: str
    cuda_visible_devices: str
    hardware: HardwareConfig
    services: ServiceConfig


def load_config(env_path: Path | None = None) -> AppConfig:
    if env_path is None:
        env_path = Path(".env")
    load_dotenv(env_path)

    root_user = os.getenv("ARABELLA_ROOT_USER", "")
    cuda_visible_devices = os.getenv("CUDA_VISIBLE_DEVICES", "0,1")

    hardware = HardwareConfig(
        gpu0_uuid=os.getenv("GPU0_UUID", ""),
        gpu1_uuid=os.getenv("GPU1_UUID", ""),
        gpu0_pci=os.getenv("GPU0_PCI_ADDR", ""),
        gpu1_pci=os.getenv("GPU1_PCI_ADDR", ""),
    )

    services = ServiceConfig(
        letta_endpoint=os.getenv("LETTA_ENDPOINT", "http://localhost:8283"),
        openclaw_endpoint=os.getenv("OPENCLAW_ENDPOINT", "http://localhost:8080"),
        personaplex_endpoint=os.getenv("PERSONAPLEX_ENDPOINT", "webrtc://localhost:9000"),
    )

    return AppConfig(
        root_user=root_user,
        cuda_visible_devices=cuda_visible_devices,
        hardware=hardware,
        services=services,
    )
