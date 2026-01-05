"""
Modul D: Der Wächter (Limit Order Manager)
Überwacht offene Positionen und führt Stop-Loss/Take-Profit aus
"""

import logging
import time
import requests
from typing import Dict, Optional
from datetime import datetime
import config
from modules.trader import Trader

logger = logging.getLogger(__name__)


class Watcher:
    """
    Der Wächter überwacht offene Positionen und führt automatische Exits aus:
    - Stop-Loss bei -15%
    - Take-Profit bei +40% (gestaffelt möglich)
    
    KEINE KI-Entscheidungen - Reine Mathematik!
    """
    
    def __init__(self, trader: Trader):
        self.trader = trader
        self.stop_loss_percent = config.STOP_LOSS_PERCENT
        self.take_profit_percent = config.TAKE_PROFIT_PERCENT
        self.check_interval = config.WATCHER_INTERVAL
        
        self.active_positions = {}  # contract_address -> position_info
        
    def add_position(self, trade_result: Dict):
        """
        Fügt eine neue Position zum Monitoring hinzu
        
        Args:
            trade_result: Trade Result vom Trader
        """
        try:
            token_address = trade_result['token_address']
            pair = trade_result.get('pair', {})
            
            position = {
                'token_address': token_address,
                'symbol': trade_result['symbol'],
                'entry_price': pair.get('price_usd', 0),
                'amount_sol': trade_result['amount_sol'],
                'amount_tokens': trade_result['amount_tokens'],
                'entry_time': datetime.now(),
                'signature': trade_result['signature'],
                'highest_price': pair.get('price_usd', 0),  # Für Trailing Stop
                'status': 'active'
            }
            
            self.active_positions[token_address] = position
            
            logger.info(
                f"Position hinzugefügt: {position['symbol']} | "
                f"Entry: ${position['entry_price']:.8f} | "
                f"Amount: {trade_result['amount_sol']} SOL"
            )
            
            # Berechne und logge Exit Levels
            stop_loss_price = position['entry_price'] * (1 - self.stop_loss_percent / 100)
            take_profit_price = position['entry_price'] * (1 + self.take_profit_percent / 100)
            
            logger.info(
                f"Exit Levels für {position['symbol']}: "
                f"Stop-Loss @ ${stop_loss_price:.8f} (-{self.stop_loss_percent}%) | "
                f"Take-Profit @ ${take_profit_price:.8f} (+{self.take_profit_percent}%)"
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Position: {e}", exc_info=True)
    
    def monitor_positions(self):
        """
        Überwacht alle aktiven Positionen
        Läuft in einer Loop bis alle Positionen geschlossen sind
        """
        logger.info("Wächter startet Position Monitoring...")
        
        while self.active_positions:
            try:
                # Prüfe jede Position
                positions_to_check = list(self.active_positions.keys())
                
                for token_address in positions_to_check:
                    position = self.active_positions.get(token_address)
                    
                    if not position or position['status'] != 'active':
                        continue
                    
                    # Hole aktuellen Preis
                    current_price = self._get_current_price(token_address)
                    
                    if current_price is None:
                        logger.warning(f"Konnte Preis für {position['symbol']} nicht abrufen")
                        continue
                    
                    # Berechne Performance
                    entry_price = position['entry_price']
                    price_change_percent = ((current_price - entry_price) / entry_price) * 100
                    
                    # Update höchster Preis (für Trailing Stop)
                    if current_price > position['highest_price']:
                        position['highest_price'] = current_price
                    
                    logger.info(
                        f"Position Check: {position['symbol']} | "
                        f"Entry: ${entry_price:.8f} | "
                        f"Current: ${current_price:.8f} | "
                        f"Change: {price_change_percent:+.2f}%"
                    )
                    
                    # CHECK: Stop-Loss
                    if price_change_percent <= -self.stop_loss_percent:
                        logger.warning(
                            f"🛑 STOP-LOSS TRIGGERED für {position['symbol']} bei {price_change_percent:.2f}%"
                        )
                        self._execute_exit(token_address, current_price, "STOP_LOSS")
                        continue
                    
                    # CHECK: Take-Profit
                    if price_change_percent >= self.take_profit_percent:
                        logger.info(
                            f"🎯 TAKE-PROFIT TRIGGERED für {position['symbol']} bei {price_change_percent:.2f}%"
                        )
                        self._execute_exit(token_address, current_price, "TAKE_PROFIT")
                        continue
                
                # Warte vor nächster Prüfung
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Wächter wurde manuell gestoppt")
                break
            except Exception as e:
                logger.error(f"Fehler im Wächter Loop: {e}", exc_info=True)
                time.sleep(self.check_interval)
        
        logger.info("Wächter beendet - Keine aktiven Positionen mehr")
    
    def _get_current_price(self, token_address: str) -> Optional[float]:
        """
        Holt den aktuellen Preis des Tokens von DexScreener
        
        Args:
            token_address: Token Contract Address
            
        Returns:
            Optional[float]: Aktueller Preis in USD oder None
        """
        try:
            url = f"{config.DEXSCREENER_API_URL}/dex/tokens/{token_address}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'pairs' in data and len(data['pairs']) > 0:
                # Nehme das erste Pair (meist das mit höchster Liquidität)
                pair = data['pairs'][0]
                price_usd = float(pair.get('priceUsd', 0))
                return price_usd
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Preises: {e}")
            return None
    
    def _execute_exit(self, token_address: str, exit_price: float, reason: str):
        """
        Führt einen Exit (Verkauf) der Position aus
        
        Args:
            token_address: Token Contract Address
            exit_price: Aktueller Exit Preis
            reason: Grund für Exit (STOP_LOSS oder TAKE_PROFIT)
        """
        position = self.active_positions.get(token_address)
        
        if not position:
            return
        
        try:
            logger.info(f"=== EXIT EXECUTION START: {position['symbol']} ({reason}) ===")
            
            # Hole aktuellen Token Balance
            token_balance = self.trader.get_token_balance(token_address)
            
            if token_balance <= 0:
                logger.warning(f"Keine Tokens zum Verkaufen für {position['symbol']}")
                position['status'] = 'closed'
                return
            
            # Führe Verkauf via Jupiter aus
            exit_result = self._execute_jupiter_sell(token_address, position['symbol'], token_balance)
            
            if exit_result:
                # Berechne Profit/Loss
                entry_value_usd = position['entry_price'] * token_balance
                exit_value_usd = exit_price * token_balance
                pnl_usd = exit_value_usd - entry_value_usd
                pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                
                logger.info(
                    f"✅ EXIT ERFOLGREICH: {position['symbol']} | "
                    f"Reason: {reason} | "
                    f"PnL: ${pnl_usd:.2f} ({pnl_percent:+.2f}%) | "
                    f"Entry: ${position['entry_price']:.8f} | "
                    f"Exit: ${exit_price:.8f}"
                )
                
                position['exit_price'] = exit_price
                position['exit_time'] = datetime.now()
                position['exit_reason'] = reason
                position['pnl_usd'] = pnl_usd
                position['pnl_percent'] = pnl_percent
                position['status'] = 'closed'
                position['exit_signature'] = exit_result.get('signature')
                
                # Entferne aus aktiven Positionen
                del self.active_positions[token_address]
                
            else:
                logger.error(f"❌ EXIT FEHLGESCHLAGEN für {position['symbol']}")
                
        except Exception as e:
            logger.error(f"Fehler beim Exit Execution: {e}", exc_info=True)
    
    def _execute_jupiter_sell(self, token_address: str, symbol: str, amount: float) -> Optional[Dict]:
        """
        Verkauft Token via Jupiter (vereinfachte Version)
        
        Args:
            token_address: Token zu verkaufen
            symbol: Token Symbol
            amount: Anzahl Token
            
        Returns:
            Optional[Dict]: Sell Result oder None
        """
        try:
            logger.info(f"Verkaufe {amount} {symbol} via Jupiter...")
            
            # SOL Mint Address
            sol_mint = "So11111111111111111111111111111111111111112"
            
            # Hole Quote für Verkauf (Token -> SOL)
            quote_url = f"{config.JUPITER_API_URL}/quote"
            quote_params = {
                'inputMint': token_address,
                'outputMint': sol_mint,
                'amount': int(amount),  # Ganzzahl der kleinsten Einheit
                'slippageBps': 100  # 1% Slippage bei Verkauf
            }
            
            quote_response = requests.get(quote_url, params=quote_params, timeout=30)
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            
            if 'error' in quote_data:
                logger.error(f"Jupiter Quote Error: {quote_data['error']}")
                return None
            
            out_amount = int(quote_data.get('outAmount', 0))
            out_sol = out_amount / 1_000_000_000
            logger.info(f"Quote erhalten: {out_sol} SOL für {amount} {symbol}")
            
            # Hole Swap Transaction
            swap_url = f"{config.JUPITER_API_URL}/swap"
            swap_payload = {
                'quoteResponse': quote_data,
                'userPublicKey': str(self.trader.wallet.pubkey()),
                'wrapAndUnwrapSol': True,
                'dynamicComputeUnitLimit': True,
                'prioritizationFeeLamports': 'auto'
            }
            
            swap_response = requests.post(swap_url, json=swap_payload, timeout=30)
            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            if 'swapTransaction' not in swap_data:
                logger.error("Keine Swap Transaction in Jupiter Response")
                return None
            
            # Decode, Sign und Send Transaction
            import base64
            from solders.transaction import VersionedTransaction
            
            swap_transaction_b64 = swap_data['swapTransaction']
            transaction_bytes = base64.b64decode(swap_transaction_b64)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            transaction.sign([self.trader.wallet])
            
            logger.info(f"Sende Sell Transaction für {symbol}...")
            tx_response = self.trader.rpc_client.send_transaction(transaction)
            
            signature = str(tx_response.value)
            logger.info(f"Transaction gesendet: {signature}")
            
            # Warte auf Confirmation
            confirmation = self.trader.rpc_client.confirm_transaction(signature, commitment="confirmed")
            
            if confirmation.value:
                logger.info(f"✅ Sell Transaction bestätigt: {signature}")
                return {
                    'signature': signature,
                    'amount_sold': amount,
                    'amount_sol_received': out_sol,
                    'success': True
                }
            else:
                logger.error(f"❌ Sell Transaction nicht bestätigt: {signature}")
                return None
            
        except Exception as e:
            logger.error(f"Fehler beim Sell Execution: {e}", exc_info=True)
            return None
    
    def get_active_positions_count(self) -> int:
        """
        Returns:
            int: Anzahl aktiver Positionen
        """
        return len(self.active_positions)
