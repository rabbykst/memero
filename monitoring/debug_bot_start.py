#!/usr/bin/env python3
"""
Debug-Script für Bot-Start-Probleme
Führe dieses Script auf dem Server aus um zu prüfen warum der Bot nicht startet
"""

import sys
import os
from pathlib import Path

# Füge monitoring zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("MEMERO Bot-Start Diagnose")
print("=" * 70)

# 1. Environment prüfen
print("\n1️⃣  Environment Check:")
print("-" * 70)

from monitoring.config import BASE_DIR, BOT_MAIN_FILE, BOT_START_SCRIPT

print(f"✓ BASE_DIR: {BASE_DIR}")
print(f"  Exists: {BASE_DIR.exists()}")

print(f"\n✓ BOT_MAIN_FILE: {BOT_MAIN_FILE}")
print(f"  Exists: {BOT_MAIN_FILE.exists()}")

print(f"\n✓ BOT_START_SCRIPT: {BOT_START_SCRIPT}")
print(f"  Exists: {BOT_START_SCRIPT.exists()}")
print(f"  Executable: {os.access(BOT_START_SCRIPT, os.X_OK)}")

# 2. Python Executables prüfen
print("\n2️⃣  Python Executables:")
print("-" * 70)

venv_python = BASE_DIR / 'venv' / 'bin' / 'python3'
env_python = BASE_DIR / 'env' / 'bin' / 'python3'

print(f"venv/bin/python3: {venv_python.exists()}")
if venv_python.exists():
    print(f"  → {venv_python}")

print(f"env/bin/python3: {env_python.exists()}")
if env_python.exists():
    print(f"  → {env_python}")

# 3. .env Datei prüfen
print("\n3️⃣  Environment Variables (.env):")
print("-" * 70)

env_file = BASE_DIR / '.env'
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    required_vars = [
        'OPENROUTER_API_KEY',
        'WALLET_PRIVATE_KEY',
        'WALLET_PUBLIC_KEY',
        'SOLANA_RPC_URL'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Nur erste/letzte 4 Zeichen zeigen
            if len(value) > 10:
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = "***"
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ❌ {var}: FEHLT!")

# 4. Dependencies prüfen
print("\n4️⃣  Python Dependencies:")
print("-" * 70)

try:
    import solana
    print(f"✓ solana: {solana.__version__}")
except ImportError as e:
    print(f"❌ solana: {e}")

try:
    import openai
    print(f"✓ openai: {openai.__version__}")
except ImportError as e:
    print(f"❌ openai: {e}")

try:
    import requests
    print(f"✓ requests: {requests.__version__}")
except ImportError as e:
    print(f"❌ requests: {e}")

# 5. Bot-Prozess prüfen
print("\n5️⃣  Aktueller Bot-Status:")
print("-" * 70)

from monitoring.bot_control import bot_controller

is_running = bot_controller.is_bot_running()
pid = bot_controller.get_bot_pid()

print(f"Bot läuft: {is_running}")
if pid:
    print(f"Bot PID: {pid}")
    
    import psutil
    try:
        proc = psutil.Process(pid)
        print(f"  Prozess-Name: {proc.name()}")
        print(f"  Cmdline: {' '.join(proc.cmdline())}")
        print(f"  Working Dir: {proc.cwd()}")
        print(f"  CPU: {proc.cpu_percent(interval=0.1)}%")
        print(f"  RAM: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"  ❌ Prozess-Info-Fehler: {e}")

# 6. Test Bot-Start (DRY RUN)
print("\n6️⃣  Bot-Start Test (Simulation):")
print("-" * 70)

print("\nDer Bot würde mit folgendem Befehl gestartet:")

if venv_python.exists():
    python_exe = venv_python
elif env_python.exists():
    python_exe = env_python
else:
    python_exe = "python3"

print(f"  {python_exe} {BOT_MAIN_FILE}")
print(f"  Working Directory: {BASE_DIR}")
print(f"  Output Log: {BASE_DIR / 'bot_output.log'}")

# 7. Log-File prüfen
print("\n7️⃣  Letzte Bot-Logs:")
print("-" * 70)

log_file = BASE_DIR / 'bot_output.log'
if log_file.exists():
    print(f"Log-Datei: {log_file}")
    print(f"Größe: {log_file.stat().st_size} bytes")
    print("\nLetzte 15 Zeilen:")
    print("-" * 70)
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines[-15:]:
            print(line.rstrip())
else:
    print("❌ Keine bot_output.log gefunden")

# 8. Empfehlungen
print("\n" + "=" * 70)
print("📋 EMPFEHLUNGEN:")
print("=" * 70)

issues = []

if not BOT_MAIN_FILE.exists():
    issues.append("❌ main.py nicht gefunden - prüfe Installation")

if not env_file.exists():
    issues.append("❌ .env Datei fehlt - kopiere .env.example zu .env")

if not venv_python.exists() and not env_python.exists():
    issues.append("⚠️  Keine Virtual Environment gefunden - installiere Dependencies")

if not is_running and log_file.exists():
    issues.append("⚠️  Bot läuft nicht - prüfe bot_output.log für Fehler")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ Keine offensichtlichen Probleme gefunden")

print("\n" + "=" * 70)
print("💡 Zum manuellen Testen:")
print("=" * 70)
print(f"cd {BASE_DIR}")
if venv_python.exists():
    print("source venv/bin/activate")
elif env_python.exists():
    print("source env/bin/activate")
print("python main.py")
print("\n")
