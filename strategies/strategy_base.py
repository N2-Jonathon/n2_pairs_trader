import sys
from configparser import ConfigParser
import os

print(os.getcwd())
sys.path.append(os.getcwd())

from main import config
from core.position_manager import PositionManager, Position
from core.utils import get_synth_pair_symbol, create_synthetic_pair
from pandas import DataFrame


"""
config = configparser.ConfigParser
user_config_path = os.path.join(os.getcwd(), 'user-config.ini')
user_config.read(config_path)
"""


class StrategyBase:

    def __init__(self, base_pair: str, quote_pair: str, timeframes=[], paper_trade=False, config: ConfigParser = config):
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

        for timeframe in timeframes:
            if timeframe.lower in ['1m', '5m', '15m', '1h', '4h', '1d', '1w']:
                self.timeframes.append(timeframe)

    def get_synth_ohlcv(self, timeframe="1m", limit=50):
        base_bars = self.fetch_ohlcv(self.base_pair, timeframe=timeframe, limit=limit)
        quote_bars = self.fetch_ohlcv(self.quote_pair, timeframe=timeframe, limit=limit)

        ohlcv: DataFrame = create_synthetic_pair(base_bars, quote_bars)

        return ohlcv

    def get_current_signal(self):

        return self.current_signal
