from pandas import DataFrame
import core
from strategies.n2_supertrend import N2SuperTrend, StrategyBase

from core.constants import USER_CONFIG_PATH

from pprint import pprint

from core.exchanges.kucoin_extended import kucoin_extended

exchange = kucoin_extended()

info = exchange.describe()

balances = exchange.fetch_balance()


pprint(info)

