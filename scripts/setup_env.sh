#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "This script must be run as root." >&2
  exit 1
fi

echo "[Phase 1] Starting System Setup for Arabella (Dual-P100 / Debian 12)"

# 1. Install System Dependencies
echo "[+] Updating apt and installing build tools..."
apt-get update
apt-get install -y software-properties-common curl git build-essential \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    cmake  # Required for llama-cpp build

# 2. Nvidia Drivers & CUDA 12 (Pascal Compatible)
echo "[+] Configuring Nvidia Drivers..."
if ! command -v nvidia-smi &> /dev/null; then
    if [[ -f /etc/apt/sources.list.d/debian.sources ]]; then
      sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
    else
      # Backup original if exists
      cp /etc/apt/sources.list /etc/apt/sources.list.bak 2>/dev/null || true
      cat <<'EOF' > /etc/apt/sources.list
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF
    fi
    apt-get update
    apt-get install -y nvidia-driver cuda-toolkit-12
else
    echo "[-] Nvidia drivers detected. Skipping install."
fi

# 3. Python 3.12 Installation (Build from Source for Debian Stability)
PYTHON_VER="3.12.2"
if ! command -v python3.12 &> /dev/null; then
    echo "[+] Python 3.12 not found. Building from source (this takes a few minutes)..."
    cd /tmp
    wget https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz
    tar -xf Python-${PYTHON_VER}.tgz
    cd Python-${PYTHON_VER}
    ./configure --enable-optimizations
    make -j$(nproc)
    make altinstall
    cd ..
    rm -rf Python-${PYTHON_VER}*
    echo "[+] Python 3.12 installed."
else
    echo "[-] Python 3.12 already installed."
fi

# 4. User Setup
echo "[+] Configuring user 'arabella'..."
if ! id -u arabella >/dev/null 2>&1; then
  useradd --system --shell /sbin/nologin --create-home arabella
fi

# 5. Virtual Environment
echo "[+] Creating Virtual Environment..."
# Run as the arabella user (or root if preferred, but usually we own the venv)
# Here we create it in the current dir for the project
if [[ ! -d ".venv" ]]; then
    /usr/local/bin/python3.12 -m venv .venv
    echo "[+] .venv created."
fi

# 6. Install PyTorch (CUDA 12.1 Specific)
echo "[+] Installing PyTorch for CUDA 12..."
source .venv/bin/activate
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu121

echo "[SUCCESS] Environment Setup Complete."
