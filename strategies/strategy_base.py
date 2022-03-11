import sys
from configparser import ConfigParser
import os

print(os.getcwd())
sys.path.append(os.getcwd())

from core.position_manager import PositionManager, Position
from core.utils import get_synth_pair_symbol, create_synthetic_pair
from pandas import DataFrame

"""
config = ConfigParser
user_config_path = os.path.join(os.getcwd(), 'user/user-config.ini')
config.read(self=config, filenames=user_config_path)
"""

class StrategyBase:

    def __init__(self, config: ConfigParser, base_pair: str, quote_pair: str, timeframes=[],  paper_trade=False):
        self.config = config
        self.exchange_id = config['Global Settings']['exchange']
        self.name = None
        self.current_signal = None
        self.base_pair = base_pair
        self.quote_pair = quote_pair
        self.synth_pair = get_synth_pair_symbol(base_pair, quote_pair)
        self.paper_trade = paper_trade
        self.timeframes = []
        self.manager = PositionManager
        self.ohlcv_data = {
            "1m": None,
            "5m": None,
            "15m": None,
            "1h": None,
            "4h": None,
            "1d": None,
            "1w": None
        }

        for timeframe in timeframes:
            if timeframe.lower in ['1m', '5m', '15m', '1h', '4h', '1d', '1w']:
                self.timeframes.append(timeframe)

    def get_synth_ohlcv(self, timeframe="1m", limit=50):
        base_bars = self.fetch_ohlcv(self.base_pair, timeframe=timeframe, limit=limit)
        quote_bars = self.fetch_ohlcv(self.quote_pair, timeframe=timeframe, limit=limit)

        self.ohlcv_data[timeframe]: DataFrame = create_synthetic_pair(base_bars, quote_bars)

        return self.ohlcv_data

    def get_timeframe_signal(self, timeframe="1m"):
        # bars = self.e.fetch_ohlcv(pair, timeframe=_timeframe, limit=_limit)
        pass
