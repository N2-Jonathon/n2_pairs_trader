import os
import sys
from datetime import datetime
# from prompt_toolkit import print_formatted_text, prompt
# from prompt_toolkit.completion import WordCompleter
from colorama import Fore, Back
import colorama

import pandas as pd
from pandas import DataFrame

from eventhandler import EventHandler

# sys.path.append(os.getcwd())

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

    status = {}

    multi_timeframe_mode: bool
    """
    Multi-timeframe signal rules mean that signals on multiple 
    timeframes which are set to True must align with each other 
    in the signals they give ie. They must each be LONG or SHORT
    for an aggregated consensus signal to be made, otherwise the 
    signal will be None
    """
    multi_timeframe_signal_rules = {
        '1m': bool,
        '3m': bool,
        '5m': bool,
        '15m': bool,
        '30m': bool,
        '1h': bool,
        '2h': bool,
        '4h': bool,
        '6h': bool,
        '8h': bool,
        '12h': bool,
        '1d': bool,
        '1w': bool,
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

    def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
        """
        The first line: `super().__init__(params, config_filepath)` means
        it runs the __init__ method in Config and inherits its attributes
        from there, then after that, the other attributes are set.
        """
        super().__init__(params, config_filepath)

        self.name = 'StrategyBase'
        self.current_signal = None
        # self.position_manager = PositionManager()
        DEBUG_safe_symbol = self.exchange.safe_symbol(self.base_pair)
        self._ohlcv_base = self.exchange.fetch_ohlcv(self.exchange.safe_symbol(self.base_pair))
        self._ohlcv_quote = self.exchange.fetch_ohlcv(self.exchange.safe_symbol(self.quote_pair))

        # self.ohlcv_synth = self.

        self.event_handler = EventHandler('newSignal')
        self.event_handler.link(self.__on_new_signal, 'newSignal')

        colorama.init()

    def __on_new_signal(self, signal):
        self.status['msg'] = f"StrategyBase.__on_new_signal fired!"
        self.status['signal'] = signal
        if self.debug_mode:
            print("=======[DEBUG]==========\n"
                  f"{self.status['msg']}\n"
                  f"{self.status['signal']}\n"
                  "=======================\n")

    @staticmethod
    def __on_new_signal_dev(self, signal):
        """Obselete, todo: safe delete"""
        self.status['msg'] = f"StrategyBase.__on_new_signal fired!"
        if self.debug_mode:
            print("=======[DEBUG]==========\n"
                  f"{self.status['msg']}\n"
                  "=======================\n")

        if signal.upper() == 'LONG' or signal.upper() == 'SHORT':
            """If there is a new signal to LONG or SHORT:"""

            self.status['msg'] = (f"New {signal} signal on {self.synth_pair} from {self.strategy}."
                                  f"Opening new {signal.lower()} position...")
            print(self.status['msg'])

            self.open(signal=signal,
                      order_type='market')  # TODO: add support for limit orders

        elif signal.upper() == 'CLOSE':
            """If there's a signal to CLOSE, close current position"""
            self.close(self.current_position)

        else:
            self.status['msg'] = f"invalid signal: {signal}. No actions taken"
            self.status['ok'] = False
            print(self.status)

    def override_signal(self, signal):
        self.event_handler.fire('newSignal', signal)

    def prompt_to_override_signal(self):
        # override_options = WordCompleter(['Long', 'Short', 'Close'])
        override_signal = input("[DEBUG] Override signal (Press TAB for auto-complete): ").upper()
        if override_signal == "L":
            self.override_signal('LONG')  # Default if you just press enter at the prompt
        elif override_signal == "" or override_signal == "S":
            self.override_signal('SHORT')
        elif override_signal.upper() == 'SHORT' or override_signal == 'LONG':
            self.override_signal(override_signal)
        elif override_signal == 'CLOSE' or override_signal == 'C':
            self.override_signal('CLOSE')

    def fetch_synth_ohlcv(self, timeframe="1m", limit=50, timeframes=None):
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

    def convert_ohlcv_list_to_dataframe(self, ohlcv: list)-> DataFrame:
        pass

    def listen_for_signals(self, timeframe="1m"):
        raise NotImplemented("Error: listen_for_signals method not implemented for StrategyBase.\n"
                             "You can override this method in strategy classes that inherit"
                             "StrategyBase by writing a new method: `def listen_for_signals(self, timeframe):`"
                             "then putting your strategy's logic in that method.")

    def tick(self):
        pass
