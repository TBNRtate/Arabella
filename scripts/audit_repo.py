"""Repository dry-run verification suite."""
from __future__ import annotations

import sys
from pathlib import Path

# Force-add the project root directory to sys.path
# This ensures we can import 'src' modules regardless of where the script is run from
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import ast
import importlib
import json
from types import ModuleType
from typing import Iterable
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def check_manifest(paths: Iterable[str]) -> None:
    missing = [path for path in paths if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")


def validate_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def compile_python_sources(root: Path) -> None:
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
            ast.parse(source)
        except (SyntaxError, IndentationError) as exc:
            raise SyntaxError(f"Syntax error in {path}: {exc}") from exc


def _install_stub(module_name: str) -> None:
    sys.modules[module_name] = mock.Mock(spec=ModuleType)


def run_imports() -> None:
    for module_name in ("llama_cpp", "webrtcvad", "sounddevice"):
        if module_name not in sys.modules:
            _install_stub(module_name)

    importlib.import_module("src.core.main")
    importlib.import_module("src.gateways.audio_gateway")


def main() -> None:
    check_manifest(
        [
            "io_standard.json",
            "scripts/setup_env.sh",
            "src/core/sovereign_bridge.py",
            "CLAUDE.md",
        ]
    )
    validate_json(ROOT / "io_standard.json")
    compile_python_sources(ROOT / "src")
    run_imports()
    print("Dry run verification complete.")


if __name__ == "__main__":
    main()
