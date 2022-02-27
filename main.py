import config
import pandas as pd
pd.set_option('display.max_rows', None)

import numpy as np
import ccxt
import schedule

import warnings
#warnings.filterwarnings('ignore')

from datetime import datetime
import time

# [INIT VARIABLES]
exchange = ccxt.kucoin({
  "apiKey": config.KUCOIN_API_KEY,
  "secret": config.KUCOIN_SECRET_KEY,
  "password": config.KUCOIN_PASSWORD
})

trading_pair = 'ETH-USDT'
trade_qty = 0.01
in_position = False
# [/INIT VARIABLES]

# [UTILITY FUNCTIONS]

def run_bot(trading_pair, timeframe, limit, paper_trading: bool = true):
  bars = get_bars(trading_pair, timeframe, limit)
  bars_df = create_df_from_bars(bars)
  st_data = supertrend(bars_df)
  check_supertrend_signals(st_data)
  
def get_bars(pair: str, timeframe: str, limit: int):
  bars = exchange.fetch_ohlcv(pair, timeframe, limit)
  return bars

def create_df_from_bars(bars):
  df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
  df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
  return df

def check_supertrend_signals(st_data, trading_pair, trade_qty):
  global in_position
  
  print("Checking for signals")
  print(st_data.tail(5))
  
  latest_row_index = len(st_data) -1
  previous_row_index = latest_row_index -1
  
  if not st_data['in_uptrend'][previous_row_index] and st_data['in_uptrend'][latest_row_index]:
    if not in_position:
      print('Signal: BUY (Uptrend started)')
      order = exchange.create_market_buy_order(trading_pair, trade_qty)
      print(order)
      in_position = True
    else:
      print("Already in a position. Nothing to do.")
  
  if st_data['in_uptrend'][previous_row_index] and not st_data['in_uptrend'][latest_row_index]:
    if not in_position:
      print('Signal: SELL (Downtrend started)')
      order = exchance.create_market_sell_order(trading_pair, trade_qty)
      print(order)
      in_position = False
    else:
      print("Not currently in a position. Nothing to sell.")

    
def open_synth_position(base_pair: str, quote_pair: str, direction: str, quantity: float):
  
  #TODO: implement this. For now, just test with normal pairs.
  raise NotImplementedError("TODO: implement open_synth_position() function.\nFor now, just test with normal pairs.")
  


def create_synthetic_pair(base_df, quote_df):
  # TODO: implement
  pass
# [/UTILITY FUNCTIONS]

# [INDICATOR FUNCTIONS]
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

def supertrend(df, period=7, atr_multiplier=3):
  """Calculates SuperTrend"""
  hl2 = (df['high'] + df['low']) / 2
  df['atr'] = average_true_range(df, period)
  df['upperband'] = hl2 + (atr_multiplier * df['atr'])
  df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
  df['in_uptrend'] = None
  
  for current in range(1, len(df.index)):
    previous = current -1
    
    if df['close'][current] > df['upperband'][previous]:
      df['in_uptrend'][current] = True
    elif df['close'][current] < df['lowerband'][previous]:
      df['in_uptrend'][current] = False
    else:
      df['in_uptrend'][current] = df['in_uptrend'][previous]
      
      if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
        df['lowerband'][current] = df['lowerband'][previous]
        
      if not df['in_uptrend'][current] and df['upperband'] > df['upperband'][previous]:
        df['lowerband'][current] = df['lowerband'][previous]
        
  return df
# [/INDICATOR FUNCTIONS]