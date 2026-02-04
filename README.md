# Arabella

Arabella is a sovereign, cross-modal agent targeting a dual Tesla P100 Debian minimal host. This repository lays down the Phase 0-1 scaffolding for IO unification, gateway services, and core orchestration.

## Quick Start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Install dependencies (inside a virtual environment):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run Phase 1 setup (CUDA + drivers + system user):

```bash
bash scripts/setup_env.sh
```

4. Start the core service:

```bash
bash scripts/start_core.sh
```

## Layout

- `io_standard.json`: Canonical Sense-Packet schema.
- `src/`: Core services, gateways, memory, monologue, and model wrappers.
- `scripts/`: Deployment + maintenance scripts.
- `config/`: Prompts and systemd unit.
- `data/`: Persistent storage for Letta and VAD.

## Notes

- GPU 0 is reserved for DeepSeek-R1 inference.
- GPU 1 is reserved for PersonaPlex + Letta.
