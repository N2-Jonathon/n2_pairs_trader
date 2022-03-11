from strategy_base import StrategyBase

from pandas import DataFrame as df

from core.indicators import supertrend


class SuperTrend(StrategyBase):
    def __init__(self):
        self.name = "SuperTrend Strategy"

    def get_current_signal(self):
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

