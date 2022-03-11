
import importlib
from pprint import pprint
import ccxt
import os
import sys
sys.path.append(os.getcwd())
from strategies.strategy_base import StrategyBase
from core.utils import get_exchange_module_from_id

binance = get_exchange_module_from_id('binance')


binance.describe()


"""
kucoin_id = 'kucoin'
gemini_id = 'gemini'

kucoin = importlib.import_module(f"ccxt.{kucoin_id}", "")
gemini = importlib.import_module(f"ccxt.{gemini_id}")

from ccxt.kucoin import kucoin

importlib.invalidate_caches()

kucoin_2 = ccxt.kucoin()

pprint(kucoin.describe(self=ccxt.kucoin()))
pprint(kucoin.describe(self=ccxt.kucoin()))
"""