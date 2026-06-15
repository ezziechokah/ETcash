#!/bin/bash

# ETcash Linux/macOS Installation Script
# Run with: sudo ./install.sh

set -e

INSTALL_PATH="/opt/etcash"
DATA_PATH="$HOME/.etcash"
DB_PATH="$DATA_PATH/database"
LOG_PATH="$DATA_PATH/logs"
BACKUP_PATH="$DATA_PATH/backups"

echo "========================================"
echo "ETcash Installation"
echo "========================================"

# Check if running as root for system install
if [ "$EUID" -eq 0 ]; then
    INSTALL_FOR="system"
else
    INSTALL_FOR="user"
    INSTALL_PATH="$HOME/.local/share/etcash"
fi

# Create directories
echo -e "\n[1/5] Creating directories..."
mkdir -p "$INSTALL_PATH"
mkdir -p "$DATA_PATH"
mkdir -p "$DB_PATH"
mkdir -p "$LOG_PATH"
mkdir -p "$BACKUP_PATH"

# Copy files
echo "[2/5] Installing application files..."
cp -r ./* "$INSTALL_PATH/"

# Setup Python environment
echo "[3/5] Setting up Python environment..."
cd "$INSTALL_PATH"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
echo "[4/5] Initializing database..."
export ETCASH_DATA_DIR="$DATA_PATH"
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com --noinput || true
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('Admin1234!'); user.save()"

# Seed demo data
read -p "Seed demo data? (y/n): " seed_demo
if [ "$seed_demo" = "y" ]; then
    python scripts/seed_demo.py
fi

# Create startup script
echo "[5/5] Creating startup scripts..."
cat > "$INSTALL_PATH/start_etcash.sh" << EOF
#!/bin/bash
cd "$INSTALL_PATH"
source venv/bin/activate
export ETCASH_DATA_DIR="$DATA_PATH"
python manage.py runserver 127.0.0.1:8000 &
sleep 3
cd frontend
npm start &
echo "ETcash started! Access at http://localhost:5173"
echo "Press Ctrl+C to stop"
wait
EOF

chmod +x "$INSTALL_PATH/start_etcash.sh"

# Create desktop entry for Linux
if [ "$INSTALL_FOR" = "system" ] && [ -d "/usr/share/applications" ]; then
    cat > /usr/share/applications/etcash.desktop << EOF
[Desktop Entry]
Name=ETcash
Comment=Kenya-first Financial System
Exec=$INSTALL_PATH/start_etcash.sh
Icon=$INSTALL_PATH/frontend/public/icon.png
Terminal=true
Type=Application
Categories=Office;Finance;
EOF
    echo "Desktop entry created"
fi

echo -e "\n========================================"
echo "INSTALLATION COMPLETE!"
echo "========================================"
echo "Installation Path: $INSTALL_PATH"
echo "Data Path: $DATA_PATH"
echo -e "\nTo start ETcash:"
echo "  Run: $INSTALL_PATH/start_etcash.sh"
echo -e "\nDefault Login:"
echo "  Username: admin"
echo "  Password: Admin1234!"