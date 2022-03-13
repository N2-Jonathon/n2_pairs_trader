import sys
from configparser import ConfigParser
import os
import ccxt
import pandas as pd
from pandas import DataFrame
import importlib
sys.path.append(os.getcwd())

from core.config import Config
from core.position_manager import PositionManager, Position
from core.utils import get_synth_pair_symbol, get_exchange_module_from_id  # , create_synthetic_pair


class StrategyBase(Config):

    def __int__(self, config=Config(params=None),):
        self.exchange_id = config.exchange_id
        self.exchange = config.exchange
        self.prompt_for_pairs = config.prompt_for_pairs
        self.base_pair = config.base_pair
        self.quote_pair = config.quote_pair
        self.stake_currency = config.stake_currency

    def __init__(self, exchange: ccxt.Exchange, base_pair: str, quote_pair: str, timeframes=[], paper_trade=False):

        self.exchange_id: str = exchange
        self.exchange: ccxt.Exchange = exchanges[exchange]
        self.base_pair: str = base_pair
        self.quote_pair: str = quote_pair
        self.timeframes = timeframes
        self.paper_trade = paper_trade

        self.name = None
        self.current_signal = None
        self.synth_pair = get_synth_pair_symbol(base_pair, quote_pair)
        self.manager = PositionManager
        self.ohlcv_data = {
            "1m": DataFrame,
            "5m": DataFrame,
            "15m": DataFrame,
            "1h": DataFrame,
            "4h": DataFrame,
            "1d": DataFrame,
            "1w": DataFrame
        }

        for timeframe in timeframes:
            if timeframe.lower in ['1m', '5m', '15m', '1h', '4h', '1d', '1w']:
                self.timeframes.append(timeframe)

    def get_synth_ohlcv(self, timeframe="1m", limit=50):
        base_bars = self.exchange.fetch_ohlcv(self.base_pair, timeframe=timeframe, limit=limit)
        quote_bars = self.exchange.fetch_ohlcv(self.quote_pair, timeframe=timeframe, limit=limit)

        self.ohlcv_data[timeframe]: DataFrame = self.update_synthetic_pair(base_bars, quote_bars)

        return self.ohlcv_data[timeframe]

    def get_timeframe_signal(self, timeframe="1m"):
        # bars = self.e.fetch_ohlcv(pair, timeframe=_timeframe, limit=_limit)
        pass

    def update_synthetic_pair(self, timeframe="1m", limit=50):
        """
          This takes raw kline data from calling
          ccxt.exchange.fetch_ohlcv() as inputs,
          turns them into DataFrames, then divides
          each base OHLCV data point value by its
          corresponding quote value, and returns
          a new DataFrame with the new OHLCV values.
        """

        print(f"{self.base_pair}\n"
              f"{self.quote_pair}")

        base_bars = self.exchange.fetch_ohlcv(symbol=self.base_pair, timeframe=timeframe, since=0, limit=limit)
        quote_bars = self.exchange.fetch_ohlcv(symbol=self.quote_pair, timeframe=timeframe, since=0, limit=limit)

        # base_bars = self.exchange.fe


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