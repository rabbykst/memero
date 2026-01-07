# MEMERO Monitoring Dashboard - Installation & Setup

## 📋 Schritt-für-Schritt Anleitung für VPS-Deployment

### 1️⃣ Dependencies installieren

```bash
cd /path/to/memero
pip install flask werkzeug psutil
```

Oder alle Dependencies auf einmal:

```bash
pip install -r requirements.txt
```

### 2️⃣ .env Konfiguration erweitern

Öffne deine `.env` Datei und füge hinzu:

```bash
# Monitoring Dashboard Konfiguration
MONITOR_HOST=0.0.0.0          # 0.0.0.0 = öffentlich erreichbar
MONITOR_PORT=5000             # Port für Webserver
MONITOR_DEBUG=False           # Produktions-Modus
WALLET_PUBLIC_KEY=3UMApZc9mgze9QGpaifquc4VzyjiBGp2DALhwuqjnHZD
```

> ⚠️ **WICHTIG:** `WALLET_PUBLIC_KEY` ist NUR deine **PUBLIC KEY** (nicht der Private Key!)
> Diese wird nur für Balance-Abfragen verwendet, kein Schreibzugriff.

### 3️⃣ Firewall konfigurieren (VPS)

```bash
# Ubuntu/Debian mit UFW
sudo ufw allow 5000/tcp
sudo ufw reload
sudo ufw status

# Oder mit iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### 4️⃣ Monitoring starten

**Option A: Direkt im Terminal**
```bash
./start_monitor.sh
```

**Option B: Im Hintergrund mit Screen**
```bash
screen -S memero-monitor
./start_monitor.sh
# Ctrl+A, dann D zum Detachen
```

**Option C: Im Hintergrund mit Tmux**
```bash
tmux new -s monitor
./start_monitor.sh
# Ctrl+B, dann D zum Detachen
```

**Option D: Als Systemd Service** (empfohlen für Production)
```bash
sudo nano /etc/systemd/system/memero-monitor.service
```

Inhalt:
```ini
[Unit]
Description=MEMERO Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/memero
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m monitoring.monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Service aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable memero-monitor
sudo systemctl start memero-monitor
sudo systemctl status memero-monitor
```

### 5️⃣ Dashboard aufrufen

**Lokal testen:**
```
http://localhost:5000
```

**Von außen (VPS):**
```
http://YOUR_SERVER_IP:5000
```

Oder mit Domain:
```
http://memero.yourdomain.com:5000
```

### 6️⃣ Login

- **Username:** `admin`
- **Passwort:** `yummyringtoneremix`

> 💡 **Tipp:** Du kannst Username/Passwort in `monitoring/config.py` ändern.

---

## 🔍 Überprüfung

### Service Status prüfen
```bash
# Systemd Service
sudo systemctl status memero-monitor

# Prozess suchen
ps aux | grep monitor.py

# Port prüfen
sudo netstat -tulpn | grep 5000
```

### Logs ansehen
```bash
# Systemd Logs
sudo journalctl -u memero-monitor -f

# Direkt im Terminal (wenn nicht als Service)
# Die Ausgabe erscheint direkt im Terminal
```

### Bot-Status prüfen
```bash
# Haupt-Bot läuft?
ps aux | grep main.py

# Bot-Logs
tail -f bot.log
```

---

## 🌐 Nginx Reverse Proxy (Optional)

Für saubere URLs ohne Port-Angabe:

```nginx
server {
    listen 80;
    server_name memero.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Mit SSL (Let's Encrypt):
```bash
sudo certbot --nginx -d memero.yourdomain.com
```

---

## 🛡️ Sicherheit

### Passwort ändern

In `monitoring/config.py`:
```python
ADMIN_USERNAME = 'dein_username'
ADMIN_PASSWORD = 'dein_sicheres_passwort'
```

### Firewall-Zugriff einschränken

Nur bestimmte IPs erlauben:
```bash
sudo ufw delete allow 5000/tcp
sudo ufw allow from YOUR_HOME_IP to any port 5000
```

### HTTPS mit SSL

Empfohlen mit Nginx Reverse Proxy + Let's Encrypt (siehe oben).

---

## 🐛 Troubleshooting

### "Address already in use"
Port 5000 ist belegt:
```bash
# Anderen Port verwenden
echo "MONITOR_PORT=8080" >> .env

# Oder belegten Prozess beenden
sudo lsof -t -i:5000 | xargs kill -9
```

### "Connection refused"
Firewall blockiert:
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

### "bot.log not found"
Log-Datei existiert nicht:
```bash
# Bot muss mindestens einmal gelaufen sein
touch bot.log

# Oder Bot starten
./start.sh
```

### "Wallet Balance Error"
Public Key nicht konfiguriert:
```bash
# In .env setzen
echo "WALLET_PUBLIC_KEY=YOUR_PUBLIC_KEY" >> .env
```

---

## 📊 Features im Detail

### Verfügbare Daten

| Feature | Beschreibung | Quelle |
|---------|-------------|--------|
| Bot Status | Läuft / Gestoppt | Letzte Log-Aktivität |
| Server Health | CPU/RAM/Disk | psutil |
| Wallet Balance | SOL & USD | Solana RPC |
| Performance | PnL, Win-Rate | Trade-Logs parsen |
| Trades | Historie | bot.log parsen |
| Logs | Letzte 100 Zeilen | bot.log lesen |

### Auto-Refresh

Dashboard aktualisiert sich **alle 10 Sekunden** automatisch:
- Server Health
- Bot Status
- Wallet Balance
- Performance Stats
- Logs

Konfigurierbar in `monitoring/static/js/dashboard.js`:
```javascript
const REFRESH_INTERVAL = 10000; // in Millisekunden
```

---

## 🎨 Anpassungen

### Logo ändern

Platziere dein Logo in:
```
monitoring/static/img/logo.png
```

Dann in `templates/dashboard.html` referenzieren.

### Farben ändern

In `monitoring/static/css/dashboard.css`:
```css
:root {
    --primary-color: #667eea;     /* Deine Primärfarbe */
    --secondary-color: #764ba2;   /* Deine Sekundärfarbe */
    --success-color: #10b981;
    --danger-color: #ef4444;
}
```

### Zusätzliche Metriken

In `monitoring/data_reader.py` neue Funktionen hinzufügen:
```python
def get_custom_metric(self) -> Dict:
    # Deine eigene Logik
    return {'metric': 'value'}
```

Dann in `monitor.py` neuen Endpoint:
```python
@app.route('/api/custom')
@login_required
def api_custom():
    return jsonify(data_reader.get_custom_metric())
```

---

## ✅ Checkliste für Production

- [ ] Dependencies installiert (`pip install flask werkzeug psutil`)
- [ ] `.env` konfiguriert (MONITOR_HOST, PORT, WALLET_PUBLIC_KEY)
- [ ] Firewall-Port geöffnet (`sudo ufw allow 5000/tcp`)
- [ ] Systemd Service eingerichtet (optional, empfohlen)
- [ ] Dashboard erreichbar unter `http://SERVER_IP:5000`
- [ ] Login funktioniert (admin/yummyringtoneremix)
- [ ] Alle Dashboard-Bereiche zeigen Daten
- [ ] Auto-Refresh funktioniert
- [ ] Bot läuft parallel (main.py)
- [ ] Logs werden korrekt angezeigt

---

**Made with 💜 for MEMERO**

Bei Fragen: Prüfe [monitoring/README.md](README.md) oder die Haupt-Dokumentation.
