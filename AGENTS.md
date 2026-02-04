# Arabella AGENTS Log

## Phase 0
- Initialized IO Standard schemas (`io_standard.json`).
- Implemented GPU-1 audio gateway stub with Priority Interruption flag handling.
- Implemented GPU-0 file orchestrator with atomic write semantics.

## Phase 0 (Revision)
- Added repository scaffolding (config/, scripts/, src/, data/) and deployment docs.
- Moved gateway stubs into src/gateways and added telemetry bridge.
- Added core orchestration stubs (config, event bus, sovereign bridge).
- Added memory, monologue, and model interface stubs.

## Phase 0 (Deployment Fixes)
- Rewrote setup_env.sh with Debian 12 CUDA/NVIDIA install steps and torch CUDA 12 install.
- Implemented DeepSeek LLM wrapper using llama-cpp-python.

## Phase 0 (Interaction Mode)
- Added interaction_mode to Sense-Packet schema.
- Routed SovereignBridge output based on duplex voice vs text chat modes.
- Added system prompt modifiers for text chat, voice call, and silent command modes.

## Phase 0 (Dry Run Suite)
- Added scripts/audit_repo.py for file, JSON, syntax, and import checks.
- Added GitHub Actions sanity_check workflow to run the audit.
