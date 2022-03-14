import ccxt

from strategies.strategy_base import StrategyBase
from core.constants import USER_CONFIG_PATH
import core.utils as utils
from core.position_manager import PositionManager
from core.indicators import supertrend

from pandas import DataFrame


class N2SuperTrend(StrategyBase):

    def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
        super().__init__(params, config_filepath)

        self.name = 'n2_supertrend'

    def get_signal(self, timeframe="1m"):

        self.fetch_bars(timeframe=timeframe)
        bars = self.ohlcv_data[timeframe]["df"]["synth_pair"]

        supertrend_data = supertrend(bars, period=10, atr_multiplier=2)

        # return 'DEBUG_LONG'

        last_row_index = len(supertrend_data.index) - 1
        previous_row_index = last_row_index - 1

        # If the supertrend changes from red to green:
        if not supertrend_data['in_uptrend'][previous_row_index] and supertrend_data['in_uptrend'][last_row_index]:
            if self.manager.get_current_position() is None:
                # If not in a position, long signal
                return "LONG"
            else:
                # If in a position, close signal
                return "CLOSE"
        # If the supertrend changes from green to red:
        if supertrend_data['in_uptrend'][previous_row_index] and not supertrend_data['in_uptrend'][last_row_index]:
            if self.manager.get_current_position() is None:
                # If not in a position, short signal
                return "SHORT"
            else:
                # If in a position, close signal
                return "CLOSE"


