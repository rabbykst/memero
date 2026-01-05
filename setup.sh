#!/bin/bash

# Memero Trading Bot - Setup Script für Linux Server

set -e

echo "=================================="
echo "Memero Bot Setup für Linux"
echo "=================================="
echo ""

# Prüfe Python Version
echo "Prüfe Python Version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nicht gefunden. Bitte installiere Python 3.10+"
    exit 1
fi

# Erstelle Virtual Environment
echo ""
echo "Erstelle Virtual Environment..."
python3 -m venv venv

# Aktiviere Virtual Environment
echo "Aktiviere Virtual Environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Update pip..."
pip install --upgrade pip

# Installiere Dependencies
echo ""
echo "Installiere Dependencies..."
pip install -r requirements.txt

# Erstelle .env aus Template
if [ ! -f .env ]; then
    echo ""
    echo "Erstelle .env Datei..."
    cp .env.example .env
    echo "✓ .env Datei erstellt"
    echo ""
    echo "⚠️  WICHTIG: Bitte fülle die .env Datei mit deinen Credentials aus!"
    echo "   nano .env"
else
    echo ""
    echo "✓ .env Datei existiert bereits"
fi

echo ""
echo "=================================="
echo "✅ Setup abgeschlossen!"
echo "=================================="
echo ""
echo "Nächste Schritte:"
echo "1. Konfiguriere .env: nano .env"
echo "2. Aktiviere venv: source venv/bin/activate"
echo "3. Starte Bot: python main.py"
echo ""
