import pandas as pd
import ccxt
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")

exchange = ccxt.kucoin({
  "apiKey": config['KuCoin']['apiKey'],
  "secret": config['KuCoin']['secret'],
  "password": config['KuCoin']['password']
})


def get_bars(pair: str, _timeframe: str, _limit: int):
    # print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(pair, timeframe=_timeframe, limit=_limit)
    return bars


def check_buy_sell_signals(df, open_position=None):
    # print("Checking for signals")
    # print(df.tail(50))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        if open_position is None:
            return "LONG"
        else:
            return "CLOSE"

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if open_position is None:
            return "SHORT"
        else:
            return "CLOSE"

def create_synthetic_pair(base_bars, quote_bars):
    """
      This takes raw kline data from calling
      ccxt.exchange.fetch_ohlcv() as inputs,
      turns them into DataFrames, then divides
      each base OHLCV data point value by its
      corresponding quote value, and returns
      a new DataFrame with the new OHLCV values.
    """
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

    print(  # "\n----------------------------------------------------------------\n"
            # f"[df_base]\n{df_base}"
            # "\n----------------------------------------------------------------\n"
            # f "[df_quote]\n{df_quote}"
            "\n----------------------------------------------------------------\n"
            f"[Kline DataFrame]\n"
            f"{df_synth}"
            "\n----------------------------------------------------------------\n")
    return df_synth
