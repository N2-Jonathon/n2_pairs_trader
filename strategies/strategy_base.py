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

from finta.finta import inputvalidator


inputvalidator()


class StrategyBase(Config):

    def __int__(self, params={}, config_filepath=None):
        super(params, config_filepath)

        self.name = None
        self.current_signal = None
        self.synth_pair = get_synth_pair_symbol(self.base_pair, self.quote_pair)
        self.position_manager = PositionManager()
        self.ohlcv_data = {
            "1m": {
                "df": DataFrame,
                "raw_ohlcv": str
            },
            "5m": DataFrame,
            "15m": DataFrame,
            "1h": DataFrame,
            "4h": DataFrame,
            "1d": DataFrame,
            "1w": DataFrame
        }

    def get_bars(self, timeframe="1m", limit=50):
        base_bars = self.exchange.fetch_ohlcv(self.base_pair, timeframe=timeframe, limit=limit)
        quote_bars = self.exchange.fetch_ohlcv(self.quote_pair, timeframe=timeframe, limit=limit)

        self.ohlcv_data[timeframe]: DataFrame = self.update_synthetic_pair(base_bars, quote_bars)

        return self.ohlcv_data[timeframe]

    def get_signal(self, timeframe="1m", timeframes=None):
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
