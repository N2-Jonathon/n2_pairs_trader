import asyncio
import pandas as pd
import warnings
from configparser import ConfigParser

from strategies.n2_supertrend import N2SuperTrend
from core.position_manager import Position, PositionManager

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

exchange = kucoin


# print(balances)

async def main(base_pair=config['Global Settings']['base_pair_default'],
               quote_pair=config['Global Settings']['quote_pair_default']):
    running = True
    strategy = N2SuperTrend(config, base_pair, quote_pair)
    manager = strategy.position_manager

    while running:

        # This code is for one timeframe. Later, do the same iterated for each timeframe.

        signal = strategy.get_timeframe_signal()

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
