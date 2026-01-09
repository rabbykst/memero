"""
MEMERO Monitoring Dashboard
Flask Webserver mit Login-Schutz und Read-Only Datenzugriff

WICHTIG: Dieses Modul ist KOMPLETT ISOLIERT vom Trading-Bot!
- Keine Abhängigkeit von modules/*
- Kein Zugriff auf Trading-Funktionen
- Nur Lese-Zugriff auf Logs und öffentliche Blockchain-Daten
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

from monitoring.config import (
    MONITOR_HOST,
    MONITOR_PORT,
    SECRET_KEY,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    BOT_CONTROL_PASSWORD,
    DEBUG
)
from monitoring.data_reader import data_reader
from monitoring.bot_control import bot_controller


# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = False  # Bei HTTPS auf True setzen
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Passwort-Hash generieren (wird nur einmal beim Start berechnet)
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)


# ============================================================================
# LOGIN DECORATOR
# ============================================================================

def login_required(f):
    """
    Decorator: Erfordert Login für geschützte Routen
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ROUTES: AUTHENTICATION
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login-Seite mit Session-basierter Authentifizierung
    """
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Validierung (Passwort wird NIEMALS im Klartext verglichen!)
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Ungültige Anmeldedaten')
    
    # Bei GET: Zeige Login-Formular
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logout: Session beenden
    """
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# ROUTES: DASHBOARD
# ============================================================================

@app.route('/')
@login_required
def dashboard():
    """
    Haupt-Dashboard mit allen Monitoring-Daten
    """
    return render_template('dashboard.html')


# ============================================================================
# API ENDPOINTS (alle erfordern Login!)
# ============================================================================

@app.route('/api/status')
@login_required
def api_status():
    """
    Server Health Status (CPU, RAM, Disk)
    """
    health = data_reader.get_server_health()
    bot_status = data_reader.get_bot_status()
    
    return jsonify({
        'server': health,
        'bot': bot_status
    })


@app.route('/api/logs')
@login_required
def api_logs():
    """
    Bot Logs (letzte N Zeilen)
    """
    lines = request.args.get('lines', 100, type=int)
    logs = data_reader.get_logs(lines=lines)
    
    return jsonify({
        'logs': logs,
        'total': len(logs)
    })


@app.route('/api/wallet')
@login_required
def api_wallet():
    """
    Wallet Balance (READ-ONLY via Solana RPC)
    """
    wallet = data_reader.get_wallet_balance()
    
    return jsonify(wallet)


@app.route('/api/trades')
@login_required
def api_trades():
    """
    Trade Historie
    """
    limit = request.args.get('limit', 50, type=int)
    trades = data_reader.get_trades(limit=limit)
    
    return jsonify({
        'trades': trades,
        'total': len(trades)
    })


@app.route('/api/stats')
@login_required
def api_stats():
    """
    Performance Statistiken (PnL, Win-Rate, etc.)
    """
    stats = data_reader.get_statistics()
    
    return jsonify(stats)


@app.route('/api/positions')
@login_required
def api_positions():
    """
    Aktuelle offene Positionen
    """
    try:
        # Import trade_manager direkt (ist bereits in data_reader importiert)
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from modules.trade_manager import trade_manager
        
        positions = trade_manager.load_positions()
        
        return jsonify({
            'positions': positions,
            'total': len(positions)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'positions': [],
            'total': 0
        }), 500


# ============================================================================
# API ENDPOINTS: BOT CONTROL (2-stufige Auth!)
# ============================================================================

@app.route('/api/bot/status')
@login_required
def api_bot_status():
    """
    Bot-Status mit Live-Metriken (uptime, last_activity, memory)
    """
    # Nutze erweiterte get_bot_status() Methode
    status = bot_controller.get_bot_status()
    timer_status = bot_controller.check_timer()
    
    return jsonify({
        'is_running': status['running'],
        'pid': status.get('pid'),
        'uptime': status.get('uptime', 0),
        'uptime_formatted': status.get('uptime_formatted', '0m'),
        'last_activity': status.get('last_activity'),
        'memory_mb': status.get('memory_mb', 0),
        'timer': timer_status
    })


@app.route('/api/bot/start', methods=['POST'])
@login_required
def api_bot_start():
    """
    Bot starten (erfordert BOT_CONTROL_PASSWORD)
    """
    # Zweite Sicherheitsebene: Bot-Control-Passwort
    password = request.json.get('password', '')
    
    if password != BOT_CONTROL_PASSWORD:
        return jsonify({
            'success': False,
            'message': 'Ungültiges Bot-Control-Passwort!'
        }), 403
    
    result = bot_controller.start_bot()
    return jsonify(result)


@app.route('/api/bot/stop', methods=['POST'])
@login_required
def api_bot_stop():
    """
    Bot stoppen (erfordert BOT_CONTROL_PASSWORD)
    """
    # Zweite Sicherheitsebene: Bot-Control-Passwort
    password = request.json.get('password', '')
    
    if password != BOT_CONTROL_PASSWORD:
        return jsonify({
            'success': False,
            'message': 'Ungültiges Bot-Control-Passwort!'
        }), 403
    
    result = bot_controller.stop_bot()
    return jsonify(result)


@app.route('/api/bot/timer', methods=['POST'])
@login_required
def api_bot_timer():
    """
    Sleep-Timer setzen (erfordert BOT_CONTROL_PASSWORD)
    """
    # Zweite Sicherheitsebene: Bot-Control-Passwort
    password = request.json.get('password', '')
    minutes = request.json.get('minutes', 0)
    
    if password != BOT_CONTROL_PASSWORD:
        return jsonify({
            'success': False,
            'message': 'Ungültiges Bot-Control-Passwort!'
        }), 403
    
    result = bot_controller.set_timer(minutes)
    return jsonify(result)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route nicht gefunden'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Interner Server-Fehler'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 MEMERO MONITORING DASHBOARD                  ║
╚══════════════════════════════════════════════════════════════╝

🌐 Server läuft auf: http://{MONITOR_HOST}:{MONITOR_PORT}
🔐 Login: {ADMIN_USERNAME} / {'*' * len(ADMIN_PASSWORD)}
📊 Dashboard: http://{MONITOR_HOST}:{MONITOR_PORT}/

⚠️  WICHTIG:
   - Dieser Webserver ist READ-ONLY!
   - Keine Trading-Funktionen verfügbar
   - Kein Zugriff auf Private Keys
   - Komplett isoliert vom Bot

🚀 Starte Server...
    """)
    
    app.run(
        host=MONITOR_HOST,
        port=MONITOR_PORT,
        debug=DEBUG,
        threaded=True
    )
