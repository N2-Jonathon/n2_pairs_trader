import ccxt
import config
import schedule
import pandas as pd
import numpy as np
import time
import warnings

from indicators import supertrend
from utilities import check_buy_sell_signals, create_synthetic_pair

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')


exchange = ccxt.kucoin({
  "apiKey": config.KUCOIN_API_KEY,
  "secret": config.KUCOIN_SECRET_KEY,
  "password": config.KUCOIN_PASSWORD
})
in_position = False


# ##[SCHEDULE]## #
def run_bot(base_pair, quote_pair):

    # This code is for one timeframe. Later, do the same iterated for each timeframe.
    base_bars = exchange.fetch_ohlcv(base_pair, timeframe="1d", limit=50)
    quote_bars = exchange.fetch_ohlcv(quote_pair, timeframe="1d", limit=50)

    df = create_synthetic_pair(base_bars, quote_bars)

    supertrend_data = supertrend(df)

    check_buy_sell_signals(supertrend_data)


schedule.every(10).seconds.do(run_bot('ETH/USDT', 'BTC/USDT'))

while True:
    schedule.run_pending()
    time.sleep(1)
# ##[/SCHEDULE]## #

