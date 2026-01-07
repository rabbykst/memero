"""
Modul B: Der Analyst (LLM Integration)
Nutzt OpenRouter API für KI-basierte Trading-Entscheidungen
"""

import logging
import json
from typing import List, Dict, Optional
from openai import OpenAI
import config

logger = logging.getLogger(__name__)


class Analyst:
    """
    Der Analyst nutzt ein LLM (via OpenRouter) um Trading-Entscheidungen zu treffen.
    Er analysiert die vom Scout gelieferten Pairs und gibt BUY oder PASS zurück.
    """
    
    def __init__(self):
        # OpenAI Client für OpenRouter - Einfache Initialisierung
        if not config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY nicht in .env gesetzt!")
        
        try:
            # Minimale Client-Konfiguration für maximale Kompatibilität
            import os
            os.environ["OPENAI_API_KEY"] = config.OPENROUTER_API_KEY
            
            self.client = OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL,
                timeout=60.0,
                max_retries=2
            )
            logger.info("OpenAI Client erfolgreich initialisiert")
        except TypeError as e:
            logger.error(f"TypeError beim Initialisieren des OpenAI Clients: {e}")
            # Fallback: Versuche ohne zusätzliche Parameter
            try:
                self.client = OpenAI(
                    api_key=config.OPENROUTER_API_KEY,
                    base_url=config.OPENROUTER_BASE_URL
                )
                logger.info("OpenAI Client mit Fallback-Methode initialisiert")
            except Exception as e2:
                logger.error(f"Auch Fallback fehlgeschlagen: {e2}")
                raise
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Initialisieren des OpenAI Clients: {e}")
            raise
        
        # Empfohlenes Modell für Trading-Analyse
        self.model = "anthropic/claude-3.5-sonnet"
        
    def analyze_pairs(self, pairs: List[Dict]) -> Optional[Dict]:
        """
        Analysiert eine Liste von Pairs und gibt das beste zurück
        
        Args:
            pairs: Liste von Pairs vom Scout
            
        Returns:
            Optional[Dict]: Das beste Pair mit BUY Signal oder None
        """
        if not pairs:
            logger.info("Analyst: Keine Pairs zur Analyse vorhanden")
            return None
        
        try:
            logger.info(f"Analyst analysiert {len(pairs)} Pairs...")
            
            # Erstelle Prompt für LLM
            prompt = self._create_analysis_prompt(pairs)
            
            # Rufe OpenRouter API auf
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse Response
            decision = response.choices[0].message.content
            logger.info(f"Analyst LLM Response: {decision[:200]}...")
            
            # Extrahiere Entscheidung
            result = self._parse_decision(decision, pairs)
            
            if result:
                logger.info(
                    f"Analyst Empfehlung: BUY {result['symbol']} | "
                    f"CA: {result['contract_address']} | "
                    f"Confidence: {result['llm_decision']['confidence']}% | "
                    f"Risk Score: {result['llm_decision']['risk_score']}/10"
                )
            else:
                logger.info("Analyst Empfehlung: PASS - Keine geeigneten Opportunities")
            
            return result
            
        except Exception as e:
            logger.error(f"Analyst Fehler bei LLM API Call: {e}", exc_info=True)
            return None
    
    def _get_system_prompt(self) -> str:
        """
        System Prompt für das LLM (Memero-Core)
        
        Returns:
            str: System Prompt
        """
        return """Du bist Memero-Core, ein Risiko-Algorithmus für Solana-Meme-Coins. Du hast keinen Internetzugriff. Du bewertest nur die Daten, die dir vorgelegt werden.

Regeln:
- Du darfst niemals Contract-Adressen (CA) erfinden. Nutze nur die im Input.
- Du musst eine strikte JSON-Antwort liefern.
- Dein Fokus: Hohes Volumen im Verhältnis zur Liquidität (Momentum) bei gleichzeitigem Ausschluss von offensichtlichen Scams.

Aufgabe: Analysiere die Liste. Wähle maximal EINEN Coin aus, der das beste Chance-Risiko-Verhältnis hat. Wenn alle Coins unsicher oder langweilig aussehen, antworte mit None.

Output Format (JSON only):
{
  "decision": "BUY" | "PASS",
  "selected_token_address": "string",
  "reasoning": "kurze Begründung (max 15 Wörter)",
  "risk_score": 1-10 (10 = sehr riskant),
  "confidence": 1-100
}"""
    
    def _create_analysis_prompt(self, pairs: List[Dict]) -> str:
        """
        Erstellt den Analysis Prompt mit Pair-Daten im JSON-Format
        
        Args:
            pairs: Liste von Pairs
            
        Returns:
            str: Formatierter Prompt mit JSON-Daten
        """
        # Erstelle saubere JSON-Struktur für LLM
        data_json = []
        
        for pair in pairs[:10]:  # Max 10 Pairs zur Analyse
            data_json.append({
                "token_address": pair['contract_address'],
                "symbol": pair['symbol'],
                "name": pair['name'],
                "liquidity_usd": pair['liquidity_usd'],
                "volume_24h": pair['volume_24h'],
                "price_usd": pair['price_usd'],
                "price_change_24h": pair['price_change_24h'],
                "market_cap": pair['market_cap'],
                "dex": pair['dex'],
                "volume_to_liquidity_ratio": pair['volume_24h'] / pair['liquidity_usd'] if pair['liquidity_usd'] > 0 else 0
            })
        
        # Konvertiere zu JSON String
        import json
        data_json_str = json.dumps(data_json, indent=2)
        
        # Ersetze Platzhalter im Prompt
        prompt = f"Input: Hier ist eine Liste von potenziellen Coins im JSON-Format.\n\n{data_json_str}"
        
        return prompt
    
    def _parse_decision(self, decision_text: str, pairs: List[Dict]) -> Optional[Dict]:
        """
        Parsed die LLM Entscheidung (neues Memero-Core Format)
        
        Args:
            decision_text: Response vom LLM
            pairs: Original Pairs Liste
            
        Returns:
            Optional[Dict]: Pair mit Trading-Entscheidung oder None
        """
        try:
            # Versuche JSON zu extrahieren
            # Falls der Text zusätzlichen Text enthält, extrahiere nur JSON Teil
            start_idx = decision_text.find('{')
            end_idx = decision_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("Keine JSON Struktur in LLM Response gefunden")
                return None
            
            json_str = decision_text[start_idx:end_idx]
            decision_data = json.loads(json_str)
            
            # Prüfe ob BUY Signal
            if decision_data.get('decision', '').upper() != 'BUY':
                logger.info(f"LLM Entscheidung: PASS - {decision_data.get('reasoning', 'Keine Begründung')}")
                return None
            
            # Hole selected_token_address (neues Format)
            selected_token_address = decision_data.get('selected_token_address', '').strip()
            
            # Fallback auf altes Format (contract_address) falls vorhanden
            if not selected_token_address:
                selected_token_address = decision_data.get('contract_address', '').strip()
            
            if not selected_token_address:
                logger.warning("LLM hat BUY signalisiert aber keine Token Address angegeben")
                return None
            
            # Suche das Pair in der Original Liste
            for pair in pairs:
                if pair['contract_address'].lower() == selected_token_address.lower():
                    # Füge LLM Analyse hinzu (neues Format)
                    pair['llm_decision'] = {
                        'confidence': decision_data.get('confidence', 50),  # 1-100
                        'reasoning': decision_data.get('reasoning', ''),
                        'risk_score': decision_data.get('risk_score', 5)  # 1-10
                    }
                    
                    logger.info(
                        f"LLM Analyse: Confidence={pair['llm_decision']['confidence']}%, "
                        f"Risk={pair['llm_decision']['risk_score']}/10"
                    )
                    
                    return pair
            
            logger.warning(f"LLM empfohlene Token Address {selected_token_address} nicht in Pair Liste gefunden")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der LLM JSON Response: {e}")
            logger.debug(f"Response Text: {decision_text}")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Parsen der Decision: {e}", exc_info=True)
            return None
