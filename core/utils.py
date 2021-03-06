import warnings

import pandas as pd
import ccxt
import importlib
import os
import sys

from core.constants import USER_CONFIG_PATH
from ccxt.base.errors import BadSymbol
import configparser
from datetime import datetime

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

"""
config = configparser.ConfigParser()
config.read("user-config.ini")

exchange = ccxt.kucoin({
    "apiKey": config['KuCoin']['apiKey'],
    "secret": config['KuCoin']['secret'],
    "password": config['KuCoin']['password']
})
"""


def get_synth_pair_tuple(base_pair, quote_pair):
    base_pair_split = split_pair(base_pair)
    quote_pair_split = split_pair(quote_pair)

    synth_pair = (f"{base_pair_split[0]}{base_pair_split[1]}"
                  f"/{quote_pair_split[0]}{quote_pair_split[1]}")

    synth_pair_tuple = (synth_pair,
                        base_pair_split[0],
                        base_pair_split[1],
                        quote_pair_split[0],
                        quote_pair_split[1])
    return synth_pair_tuple


def get_borrow_coin(synth_pair_tuple, position_direction):

    if position_direction == 'LONG':
        borrow_coin = synth_pair_tuple[3]
        pass
    elif position_direction == 'SHORT':
        borrow_coin = synth_pair_tuple[1]

    else:
        borrow_coin = ValueError("Invalid position signal. (Must be 'LONG' or 'SHORT')")

    return borrow_coin


def fetch_ticker(_exchange, symbol, params={}):
    if _exchange.has['fetchTickers']:
        tickers = _exchange.fetch_tickers([symbol], params)
        ticker = _exchange.safe_value(tickers, symbol)
        if ticker is None:
            return None
        else:
            return ticker
    else:
        raise Exception(f' fetchTicker not supported yet by {_exchange}')


def is_valid_coin(_exchange: ccxt.Exchange, symbol, params={}):
    balances = _exchange.base_currencies


def split_pair(pair, pair_type=None):

    if '/' in pair:
        return pair.split('/')
    else:
        raise ValueError('Invalid trading pair')
    pass


def get_bars(exchange, pair: str, _timeframe: str, _limit: int):
    """
    Unused
    """
    # print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(pair, timeframe=_timeframe, limit=_limit)
    return bars


def check_signals(df, open_position=None):
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


def get_exchange_module_from_id(name: str):
    if name.lower() in ccxt.exchanges:
        exchange_module_path = f"ccxt.{name.lower()}"
        print(exchange_module_path)
        exchange = importlib.import_module(exchange_module_path)
        return exchange

        pass
        # return exchange
    else:
        raise ValueError("Invalid exchange name")
    pass


def get_project_root():
    root_dir_name = 'n2_pairs_trader'
    cwd = os.getcwd()
    sys.path.append(cwd)
    for path in sys.path:
        if path.endswith(root_dir_name):
            return path
        elif root_dir_name in path:
            end_index = path.find(root_dir_name) + len(root_dir_name)
            root_path = path[:end_index]
            return root_path
            pass

    raise ValueError("It should be impossible for this error to raise. If it does, maybe the world has ended...")


def get_user_config_path():
    root = get_project_root()
    return f"{root}/user/user-config.ini"
# DEBUG



