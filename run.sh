#!/usr/bin/env bash
# Start FastAPI + React on port 8000. Run from project root: bash run.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR"

# Load .env if present (simple: no quoted values)
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1090
  . ./.env
  set +a
fi

if [ ! -d "venv" ]; then
  echo "Run setup.sh first (bash setup.sh)."
  exit 1
fi

# Activate venv and run uvicorn
source venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
