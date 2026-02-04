#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "This script must be run as root." >&2
  exit 1
fi

echo "[Phase 1] Installing system dependencies (CUDA 12.x, NVIDIA drivers, Node.js, Python 3.11)."

apt-get update
apt-get install -y software-properties-common curl git build-essential

if [[ -f /etc/apt/sources.list.d/debian.sources ]]; then
  sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
else
  cat <<'EOF' > /etc/apt/sources.list
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF
fi

apt-get update
apt-get install -y nvidia-driver cuda-toolkit-12
apt-get install -y python3.11-venv python3-pip nodejs

if ! id -u arabella >/dev/null 2>&1; then
  useradd --system --shell /sbin/nologin --create-home arabella
fi

python3.11 -m pip install --upgrade pip
python3.11 -m pip install torch --index-url https://download.pytorch.org/whl/cu121
