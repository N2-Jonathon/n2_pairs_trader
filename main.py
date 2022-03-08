import asyncio
import ccxt
import configparser
import pandas as pd
import time
import warnings

from indicators import supertrend
from utilities import check_buy_sell_signals, create_synthetic_pair

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

    # This code is for one timeframe. Later, do the same iterated for each timeframe.
    base_bars = exchange.fetch_ohlcv(base_pair, timeframe="1d", limit=50)
    quote_bars = exchange.fetch_ohlcv(quote_pair, timeframe="1d", limit=50)

    pair = create_synthetic_pair(base_bars, quote_bars)

    supertrend_data = supertrend(pair)

    signal = check_buy_sell_signals(supertrend_data)

    print(f"Signal: {signal}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

