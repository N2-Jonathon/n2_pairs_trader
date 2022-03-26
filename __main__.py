import os
import time
import asyncio


from core.position_manager import Position, PositionManager
from strategies.n2_supertrend import N2SuperTrend

"""
pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')
"""


def run_bot(strategy=N2SuperTrend()):
    running = True

    pm = PositionManager(strategy)

    while running:

        if pm.debug_mode:
            """If in debug mode, prompt for signal override"""
            DEBUG_override_signal = input("[DEBUG]Enter a signal to emulate (LONG|[SHORT]|CLOSE):").upper()
            if DEBUG_override_signal == "L":
                strategy.emulate_signal('LONG')  # Default if you just press enter at the prompt
            elif DEBUG_override_signal == "" or DEBUG_override_signal == "S":
                strategy.emulate_signal('SHORT')
            elif DEBUG_override_signal.upper() == 'SHORT' or DEBUG_override_signal == 'LONG':
                strategy.emulate_signal(DEBUG_override_signal)
            elif DEBUG_override_signal == 'CLOSE' or DEBUG_override_signal == 'C':
                strategy.emulate_signal('CLOSE')
        else:
            """If not in debug mode, call the get_signal method of the strategy"""
            strategy.listen_for_signals()


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

    run_bot()  # Can pass a Strategy to override default eg. main(strategy=YourStrategy)

    # Later I plan to take advantage of async to run multiple strategies
    # asyncio.run(run_bot())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run_bot())
