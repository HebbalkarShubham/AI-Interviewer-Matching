#!/usr/bin/env bash
# One-time EC2 setup: install Python, pip, venv, MySQL, Node.js and project deps.
# Run from project root: bash setup.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "==> Detecting OS..."
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS="$ID"
else
  OS="unknown"
fi

echo "==> Installing system packages for $OS"
case "$OS" in
  amzn)
    sudo yum update -y
    sudo yum install -y python3 python3-pip python3-devel
    # MySQL (MariaDB on Amazon Linux 2)
    sudo yum install -y mariadb105-server mariadb105
    sudo systemctl start mariadb
    sudo systemctl enable mariadb
    # Node.js 18 from Amazon Linux extras or install script
    if ! command -v node &>/dev/null; then
      curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
      sudo yum install -y nodejs
    fi
    ;;
  ubuntu|debian)
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv python3-dev
    sudo apt-get install -y mysql-server
    sudo systemctl start mysql
    sudo systemctl enable mysql
    if ! command -v node &>/dev/null; then
      curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
      sudo apt-get install -y nodejs
    fi
    ;;
  *)
    echo "Unsupported OS: $OS. Install manually: python3, pip, venv, mysql, node."
    exit 1
    ;;
esac

echo "==> Creating Python venv and installing backend deps"
python3 -m venv "$BACKEND_DIR/venv"
# shellcheck disable=SC1090
source "$BACKEND_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"
deactivate

echo "==> Building frontend and copying to backend/static"
if [ -d "$FRONTEND_DIR" ]; then
  (cd "$FRONTEND_DIR" && npm ci && npm run build)
  rm -rf "$BACKEND_DIR/static"
  cp -r "$FRONTEND_DIR/dist" "$BACKEND_DIR/static"
  echo "    Frontend build copied to backend/static"
else
  echo "    No frontend/ dir found; skip build. Copy frontend/dist to backend/static manually."
fi

echo ""
echo "==> Setup done. Next steps:"
echo "    1. Configure backend/.env (DATABASE_URL, OPENAI_API_KEY, etc.)."
echo "    2. Create MySQL DB and user, then run migrations if any."
echo "    3. Start app: bash run.sh"
echo ""
