#!/bin/bash

###############################################################################
# MEMERO Monitoring Dashboard - Start Script
# Startet den Flask Webserver für das Monitoring-Interface
###############################################################################

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          MEMERO MONITORING DASHBOARD - Starten               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Zum Projekt-Verzeichnis wechseln
cd "$(dirname "$0")"

# Prüfen ob .env existiert
if [ ! -f .env ]; then
    echo "❌ FEHLER: .env Datei nicht gefunden!"
    echo "   Bitte .env.example kopieren und konfigurieren."
    exit 1
fi

# Prüfen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ FEHLER: Python 3 nicht gefunden!"
    exit 1
fi

# Virtual Environment aktivieren (falls vorhanden)
if [ -d "venv" ]; then
    echo "🔧 Aktiviere Virtual Environment..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo "🔧 Aktiviere Virtual Environment..."
    source env/bin/activate
else
    echo "⚠️  WARNUNG: Kein Virtual Environment gefunden!"
    echo "   Führe zuerst ./setup.sh aus oder erstelle eins mit: python3 -m venv venv"
fi

# Dependencies prüfen
echo "📦 Prüfe Monitoring-Dependencies..."
python3 -c "import flask" 2>/dev/null || {
    echo "⚠️  Flask nicht installiert. Installiere Dependencies..."
    pip install flask werkzeug psutil
}

# Monitoring-Server starten
echo ""
echo "🚀 Starte Monitoring-Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

python3 -m monitoring.monitor

# Falls Server beendet wird
echo ""
echo "🛑 Monitoring-Server gestoppt."
