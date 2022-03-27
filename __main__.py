from core.position_manager import Position, PositionManager
from core.notifier import Notifier
from strategies.n2_supertrend import N2SuperTrend


def run_bot(strategy=N2SuperTrend()):
    running = True

    pm = PositionManager(strategy)
    notifier = Notifier(pm)

    while running:

        if strategy.debug_mode:
            """If in debug mode, prompt for signal override"""
            strategy.prompt_to_emulate_signal()
        else:
            """If not in debug mode, have the strategy listen for signals"""
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
