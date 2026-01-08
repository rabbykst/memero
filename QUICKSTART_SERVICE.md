# 🎉 24/7 Monitoring Service - Schnellanleitung

## Auf dem Server ausführen:

### 1. Code aktualisieren
```bash
cd /root/memero
git pull
```

### 2. Service installieren (einmalig)
```bash
cd monitoring
sudo ./install_service.sh
```

**Das war's!** ✅

---

## Was du jetzt hast:

✅ **Monitoring läuft 24/7** - auch wenn SSH abbricht  
✅ **Auto-Start** - startet nach Server-Reboot automatisch  
✅ **Auto-Restart** - startet sich selbst neu bei Crash  
✅ **Professionelles Logging** - alle Logs in `monitoring/monitor.log`  

---

## Dashboard öffnen:

```
http://<deine-server-ip>:5000
```

Login: `admin` / `yummyringtoneremix`

---

## Wichtige Befehle:

```bash
# Status prüfen
systemctl status memero-monitor

# Neu starten (nach Code-Updates)
sudo systemctl restart memero-monitor

# Stoppen
sudo systemctl stop memero-monitor

# Starten
sudo systemctl start memero-monitor

# Live-Logs anzeigen
journalctl -u memero-monitor -f

# Oder:
tail -f /root/memero/monitoring/monitor.log
```

---

## Nach Code-Updates (git pull):

```bash
cd /root/memero
git pull

# Neu starten
sudo systemctl restart memero-monitor

# Browser: Strg+Shift+R (Cache leeren)
```

---

## Troubleshooting:

### Service startet nicht?
```bash
# Diagnose:
journalctl -u memero-monitor -n 50

# Häufigste Ursache: Virtual Environment fehlt
cd /root/memero
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart memero-monitor
```

### Dashboard nicht erreichbar?
```bash
# Firewall öffnen:
sudo ufw allow 5000/tcp

# Port-Status prüfen:
sudo netstat -tulpn | grep 5000
```

---

## Service deinstallieren:

```bash
cd /root/memero/monitoring
sudo ./uninstall_service.sh
```

---

## Vollständige Dokumentation:

📖 [SERVICE_SETUP.md](SERVICE_SETUP.md) - Detaillierte Anleitung mit allen Optionen
