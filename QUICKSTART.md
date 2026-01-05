# 🚀 Memero Bot - Quick Start Guide

## Schnellstart (3 Schritte)

### 1. Setup ausführen
```bash
./setup.sh
```

### 2. Environment konfigurieren
```bash
nano .env
```

**Wichtig - Fülle diese Felder aus:**
- `SOLANA_PRIVATE_KEY`: Dein Solana Wallet Private Key (Base58)
- `OPENROUTER_API_KEY`: Dein OpenRouter API Key

**Wie bekomme ich diese Keys?**

#### Solana Private Key:
```bash
# Option 1: Von Phantom Wallet exportieren
# Settings → Security & Privacy → Export Private Key

# Option 2: Neues Wallet mit solana CLI erstellen
solana-keygen new --outfile ~/wallet.json
solana-keygen pubkey ~/wallet.json  # Zeigt Public Key
cat ~/wallet.json  # Array in Base58 konvertieren
```

#### OpenRouter API Key:
1. Gehe zu https://openrouter.ai/
2. Registriere dich / Login
3. Gehe zu "Keys" → "Create Key"
4. Kopiere den Key

### 3. Bot starten
```bash
./start.sh
```

## 📝 Wichtige Hinweise

### Vor dem ersten Start

1. **Wallet mit SOL aufladen**
   ```bash
   # Prüfe deine Wallet Adresse
   python3 -c "import base58; from solders.keypair import Keypair; import os; from dotenv import load_dotenv; load_dotenv(); pk = Keypair.from_bytes(base58.b58decode(os.getenv('SOLANA_PRIVATE_KEY'))); print(pk.pubkey())"
   
   # Sende SOL an diese Adresse
   # Minimum: 0.5 SOL (für Trades + Fees)
   ```

2. **OpenRouter Budget setzen**
   - Gehe zu https://openrouter.ai/settings/limits
   - Setze ein monatliches Limit (z.B. $10)

3. **Teste erst mit kleinen Beträgen**
   - In `.env` setze: `TRADE_AMOUNT_SOL=0.01`

### Tests ausführen

Vor dem echten Trading - teste alle Module:
```bash
python test_bot.py
```

## ⚙️ Konfiguration anpassen

### Trading Parameters
```bash
nano .env
```

**Empfohlene Settings für Anfänger:**
```env
TRADE_AMOUNT_SOL=0.01        # Nur 0.01 SOL pro Trade
STOP_LOSS_PERCENT=10         # Früher aussteigen
TAKE_PROFIT_PERCENT=30       # Konservativerer Profit
SCOUT_INTERVAL=600           # Nur alle 10 Min scannen
```

**Aggressive Settings für Profis:**
```env
TRADE_AMOUNT_SOL=0.5         # Größere Trades
STOP_LOSS_PERCENT=20         # Mehr Raum für Volatilität
TAKE_PROFIT_PERCENT=100      # Höhere Gewinne anstreben
SCOUT_INTERVAL=180           # Alle 3 Min scannen
```

## 🖥️ Linux Server Deployment

### Als Systemd Service (empfohlen)

```bash
# 1. Service installieren
./install_service.sh

# 2. Service starten
sudo systemctl start memero-bot

# 3. Status prüfen
sudo systemctl status memero-bot

# 4. Logs anschauen
sudo journalctl -u memero-bot -f

# 5. Autostart aktivieren
sudo systemctl enable memero-bot
```

### Im Screen (Alternative)

```bash
# Screen Session starten
screen -S memero

# Bot starten
./start.sh

# Detach: Ctrl+A dann D
# Wieder anhängen: screen -r memero
```

## 📊 Logs überwachen

### Live Logs
```bash
tail -f bot.log
```

### Nur Errors
```bash
grep ERROR bot.log
```

### Erfolgreiche Trades
```bash
grep "TRADE ERFOLGREICH" bot.log
```

## 🛑 Bot stoppen

### Normal
```bash
# Ctrl+C im Terminal
```

### Systemd Service
```bash
sudo systemctl stop memero-bot
```

### Screen
```bash
screen -r memero  # Anhängen
# Dann Ctrl+C
```

## ⚠️ Troubleshooting

### Import Errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission Denied" bei Scripts
```bash
chmod +x setup.sh start.sh install_service.sh
```

### RPC Errors
```bash
# In .env einen anderen RPC nutzen
SOLANA_RPC_URL=https://rpc.ankr.com/solana
# Oder: https://solana-api.projectserum.com
```

### Jupiter API Timeout
- Normal bei hoher Last
- Bot versucht automatisch erneut
- Evtl. SCOUT_INTERVAL erhöhen

## 💰 Wallet Management

### Balance prüfen
```bash
# Im Python Terminal
python3
>>> from modules.trader import Trader
>>> trader = Trader()
>>> # Wallet Address zeigen
>>> print(trader.wallet.pubkey())
```

### SOL Balance via CLI
```bash
solana balance <DEINE_WALLET_ADDRESS>
```

## 📈 Performance Tracking

Der Bot loggt automatisch:
- Jeden Trade (Entry Price, Amount)
- Jeden Exit (Exit Price, PnL)
- Security Check Results

Finde alle Exits:
```bash
grep "EXIT ERFOLGREICH" bot.log
```

## 🔐 Security Checklist

- [ ] Private Key nur in .env (nie im Code)
- [ ] .env in .gitignore (nie committen)
- [ ] Separates Wallet nur für Bot
- [ ] Kleiner Betrag zum Testen
- [ ] OpenRouter Budget Limit gesetzt
- [ ] Logs regelmäßig prüfen

## 📞 Wenn etwas nicht funktioniert

1. **Prüfe Logs:** `tail -50 bot.log`
2. **Teste Module:** `python test_bot.py`
3. **Prüfe .env:** Alle Keys gesetzt?
4. **Prüfe Balance:** Genug SOL im Wallet?
5. **Prüfe Network:** `ping api.dexscreener.com`

## 🎯 Nächste Schritte

Nach erfolgreichem Test:
1. Erhöhe `TRADE_AMOUNT_SOL` schrittweise
2. Optimiere `STOP_LOSS` / `TAKE_PROFIT`
3. Experimentiere mit verschiedenen Modellen in `analyst.py`
4. Monitore Performance über mehrere Tage

---

**Happy Trading! 🚀**

*Disclaimer: Nur Geld einsetzen, das du verlieren kannst.*
