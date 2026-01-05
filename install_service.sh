#!/bin/bash

# Memero Trading Bot - Systemd Service Installer

SERVICE_NAME="memero-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
WORKING_DIR="$(pwd)"
USER="$(whoami)"

echo "Installiere Memero Bot als Systemd Service..."
echo ""
echo "Working Directory: $WORKING_DIR"
echo "User: $USER"
echo ""

# Erstelle Service File
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Memero Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$WORKING_DIR/venv/bin:/usr/bin"
ExecStart=$WORKING_DIR/venv/bin/python $WORKING_DIR/main.py
Restart=on-failure
RestartSec=10
StandardOutput=append:$WORKING_DIR/bot.log
StandardError=append:$WORKING_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service File erstellt: $SERVICE_FILE"

# Reload Systemd
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"

# Service Commands
echo ""
echo "Service wurde installiert!"
echo ""
echo "Verfügbare Commands:"
echo "  sudo systemctl start $SERVICE_NAME      # Bot starten"
echo "  sudo systemctl stop $SERVICE_NAME       # Bot stoppen"
echo "  sudo systemctl restart $SERVICE_NAME    # Bot neustarten"
echo "  sudo systemctl status $SERVICE_NAME     # Status anzeigen"
echo "  sudo systemctl enable $SERVICE_NAME     # Autostart aktivieren"
echo "  sudo journalctl -u $SERVICE_NAME -f    # Logs anzeigen"
echo ""
