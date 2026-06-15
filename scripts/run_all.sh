#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"

activate_venv() {
  if [ -f "$VENV_DIR/bin/activate" ]; then
    # Unix-style virtualenv
    # shellcheck source=/dev/null
    . "$VENV_DIR/bin/activate"
  elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Git Bash / MSYS / Cygwin on Windows
    # shellcheck source=/dev/null
    . "$VENV_DIR/Scripts/activate"
  else
    echo "ERROR: Python virtual environment not found in $VENV_DIR"
    exit 1
  fi
}

start_backend() {
  echo "==> Starting backend server on http://127.0.0.1:8765"
  cd "$BACKEND_DIR"
  python manage.py migrate
  echo "==> Ensuring admin user exists"
  python manage.py shell <<'PY'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.co.ke', 'Admin1234!')
    print('Created admin user admin / Admin1234!')
else:
    print('Admin user already exists')
PY
  python manage.py runserver 127.0.0.1:8765 &
  BACKEND_PID=$!
  echo "Backend running (pid=$BACKEND_PID)"
}

start_frontend() {
  echo "==> Installing frontend dependencies"
  cd "$FRONTEND_DIR"
  npm install >/dev/null 2>&1
  echo "==> Starting frontend dev server on http://127.0.0.1:5173"
  npm run dev -- --host 127.0.0.1 &
  FRONTEND_PID=$!
  echo "Frontend running (pid=$FRONTEND_PID)"
}

cleanup() {
  echo ""
  echo "Shutting down servers..."
  if [ -n "${BACKEND_PID:-}" ]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [ -n "${FRONTEND_PID:-}" ]; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

activate_venv
start_backend
start_frontend

echo ""
echo "========================================="
echo "Backend running on http://127.0.0.1:8765"
echo "Frontend running on http://127.0.0.1:5173"
echo ""
echo "Open http://localhost:5173 in your browser"
echo "Login: admin / Admin1234!"
echo "========================================="
echo ""

wait
