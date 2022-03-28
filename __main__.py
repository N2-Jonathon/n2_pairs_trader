from core.position_manager import Position, PositionManager
from core.notifier import Notifier
from strategies.n2_supertrend import N2SuperTrend
from strategies.strategy_base import StrategyBase
import asyncio

strategy = N2SuperTrend()
pm = PositionManager(strategy)
notifier = Notifier(pm)
telegram_client = notifier.telegram_client


async def emulate_signals(strategy):
    if strategy.debug_mode:
        """If in debug mode, prompt for signal override"""
        await strategy.prompt_to_emulate_signal()
    else:
        """If not in debug mode, have the strategy listen for signals"""
        await strategy.listen_for_signals()


async def run_bot(strategy: StrategyBase):
    running = True
    # pm = PositionManager(strategy)
    # notifier = Notifier(pm)

    # telegram_client =
    f1 = telegram_client.loop.create_task(notifier.authenticate_telegram(notifier.api_keys['telegram']['phone']))
    f2 = loop.create_task(emulate_signals(strategy))

    await asyncio.wait([f1, f2])









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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(notifier.authenticate_telegram(notifier.api_keys['telegram']['phone']))

    asyncio.run(run_bot(strategy))  # Can pass a Strategy to override default eg. main(strategy=YourStrategy)
