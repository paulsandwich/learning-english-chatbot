#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Creating data and transcripts directories ==="
mkdir -p data transcripts

echo "=== Initialising SQLite database ==="
python -c "from bot.db import init_db; init_db(); print('DB initialised.')"

echo "=== Done! ==="
echo "Next: copy .env.example to .env and fill in your tokens, then enable the systemd service."
