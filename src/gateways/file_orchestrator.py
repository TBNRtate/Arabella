"""OpenClaw file orchestration with atomic write semantics."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Iterable


@dataclasses.dataclass(frozen=True)
class FileDescriptor:
    name: str
    mime: str
    size_bytes: int
    sha256: str
    uri: str


class FileOrchestrator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def atomic_write(self, relative_path: Path, data: bytes) -> FileDescriptor:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp_file:
            tmp_file.write(data)
            tmp_path = Path(tmp_file.name)

        os.replace(tmp_path, target)
        sha256 = hashlib.sha256(data).hexdigest()

        return FileDescriptor(
            name=target.name,
            mime="application/octet-stream",
            size_bytes=len(data),
            sha256=sha256,
            uri=str(target),
        )

    def read_file(self, relative_path: Path) -> bytes:
        target = self.root / relative_path
        return target.read_bytes()

    def build_sense_packet(
        self,
        packet_id: str,
        gpu: int,
        modalities: Iterable[str],
        files: Iterable[FileDescriptor],
    ) -> dict:
        return {
            "packet_id": packet_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": {"node": f"gpu-{gpu}", "gpu": gpu},
            "modalities": list(modalities),
            "priority": "normal",
            "payload": {
                "files": [dataclasses.asdict(file) for file in files],
            },
        }

    def write_metadata(self, descriptor: FileDescriptor) -> Path:
        metadata_path = self.root / f"{descriptor.name}.json"
        metadata_path.write_text(json.dumps(dataclasses.asdict(descriptor), indent=2))
        return metadata_path


__all__ = ["FileDescriptor", "FileOrchestrator"]
