"""
Modul A: Der Scout (Data Fetcher)
Scannt DexScreener API nach neuen Solana-Pairs mit definierten Filtern
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

logger = logging.getLogger(__name__)


class Scout:
    """
    Der Scout ist verantwortlich für das Auffinden neuer Trading-Opportunities.
    Er scannt DexScreener nach neuen Solana-Pairs und filtert nach:
    - Liquidität > $5.000
    - Alter > 15 Minuten
    - Volumen > $10.000
    """
    
    def __init__(self):
        self.api_url = config.DEXSCREENER_API_URL
        self.min_liquidity = config.MIN_LIQUIDITY_USD
        self.min_age_minutes = config.MIN_AGE_MINUTES
        self.min_volume = config.MIN_VOLUME_USD
        
    def fetch_new_pairs(self) -> List[Dict]:
        """
        Fetcht neue Solana-Pairs von DexScreener
        
        Returns:
            List[Dict]: Liste von gefilterten Pairs
        """
        try:
            logger.info("Scout startet DexScreener API Scan...")
            
            # DexScreener API für neue Solana Pairs
            url = f"{self.api_url}/dex/tokens/solana"
            
            response = requests.get(
                url,
                timeout=30,
                headers={'User-Agent': 'Memero Bot/1.0'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'pairs' not in data:
                logger.warning("Keine Pairs in API Response gefunden")
                return []
            
            pairs = data['pairs']
            logger.info(f"Scout hat {len(pairs)} Pairs gefunden")
            
            # Filtere Pairs nach Kriterien
            filtered_pairs = self._filter_pairs(pairs)
            
            logger.info(f"Scout hat {len(filtered_pairs)} Pairs nach Filterung übrig")
            
            return filtered_pairs
            
        except requests.exceptions.Timeout:
            logger.error("DexScreener API Timeout - keine Antwort innerhalb 30s")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"DexScreener API Request Fehler: {e}")
            return []
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Scout: {e}", exc_info=True)
            return []
    
    def _filter_pairs(self, pairs: List[Dict]) -> List[Dict]:
        """
        Filtert Pairs nach Hard-Coded Kriterien
        
        Args:
            pairs: Liste von Pairs aus DexScreener
            
        Returns:
            List[Dict]: Gefilterte Pairs die alle Kriterien erfüllen
        """
        filtered = []
        
        for pair in pairs:
            try:
                # Extrahiere relevante Daten
                liquidity_usd = float(pair.get('liquidity', {}).get('usd', 0))
                volume_24h = float(pair.get('volume', {}).get('h24', 0))
                pair_created_at = pair.get('pairCreatedAt')
                
                # Prüfe Liquidität
                if liquidity_usd < self.min_liquidity:
                    continue
                
                # Prüfe Volumen
                if volume_24h < self.min_volume:
                    continue
                
                # Prüfe Alter (mindestens 15 Minuten alt)
                if pair_created_at:
                    created_time = datetime.fromtimestamp(pair_created_at / 1000)
                    age_minutes = (datetime.now() - created_time).total_seconds() / 60
                    
                    if age_minutes < self.min_age_minutes:
                        continue
                
                # Extrahiere relevante Informationen
                filtered_pair = {
                    'contract_address': pair.get('baseToken', {}).get('address'),
                    'symbol': pair.get('baseToken', {}).get('symbol'),
                    'name': pair.get('baseToken', {}).get('name'),
                    'liquidity_usd': liquidity_usd,
                    'volume_24h': volume_24h,
                    'price_usd': float(pair.get('priceUsd', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                    'market_cap': float(pair.get('fdv', 0)),
                    'pair_address': pair.get('pairAddress'),
                    'dex': pair.get('dexId'),
                    'created_at': pair_created_at,
                    'url': pair.get('url', '')
                }
                
                # Validierung: Contract Address muss existieren
                if not filtered_pair['contract_address']:
                    logger.warning(f"Pair {filtered_pair.get('symbol')} hat keine Contract Address - überspringe")
                    continue
                
                filtered.append(filtered_pair)
                
                logger.debug(
                    f"Pair gefunden: {filtered_pair['symbol']} | "
                    f"Liq: ${liquidity_usd:,.0f} | "
                    f"Vol: ${volume_24h:,.0f} | "
                    f"CA: {filtered_pair['contract_address']}"
                )
                
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Fehler beim Parsen eines Pairs: {e}")
                continue
        
        return filtered
    
    def get_trending_pairs(self) -> List[Dict]:
        """
        Alternative Methode: Holt trending Pairs (falls neue Pairs nicht verfügbar)
        
        Returns:
            List[Dict]: Liste von trending Pairs
        """
        try:
            logger.info("Scout fetcht trending Solana Pairs...")
            
            url = f"{self.api_url}/dex/search?q=SOL"
            
            response = requests.get(
                url,
                timeout=30,
                headers={'User-Agent': 'Memero Bot/1.0'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'pairs' in data:
                pairs = data['pairs']
                # Filtere nur Solana Pairs
                solana_pairs = [p for p in pairs if p.get('chainId') == 'solana']
                return self._filter_pairs(solana_pairs)
            
            return []
            
        except Exception as e:
            logger.error(f"Fehler beim Fetchen von Trending Pairs: {e}")
            return []
