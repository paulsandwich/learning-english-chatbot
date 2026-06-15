#!/bin/bash
set -e

echo "=== Creating Python virtual environment ==="
python3 -m venv .venv

echo "=== Installing Python dependencies ==="
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "=== Creating data and transcripts directories ==="
mkdir -p data transcripts

echo "=== Initialising SQLite database ==="
.venv/bin/python -c "from bot.db import init_db; init_db(); print('DB initialised.')"

echo "=== Done! ==="
echo "Next: copy .env.example to .env and fill in your tokens, then enable the systemd service."
