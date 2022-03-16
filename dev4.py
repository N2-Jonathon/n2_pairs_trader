import ccxt
from ccxt import Exchange
import importlib

exchange_id = 'kucoin'

import_path = f"ccxt.{exchange_id}"

ccxt_exchange: ccxt.Exchange = importlib.import_module(import_path)


print(ccxt_exchange.requiredCredentials)


