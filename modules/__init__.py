"""
Modules Package
Enthält alle 4 Trading-Bot Module
"""

from modules.scout import Scout
from modules.analyst import Analyst
from modules.trader import Trader
from modules.watcher import Watcher

__all__ = ['Scout', 'Analyst', 'Trader', 'Watcher']
