from configparser import ConfigParser

import ccxt

from strategies.strategy_base import StrategyBase
import core.utils as utils
from core.utils import get_exchange_module_from_id
from core.position_manager import PositionManager

from pandas import DataFrame


class N2SuperTrend(StrategyBase):

    def __init__(self, exchange: ccxt.Exchange, config: ConfigParser, base_pair: str, quote_pair: str, timeframes=[], paper_trade=False):

        self.name = 'n2_supertrend'

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

    def get_signal(self, timeframe="1m", timeframes=None):

        return 'DEBUG_LONG'

        df = self.ohlcv_data.get('timeframe')
        #raw_ohlcv = self.get_synth_ohlcv("1m")
        #df = utils.create_synthetic_pair(raw_ohlcv)

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


