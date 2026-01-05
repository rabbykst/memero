"""
Configuration Module für Memero Trading Bot
Lädt alle Konfigurationsparameter aus Environment-Variablen (.env)
"""

import os
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

# Solana Configuration
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
SOLANA_PRIVATE_KEY = os.getenv('SOLANA_PRIVATE_KEY')

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')

# Trading Parameters
TRADE_AMOUNT_SOL = float(os.getenv('TRADE_AMOUNT_SOL', '0.1'))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '15'))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '40'))

# Scout Configuration (in seconds)
SCOUT_INTERVAL = int(os.getenv('SCOUT_INTERVAL', '300'))  # 5 Minuten

# Watcher Configuration (in seconds)
WATCHER_INTERVAL = int(os.getenv('WATCHER_INTERVAL', '3'))

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Filter-Kriterien für Scout (Hard-Coded wie gefordert)
MIN_LIQUIDITY_USD = 5000
MIN_AGE_MINUTES = 15
MIN_VOLUME_USD = 10000

# Jupiter Aggregator API
JUPITER_API_URL = "https://quote-api.jup.ag/v6"

# DexScreener API
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest"

# Validierung der kritischen Konfigurationen
def validate_config():
    """Validiert, ob alle kritischen Konfigurationen gesetzt sind"""
    errors = []
    
    if not SOLANA_PRIVATE_KEY:
        errors.append("SOLANA_PRIVATE_KEY nicht gesetzt")
    
    if not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY nicht gesetzt")
    
    if errors:
        raise ValueError(f"Konfigurationsfehler: {', '.join(errors)}")
    
    return True
