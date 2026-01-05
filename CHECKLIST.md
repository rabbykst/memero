# ✅ Setup Checklist für Memero Bot

Folge dieser Liste Schritt für Schritt um den Bot betriebsbereit zu machen.

## Phase 1: Grundsetup ⚙️

- [ ] **Python 3.10+ installiert**
  ```bash
  python3 --version  # Sollte >= 3.10 sein
  ```

- [ ] **Dependencies installiert**
  ```bash
  ./setup.sh
  ```

- [ ] **Virtual Environment aktiviert**
  ```bash
  source venv/bin/activate
  ```

## Phase 2: API Keys & Wallet 🔑

### Solana Wallet

- [ ] **Wallet erstellt oder exportiert**
  - Option A: Phantom Wallet → Export Private Key
  - Option B: `solana-keygen new --outfile ~/wallet.json`

- [ ] **Private Key in Base58 Format**
  - Von Phantom: Direkt Base58
  - Von solana-keygen: Array → Base58 konvertieren

- [ ] **Private Key in .env gesetzt**
  ```bash
  cp .env.example .env
  nano .env
  # Füge SOLANA_PRIVATE_KEY=dein_key ein
  ```

- [ ] **Wallet mit SOL geladen**
  - Minimum: 0.5 SOL
  - Empfohlen für Tests: 1 SOL
  - Sende SOL an deine Wallet Address

### OpenRouter API

- [ ] **OpenRouter Account erstellt**
  - https://openrouter.ai/

- [ ] **API Key erstellt**
  - Dashboard → Keys → Create Key

- [ ] **API Key in .env gesetzt**
  ```bash
  nano .env
  # Füge OPENROUTER_API_KEY=dein_key ein
  ```

- [ ] **Budget Limit gesetzt**
  - Dashboard → Settings → Limits
  - Empfohlen: $10/Monat für Start

## Phase 3: Konfiguration 📝

- [ ] **.env vollständig ausgefüllt**
  ```bash
  cat .env
  # Prüfe dass beide Keys gesetzt sind
  ```

- [ ] **Trading Parameter angepasst**
  - Für Tests: `TRADE_AMOUNT_SOL=0.01`
  - Für Echtbetrieb: Nach Präferenz

- [ ] **RPC URL geprüft**
  - Default: `https://api.mainnet-beta.solana.com`
  - Alternative: `https://rpc.ankr.com/solana`

## Phase 4: Testing 🧪

- [ ] **Konfiguration getestet**
  ```bash
  python test_bot.py
  ```
  → Alle Tests sollten PASSED sein

- [ ] **Scout Test**
  ```bash
  python3 -c "from modules.scout import Scout; s = Scout(); print(f'Found {len(s.fetch_new_pairs())} pairs')"
  ```

- [ ] **Trader Test (Wallet Adresse anzeigen)**
  ```bash
  python3 -c "from modules.trader import Trader; t = Trader(); print(f'Wallet: {t.wallet.pubkey()}')"
  ```

- [ ] **SOL Balance geprüft**
  - Nutze Solana Explorer: https://explorer.solana.com/
  - Gib deine Wallet Adresse ein

## Phase 5: Erster Start 🚀

- [ ] **Backup von .env erstellt**
  ```bash
  cp .env .env.backup
  ```

- [ ] **Log-Datei Platz geprüft**
  ```bash
  df -h .  # Mindestens 1GB frei
  ```

- [ ] **Bot im Test-Modus gestartet**
  ```bash
  # Mit kleinem Betrag
  ./start.sh
  ```

- [ ] **Logs überwacht**
  ```bash
  # In neuem Terminal
  tail -f bot.log
  ```

- [ ] **Ersten Scout-Cycle abgewartet** (5 Min)

- [ ] **Security Checks beobachtet**
  - Logs zeigen: "✓ ALLE SECURITY CHECKS BESTANDEN"

## Phase 6: Linux Server Deployment (Optional) 🖥️

- [ ] **Als Systemd Service installiert**
  ```bash
  ./install_service.sh
  ```

- [ ] **Service gestartet**
  ```bash
  sudo systemctl start memero-bot
  ```

- [ ] **Autostart aktiviert**
  ```bash
  sudo systemctl enable memero-bot
  ```

- [ ] **Service Logs geprüft**
  ```bash
  sudo journalctl -u memero-bot -f
  ```

## Phase 7: Monitoring & Optimization 📊

- [ ] **Ersten Trade abgewartet** (kann Stunden dauern)

- [ ] **Trade Performance geprüft**
  ```bash
  grep "TRADE ERFOLGREICH" bot.log
  grep "EXIT ERFOLGREICH" bot.log
  ```

- [ ] **Stop-Loss/Take-Profit optimiert**
  - Basierend auf ersten Ergebnissen

- [ ] **Trade Amount angepasst**
  - Nur wenn Tests erfolgreich

- [ ] **Log Rotation eingerichtet** (bei Dauerbetrieb)
  ```bash
  # /etc/logrotate.d/memero-bot
  ```

## ⚠️ Wichtige Sicherheits-Checks

- [ ] **Private Key NIE geteilt**
- [ ] **Private Key NIE committet** (in .gitignore)
- [ ] **Separates Wallet für Bot** (nicht Haupt-Wallet)
- [ ] **Nur Test-Beträge am Anfang**
- [ ] **OpenRouter Budget Limit gesetzt**
- [ ] **Regelmäßige Log-Prüfung** (täglich)

## 📈 Success Metriken

Nach 24h Betrieb:
- [ ] Keine Crashes in Logs
- [ ] Security Checks funktionieren
- [ ] Mindestens 1 Scout-Cycle erfolgreich
- [ ] Analyst macht Entscheidungen (BUY/PASS)
- [ ] Bei Trade: Exit wird korrekt ausgeführt

Nach 1 Woche:
- [ ] Performance Tracking
- [ ] Win-Rate berechnen
- [ ] Parameter Optimierung

## 🆘 Notfall-Kontakte

Bei Problemen:
1. **Stop Bot:** `sudo systemctl stop memero-bot` oder Ctrl+C
2. **Check Logs:** `tail -100 bot.log`
3. **Check Wallet:** Solana Explorer
4. **Test Module:** `python test_bot.py`

## 📞 Support Resourcen

- DexScreener Docs: https://docs.dexscreener.com/
- Jupiter Docs: https://station.jup.ag/docs
- Solana Docs: https://docs.solana.com/
- OpenRouter Docs: https://openrouter.ai/docs

---

**Wenn alle Checkboxen ✅ sind: Der Bot ist produktionsbereit! 🎉**

*Letzte Erinnerung: Nur Geld einsetzen, das du verlieren kannst. Meme-Coins sind hochriskant!*
