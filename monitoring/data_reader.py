"""
MEMERO Monitoring - Data Reader
Liest Bot-Daten aus Logs, JSON-Dateien und Solana RPC

WICHTIG: Dieser Code hat NUR LESE-ZUGRIFF!
- Keine Trades ausführen
- Keine Wallet-Transaktionen
- Keine Log-Dateien verändern
- Keine Bot-Konfiguration ändern
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import psutil
import pytz
import sys

# Füge Parent-Directory zum Path hinzu für trade_manager Import
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.trade_manager import trade_manager

from monitoring.config import (
    BOT_LOG_FILE,
    SOLANA_RPC_URL,
    WALLET_PUBLIC_KEY,
    TRADES_DB_FILE,
    MAX_LOG_LINES,
    TIMEZONE
)


class DataReader:
    """
    Read-Only Datenzugriff für Monitoring
    """
    
    def __init__(self):
        self.timezone = pytz.timezone(TIMEZONE)
    
    # ========================================================================
    # SERVER HEALTH
    # ========================================================================
    
    def get_server_health(self) -> Dict:
        """
        Liest Server-Ressourcen (CPU, RAM, Disk)
        
        Returns:
            Dict mit cpu_percent, ram_percent, disk_percent, etc.
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': round(cpu_percent, 1),
                'ram_percent': round(ram.percent, 1),
                'ram_used_gb': round(ram.used / (1024**3), 2),
                'ram_total_gb': round(ram.total / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'status': 'healthy' if cpu_percent < 80 and ram.percent < 90 else 'warning'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    # ========================================================================
    # BOT LOGS
    # ========================================================================
    
    def get_logs(self, lines: int = 100) -> List[Dict]:
        """
        Liest die letzten N Zeilen aus der Bot-Log-Datei
        
        Args:
            lines: Anzahl der Zeilen (max MAX_LOG_LINES)
            
        Returns:
            List von Log-Einträgen mit timestamp, level, message
        """
        try:
            if not BOT_LOG_FILE.exists():
                return [{'timestamp': 'N/A', 'level': 'WARNING', 'message': 'Log-Datei nicht gefunden'}]
            
            lines = min(lines, MAX_LOG_LINES)
            
            with open(BOT_LOG_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:]
            
            # Parse Log-Zeilen (Format: "2026-01-07 18:28:05 | INFO | ...")
            parsed_logs = []
            log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(\w+)\s*\|\s*(.+)$'
            
            for line in last_lines:
                match = re.match(log_pattern, line.strip())
                if match:
                    timestamp, level, message = match.groups()
                    parsed_logs.append({
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    })
                else:
                    # Zeile ohne Standard-Format (z.B. Multiline)
                    parsed_logs.append({
                        'timestamp': '',
                        'level': 'DEBUG',
                        'message': line.strip()
                    })
            
            return parsed_logs
            
        except Exception as e:
            return [{'timestamp': 'ERROR', 'level': 'ERROR', 'message': f'Fehler beim Log-Lesen: {e}'}]
    
    # ========================================================================
    # WALLET BALANCE
    # ========================================================================
    
    def get_wallet_balance(self) -> Dict:
        """
        Liest Wallet-Balance über Solana RPC (READ-ONLY!)
        
        Returns:
            Dict mit balance_sol, balance_usd (geschätzt), address
        """
        try:
            if not WALLET_PUBLIC_KEY:
                return {
                    'error': 'WALLET_PUBLIC_KEY nicht in .env konfiguriert',
                    'balance_sol': 0,
                    'address': 'N/A'
                }
            
            # Solana RPC Call: getBalance
            payload = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'getBalance',
                'params': [WALLET_PUBLIC_KEY]
            }
            
            response = requests.post(SOLANA_RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'result' in data and 'value' in data['result']:
                lamports = data['result']['value']
                balance_sol = lamports / 1_000_000_000
                
                # Geschätzter USD-Wert (würde in Produktion SOL/USD-Preis abfragen)
                balance_usd = balance_sol * 100  # Placeholder: 1 SOL = $100
                
                return {
                    'balance_sol': round(balance_sol, 6),
                    'balance_usd': round(balance_usd, 2),
                    'address': WALLET_PUBLIC_KEY,
                    'last_update': datetime.now(self.timezone).isoformat()
                }
            else:
                return {'error': 'Keine Balance-Daten in RPC Response', 'balance_sol': 0}
                
        except Exception as e:
            return {'error': f'RPC Error: {e}', 'balance_sol': 0, 'address': WALLET_PUBLIC_KEY or 'N/A'}
    
    # ========================================================================
    # TRADES
    # ========================================================================
    
    def get_trades(self, limit: int = 50) -> List[Dict]:
        """
        Liest Trade-Historie aus trades.json via trade_manager
        
        Args:
            limit: Max Anzahl Trades
            
        Returns:
            List von Trade-Objekten
        """
        try:
            # Lade Trades aus trade_manager (nutzt trades.json)
            all_trades = trade_manager.load_trades()
            return all_trades[-limit:] if all_trades else []
            
        except Exception as e:
            return [{'error': f'Fehler beim Trade-Lesen: {e}'}]
    
    # ========================================================================
    # STATISTICS & PERFORMANCE
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """
        Berechnet Performance-Statistiken aus echten Trade-Daten via trade_manager
        
        Returns:
            Dict mit total_trades, win_rate, total_pnl, avg_profit, etc.
        """
        try:
            # Nutze trade_manager für echte Performance-Daten
            stats = trade_manager.get_trade_stats()
            all_trades = trade_manager.load_trades()
            
            # Berechne zusätzliche Metriken
            completed_trades = [
                t for t in all_trades 
                if t.get('type') == 'SELL' and t.get('status') == 'SUCCESS'
            ]
            
            # Best/Worst Trade aus profit_percent
            profits = [t.get('profit_percent', 0) for t in completed_trades]
            best_trade = max(profits) if profits else 0
            worst_trade = min(profits) if profits else 0
            
            # Durchschnitt nur von completed trades
            avg_profit = (stats['total_profit_sol'] / len(completed_trades)) if completed_trades else 0
            
            # Heute's PnL (Filter nach Datum)
            today = datetime.now(self.timezone).date()
            today_trades = [
                t for t in completed_trades
                if t.get('timestamp', '').startswith(str(today))
            ]
            today_pnl = sum(t.get('profit_sol', 0) for t in today_trades)
            
            return {
                'total_trades': stats['total_trades'],
                'successful_trades': stats['successful_trades'],
                'loss_trades': stats['losses'],
                'failed_trades': stats['failed_trades'],
                'win_rate': round(stats['win_rate'], 2),
                'total_pnl': round(stats['total_profit_sol'], 6),
                'avg_profit': round(avg_profit, 6),
                'today_pnl': round(today_pnl, 6),
                'best_trade': round(best_trade, 2),
                'worst_trade': round(worst_trade, 2),
                'wins': stats['wins']  # Für Win/Loss/Failed Chart
            }
            
        except Exception as e:
            return {'error': f'Fehler bei Statistik-Berechnung: {e}'}
    
    # ========================================================================
    # BOT STATUS
    # ========================================================================
    
    def get_bot_status(self) -> Dict:
        """
        Prüft ob der Trading-Bot läuft
        
        Returns:
            Dict mit is_running, last_activity, uptime
        """
        try:
            if not BOT_LOG_FILE.exists():
                return {'is_running': False, 'last_activity': 'N/A'}
            
            # Lese letzte Log-Zeile
            logs = self.get_logs(lines=1)
            if logs:
                last_log = logs[-1]
                last_timestamp = last_log.get('timestamp', '')
                
                # Parse Timestamp
                if last_timestamp:
                    last_time = datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S')
                    last_time = self.timezone.localize(last_time)
                    now = datetime.now(self.timezone)
                    
                    # Bot läuft, wenn letzte Aktivität < 10 Minuten
                    time_diff = (now - last_time).total_seconds()
                    is_running = time_diff < 600  # 10 Minuten
                    
                    return {
                        'is_running': is_running,
                        'last_activity': last_timestamp,
                        'seconds_since_activity': int(time_diff)
                    }
            
            return {'is_running': False, 'last_activity': 'N/A'}
            
        except Exception as e:
            return {'is_running': False, 'error': str(e)}


# Singleton Instance
data_reader = DataReader()
