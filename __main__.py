import asyncio
from configparser import ConfigParser
import ccxt
import time

from core.indicators import supertrend
from core.position_manager import Position, PositionManager
from core.utils import create_synthetic_pair, check_signals
from core.config import Config

"""
pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
"""


def main(config: Config = Config()):

    running = True

    strategy_name = config.strategy_name

    strategy = config.strategy
    manager = PositionManager()

    strategy_timeframes = ['1m', '5m', '15m', '1h']
    signals = {
        "1m": None,
        "5m": None,
        "15m": None,
        "1h": None,
        "4h": None,
        "1d": None,
        "1w": None
    }

    while running:

        for timeframe in strategy_timeframes:
            base_bars = config.exchange.fetch_ohlcv(config.base_pair, timeframe=timeframe, limit=50)
            quote_bars = config.exchange.fetch_ohlcv(config.quote_pair, timeframe=timeframe, limit=50)

            synth_pair = create_synthetic_pair(base_bars, quote_bars)

            supertrend_data = supertrend(synth_pair)

            signal = check_signals(supertrend_data)
            signals[timeframe] = signal
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

        print(f"Signals: \n"
              f"1m: {signals['1m']}\n"
              f"5m: {signals['5m']}\n"
              f"15m: {signals['15m']}\n"
              f"1h: {signals['1h']}\n"
              f"4h: {signals['4h']}\n"
              f"1d: {signals['1d']}\n"
              f"1w: {signals['1w']}\n")

        if signal is not None and signal != 'CLOSE':

            if manager.get_current_position() is None:
                position = Position(config.base_pair, config.quote_pair,
                                    direction=signal,
                                    order_type='limit').open()
                manager.set_current_position(position)

        elif signal == 'CLOSE':
            manager.current_position.close()

        time.sleep(60)
        # await asyncio.sleep(60)


if __name__ == '__main__':
    # - The param inside main() `config=Config()` is
    # doing the same thing as below, except with the
    # values read from user-config
    # - So, assigning it again  is actually redundant,
    # and it's just to demonstrate how to override the
    # default config. If you delete the following 6
    # lines it will be the user-config defaults:
    config = Config()


    config.new(exchange='kucoin',
                          strategy_name='n2_supertrend',
                          prompt_for_pairs=False,
                          base_pair='ETH/USDT',
                          quote_pair='BTC/USDT',
                          stake_currency='USDT',
                          paper_trade=False)
    main(config)

# asyncio.run(main())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
