#!/bin/bash

###############################################################################
# MEMERO Monitoring - systemd Service Installation
# Installiert das Monitoring als systemd-Service für 24/7-Betrieb
###############################################################################

set -e  # Bei Fehler abbrechen

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        MEMERO Monitoring - systemd Service Installer        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Root-Check
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bitte als root ausführen: sudo ./install_service.sh${NC}"
    exit 1
fi

# Pfade ermitteln
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}📁 Erkannte Pfade:${NC}"
echo "   BASE_DIR: $BASE_DIR"
echo "   MONITORING_DIR: $SCRIPT_DIR"
echo ""

# Python Virtual Environment prüfen
if [ -d "$BASE_DIR/venv" ]; then
    PYTHON_BIN="$BASE_DIR/venv/bin/python3"
    echo -e "${GREEN}✓ Virtual Environment gefunden: venv${NC}"
elif [ -d "$BASE_DIR/env" ]; then
    PYTHON_BIN="$BASE_DIR/env/bin/python3"
    echo -e "${GREEN}✓ Virtual Environment gefunden: env${NC}"
else
    echo -e "${YELLOW}⚠️  Kein Virtual Environment gefunden!${NC}"
    echo -e "${YELLOW}   Erstelle Virtual Environment...${NC}"
    python3 -m venv "$BASE_DIR/venv"
    PYTHON_BIN="$BASE_DIR/venv/bin/python3"
    
    # Dependencies installieren
    echo -e "${YELLOW}   Installiere Dependencies...${NC}"
    "$BASE_DIR/venv/bin/pip" install --upgrade pip
    "$BASE_DIR/venv/bin/pip" install -r "$BASE_DIR/requirements.txt"
    "$BASE_DIR/venv/bin/pip" install psutil python-dotenv
    echo -e "${GREEN}✓ Virtual Environment erstellt${NC}"
fi

# Prüfe ob Python executable existiert
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}❌ Python nicht gefunden: $PYTHON_BIN${NC}"
    exit 1
fi

# Service-Datei anpassen mit korrekten Pfaden
SERVICE_FILE="$SCRIPT_DIR/memero-monitor.service"
SYSTEMD_SERVICE="/etc/systemd/system/memero-monitor.service"

echo -e "${YELLOW}📝 Erstelle Service-Datei...${NC}"

# Dynamische Service-Datei erstellen
cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=MEMERO Monitoring Dashboard
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$BASE_DIR
Environment="PATH=$BASE_DIR/venv/bin:$BASE_DIR/env/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$BASE_DIR"
Environment="PYTHONUNBUFFERED=1"

# Haupt-Befehl - WICHTIG: Mit -m als Modul starten!
ExecStart=$PYTHON_BIN -m monitoring.monitor

# Automatischer Neustart bei Absturz
Restart=always
RestartSec=10

# Timeout-Settings
TimeoutStartSec=30
TimeoutStopSec=30

# Logs zu systemd journal
StandardOutput=journal
StandardError=journal
SyslogIdentifier=memero-monitor

# Prozess-Limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service-Datei erstellt: $SYSTEMD_SERVICE${NC}"

# systemd neu laden
echo -e "${YELLOW}🔄 Lade systemd neu...${NC}"
systemctl daemon-reload

# Service aktivieren (Auto-Start beim Boot)
echo -e "${YELLOW}🔧 Aktiviere Auto-Start beim Boot...${NC}"
systemctl enable memero-monitor.service

# Service starten
echo -e "${YELLOW}🚀 Starte Service...${NC}"
systemctl start memero-monitor.service

# Warte kurz
sleep 2

# Status prüfen
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation abgeschlossen!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Status anzeigen
systemctl status memero-monitor.service --no-pager -l

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    WICHTIGE BEFEHLE                          ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}  Service starten:    ${NC}systemctl start memero-monitor"
echo -e "${YELLOW}  Service stoppen:    ${NC}systemctl stop memero-monitor"
echo -e "${BLUE}  Service neu laden:  ${NC}systemctl restart memero-monitor"
echo -e "${YELLOW}  Status prüfen:      ${NC}systemctl status memero-monitor"
echo -e "${GREEN}  Logs anzeigen:      ${NC}journalctl -u memero-monitor -f"
echo -e "${RED}  Service deaktivieren:${NC}systemctl disable memero-monitor"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 Dashboard läuft jetzt auf: http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo -e "${GREEN}🔐 Login: admin / yummyringtoneremix${NC}"
echo ""
echo -e "${YELLOW}💡 Der Service läuft jetzt 24/7, auch nach SSH-Disconnect!${NC}"
echo -e "${YELLOW}💡 Bei Server-Neustart startet der Service automatisch!${NC}"
echo ""
