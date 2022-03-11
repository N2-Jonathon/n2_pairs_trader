import asyncio
import pandas as pd
import warnings
from configparser import ConfigParser
from pprint import pprint
import ccxt

from core.indicators import supertrend
from strategies.strategy_base import StrategyBase
from strategies.n2_supertrend import N2SuperTrend
from core.position_manager import Position, PositionManager
from core.utils import create_synthetic_pair, check_signals

from scripts.kucoin_extended import KuCoinExtended
"""
pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
"""
config = ConfigParser()
config.read("user/user-config.ini")

kucoin = KuCoinExtended({
    "apiKey": config['KuCoin']['apiKey'],
    "secret": config['KuCoin']['secret'],
    "password": config['KuCoin']['password']
})

hitbtc = ccxt.hitbtc({
    "apiKey": config['HitBTC']['apiKey'],
    "secret": config['HitBTC']['apiKey']
})

exchange = kucoin


# print(balances)

async def main(base_pair=config['Global Settings']['base_pair_default'],
               quote_pair=config['Global Settings']['quote_pair_default']):
    running = True
    strategy = N2SuperTrend(exchange, config, base_pair, quote_pair)
    manager = strategy.position_manager

    while running:

        # This code is for one timeframe. Later, do the same iterated for each timeframe.
        # ---------------------------------------------------
        base_bars = exchange.fetch_ohlcv(base_pair)
        quote_bars = exchange.fetch_ohlcv(quote_pair)

        synth_pair = create_synthetic_pair(base_bars, quote_bars)

        supertrend_data = supertrend(synth_pair)

        signal = check_signals(supertrend_data)
        # ---------------------------------------------------


        # ---------------------------------------------------
        # Trying to get the above to be abstracted away, but
        # spent ages debugging and decided to implement this
        # by using strategy.exchange instead of global exchange
        #
        # current_ohlcv = strategy.update_synthetic_pair()
        # signal = strategy.get_timeframe_signal()
        # ---------------------------------------------------




        # [DEBUG] Un-comment one of the three lines below to force a signal:
        # signal = 'LONG'
        # signal = 'SHORT'
        # signal = 'CLOSE'

        print(f"Signal: {signal}")

        if signal is not None and signal != 'CLOSE':

            if manager.get_current_position() is None:
                position = Position(base_pair, quote_pair,
                                    direction=signal,
                                    order_type='limit').open()
                manager.set_current_position(position)

        elif signal == 'CLOSE':
            manager.current_position.close()

        await asyncio.sleep(60)


asyncio.run(main())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
