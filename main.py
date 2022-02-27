import config
import pandas as pd
pd.set_option('display.max_rows', None)

import numpy as np
import ccxt
import schedule

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
import time

exchange = ccxt.kucoin({
  "apiKey": config.KUCOIN_API_KEY,
  "secret": config.KUCOIN_SECRET_KEY,
  "password": config.KUCOIN_PASSWORD
})

trading_pair = 'ETH-USDT'

def true_range(data):
  """calculates true range"""
  data['previous_close'] = data['close'].shift(1)
  data['high-low'] = abs(data['high'] - data['low'])
  data['high-pc'] = abs(data['high'] - data['previous_close'])
  data['low-pc'] = abs(data['low'] - data['previous_close'])
  
  tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)
  return tr

def average_true_range(data, period):
  """calculates average true range (ATR)"""
  data['tr'] = true_range(data)
  atr = data['tr'].rolling(period).mean()
  
  return atr

def supertrend(df, period=7, atr_multiplier=3):
  """calculates SuperTrend"""
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