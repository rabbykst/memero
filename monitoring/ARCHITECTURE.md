# MEMERO Monitoring - Architektur

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MEMERO ECOSYSTEM                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐     ┌──────────────────────────────┐
│     TRADING BOT (main.py)    │     │  MONITORING DASHBOARD        │
│        ⚠️ SCHREIBZUGRIFF      │     │     ✅ NUR LESEN              │
└──────────────────────────────┘     └──────────────────────────────┘
         │                                      │
         │                                      │
         ▼                                      ▼
┌─────────────────────┐              ┌─────────────────────┐
│ modules/            │              │ monitoring/         │
│ ├─ scout.py         │              │ ├─ monitor.py       │
│ ├─ analyst.py       │              │ ├─ data_reader.py   │
│ ├─ trader.py        │              │ ├─ config.py        │
│ └─ watcher.py       │              │ └─ templates/       │
└─────────────────────┘              └─────────────────────┘
         │                                      │
         │                                      │
         │                                      │
         ▼                                      ▼
┌─────────────────────────────────────────────────────────┐
│                    DATENQUELLEN                         │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   bot.log    │  │ Solana RPC   │  │ trades.json  │ │
│  │ (read-only)  │  │ (read-only)  │  │ (optional)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════

DATENFLUSS:

1️⃣ TRADING BOT → DATENQUELLEN (Schreibt Logs, führt Trades aus)
   ├─ scout.py     → DexScreener API
   ├─ analyst.py   → OpenRouter API
   ├─ trader.py    → Jupiter API + Solana Blockchain
   └─ watcher.py   → Jupiter API
   
   Schreibt: bot.log, trades.json (optional)
   
2️⃣ MONITORING → DATENQUELLEN (Liest nur!)
   ├─ data_reader.py → bot.log (read-only)
   ├─ data_reader.py → Solana RPC (getBalance nur)
   └─ data_reader.py → trades.json (read-only)
   
   Schreibt: NICHTS!

═══════════════════════════════════════════════════════════════════

API ENDPUNKTE (Monitoring):

┌─────────────────────────────────────────────────────────────────┐
│  HTTP Request          │  Datenquelle           │  Typ          │
├────────────────────────┼────────────────────────┼───────────────┤
│  GET /api/status       │  psutil + bot.log      │  Read-Only    │
│  GET /api/logs         │  bot.log               │  Read-Only    │
│  GET /api/wallet       │  Solana RPC            │  Read-Only    │
│  GET /api/trades       │  bot.log / trades.json │  Read-Only    │
│  GET /api/stats        │  bot.log / trades.json │  Read-Only    │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

SICHERHEITSMODELL:

┌─────────────────────────────────────────────────────────────────┐
│                        ISOLATION                                │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Separate Codebases (modules/ vs monitoring/)                │
│  ✅ Keine gemeinsamen Imports                                   │
│  ✅ Monitoring nutzt KEINE Trading-Module                       │
│  ✅ Monitoring hat KEINEN Private Key Zugriff                   │
│  ✅ Alle API-Endpunkte sind Login-geschützt                     │
│  ✅ Passwort-Hashing (PBKDF2-SHA256)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ZUGRIFFSKONTROLLE                          │
├─────────────────────────────────────────────────────────────────┤
│  Trading Bot:                                                   │
│    - Private Key: ✅ JA (aus .env)                              │
│    - Wallet Schreibzugriff: ✅ JA (für Trades)                  │
│    - Jupiter API: ✅ JA (Swap-Execution)                        │
│    - Log-Dateien: ✅ SCHREIBEN                                  │
│                                                                 │
│  Monitoring Dashboard:                                          │
│    - Private Key: ❌ NEIN (niemals!)                            │
│    - Wallet Schreibzugriff: ❌ NEIN (nur Balance lesen)         │
│    - Jupiter API: ❌ NEIN (kein Trading)                        │
│    - Log-Dateien: ✅ NUR LESEN                                  │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

DEPLOYMENT-SZENARIEN:

Szenario 1: Bot + Monitoring auf EINEM Server
┌────────────────────────────────────────┐
│         Linux VPS                      │
│  ┌──────────────────────────────────┐  │
│  │  Terminal 1: python main.py      │  │
│  │  → Trading Bot läuft             │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Terminal 2: ./start_monitor.sh  │  │
│  │  → Dashboard auf Port 5000       │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
   Zugriff: http://SERVER_IP:5000

Szenario 2: Bot auf Server A, Monitoring auf Server B
┌─────────────────┐         ┌─────────────────┐
│   Server A      │         │   Server B      │
│  Trading Bot    │         │  Monitoring     │
│  writes bot.log │───sync──│  reads bot.log  │
└─────────────────┘         └─────────────────┘
   (z.B. via rsync oder shared filesystem)

Szenario 3: Bot + Monitoring + Nginx
┌────────────────────────────────────────┐
│         Linux VPS                      │
│  ┌──────────────────────────────────┐  │
│  │  Trading Bot (main.py)           │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Monitoring (Port 5000)          │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Nginx Reverse Proxy (Port 80)   │  │
│  │  → SSL Termination               │  │
│  │  → memero.domain.com → :5000     │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
   Zugriff: https://memero.domain.com

═══════════════════════════════════════════════════════════════════

TECHNOLOGIE-STACK:

Trading Bot:
  - Python 3.10+
  - Solana SDK (solana-py, solders)
  - OpenAI Client (OpenRouter)
  - Jupiter Aggregator API
  - DexScreener API

Monitoring Dashboard:
  - Flask 3.0 (Webserver)
  - Werkzeug (Session-Management)
  - psutil (System-Metriken)
  - Chart.js (Frontend Charts)
  - Vanilla JS (kein Framework)
  - CSS3 (Glassmorphism Design)

═══════════════════════════════════════════════════════════════════
