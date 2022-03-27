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
            strategy.prompt_to_emulate_signal()
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
