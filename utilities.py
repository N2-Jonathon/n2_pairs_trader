import pandas as pd
from datetime import datetime


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
            # order = exchange.create_market_buy_order('ETH/USDT', 0.05)
            # print(order)
            print("Entering long position")
            # - [ ] TODO: Long position logic here
            in_position = True
        else:
            print("Already in a position. Nothing to do.")

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if in_position:
            print("Signal: SELL (Downtrend started)")
            # order = exchange.create_market_sell_order('ETH/USDT', 0.05)
            # print(order)
            print("Entering short position")
            # - [ ] TODO: Short position logic here
            in_position = False
        else:
            print("Not currently in a position. Nothing to sell.")


def create_synthetic_pair(base_bars, quote_bars):
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
                .pipe(lambda x: x.assign(open=x.open_base / x.open_quote,
                                         high=x.high_base / x.high_quote,
                                         low=x.low_base / x.low_quote,
                                         close=x.close_base / x.close_quote,
                                         volume=x.volume_base / x.volume_quote))
                )
    for name in df_synth.iteritems():
        if name[0].endswith('_base') or name[0].endswith('_quote'):
            df_synth = df_synth.drop(name[0], 1)

    print("\n------------------------------------------------\n"
          + f"[df_base]\n{df_base}"
          + "\n------------------------------------------------\n"
          + f"[df_quote]\n{df_quote}"
          + "\n------------------------------------------------\n"
          + f"[df_synth]\n{df_synth}"
          + "\n------------------------------------------------\n")
    return df_synth
