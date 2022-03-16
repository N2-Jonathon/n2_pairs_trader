import ccxt
import core
import importlib
importlib.reload(core)
from core.exchanges.kucoin_extended import KuCoinExtended

# Originally I tried dynamically getting the module import path,
# then use importlib.import_module, but I couldn't get it to
# work without problems, so each exchange that's enabled goes here.
"""
{
    "kucoin": {"name": "KuCoin",
               "module": KuCoinExtended},
    "hitbtc": {"name": "HitBTC",
               "module": ccxt.hitbtc},
}
"""