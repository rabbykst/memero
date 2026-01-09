"""
MEMERO Trading Bot - Trade Manager
Persistente Trade-Datenbank für Monitoring

Speichert alle Trades in trades.json:
- Entry Trades (BUY)
- Exit Trades (SELL)
- Trade Status
- Performance Metrics
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Pfade
TRADES_FILE = Path(__file__).parent.parent / 'trades.json'
POSITIONS_FILE = Path(__file__).parent.parent / 'positions.json'


class TradeType(Enum):
    """Trade Typ"""
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(Enum):
    """Trade Status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class ExitReason(Enum):
    """Exit Grund"""
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    TIMEOUT = "TIMEOUT"
    MANUAL = "MANUAL"


class TradeManager:
    """
    Verwaltet Trade-Historie und offene Positionen
    """
    
    def __init__(self):
        self.trades_file = TRADES_FILE
        self.positions_file = POSITIONS_FILE
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Erstellt Dateien falls nicht vorhanden"""
        if not self.trades_file.exists():
            self._save_trades([])
        if not self.positions_file.exists():
            self._save_positions({})
    
    # ========================================================================
    # TRADES
    # ========================================================================
    
    def save_trade(self, trade_data: Dict) -> bool:
        """
        Speichert einen Trade in trades.json
        
        Args:
            trade_data: Trade-Informationen mit allen Details
            
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            trades = self.load_trades()
            
            # Erstelle Trade-Eintrag
            trade_entry = {
                'id': len(trades) + 1,
                'timestamp': datetime.now().isoformat(),
                'type': trade_data.get('type', 'BUY'),
                'status': trade_data.get('status', 'PENDING'),
                'token_address': trade_data.get('token_address'),
                'symbol': trade_data.get('symbol'),
                'signature': trade_data.get('signature'),
                
                # Trade-Details
                'amount_sol': trade_data.get('amount_sol', 0),
                'amount_tokens': trade_data.get('amount_tokens', 0),
                'entry_price': trade_data.get('entry_price'),
                'exit_price': trade_data.get('exit_price'),
                
                # Performance
                'profit_sol': trade_data.get('profit_sol'),
                'profit_percent': trade_data.get('profit_percent'),
                
                # Exit Info
                'exit_reason': trade_data.get('exit_reason'),
                'error_message': trade_data.get('error_message'),
                
                # Analyst Info
                'confidence': trade_data.get('confidence'),
                'risk_score': trade_data.get('risk_score'),
                'reasoning': trade_data.get('reasoning')
            }
            
            trades.append(trade_entry)
            self._save_trades(trades)
            
            logger.info(f"Trade #{trade_entry['id']} gespeichert: {trade_entry['type']} {trade_entry['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Trades: {e}")
            return False
    
    def load_trades(self) -> List[Dict]:
        """
        Lädt alle Trades aus trades.json
        
        Returns:
            List[Dict]: Liste aller Trades
        """
        try:
            with open(self.trades_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Trades: {e}")
            return []
    
    def _save_trades(self, trades: List[Dict]):
        """Speichert Trades in Datei"""
        with open(self.trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
    
    def get_trade_stats(self) -> Dict:
        """
        Berechnet Statistiken aus Trade-Historie
        
        Returns:
            Dict: Performance-Metriken
        """
        trades = self.load_trades()
        
        if not trades:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'total_profit_sol': 0,
                'total_profit_percent': 0,
                'win_rate': 0,
                'wins': 0,
                'losses': 0
            }
        
        successful = [t for t in trades if t.get('status') == 'SUCCESS']
        failed = [t for t in trades if t.get('status') == 'FAILED']
        
        # Nur Trades mit Exit (vollständig)
        completed = [t for t in successful if t.get('exit_price') is not None]
        
        wins = [t for t in completed if (t.get('profit_percent') or 0) > 0]
        losses = [t for t in completed if (t.get('profit_percent') or 0) < 0]
        
        total_profit_sol = sum(t.get('profit_sol', 0) for t in completed)
        avg_profit_percent = sum(t.get('profit_percent', 0) for t in completed) / len(completed) if completed else 0
        
        return {
            'total_trades': len(trades),
            'successful_trades': len(successful),
            'failed_trades': len(failed),
            'completed_trades': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'total_profit_sol': round(total_profit_sol, 6),
            'avg_profit_percent': round(avg_profit_percent, 2),
            'win_rate': round((len(wins) / len(completed) * 100) if completed else 0, 1)
        }
    
    # ========================================================================
    # POSITIONS
    # ========================================================================
    
    def add_position(self, position_data: Dict) -> bool:
        """
        Fügt eine offene Position hinzu
        
        Args:
            position_data: Position-Informationen
            
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            positions = self.load_positions()
            
            token_address = position_data['token_address']
            
            position = {
                'token_address': token_address,
                'symbol': position_data.get('symbol'),
                'entry_timestamp': datetime.now().isoformat(),
                'entry_price': position_data.get('entry_price'),
                'amount_sol': position_data.get('amount_sol'),
                'amount_tokens': position_data.get('amount_tokens'),
                'signature': position_data.get('signature'),
                'confidence': position_data.get('confidence'),
                'risk_score': position_data.get('risk_score')
            }
            
            positions[token_address] = position
            self._save_positions(positions)
            
            logger.info(f"Position hinzugefügt: {position['symbol']} ({token_address[:8]}...)")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Position: {e}")
            return False
    
    def remove_position(self, token_address: str) -> bool:
        """
        Entfernt eine Position (nach Exit)
        
        Args:
            token_address: Token Contract Address
            
        Returns:
            bool: True wenn erfolgreich
        """
        try:
            positions = self.load_positions()
            
            if token_address in positions:
                del positions[token_address]
                self._save_positions(positions)
                logger.info(f"Position entfernt: {token_address[:8]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen der Position: {e}")
            return False
    
    def load_positions(self) -> Dict:
        """
        Lädt alle offenen Positionen
        
        Returns:
            Dict: {token_address: position_data}
        """
        try:
            with open(self.positions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Positionen: {e}")
            return {}
    
    def _save_positions(self, positions: Dict):
        """Speichert Positionen in Datei"""
        with open(self.positions_file, 'w') as f:
            json.dump(positions, f, indent=2)
    
    def update_position_pnl(self, token_address: str, current_price: float, pnl_percent: float):
        """
        Aktualisiert PnL einer Position
        
        Args:
            token_address: Token Address
            current_price: Aktueller Preis
            pnl_percent: Profit/Loss in Prozent
        """
        try:
            positions = self.load_positions()
            
            if token_address in positions:
                positions[token_address]['current_price'] = current_price
                positions[token_address]['pnl_percent'] = pnl_percent
                positions[token_address]['last_update'] = datetime.now().isoformat()
                self._save_positions(positions)
                
        except Exception as e:
            logger.error(f"Fehler beim Update der Position PnL: {e}")


# Singleton Instance
trade_manager = TradeManager()
