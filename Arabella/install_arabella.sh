#!/usr/bin/env bash
# Installation script for ArabellaOS.
# This script prepares a Debian Minimal system for running Arabella.
# It installs required packages, sets up directories and virtualenv, and
# configures login hooks and boot settings. Run as root.

set -euo pipefail

# Update package lists and install prerequisites
apt update -y
apt install -y \
    python3-full \
    python3-pip \
    python3-venv \
    git \
    zsh \
    htop \
    lm-sensors

# Create the Arabella directory structure
mkdir -p /opt/arabella/brain /opt/arabella/memories /opt/arabella/skills /opt/arabella/data

# Set up Python virtual environment
python3 -m venv /opt/arabella/venv
/opt/arabella/venv/bin/pip install --upgrade pip
/opt/arabella/venv/bin/pip install langchain langchain-ollama chromadb psutil sentence-transformers

# Detect the user's shell and choose appropriate rc file
user_shell=$(basename "$SHELL")
rc_file="$HOME/.bashrc"
if [ "$user_shell" = "zsh" ]; then
    rc_file="$HOME/.zshrc"
fi

# Append a login hook to run the welcome script
if ! grep -q "arabella_welcome.py" "$rc_file"; then
    echo "# Launch Arabella welcome screen on login" >> "$rc_file"
    echo "/opt/arabella/venv/bin/python3 /opt/arabella/brain/arabella_welcome.py || true" >> "$rc_file"
fi

# Configure GRUB for silent boot (quiet splash and lower loglevel)
sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash loglevel=0"/' /etc/default/grub

# Inform the user to run update-grub manually after the installation
cat <<'MSG'
To apply the silent boot settings, please run:
  sudo update-grub
MSG

# Overwrite the issue file with a security warning
printf "ARABELLA OS\nUNAUTHORIZED ACCESS IS PROHIBITED.\n" > /etc/issue

exit 0
