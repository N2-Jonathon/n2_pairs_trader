import ccxt
import importlib

kucoin_id = 'kucoin'
gemini_id = 'gemini'

kucoin = importlib.import_module(f"ccxt.{kucoin_id}")
gemini = importlib.import_module(f"ccxt.{gemini_id}")

print(f"{str(kucoin)}"
      f"{type(gemini)}")
