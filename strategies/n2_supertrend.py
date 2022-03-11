# from main import config
from configparser import ConfigParser
from strategies.strategy_base import StrategyBase
import core.utils as utils
from core.position_manager import PositionManager

# from pandas import DataFrame as df


class N2SuperTrend(StrategyBase):

    def __init__(self, config: ConfigParser, base_pair: str, quote_pair: str, timeframes=[],  paper_trade=False):
        self.name = "SuperTrend Strategy"
        self.config = config
        self.exchange_id = config['Global Settings']['exchange']
        self.name = None
        self.current_signal = None
        self.base_pair = base_pair
        self.quote_pair = quote_pair
        self.synth_pair = utils.get_synth_pair_symbol(base_pair, quote_pair)
        self.paper_trade = paper_trade
        self.timeframes = []
        self.position_manager = PositionManager()
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

    def get_timeframe_signal(self, timeframe="1m"):
        df = self.ohlcv_data.get('timeframe')



        last_row_index = len(df.index) - 1
        previous_row_index = last_row_index - 1

        if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
            if self.manager.get_current_position() is None:
                return "LONG"
            else:
                return "CLOSE"

        if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
            if self.manager.get_current_position() is None:
                return "SHORT"
            else:
                return "CLOSE"

