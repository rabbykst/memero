"""
MEMERO Monitoring - Konfiguration
Komplett isoliert vom Trading-Bot - NUR LESE-ZUGRIFF!
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# .ENV LADEN (WICHTIG!)
# ============================================================================

# Lade .env aus Parent-Verzeichnis (memero/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# ============================================================================
# BASIS KONFIGURATION
# ============================================================================

# Pfad zum Root-Verzeichnis (ein Level höher als monitoring/)
BASE_DIR = Path(__file__).parent.parent

# Webserver Konfiguration
MONITOR_HOST = os.getenv('MONITOR_HOST', '0.0.0.0')  # 0.0.0.0 für VPS-Zugriff
MONITOR_PORT = int(os.getenv('MONITOR_PORT', '5000'))
SECRET_KEY = os.getenv('MONITOR_SECRET_KEY', 'change-this-in-production-memero-2026')

# Login Credentials (Passwort-Hash wird in monitor.py generiert)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'yummyringtoneremix'  # Wird gehashed, niemals im Frontend sichtbar

# Bot-Steuerungs-Passwort (zweite Sicherheitsebene)
BOT_CONTROL_PASSWORD = 'f1f3f4escpaulmarcschnee'

# ============================================================================
# DATENQUELLEN (READ-ONLY!)
# ============================================================================

# Bot Log-Datei (wird NUR gelesen, niemals geschrieben)
BOT_LOG_FILE = BASE_DIR / 'bot.log'

# Solana RPC Endpoint (nur für Balance-Abfragen, kein Wallet-Zugriff)
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')

# Wallet Public Key (NUR für Balance-Abfrage, KEIN Private Key!)
# Wird aus .env geladen - WICHTIG: Nicht SOLANA_PRIVATE_KEY!
WALLET_PUBLIC_KEY = os.getenv('WALLET_PUBLIC_KEY', None)

# Debug: Zeige ob Key geladen wurde
if WALLET_PUBLIC_KEY:
    print(f"✅ Wallet Public Key geladen: {WALLET_PUBLIC_KEY[:8]}...{WALLET_PUBLIC_KEY[-4:]}")
else:
    print("⚠️  WALLET_PUBLIC_KEY nicht in .env gefunden!")

# Optional: Trades-Datenbank (falls Bot später Trades persistiert)
TRADES_DB_FILE = BASE_DIR / 'trades.json'

# ============================================================================
# BOT-STEUERUNG (Prozess-Kontrolle)
# ============================================================================

# Pfad zum Bot-Start-Script
BOT_START_SCRIPT = BASE_DIR / 'start.sh'

# Pfad zur main.py (für Prozess-Erkennung)
BOT_MAIN_FILE = BASE_DIR / 'main.py'

# ============================================================================
# MONITORING EINSTELLUNGEN
# ============================================================================

# Wie viele Log-Zeilen sollen maximal angezeigt werden?
MAX_LOG_LINES = 500

# Update-Intervall für Auto-Refresh (Sekunden)
AUTO_REFRESH_INTERVAL = 10

# Zeitzone für Anzeige
TIMEZONE = 'Europe/Berlin'

# ============================================================================
# DEBUGGING
# ============================================================================

DEBUG = os.getenv('MONITOR_DEBUG', 'False').lower() == 'true'

print(f"""
╔══════════════════════════════════════════════════════════════╗
║          MEMERO MONITORING - Konfiguration geladen           ║
╚══════════════════════════════════════════════════════════════╝

🌐 Host: {MONITOR_HOST}:{MONITOR_PORT}
📂 Log-Datei: {BOT_LOG_FILE}
🔗 Solana RPC: {SOLANA_RPC_URL}
👤 Admin User: {ADMIN_USERNAME}
🔐 Secret Key: {'***' + SECRET_KEY[-8:]}

⚠️  WICHTIG: Dieses Monitoring hat NUR LESE-ZUGRIFF!
   Der Trading-Bot wird NICHT beeinflusst oder verändert.
""")
