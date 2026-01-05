# Memero Trading Bot

Ein vollautomatischer, KI-gestützter Trading-Bot für Solana Meme-Coins mit strengen Security-Checks.

## 🔐 Sicherheits-Features

- **Mint Authority Check**: Verifiziert dass Token-Supply nicht manipuliert werden kann
- **Freeze Authority Check**: Stellt sicher dass Tokens nicht eingefroren werden können
- **Private Key Security**: Keys werden NUR aus Environment-Variablen geladen
- **Jupiter Aggregator**: Best-Price Execution für alle Trades

## 🏗️ Architektur

Das System besteht aus 4 unabhängigen Modulen:

### Modul A: Scout (Data Fetcher)
- Scannt DexScreener API alle 5 Minuten
- Filter: Liquidität > $5.000, Alter > 15 Min, Volumen > $10.000
- Liefert validierte Token-Pairs

### Modul B: Analyst (LLM Integration)
- Nutzt OpenRouter API (Claude 3.5 Sonnet)
- Analysiert Sentiment und Metriken
- Gibt BUY oder PASS Empfehlung

### Modul C: Trader (Execution & Security)
- Führt kritische Security Checks durch
- Executed Trades via Jupiter Aggregator
- Sichere Private Key Verwaltung

### Modul D: Watcher (Limit Order Manager)
- Überwacht Positionen in Echtzeit
- Stop-Loss: -15%
- Take-Profit: +40%
- Reine mathematische Entscheidungen

## 🚀 Installation

### Voraussetzungen
- Python 3.10+
- Linux Server (getestet auf Ubuntu 22.04)
- Solana Wallet mit SOL für Trading
- OpenRouter API Key

### Setup

1. **Repository klonen**
```bash
cd /Users/mac/memero
```

2. **Virtual Environment erstellen**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

4. **Environment-Variablen konfigurieren**
```bash
cp .env.example .env
nano .env
```

Fülle folgende Werte aus:
- `SOLANA_PRIVATE_KEY`: Dein Base58 encoded Private Key
- `OPENROUTER_API_KEY`: Dein OpenRouter API Key
- Optional: Passe Trading-Parameter an

5. **Bot starten**
```bash
python main.py
```

## ⚙️ Konfiguration

Alle Parameter können in der `.env` Datei angepasst werden:

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `TRADE_AMOUNT_SOL` | 0.1 | SOL pro Trade |
| `STOP_LOSS_PERCENT` | 15 | Stop-Loss Prozent |
| `TAKE_PROFIT_PERCENT` | 40 | Take-Profit Prozent |
| `SCOUT_INTERVAL` | 300 | Scout Interval (Sekunden) |
| `WATCHER_INTERVAL` | 3 | Watcher Check Interval (Sekunden) |

## 📊 Logs

Der Bot erstellt detaillierte Logs in:
- **Console**: INFO Level
- **bot.log**: DEBUG Level (alle Details)

## 🔧 Projekt-Struktur

```
memero/
├── main.py                 # Main Orchestrator
├── config.py              # Konfiguration
├── requirements.txt       # Python Dependencies
├── .env                   # Environment Variablen (nicht in Git)
├── .env.example          # Environment Template
├── bot.log               # Log Datei
└── modules/
    ├── scout.py          # Modul A: Data Fetcher
    ├── analyst.py        # Modul B: LLM Integration
    ├── trader.py         # Modul C: Execution & Security
    └── watcher.py        # Modul D: Position Manager
```

## ⚠️ Wichtige Hinweise

### Security
- **NIEMALS** deinen Private Key committen oder teilen
- Nutze einen separaten Wallet nur für den Bot
- Starte mit kleinen Beträgen zum Testen
- Überprüfe regelmäßig die Logs

### Trading Risiken
- Meme-Coins sind **hochriskant**
- Der Bot kann Geld verlieren
- Keine Garantie für Profit
- Nur Geld einsetzen, das du verlieren kannst

### OpenRouter API
- API Calls kosten Geld
- Claude 3.5 Sonnet ca. $3/1M Input Tokens
- Budget in OpenRouter Dashboard setzen
- Alternative: Günstigeres Modell in `modules/analyst.py` konfigurieren

## 🐛 Troubleshooting

### "Import konnte nicht aufgelöst werden"
```bash
pip install -r requirements.txt
```

### "SOLANA_PRIVATE_KEY nicht gesetzt"
Überprüfe deine `.env` Datei:
```bash
cat .env | grep SOLANA_PRIVATE_KEY
```

### "Jupiter API Timeout"
- Netzwerkverbindung prüfen
- Jupiter API Status: https://status.jup.ag

### "DexScreener API Fehler"
- Rate Limits möglich
- Warte 1-2 Minuten und versuche erneut

## 📝 Entwicklung

### Module einzeln testen

**Scout testen:**
```python
from modules.scout import Scout
scout = Scout()
pairs = scout.fetch_new_pairs()
print(f"Gefunden: {len(pairs)} Pairs")
```

**Analyst testen:**
```python
from modules.analyst import Analyst
analyst = Analyst()
# Benötigt Pairs vom Scout
decision = analyst.analyze_pairs(pairs)
```

## 📄 Lizenz

Dieses Projekt ist für Bildungszwecke. Nutze es auf eigene Verantwortung.

## 🤝 Support

Bei Fragen oder Problemen:
1. Prüfe die Logs in `bot.log`
2. Überprüfe deine `.env` Konfiguration
3. Stelle sicher dass alle Dependencies installiert sind

---

**Disclaimer**: Trading ist riskant. Dieser Bot ist ein Werkzeug, keine Finanzberatung.
