# Dashboard Troubleshooting Guide

## Problem: Features funktionieren nicht auf dem Server

### Checkliste nach `git pull`:

#### 1. Browser-Cache leeren
**WICHTIG:** Browser cached CSS/JS-Dateien!

```bash
# Chrome/Firefox: Strg+Shift+R (Hard Reload)
# Safari: Cmd+Option+R
```

Oder in den DevTools:
- F12 öffnen
- Network Tab → "Disable cache" aktivieren
- Seite neu laden

---

#### 2. Monitoring neu starten

```bash
# Auf dem Server:
cd /root/memero
git pull

# Dependencies installieren
pip install psutil python-dotenv

# Monitoring stoppen
pkill -f "monitor.py"

# Neu starten
./start_monitor.sh

# ODER manuell:
cd monitoring
python3 monitor.py
```

---

#### 3. Browser Console prüfen

**F12 → Console Tab**

Erwartete Ausgabe:
```
MEMERO Dashboard geladen
MEMERO Dashboard JavaScript geladen ✓
```

Fehler checken:
- ❌ `404 Not Found` → Datei nicht geladen
- ❌ `Uncaught ReferenceError` → Funktion fehlt
- ❌ `Failed to fetch` → API-Endpunkt antwortet nicht

---

#### 4. API-Endpunkte testen

**Im Browser:**
```
http://<server-ip>:5000/api/bot/status
```

Erwartete Antwort:
```json
{
  "is_running": false,
  "pid": null,
  "timer": {
    "timer_active": false,
    "timer_end": null,
    "remaining_minutes": 0,
    "auto_stopped": false
  }
}
```

**Weitere Tests:**
- `/api/stats` → Muss `successful_trades`, `loss_trades`, `failed_trades` enthalten
- `/api/wallet` → Muss `address` mit Wallet-Adresse zeigen

---

#### 5. Wallet Public Key prüfen

```bash
# Auf dem Server:
cd /root/memero
cat .env | grep WALLET_PUBLIC_KEY

# Sollte anzeigen:
WALLET_PUBLIC_KEY=3UMApZc...nHZD
```

Wenn leer:
```bash
# .env Datei prüfen
ls -la .env
cat .env

# Falls dotenv-Modul fehlt:
pip install python-dotenv
```

---

#### 6. Bot Control Features testen

**Schritt-für-Schritt:**

1. **Bot-Status:**
   - Oben im Dashboard: Grüner/Roter Punkt?
   - "Status: Läuft" oder "Status: Gestoppt"?

2. **Bot stoppen:**
   - Klick auf "⏹️ Bot stoppen"
   - Modal öffnet sich?
   - Passwort eingeben: `f1f3f4escpaulmarcschnee`
   - "Bestätigen" klicken
   - Erfolgs-Meldung?

3. **Bot starten:**
   - Klick auf "▶️ Bot starten"
   - Modal öffnet sich?
   - Passwort eingeben
   - Bot startet?

4. **Timer setzen:**
   - Timer-Dropdown: "15 Minuten" auswählen
   - "Timer setzen" klicken
   - Modal öffnet sich?
   - Passwort eingeben
   - Timer-Status zeigt: "⏰ Timer aktiv: 15 Min verbleibend"?

---

#### 7. Win/Loss/Failed Chart prüfen

**Erwartet:** 3 Segmente im Doughnut-Chart
- 🟢 Grün = Gewinn
- 🔴 Rot = Verlust
- ⚫ Grau = Trade Failed

**Wenn nur 2 Kategorien:**
- Browser-Cache leeren!
- `dashboard.js` Version prüfen:
  ```bash
  grep "Trade Failed" /root/memero/monitoring/static/js/dashboard.js
  # Sollte Treffer zeigen
  ```

---

#### 8. Design dunkel prüfen

