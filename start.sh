#!/bin/bash

# Memero Trading Bot - Start Script

# Aktiviere Virtual Environment
source venv/bin/activate

# Prüfe ob .env existiert
if [ ! -f .env ]; then
    echo "❌ .env Datei nicht gefunden!"
    echo "Bitte kopiere .env.example zu .env und fülle die Werte aus:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Starte Bot
echo "Starte Memero Trading Bot..."
python main.py
