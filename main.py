"""
╔════════════════════════════════════════════════════════════════════════════╗
║                       MEMERO TRADING BOT v1.0                              ║
║                                                                            ║
║  Vollautomatischer KI-gestützter Solana Meme-Coin Trading Bot             ║
║  mit strikten Security-Checks und Risk Management                          ║
║                                                                            ║
║  Entwickelt als Senior Lead Developer & Blockchain Security Expert        ║
╚════════════════════════════════════════════════════════════════════════════╝

Main Orchestrator - Koordiniert alle 4 Module:
  1. Scout (Data Fetcher) - DexScreener API Scanning
  2. Analyst (LLM Integration) - OpenRouter AI Analysis
  3. Trader (Execution & Security) - Jupiter Aggregator + Security Checks
  4. Watcher (Position Manager) - Automated Stop-Loss/Take-Profit

Flow: Scout → Analyst → Trader → Watcher (Loop)
"""

import logging
import time
import sys
from datetime import datetime
import pytz
import config
from modules.scout import Scout
from modules.analyst import Analyst
from modules.trader import Trader
from modules.watcher import Watcher


# Logging Setup
def setup_logging():
    """Konfiguriert das Logging System mit MEZ (Mitteleuropäische Zeit)"""
    import logging
    from datetime import datetime
    import pytz
    
    # MEZ Timezone
    mez = pytz.timezone('Europe/Berlin')
    
    class MEZFormatter(logging.Formatter):
        """Custom Formatter für MEZ Zeitzone"""
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=mez)
            if datefmt:
                return dt.strftime(datefmt)
            else:
                return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    log_format = '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Root Logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console Handler mit MEZ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.setFormatter(MEZFormatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # File Handler mit MEZ
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # File bekommt alle Details
    file_handler.setFormatter(MEZFormatter(log_format, date_format))
    logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)


def print_banner():
    """Zeigt den Startup Banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🚀 MEMERO TRADING BOT v1.0 🚀               ║
    ║                                                           ║
    ║         Solana Meme-Coin Trading Bot mit KI              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    📊 Scout Interval:     {} Sekunden
    💰 Trade Amount:       {} SOL
    🛑 Stop-Loss:          {}%
    🎯 Take-Profit:        {}%
    🔍 Min Liquidität:     ${}
    📈 Min Volumen:        ${}
    ⏰ Min Alter:          {} Minuten
    """.format(
        config.SCOUT_INTERVAL,
        config.TRADE_AMOUNT_SOL,
        config.STOP_LOSS_PERCENT,
        config.TAKE_PROFIT_PERCENT,
        f"{config.MIN_LIQUIDITY_USD:,}",
        f"{config.MIN_VOLUME_USD:,}",
        config.MIN_AGE_MINUTES
    )
    print(banner)


def main():
    """
    Hauptloop des Trading Bots
    
    Flow:
    1. Scout scannt nach neuen Pairs
    2. Analyst analysiert und gibt Empfehlung
    3. Trader führt Trade aus (mit Security Checks)
    4. Watcher überwacht Position bis Exit
    5. Loop wiederholt sich
    """
    logger = setup_logging()
    
    try:
        print_banner()
        
        # Validiere Konfiguration
        logger.info("Validiere Konfiguration...")
        config.validate_config()
        logger.info("✓ Konfiguration OK")
        
        # Initialisiere Module
        logger.info("Initialisiere Module...")
        scout = Scout()
        analyst = Analyst()
        trader = Trader()
        watcher = Watcher(trader)
        logger.info("✓ Alle Module initialisiert")
        
        logger.info("=" * 70)
        logger.info("BOT GESTARTET - Bereit zum Trading")
        logger.info("=" * 70)
        
        # Main Loop
        loop_counter = 0
        
        while True:
            loop_counter += 1
            
            # MEZ Zeitstempel
            mez = pytz.timezone('Europe/Berlin')
            current_time = datetime.now(mez).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info("=" * 70)
            logger.info(f"LOOP #{loop_counter} | {current_time} MEZ")
            logger.info("=" * 70)
            
            try:
                # SCHRITT 1: SCOUT - Finde neue Opportunities
                logger.info("📡 SCHRITT 1: Scout scannt nach neuen Pairs...")
                pairs = scout.fetch_new_pairs()
                
                if not pairs:
                    logger.info("Keine Pairs gefunden die Filter erfüllen - warte bis nächster Scan")
                    time.sleep(config.SCOUT_INTERVAL)
                    continue
                
                logger.info(f"Scout hat {len(pairs)} Pairs gefunden")
                
                # SCHRITT 2: ANALYST - Analysiere mit KI
                logger.info("🤖 SCHRITT 2: Analyst analysiert Pairs...")
                recommended_pair = analyst.analyze_pairs(pairs)
                
                if not recommended_pair:
                    logger.info("Analyst empfiehlt: PASS - Keine Trading Opportunity")
                    time.sleep(config.SCOUT_INTERVAL)
                    continue
                
                logger.info(f"Analyst empfiehlt: BUY {recommended_pair['symbol']}")
                
                # SCHRITT 3: TRADER - Führe Trade aus (mit Security Checks)
                logger.info("💼 SCHRITT 3: Trader führt Trade aus...")
                trade_result = trader.execute_trade(recommended_pair)
                
                if not trade_result:
                    logger.warning("Trade wurde nicht ausgeführt (Security Check oder Fehler)")
                    time.sleep(config.SCOUT_INTERVAL)
                    continue
                
                logger.info(f"Trade erfolgreich für {trade_result['symbol']}\n")
                
                # SCHRITT 4: WATCHER - Überwache Position
                logger.info("👁️  SCHRITT 4: Watcher überwacht Position...")
                watcher.add_position(trade_result)
                
                # Starte Position Monitoring (blockiert bis Exit)
                logger.info("Starte kontinuierliches Monitoring...\n")
                watcher.monitor_positions()
                
                logger.info("\nPosition geschlossen - Bereit für nächsten Trade\n")
                
                # Kurze Pause vor nächstem Loop
                logger.info(f"Warte {config.SCOUT_INTERVAL} Sekunden bis nächster Scout-Run...")
                time.sleep(config.SCOUT_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️  Bot wird gestoppt (Ctrl+C erkannt)...")
                raise
                
            except Exception as e:
                logger.error(f"❌ Fehler im Main Loop: {e}", exc_info=True)
                logger.warning(f"⚠️  Auto-Restart in 60 Sekunden...")
                time.sleep(60)  # Warte 1 Minute vor Restart
                logger.info("🔄 Restarting Loop...")
                continue  # Fahre mit nächstem Loop fort
    
    except KeyboardInterrupt:
        logger.info("\n" + "="*70)
        logger.info("🛑 BOT WURDE MANUELL GESTOPPT (KeyboardInterrupt)")
        logger.info("="*70)
        
    except Exception as e:
        logger.critical(f"💥 KRITISCHER FEHLER im Main: {e}", exc_info=True)
        logger.critical("⚠️  Bot wird in 5 Minuten neu gestartet...")
        time.sleep(300)  # Warte 5 Minuten
        logger.info("🔄 RESTARTING BOT...")
        # Rekursiver Restart (ruft main() erneut auf)
        main()
    
    finally:
        # Cleanup
        logger.info("\nBot Shutdown abgeschlossen")
        
        # Zeige noch offene Positionen
        if watcher.get_active_positions_count() > 0:
            logger.warning(
                f"⚠️  ACHTUNG: {watcher.get_active_positions_count()} "
                f"Position(en) noch offen!"
            )


if __name__ == "__main__":
    main()