**Erwartete Farben:**
- Hintergrund: Fast schwarz (#0a0a0f)
- Karten: Dunkelgrau transparent
- Buttons: Indigo/Grün/Rot (nicht Pink/Lila)

**Wenn noch alte Farben:**
```bash
# CSS Version prüfen:
head -30 /root/memero/monitoring/static/css/dashboard.css

# Sollte zeigen:
--dark-bg: #0a0a0f;
--primary-color: #4f46e5;
```

**Falls falsch:**
- Browser-Cache leeren! (Strg+Shift+R)
- Browser DevTools → Network → dashboard.css → Status 200?

---

## Häufige Fehler

### ❌ "Wallet-Adresse wird nicht angezeigt"

**Ursache:** `.env` wird nicht geladen

**Lösung:**
```bash
pip install python-dotenv
systemctl restart memero-monitor  # oder ./start_monitor.sh
```

**Test:**
```python
# In Python-Shell:
from dotenv import load_dotenv
import os
load_dotenv('/root/memero/.env')
print(os.getenv('WALLET_PUBLIC_KEY'))
# Sollte Adresse ausgeben
```

---

### ❌ "Modal öffnet sich nicht"

**Ursache:** JavaScript nicht geladen oder Browser-Cache

**Lösung:**
1. F12 → Console → Fehler?
2. Strg+Shift+R (Hard Reload)
3. `curl http://localhost:5000/static/js/dashboard.js | grep showBotControlModal`
   - Sollte Funktion finden

---

### ❌ "Bot startet nicht"

**Ursache 1:** `start.sh` nicht ausführbar
```bash
chmod +x /root/memero/start.sh
```

**Ursache 2:** Falsche Pfade in `bot_control.py`
```bash
python3 -c "
from monitoring.config import BOT_START_SCRIPT, BOT_MAIN_FILE
print(f'START_SCRIPT: {BOT_START_SCRIPT}')
print(f'MAIN_FILE: {BOT_MAIN_FILE}')
import os
print(f'start.sh exists: {os.path.exists(BOT_START_SCRIPT)}')
print(f'main.py exists: {os.path.exists(BOT_MAIN_FILE)}')
"
```

---

### ❌ "Passwort wird nicht akzeptiert"

**Ursache:** Tippfehler oder falsches Passwort

**Korrektes Passwort:** `f1f3f4escpaulmarcschnee`

**Test:**
```bash
python3 -c "
from monitoring.config import BOT_CONTROL_PASSWORD
print(f'Gespeichertes Passwort: {BOT_CONTROL_PASSWORD}')
"
```

---

### ❌ "Chart zeigt nur 2 Kategorien"

**Ursache:** Alte JavaScript-Version im Browser-Cache

**Lösung:**
1. Browser: Strg+Shift+R
2. Server: `grep "Trade Failed" monitoring/static/js/dashboard.js`
   - MUSS Treffer zeigen!
3. Browser DevTools → Application → Clear Storage → Clear Site Data

---

## Debug-Befehle auf dem Server

```bash
# 1. Git Status prüfen
cd /root/memero
git log -1 --oneline
# Sollte zeigen: "✨ Feature: Bot Control + Dashboard Improvements"

# 2. Dateien vorhanden?
ls -la monitoring/bot_control.py
# Sollte existieren (237 Zeilen)

# 3. Monitoring-Prozess läuft?
ps aux | grep monitor.py
# Sollte Prozess zeigen

# 4. Port offen?
netstat -tulpn | grep 5000
# Sollte zeigen: 0.0.0.0:5000

# 5. Logs checken
tail -f monitoring/monitor.log  # falls vorhanden

# 6. API direkt testen
curl -s http://localhost:5000/api/bot/status | python3 -m json.tool

# 7. Dependencies installiert?
pip list | grep -E "psutil|python-dotenv"
```

---

## Wenn GAR NICHTS funktioniert

**Nuclear Option: Komplett neu installieren**

```bash
cd /root/memero

# Backup
cp .env .env.backup

# Alles neu pullen
git reset --hard HEAD
git pull

# Monitoring neu installieren
cd monitoring
pip install -r ../requirements.txt
pip install psutil python-dotenv

# .env wiederherstellen
cp ../.env.backup ../.env

# Neu starten
pkill -f monitor.py
../start_monitor.sh
```

Dann im Browser:
1. Alle Browser-Tabs schließen
2. Browser komplett beenden
3. Browser neu starten
4. http://server:5000 → Hard Reload (Strg+Shift+R)

---

## Support Checklist

Wenn du Hilfe brauchst, sende diese Infos:

```bash
# System Info
uname -a
python3 --version

# Git Info
cd /root/memero
git log -1
git status

# File Hashes
md5sum monitoring/static/js/dashboard.js
md5sum monitoring/static/css/dashboard.css
md5sum monitoring/bot_control.py

# Running Processes
ps aux | grep -E "main.py|monitor.py"

# Port Status
netstat -tulpn | grep 5000

# API Test
curl -s http://localhost:5000/api/bot/status

# Browser Console Errors (Screenshot)
# Network Tab (Screenshot)
```
