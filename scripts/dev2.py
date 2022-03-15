from pandas import DataFrame
from strategies.n2_supertrend import N2SuperTrend, StrategyBase

from pprint import pprint

from core.exchanges.kucoin_extended_new import KuCoinExtended

exchange = KuCoinExtended()

info = exchange.describe()
pprint(info)

