import asyncio
from configparser import ConfigParser
import ccxt

from core.indicators import supertrend
from core.position_manager import Position, PositionManager
from core.utils import create_synthetic_pair, check_signals

from core.exchanges.kucoin_extended import KuCoinExtended
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
    # strategy = N2SuperTrend(exchange, config, base_pair, quote_pair)
    # manager = strategy.position_manager
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

        # This code is for one timeframe. Later, do the same iterated for each timeframe.
        # ---------------------------------------------------
        for timeframe in strategy_timeframes:
            base_bars = exchange.fetch_ohlcv(base_pair, timeframe=timeframe, limit=50)
            quote_bars = exchange.fetch_ohlcv(quote_pair, timeframe=timeframe, limit=50)

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
