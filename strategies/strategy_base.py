import os
import sys
from datetime import datetime

import pandas as pd
from pandas import DataFrame

sys.path.append(os.getcwd())

from core.config import Config
from core.position_manager import PositionManager
from core.constants import USER_CONFIG_PATH

from finta.finta import inputvalidator

inputvalidator()


class StrategyBase(Config):
    """
    A strategy is an object whose main purpose is to contain regularly
    updated market data by pulling OHLCV data from both the base pair
    and the quote pair, then combining them to make the synth pair.

    The main logic which is specific to your strategy should be
    implemented in the `get_signal()` method which should then
    be called at a regular defined interval.
    """
    __dict__ = {
        "cfg_file_key": str,
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

        "multi_timeframe_mode": bool,
        "multi_timeframe_signal_rules": dict,
    }

    multi_timeframe_mode: bool
    """
    Multi-timeframe signal rules mean that signals on multiple 
    timeframes which are set to True must align with each other 
    in the signals they give ie. They must each be LONG or SHORT
    for an aggregated consensus signal to be made, otherwise the 
    signal will be None
    """
    multi_timeframe_signal_rules = {
        "1m": bool,
        "5m": bool,
        "15m": bool,
        "1h": bool,
        "1d": bool,
        "1w": bool
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
    position_manager: PositionManager = None

    def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
        """
        The first line: `super().__init__(params, config_filepath)` means
        it runs the __init__ method in Config and inherits its attributes
        from there, then after that, the other attributes are set.

        :param params:
        :type params:
        :param config_filepath:
        :type config_filepath:
        :return:
        :rtype:
        """
        super().__init__(params, config_filepath)

        self.name = 'StrategyBase'
        self.current_signal = None
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
        print(f"Fetching bars for: {self.synth_pair} {timeframe} (limit={limit}\n"
              f"[timestamp (UTC): {datetime.utcnow().isoformat()}]")

        if self.debug_mode:
            pass

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

    def get_signals(self, timeframes={"1m", "5m", "15m"}):
        if timeframes is None or len(timeframes) == 0:
            return ValueError("No timeframes were given")

        signals = {}
        for tf in timeframes:
            signals[tf] = self.get_signal(timeframe=tf)

        return signals
