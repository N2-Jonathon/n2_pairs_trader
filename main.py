import asyncio
import threading
import ccxt
import configparser
import pandas as pd
import time
import warnings

from indicators import supertrend
from utilities import check_buy_sell_signals, create_synthetic_pair
from position_manager import Position

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

config = configparser.ConfigParser()
config.read("config.ini")


exchange = ccxt.kucoin({
  "apiKey": config['KuCoin']['apiKey'],
  "secret": config['KuCoin']['secret'],
  "password": config['KuCoin']['password']
})


async def main(base_pair=config['Bot Settings']['base_pair_default'],
               quote_pair=config['Bot Settings']['quote_pair_default']):
    running = True

    while running:
        # This code is for one timeframe. Later, do the same iterated for each timeframe.
        base_bars = exchange.fetch_ohlcv(base_pair, timeframe="1m", limit=50)
        quote_bars = exchange.fetch_ohlcv(quote_pair, timeframe="1m", limit=50)

        pair = create_synthetic_pair(base_bars, quote_bars)

        supertrend_data = supertrend(pair)

        signal = check_buy_sell_signals(supertrend_data)
        print(f"Signal: {signal}")

        if signal == "BUY":
            live_position = Position().open()
            pass
        elif signal == "SELL":
            pass

        await asyncio.sleep(60)



asyncio.run(main())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
