# MEMERO Monitoring Dashboard

**Komplett isoliertes, read-only Monitoring-Interface für den MEMERO Trading Bot**

## 🎯 Was ist das Monitoring?

Ein leichtgewichtiges Web-Dashboard, das vollständig vom Trading-Bot getrennt ist und nur Lesezugriff auf Bot-Daten hat. Keine Trading-Funktionen, kein Wallet-Zugriff mit Schreibrechten.

## ✨ Features

- 🔐 **Login-geschützt** (admin/yummyringtoneremix)
- 📊 **Echtzeit-Monitoring** (Auto-Refresh alle 10 Sekunden)
- 💰 **Wallet Balance** (READ-ONLY via Solana RPC)
- 📈 **Performance-Statistiken** (PnL, Win-Rate, Trades)
- 📋 **Live Logs** (letzte 100 Zeilen aus bot.log)
- 🖥️ **Server Health** (CPU, RAM, Disk-Auslastung)
- 📊 **Charts** (Performance-Kurve, Win/Loss-Verteilung)

## 🚀 Quick Start

### 1. Dependencies installieren

```bash
pip install flask werkzeug psutil
```

Oder:

```bash
pip install -r requirements.txt
```

### 2. Konfiguration (.env erweitern)

Füge diese Zeilen zu deiner `.env` hinzu:

```bash
# Monitoring Dashboard
MONITOR_HOST=0.0.0.0          # 0.0.0.0 für VPS-Zugriff
MONITOR_PORT=5000             # Port für Webserver
WALLET_PUBLIC_KEY=3UMApZc9mgze9QGpaifquc4VzyjiBGp2DALhwuqjnHZD
```

### 3. Monitoring starten

```bash
./start_monitor.sh
```

Oder manuell:

```bash
python3 -m monitoring.monitor
```

### 4. Dashboard öffnen

**Lokal:**
```
http://localhost:5000
```

**VPS (öffentliche IP):**
```
http://YOUR_SERVER_IP:5000
```

**Login:**
- Username: `admin`
- Passwort: `yummyringtoneremix`

## 📁 Struktur

```
monitoring/
├── monitor.py          # Flask Webserver (Haupt-App)
├── config.py           # Monitoring-Konfiguration
├── data_reader.py      # Read-Only Datenzugriff
├── templates/
│   ├── login.html      # Login-Seite
│   └── dashboard.html  # Haupt-Dashboard
└── static/
    ├── css/
    │   └── dashboard.css
    └── js/
        └── dashboard.js
```

## 🔒 Sicherheit

### Was das Monitoring KANN:
✅ Logs lesen (`bot.log`)  
✅ Wallet-Balance abfragen (Solana RPC)  
✅ Server-Ressourcen anzeigen (CPU/RAM/Disk)  
✅ Trade-Historie aus Logs parsen  

### Was das Monitoring NICHT KANN:
❌ Trades ausführen  
❌ Wallet-Transaktionen signieren  
❌ Private Keys lesen  
❌ Bot-Konfiguration ändern  
❌ Log-Dateien verändern  

### Login-Schutz:
- Session-basiertes Login mit Werkzeug
- Passwort wird gehashed (PBKDF2-SHA256)
- Passwort niemals im Klartext im Frontend
- Session-Cookie mit HttpOnly-Flag

## 🌐 VPS-Deployment

### Firewall-Regel (Port öffnen)

```bash
# Ubuntu/Debian
sudo ufw allow 5000/tcp
sudo ufw reload

# Oder direkt mit iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### Im Hintergrund laufen lassen (Screen/Tmux)

**Option 1: Screen**
```bash
screen -S memero-monitor
./start_monitor.sh
# Ctrl+A, dann D zum Detachen
```

**Option 2: Tmux**
```bash
tmux new -s monitor
./start_monitor.sh
# Ctrl+B, dann D zum Detachen
```

**Option 3: Systemd Service**
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
ExecStart=/usr/bin/python3 -m monitoring.monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable memero-monitor
sudo systemctl start memero-monitor
sudo systemctl status memero-monitor
```

## 🎨 Design

- **Branding:** MEMERO Logo, Lila-Gradient (#667eea → #764ba2)
- **Stil:** Futuristisch, glassmorphism, clean
- **Responsive:** Mobile-friendly
- **Dark Theme:** Dunkler Hintergrund für lange Sessions

## 📊 API Endpunkte

Alle Endpunkte erfordern Login!

| Endpunkt | Beschreibung |
|----------|-------------|
| `GET /` | Dashboard (HTML) |
| `GET /login` | Login-Seite |
| `GET /logout` | Logout |
| `GET /api/status` | Bot & Server Status |
| `GET /api/logs?lines=100` | Bot Logs |
| `GET /api/wallet` | Wallet Balance |
| `GET /api/trades?limit=50` | Trade Historie |
| `GET /api/stats` | Performance Stats |

## 🔧 Konfiguration

Alle Einstellungen in `monitoring/config.py`:

```python
MONITOR_HOST = '0.0.0.0'           # Bind-Adresse
MONITOR_PORT = 5000                # Port
ADMIN_USERNAME = 'admin'           # Login Username
ADMIN_PASSWORD = 'yummyringtoneremix'  # Login Passwort
BOT_LOG_FILE = '../bot.log'        # Pfad zur Log-Datei
MAX_LOG_LINES = 500                # Max Log-Zeilen
AUTO_REFRESH_INTERVAL = 10         # Refresh (Sekunden)
```

## ⚠️ Wichtig

- **Keine Abhängigkeit vom Bot:** Das Monitoring kann laufen, auch wenn der Bot gestoppt ist
- **Read-Only:** Absolut kein Schreibzugriff auf irgendwelche Bot-Daten
- **Isoliert:** Nutzt KEINE Bot-Module (`modules/*`)
- **VPS-sicher:** Bindet auf `0.0.0.0` für öffentlichen Zugriff

## 🐛 Troubleshooting

**Port bereits belegt:**
```bash
# Anderen Port in .env setzen
MONITOR_PORT=8080
```

**Firewall blockiert:**
```bash
sudo ufw allow 5000/tcp
```

**Bot.log nicht gefunden:**
```bash
# In monitoring/config.py Pfad prüfen
BOT_LOG_FILE = Path(__file__).parent.parent / 'bot.log'
```

## 📝 Changelog

**v1.0.0 (2026-01-07)**
- ✅ Initial Release
- ✅ Login-System mit Session-Auth
- ✅ Dashboard mit Echtzeit-Updates
- ✅ Charts (Chart.js)
- ✅ MEMERO Branding

---

**Made with 💜 for MEMERO Trading Bot**
