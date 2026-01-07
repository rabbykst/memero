"""
MEMERO Monitoring - Bot Control
Prozess-Steuerung für Trading-Bot (Start/Stop/Status)

WICHTIG: Dieser Code ändert NICHT den Bot, sondern steuert nur den Prozess!
"""

import subprocess
import psutil
import signal
import os
from typing import Dict, Optional
from pathlib import Path
import time

from monitoring.config import BOT_START_SCRIPT, BOT_MAIN_FILE, BASE_DIR


class BotController:
    """
    Steuert den Trading-Bot-Prozess
    
    - Start: Startet bot via start.sh
    - Stop: Beendet Bot-Prozess sauber
    - Status: Prüft ob Bot läuft
    - Timer: Automatischer Stop nach X Minuten
    """
    
    def __init__(self):
        self.bot_process = None
        self.timer_end_time = None
    
    def get_bot_pid(self) -> Optional[int]:
        """
        Findet die PID des laufenden Bot-Prozesses
        
        Returns:
            Optional[int]: PID oder None
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Suche nach "python main.py" oder "python3 main.py"
                    if 'main.py' in cmdline and 'memero' in cmdline.lower():
                        return proc.info['pid']
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Fehler bei PID-Suche: {e}")
            return None
    
    def is_bot_running(self) -> bool:
        """
        Prüft ob Bot läuft
        
        Returns:
            bool: True wenn Bot läuft
        """
        pid = self.get_bot_pid()
        return pid is not None
    
    def start_bot(self) -> Dict:
        """
        Startet den Trading-Bot
        
        Returns:
            Dict mit status und message
        """
        try:
            # Prüfe ob Bot bereits läuft
            if self.is_bot_running():
                return {
                    'success': False,
                    'message': 'Bot läuft bereits!'
                }
            
            # Prüfe ob start.sh existiert
            if not BOT_START_SCRIPT.exists():
                return {
                    'success': False,
                    'message': f'Start-Script nicht gefunden: {BOT_START_SCRIPT}'
                }
            
            # Starte Bot im Hintergrund
            # Verwende nohup damit Bot weiterläuft wenn Monitoring beendet wird
            log_file = BASE_DIR / 'bot_output.log'
            
            cmd = f"cd {BASE_DIR} && nohup ./start.sh > {log_file} 2>&1 &"
            subprocess.Popen(cmd, shell=True, start_new_session=True)
            
            # Warte kurz und prüfe ob Prozess gestartet wurde
            time.sleep(2)
            
            if self.is_bot_running():
                return {
                    'success': True,
                    'message': 'Bot erfolgreich gestartet!',
                    'pid': self.get_bot_pid()
                }
            else:
                return {
                    'success': False,
                    'message': 'Bot-Start fehlgeschlagen. Prüfe bot_output.log'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Bot-Start: {str(e)}'
            }
    
    def stop_bot(self) -> Dict:
        """
        Stoppt den Trading-Bot sauber
        
        Returns:
            Dict mit status und message
        """
        try:
            pid = self.get_bot_pid()
            
            if pid is None:
                return {
                    'success': False,
                    'message': 'Bot läuft nicht!'
                }
            
            # Sende SIGTERM für sauberen Shutdown
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                
                # Warte bis zu 10 Sekunden auf sauberes Beenden
                proc.wait(timeout=10)
                
                return {
                    'success': True,
                    'message': 'Bot erfolgreich gestoppt!',
                    'pid': pid
                }
                
            except psutil.TimeoutExpired:
                # Falls SIGTERM nicht funktioniert, SIGKILL
                proc.kill()
                return {
                    'success': True,
                    'message': 'Bot gestoppt (forciert)',
                    'pid': pid
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Bot-Stop: {str(e)}'
            }
    
    def set_timer(self, minutes: int) -> Dict:
        """
        Setzt einen Timer für automatischen Bot-Stop
        
        Args:
            minutes: Minuten bis zum Stop
            
        Returns:
            Dict mit status und end_time
        """
        try:
            if minutes <= 0:
                self.timer_end_time = None
                return {
                    'success': True,
                    'message': 'Timer deaktiviert',
                    'end_time': None
                }
            
            self.timer_end_time = time.time() + (minutes * 60)
            
            return {
                'success': True,
                'message': f'Timer gesetzt: Bot stoppt in {minutes} Minuten',
                'end_time': self.timer_end_time,
                'minutes': minutes
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Fehler beim Timer setzen: {str(e)}'
            }
    
    def check_timer(self) -> Dict:
        """
        Prüft ob Timer abgelaufen ist und stoppt Bot ggf.
        
        Returns:
            Dict mit timer_active, remaining_seconds, auto_stopped
        """
        try:
            if self.timer_end_time is None:
                return {
                    'timer_active': False,
                    'remaining_seconds': 0,
                    'auto_stopped': False
                }
            
            remaining = self.timer_end_time - time.time()
            
            if remaining <= 0:
                # Timer abgelaufen - Bot stoppen!
                result = self.stop_bot()
                self.timer_end_time = None
                
                return {
                    'timer_active': False,
                    'remaining_seconds': 0,
                    'auto_stopped': result['success'],
                    'stop_message': result['message']
                }
            else:
                return {
                    'timer_active': True,
                    'remaining_seconds': int(remaining),
                    'remaining_minutes': round(remaining / 60, 1),
                    'auto_stopped': False
                }
                
        except Exception as e:
            return {
                'timer_active': False,
                'error': str(e)
            }


# Singleton Instance
bot_controller = BotController()
