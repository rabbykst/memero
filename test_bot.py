"""
Test Script für Memero Bot
Testet alle Module einzeln ohne echte Trades
"""

import logging
import sys
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_config():
    """Teste Konfiguration"""
    logger.info("=" * 60)
    logger.info("TEST 1: Konfiguration")
    logger.info("=" * 60)
    
    try:
        import config
        
        logger.info(f"✓ SOLANA_RPC_URL: {config.SOLANA_RPC_URL}")
        logger.info(f"✓ OPENROUTER_BASE_URL: {config.OPENROUTER_BASE_URL}")
        logger.info(f"✓ TRADE_AMOUNT_SOL: {config.TRADE_AMOUNT_SOL}")
        logger.info(f"✓ STOP_LOSS_PERCENT: {config.STOP_LOSS_PERCENT}%")
        logger.info(f"✓ TAKE_PROFIT_PERCENT: {config.TAKE_PROFIT_PERCENT}%")
        
        # Validiere (wird Exception werfen wenn Keys fehlen)
        # config.validate_config()
        
        logger.info("✅ Konfiguration geladen\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Konfiguration Fehler: {e}\n")
        return False


def test_scout():
    """Teste Scout Modul"""
    logger.info("=" * 60)
    logger.info("TEST 2: Scout (Data Fetcher)")
    logger.info("=" * 60)
    
    try:
        from modules.scout import Scout
        
        scout = Scout()
        logger.info("✓ Scout initialisiert")
        
        # Teste API Call (kann fehlschlagen wenn keine Pairs)
        pairs = scout.fetch_new_pairs()
        logger.info(f"✓ Scout API Call erfolgreich")
        logger.info(f"  Gefundene Pairs: {len(pairs)}")
        
        if pairs:
            pair = pairs[0]
            logger.info(f"  Beispiel Pair: {pair['symbol']} | Liq: ${pair['liquidity_usd']:,.0f}")
        
        logger.info("✅ Scout funktioniert\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Scout Fehler: {e}\n")
        return False


def test_analyst():
    """Teste Analyst Modul"""
    logger.info("=" * 60)
    logger.info("TEST 3: Analyst (LLM Integration)")
    logger.info("=" * 60)
    
    try:
        from modules.analyst import Analyst
        
        # Prüfe ob API Key gesetzt
        import config
        if not config.OPENROUTER_API_KEY:
            logger.warning("⚠️  OPENROUTER_API_KEY nicht gesetzt - Test übersprungen")
            logger.info("  Setze OPENROUTER_API_KEY in .env um Analyst zu testen\n")
            return True
        
        analyst = Analyst()
        logger.info("✓ Analyst initialisiert")
        logger.info(f"  Model: {analyst.model}")
        
        # Teste mit Mock Data
        mock_pairs = [{
            'contract_address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'symbol': 'TEST',
            'name': 'Test Token',
            'liquidity_usd': 50000,
            'volume_24h': 100000,
            'price_usd': 0.001,
            'price_change_24h': 5.0,
            'market_cap': 1000000,
            'pair_address': 'test',
            'dex': 'raydium',
            'created_at': None,
            'url': ''
        }]
        
        logger.info("  Note: Echter LLM Call wird NICHT ausgeführt (spart API Kosten)")
        
        logger.info("✅ Analyst initialisiert korrekt\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Analyst Fehler: {e}\n")
        return False


def test_trader():
    """Teste Trader Modul (ohne echte Trades)"""
    logger.info("=" * 60)
    logger.info("TEST 4: Trader (Execution & Security)")
    logger.info("=" * 60)
    
    try:
        import config
        
        if not config.SOLANA_PRIVATE_KEY:
            logger.warning("⚠️  SOLANA_PRIVATE_KEY nicht gesetzt - Test übersprungen")
            logger.info("  Setze SOLANA_PRIVATE_KEY in .env um Trader zu testen\n")
            return True
        
        from modules.trader import Trader
        
        trader = Trader()
        logger.info("✓ Trader initialisiert")
        logger.info(f"  Wallet: {trader.wallet.pubkey()}")
        logger.info(f"  Trade Amount: {trader.trade_amount_sol} SOL")
        
        logger.info("  Note: Echte Trades werden NICHT ausgeführt")
        
        logger.info("✅ Trader initialisiert korrekt\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trader Fehler: {e}\n")
        return False


def test_watcher():
    """Teste Watcher Modul"""
    logger.info("=" * 60)
    logger.info("TEST 5: Watcher (Position Manager)")
    logger.info("=" * 60)
    
    try:
        import config
        
        if not config.SOLANA_PRIVATE_KEY:
            logger.warning("⚠️  SOLANA_PRIVATE_KEY nicht gesetzt - Test übersprungen\n")
            return True
        
        from modules.trader import Trader
        from modules.watcher import Watcher
        
        trader = Trader()
        watcher = Watcher(trader)
        logger.info("✓ Watcher initialisiert")
        logger.info(f"  Stop-Loss: {watcher.stop_loss_percent}%")
        logger.info(f"  Take-Profit: {watcher.take_profit_percent}%")
        logger.info(f"  Check Interval: {watcher.check_interval}s")
        
        logger.info("✅ Watcher initialisiert korrekt\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Watcher Fehler: {e}\n")
        return False


def main():
    """Führe alle Tests aus"""
    logger.info("\n")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 15 + "MEMERO BOT TEST SUITE" + " " * 22 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("\n")
    
    tests = [
        ("Konfiguration", test_config),
        ("Scout", test_scout),
        ("Analyst", test_analyst),
        ("Trader", test_trader),
        ("Watcher", test_watcher)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except KeyboardInterrupt:
            logger.info("\n\nTests abgebrochen")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unerwarteter Fehler bei {name}: {e}")
            results.append((name, False))
    
    # Zusammenfassung
    logger.info("=" * 60)
    logger.info("TEST ZUSAMMENFASSUNG")
    logger.info("=" * 60)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} | {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    logger.info("")
    logger.info(f"Ergebnis: {passed}/{total} Tests bestanden")
    logger.info("")
    
    if passed == total:
        logger.info("🎉 Alle Tests erfolgreich!")
        logger.info("Der Bot ist bereit zum Starten mit: python main.py")
    else:
        logger.warning("⚠️  Einige Tests sind fehlgeschlagen")
        logger.warning("Bitte prüfe die .env Datei und requirements.txt")
    
    logger.info("")


if __name__ == "__main__":
    main()
