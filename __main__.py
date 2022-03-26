import os
import time
import asyncio


from core.position_manager import Position, PositionManager
from strategies.n2_supertrend import N2SuperTrend

"""
pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
"""


async def run_bot(strategy=N2SuperTrend()):
    running = True

    pm = PositionManager(strategy)

    while running:

        if pm.debug_mode:
            """If in debug mode, prompt for signal override"""
            DEBUG_override_signal = input("[DEBUG]Enter a signal to emulate (LONG|[SHORT]|CLOSE):").upper()
            if DEBUG_override_signal == "L":
                strategy.current_signal = 'LONG'  # Default if you just press enter at the prompt
            elif DEBUG_override_signal == "" or DEBUG_override_signal == "S":
                strategy.current_signal = 'SHORT'
            elif DEBUG_override_signal.upper() == 'SHORT' or DEBUG_override_signal == 'LONG':
                strategy.current_signal = DEBUG_override_signal
            elif DEBUG_override_signal == 'CLOSE' or DEBUG_override_signal == 'C':
                strategy.current_signal = 'CLOSE'
        else:
            """If not in debug mode, call the get_signal method of the strategy"""
            await strategy.get_signal()

        '''
        if strategy.current_signal is not None and strategy.current_signal != 'CLOSE':
            """If there is a new signal to LONG or SHORT:"""
            if pm.current_position is None:
                """
                If there's no current position open, then open one
                in the direction of the signal and set it as pm's
                current_position
                """
                position = pm.open(direction=strategy.current_signal,
                                    order_type='limit')

                pm.set_current_position(position)

        elif strategy.current_signal == 'CLOSE':
            """
            If the signal is 'CLOSE', then close the pm.current_position
            """
            pm.current_position.close()

        check_signal_interval = 60  # This should be adjusted to take API rate limits into account
        """For now the tick_interval is set here, but it should be set by params or in Config"""
        time.sleep(check_signal_interval)
        # await asyncio.sleep(tick_interval)
        '''


if __name__ == '__main__':
    print("""
      ₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿          N^2 Capital
      ₿₿                             ₿₿          
      ₿₿                             ₿₿          Crypto Pairs Trader
      ₿₿                             ₿₿          v0.0.1 (Alpha)
      ₿₿                             ₿₿          
      ₿₿                                       
      ₿₿                ₿₿₿₿         ₿₿          
      ₿₿                ₿₿  ₿₿       ₿₿          
      ₿₿                ₿₿    ₿₿     ₿₿          
      ₿₿                ₿₿      ₿₿   ₿₿          
      ₿₿                ₿₿        ₿₿ ₿₿          Created by
      ₿₿₿₿₿₿₿₿₿₿₿₿₿₿₿   ₿₿  ₿₿₿₿₿₿  ₿₿₿          Jonathon Quick
          """)

    asyncio.run(run_bot())  # Can pass a Strategy to override default eg. main(strategy=YourStrategy)

    # Later I plan to take advantage of async to run multiple strategies
    # asyncio.run(run_bot())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run_bot())
