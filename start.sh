#!/bin/bash

# Memero Trading Bot - Start Script
# Mit nohup für 24/7 Betrieb

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

# Prüfe ob Bot bereits läuft
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  Bot läuft bereits!"
    echo "PID: $(pgrep -f 'python.*main.py')"
    echo "Zum Stoppen: pkill -f 'python.*main.py'"
    exit 1
fi

# Starte Bot im Hintergrund mit nohup
echo "🚀 Starte Memero Trading Bot im Hintergrund..."
nohup python main.py > bot_output.log 2>&1 &

# Speichere PID
BOT_PID=$!
echo $BOT_PID > bot.pid

echo "✅ Bot gestartet! PID: $BOT_PID"
echo "📊 Logs: tail -f bot.log"
echo "📈 Output: tail -f bot_output.log"
echo "🛑 Stoppen: pkill -f 'python.*main.py'"
