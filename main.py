import asyncio
import ccxt
import pandas as pd
import warnings
from configparser import ConfigParser

from core.indicators import supertrend
from core.utils import check_signals, create_synthetic_pair
from core.position_manager import Position, PositionManager
from strategies.strategy_base import StrategyBase

from scripts.kucoin_extended import KuCoinExtended

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

config = ConfigParser()
config.read("user-config.ini")

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
    manager = PositionManager()
    strategy = StrategyBase(config, base_pair, quote_pair)

    while running:

        # This code is for one timeframe. Later, do the same iterated for each timeframe.
        base_bars = exchange.fetch_ohlcv(base_pair, timeframe="1m", limit=50)
        quote_bars = exchange.fetch_ohlcv(quote_pair, timeframe="1m", limit=50)

        pair = create_synthetic_pair(base_bars, quote_bars)

        supertrend_data = supertrend(pair)

        signal = check_signals(supertrend_data)

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
