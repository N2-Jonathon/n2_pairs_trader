import os
import sys
from datetime import datetime

import pandas as pd
from pandas import DataFrame

sys.path.append(os.getcwd())

from core.config import Config
from core.position_manager import PositionManager
from core.utils import get_synth_pair_symbol  # , create_synthetic_pair
from core.constants import USER_CONFIG_PATH

from finta.finta import inputvalidator

inputvalidator()


class StrategyBase(Config):
    __dict__ = {
        "exchange": str,
        "strategy_name": str,
        "prompt_for_pairs": bool,
        "base_pair": str,
        "quote_pair": str,
        "synth_pair": str,  # Not sure if this is set by __init__ yet
        "stake_currency": str,
        "paper_trade": bool,

        "position_manager": PositionManager,
        "previous_tick": datetime,
        "ohlcv_data": dict,
        "signal": str,
    }

    ohlcv_data = {
        "1m": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "5m": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "15m": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "1h": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "4h": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "1d": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
        "1w": {
            "raw": {
                "base_pair": list[list[int | None]],
                "quote_pair": list[list[int | None]],
                "synth_pair": list[list[int | None]]
            },
            "df": {
                "base_pair": DataFrame,
                "quote_pair": DataFrame,
                "synth_pair": DataFrame
            }
        },
    }
    position_manager = PositionManager()

    def __int__(self, params={}, config_filepath=USER_CONFIG_PATH):
        super().__init__(self, params, config_filepath)

        self.name = None
        self.current_signal = None
        self.synth_pair = get_synth_pair_symbol(self.base_pair, self.quote_pair)
        self.position_manager = PositionManager()

    def fetch_bars(self, timeframe="1m", limit=50, timeframes=None):
        """
          This takes raw kline data from calling
          self.exchange.fetch_ohlcv() for each pair
          as inputs, turns them into DataFrames, 
          then divides each base OHLCV data point 
          value by its corresponding quote value, 
          and returns a new DataFrame with the new 
          OHLCV values.
        """
        print("Fetching bars...")
        base_bars = self.exchange.fetch_ohlcv(self.base_pair, timeframe=timeframe, limit=limit)
        quote_bars = self.exchange.fetch_ohlcv(self.quote_pair, timeframe=timeframe, limit=limit)

        self.ohlcv_data[timeframe]["raw"]["base_pair"] = base_bars
        self.ohlcv_data[timeframe]["raw"]["quote_pair"] = quote_bars
        # self.ohlcv_data[timeframe]["raw"]["synth_bars"] = ??

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

        self.ohlcv_data[timeframe]["df"]["base_pair"] = df_base
        self.ohlcv_data[timeframe]["df"]["quote_pair"] = df_quote
        self.ohlcv_data[timeframe]["df"]["synth_pair"] = df_synth
         
        return df_synth

    def get_signal(self, timeframe="1m"):
        raise NotImplemented("Error: get_signal method not implemented for StrategyBase.\n"
                             "You can override this method in strategy classes that inherit"
                             "StrategyBase by writing a new method: `def get_signal(self, timeframe):`"
                             "then putting your strategy's logic in that method.")

    def get_signals(self, timeframes=["1m", "5m", "15m"]):
        signals = {}
        for tf in timeframes:
            signals[tf] = self.get_signal(timeframe=tf)
