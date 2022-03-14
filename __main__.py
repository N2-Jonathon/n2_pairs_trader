import os
import time


from core.position_manager import Position, PositionManager
from strategies.n2_supertrend import N2SuperTrend


USER_CONFIG_PATH = f"{os.getcwd()}/user/user-config.ini"
print(USER_CONFIG_PATH)

"""
pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
"""


def main(strategy=N2SuperTrend()):
    running = True

    pm: PositionManager = strategy.position_manager

    while running:

        signal = strategy.get_signal()

        # [DEBUG] Un-comment one of the three lines below to force a signal:
        # signal = 'LONG'
        # signal = 'SHORT'
        # signal = 'CLOSE'

        if signal is not None and signal != 'CLOSE':

            if pm.get_current_position() is None:
                position = Position(strategy.base_pair, strategy.quote_pair,
                                    direction=signal,
                                    order_type='limit').open()
                pm.set_current_position(position)

        elif signal == 'CLOSE':
            pm.current_position.close()

        time.sleep(60)
        # await asyncio.sleep(60)


if __name__ == '__main__':

    main()  # Can pass a Strategy to main to override default

# asyncio.run(main())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
