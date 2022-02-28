import ccxt
import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

exchange = ccxt.kucoin({
  "apiKey": config.KUCOIN_API_KEY,
  "secret": config.KUCOIN_SECRET_KEY,
  "password": config.KUCOIN_PASSWORD
})
in_position = False

###[INDICATOR FUNCTIONS]###
def true_range(data):
    """
      Calculates true range. 
      This is needed to calculate ATR & SuperTrend.
    """
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr

def average_true_range(data, period):
    """
      Calculates average true range (ATR).
      This is needed to calculate SuperTrend.
    """
    data['tr'] = true_range(data)
    atr = data['tr'].rolling(period).mean()

    return atr

def supertrend(df, period=10, atr_multiplier=2):
    """Calculates SuperTrend"""
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = average_true_range(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
        
    return df
###[/INDICATOR FUNCTIONS]###


###[UTILITY FUNCTIONS]###
def get_bars(pair: str, timeframe: str, limit: int):
  print(f"Fetching new bars for {datetime.now().isoformat()}")
  bars = exchange.fetch_ohlcv(pair, timeframe, limit)
  return bars
def check_buy_sell_signals(df):
    global in_position

    print("Checking for signals")
    print(df.tail(10))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("Signal: BUY (Uptrend started)")
        if not in_position:
            order = exchange.create_market_buy_order('ETH/USD', 0.05)
            print(order)
            in_position = True
        else:
            print("Already in a position. Nothing to do.")
    
    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if in_position:
            print("Signal: SELL (Downtrend started)")
            order = exchange.create_market_sell_order('ETH/USD', 0.05)
            print(order)
            in_position = False
        else:
            print("Not currently in a position. Nothing to sell.")
def run_bot():
    bars = exchange.fetch_ohlcv('ETH/USDT', timeframe='1m', limit=100)
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    supertrend_data = supertrend(df)
    
    check_buy_sell_signals(supertrend_data)
    
def create_synthetic_pair(base, quote, timeframe, limit):
    """
      This is not working yet. 
    """
    base_bars = exchange.fetch_ohlcv(base, timeframe, limit)
    quote_bars = exchange.fetch_ohlcv(quote, timeframe, limit)

    df_base = pd.DataFrame(base_bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_base['timestamp'] = pd.to_datetime(df_base['timestamp'], unit='ms')
    
    df_quote = pd.DataFrame(quote_bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_quote['timestamp'] = pd.to_datetime(df_quote['timestamp'], unit='ms')
    
    df_synth = "???"
    # TODO: figure out how to calculate df_synth from df_base & df_quote 
  
###[/UTILITY FUNCTIONS]###

###[SCHEDULE]###
schedule.every(10).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)
###[/SCHEDULE]###