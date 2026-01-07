"""
Modul C: Der Trader (Execution & Security)
Führt Security Checks durch und executed Trades via Jupiter Aggregator
"""

import logging
import base58
import requests
from typing import Dict, Optional, Tuple
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
import config

logger = logging.getLogger(__name__)


class Trader:
    """
    Der Trader ist verantwortlich für:
    1. SECURITY CHECKS: Mint Authority, Freeze Authority, Liquidity Burn
    2. Trade Execution via Jupiter Aggregator
    3. Private Key Management (nur aus ENV)
    """
    
    def __init__(self):
        self.rpc_client = Client(config.SOLANA_RPC_URL)
        self.jupiter_api = config.JUPITER_API_URL
        
        # SECURITY: Private Key wird NUR aus Environment Variable geladen
        if not config.SOLANA_PRIVATE_KEY:
            raise ValueError("SOLANA_PRIVATE_KEY nicht in .env gesetzt!")
        
        try:
            # Decode Base58 Private Key
            private_key_bytes = base58.b58decode(config.SOLANA_PRIVATE_KEY)
            self.wallet = Keypair.from_bytes(private_key_bytes)
            logger.info(f"Wallet geladen: {self.wallet.pubkey()}")
        except Exception as e:
            raise ValueError(f"Ungültiger Private Key: {e}")
        
        self.trade_amount_sol = config.TRADE_AMOUNT_SOL
        
    def execute_trade(self, pair: Dict) -> Optional[Dict]:
        """
        Führt einen Trade aus - MIT SECURITY CHECKS!
        
        Args:
            pair: Das zu tradende Pair vom Analyst
            
        Returns:
            Optional[Dict]: Trade Informationen oder None bei Fehler
        """
        contract_address = pair.get('contract_address')
        symbol = pair.get('symbol')
        
        logger.info(f"=== TRADE EXECUTION START: {symbol} ({contract_address}) ===")
        
        # CRITICAL SECURITY CHECKS
        if not self._perform_security_checks(contract_address):
            logger.error(f"SECURITY CHECK FAILED für {symbol} - TRADE ABGEBROCHEN!")
            return None
        
        logger.info(f"✓ Security Checks bestanden für {symbol}")
        
        # Führe Swap via Jupiter aus
        trade_result = self._execute_jupiter_swap(contract_address, symbol)
        
        if trade_result:
            logger.info(f"=== TRADE ERFOLGREICH: {symbol} ===")
            trade_result['pair'] = pair
            return trade_result
        else:
            logger.error(f"=== TRADE FEHLGESCHLAGEN: {symbol} ===")
            return None
    
    def _perform_security_checks(self, token_address: str) -> bool:
        """
        CRITICAL SECURITY CHECKS
        
        Prüft:
        1. Mint Authority ist deaktiviert (None)
        2. Freeze Authority ist deaktiviert (None)
        3. (Optional) Burned Liquidity Check
        
        Args:
            token_address: Die Contract Address des Tokens
            
        Returns:
            bool: True wenn alle Checks bestanden, False sonst
        """
        try:
            logger.info(f"Starte Security Checks für {token_address}...")
            
            # Konvertiere zu Pubkey
            token_pubkey = Pubkey.from_string(token_address)
            
            # Hole Mint Account Info via RPC
            response = self.rpc_client.get_account_info(token_pubkey)
            
            if not response.value:
                logger.error("❌ Token Account nicht gefunden - möglicherweise ungültige Adresse")
                return False
            
            account_data = response.value.data
            
            # Parse Mint Account Data
            # Solana Mint Account Structure:
            # Bytes 0-3: mint_authority_option (0 = None, 1 = Some)
            # Bytes 4-35: mint_authority (wenn vorhanden)
            # Bytes 36-43: supply
            # Bytes 44: decimals
            # Bytes 45: is_initialized
            # Bytes 46-49: freeze_authority_option (0 = None, 1 = Some)
            # Bytes 50-81: freeze_authority (wenn vorhanden)
            
            if len(account_data) < 82:
                logger.error("❌ Ungültige Mint Account Daten - zu kurz")
                return False
            
            # CHECK 1: Mint Authority
            mint_authority_option = int.from_bytes(account_data[0:4], 'little')
            
            if mint_authority_option == 0:
                logger.info("✓ Mint Authority: DEAKTIVIERT (None)")
                mint_authority_check = True
            else:
                mint_authority = base58.b58encode(account_data[4:36]).decode('ascii')
                logger.error(f"❌ Mint Authority: AKTIV ({mint_authority})")
                logger.error("   RISIKO: Token-Supply kann beliebig erhöht werden!")
                mint_authority_check = False
            
            # CHECK 2: Freeze Authority
            freeze_authority_option = int.from_bytes(account_data[46:50], 'little')
            
            if freeze_authority_option == 0:
                logger.info("✓ Freeze Authority: DEAKTIVIERT (None)")
                freeze_authority_check = True
            else:
                freeze_authority = base58.b58encode(account_data[50:82]).decode('ascii')
                logger.error(f"❌ Freeze Authority: AKTIV ({freeze_authority})")
                logger.error("   RISIKO: Token können eingefroren werden!")
                freeze_authority_check = False
            
            # CHECK 3: Optional - Burned Liquidity Check
            # Dies ist komplexer und würde den Raydium Pool Contract prüfen
            # Für Production würde man hier zusätzlich prüfen ob LP Tokens geburnt wurden
            # Simplified Version: Log Warning
            logger.info("⚠ Burned Liquidity Check: Nicht implementiert (optional)")
            
            # Endresultat
            all_checks_passed = mint_authority_check and freeze_authority_check
            
            if all_checks_passed:
                logger.info("✅ ALLE SECURITY CHECKS BESTANDEN")
            else:
                logger.error("❌ SECURITY CHECKS FEHLGESCHLAGEN - UNSICHERER TOKEN!")
            
            return all_checks_passed
            
        except Exception as e:
            logger.error(f"Fehler bei Security Checks: {e}", exc_info=True)
            return False
    
    def _execute_jupiter_swap(self, token_address: str, symbol: str) -> Optional[Dict]:
        """
        Führt einen Swap über Jupiter Aggregator aus
        
        Args:
            token_address: Output Token Address (zu kaufender Token)
            symbol: Symbol des Tokens (für Logging)
            
        Returns:
            Optional[Dict]: Swap Informationen oder None
        """
        try:
            logger.info(f"Hole Jupiter Quote für {self.trade_amount_sol} SOL -> {symbol}...")
            
            # SOL Mint Address (wrapped SOL)
            sol_mint = "So11111111111111111111111111111111111111112"
            
            # Konvertiere SOL zu Lamports (1 SOL = 1_000_000_000 Lamports)
            amount_lamports = int(self.trade_amount_sol * 1_000_000_000)
            
            # Schritt 1: Hole Quote von Jupiter
            quote_url = f"{self.jupiter_api}/quote"
            quote_params = {
                'inputMint': sol_mint,
                'outputMint': token_address,
                'amount': amount_lamports,
                'slippageBps': 50  # 0.5% Slippage
            }
            
            quote_response = requests.get(
                quote_url, 
                params=quote_params, 
                timeout=30,
                verify=True  # SSL Verification aktiviert
            )
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            
            if 'error' in quote_data:
                logger.error(f"Jupiter Quote Error: {quote_data['error']}")
                return None
            
            out_amount = int(quote_data.get('outAmount', 0))
            logger.info(f"Quote erhalten: {out_amount} {symbol} für {self.trade_amount_sol} SOL")
            
            # Schritt 2: Hole Swap Transaction
            swap_url = f"{self.jupiter_api}/swap"
            swap_payload = {
                'quoteResponse': quote_data,
                'userPublicKey': str(self.wallet.pubkey()),
                'wrapAndUnwrapSol': True,
                'dynamicComputeUnitLimit': True,
                'prioritizationFeeLamports': 'auto'
            }
            
            swap_response = requests.post(
                swap_url, 
                json=swap_payload, 
                timeout=30,
                verify=True  # SSL Verification aktiviert
            )
            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            if 'swapTransaction' not in swap_data:
                logger.error("Keine Swap Transaction in Jupiter Response")
                return None
            
            # Schritt 3: Signiere und sende Transaction
            swap_transaction_b64 = swap_data['swapTransaction']
            
            # Decode Transaction
            import base64
            transaction_bytes = base64.b64decode(swap_transaction_b64)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Signiere Transaction
            transaction.sign([self.wallet])
            
            # Sende Transaction
            logger.info(f"Sende Swap Transaction für {symbol}...")
            tx_response = self.rpc_client.send_transaction(transaction)
            
            signature = str(tx_response.value)
            logger.info(f"Transaction gesendet: {signature}")
            
            # Warte auf Confirmation
            logger.info("Warte auf Transaction Confirmation...")
            confirmation = self.rpc_client.confirm_transaction(signature, commitment="confirmed")
            
            if confirmation.value:
                logger.info(f"✅ Transaction bestätigt: {signature}")
                
                return {
                    'signature': signature,
                    'token_address': token_address,
                    'symbol': symbol,
                    'amount_sol': self.trade_amount_sol,
                    'amount_tokens': out_amount,
                    'success': True
                }
            else:
                logger.error(f"❌ Transaction nicht bestätigt: {signature}")
                return None
            
        except requests.exceptions.Timeout:
            logger.error("Jupiter API Timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Jupiter API Request Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Fehler beim Swap Execution: {e}", exc_info=True)
            return None
    
    def get_token_balance(self, token_address: str) -> float:
        """
        Holt den aktuellen Token Balance
        
        Args:
            token_address: Token Mint Address
            
        Returns:
            float: Token Balance
        """
        try:
            token_pubkey = Pubkey.from_string(token_address)
            
            # Hole Token Accounts für Wallet
            response = self.rpc_client.get_token_accounts_by_owner(
                self.wallet.pubkey(),
                {"mint": token_pubkey}
            )
            
            if response.value:
                # Parse Token Amount
                token_account = response.value[0]
                amount_str = token_account.account.data.parsed['info']['tokenAmount']['uiAmount']
                return float(amount_str)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Token Balance: {e}")
            return 0.0
