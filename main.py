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
      Can be calculated with either SMA or RMA.
      TradingView uses RMA so this also does. 
    """
    data['tr'] = true_range(data)
    atr = data['tr'].rolling(window=period).mean()
    atr_sma = simple_moving_average(data['tr'], period)
    atr_rma = relative_moving_average(data['tr'], period)
    #print(f"\n[atr]\n{atr}\n[atr_sma]\n{atr_sma}\n[atr_rma]\n{atr_rma}")
    return atr_rma

def supertrend(df, period=10, atr_multiplier=2):
    """Calculates SuperTrend"""
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = average_true_range(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = None

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

def simple_moving_average(data, period):
  sma = data.rolling(window=period).mean()
  return sma
  

def relative_moving_average(data, period):
  rma = data.ewm(
  alpha=1/period, adjust=False).mean()
  return rma

###[/INDICATOR FUNCTIONS]###


###[UTILITY FUNCTIONS]###
def get_bars(pair: str, _timeframe: str, _limit: int):
  print(f"Fetching new bars for {datetime.now().isoformat()}")
  bars = exchange.fetch_ohlcv(pair, timeframe=_timeframe, limit=_limit)
  return bars

def check_buy_sell_signals(df):
    global in_position

    print("Checking for signals")
    print(df.tail(50))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("Signal: BUY (Uptrend started)")
        if not in_position:
            #order = exchange.create_market_buy_order('ETH/USDT', 0.05)
            #print(order)
            print("Entering long position")
            # - [ ] TODO: Long position logic here
            in_position = True
        else:
            print("Already in a position. Nothing to do.")
    
    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if in_position:
            print("Signal: SELL (Downtrend started)")
            #order = exchange.create_market_sell_order('ETH/USDT', 0.05)
            #print(order)
            print("Entering short position")
            # - [ ] TODO: Short position logic here
            in_position = False
        else:
            print("Not currently in a position. Nothing to sell.")
def run_bot():
    base_bars = exchange.fetch_ohlcv('ETH/USDT', timeframe="1d", limit=50)
    quote_bars = exchange.fetch_ohlcv('BTC/USDT', timeframe="1d", limit=50)

    df = create_synthetic_pair(base_bars, quote_bars)
    
    supertrend_data = supertrend(df)
    
    check_buy_sell_signals(supertrend_data)
    
    
def create_synthetic_pair(base_bars, quote_bars): #def create_synthetic_pair(base, quote, _timeframe, _limit):
    """
      This takes raw kline data from calling
      ccxt.exchange.fetch_ohlcv() as inputs,
      turns them into DataFrames, then divides 
      each base OHLCV data point value by its 
      corresponding quote value, and returns
      a new DataFrame with the new OHLCV values.
    """
    global exchange

    df_base = pd.DataFrame(base_bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_base['timestamp'] = pd.to_datetime(df_base['timestamp'], unit='ms')
    
    df_quote = pd.DataFrame(quote_bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_quote['timestamp'] = pd.to_datetime(df_quote['timestamp'], unit='ms')

    df_synth = (df_base.merge(df_quote, on='timestamp', how='left', suffixes=['_base', '_quote'], sort=False)
                  .pipe(lambda x: x.assign(open=x.open_base/x.open_quote, 
                                           high=x.high_base/x.high_quote,
                                           low=x.low_base/x.low_quote,
                                           close=x.close_base/x.close_quote,
                                           volume=x.volume_base/x.volume_quote))
                )
    for name in df_synth.iteritems():
      if name[0].endswith('_base') or name[0].endswith('_quote'):
        df_synth = df_synth.drop(name[0] , 1)

    print("\n------------------------------------------------\n"
          +f"[df_base]\n{df_base}"
          +"\n------------------------------------------------\n"
          +f"[df_quote]\n{df_quote}"
          +"\n------------------------------------------------\n"
          +f"[df_synth]\n{df_synth}"
          +"\n------------------------------------------------\n")
    return df_synth 
  
###[/UTILITY FUNCTIONS]###

###[SCHEDULE]###
schedule.every(10).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)
###[/SCHEDULE]###