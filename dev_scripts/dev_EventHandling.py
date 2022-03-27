from eventhandler import EventHandler
from datetime import datetime

from pprint import pprint


class StrategyBase:

    def __init__(self):
        self.event_handler = EventHandler('newSignal')
        self.event_handler.link(self.__on_new_signal, 'newSignal')

    def __on_new_signal(self, signal):
        print("=======================\n"
              f"StrategyBase.__on_new_signal fired!\n"
              "=======================\n")

    def emulate_signal(self, signal):
        self.event_handler.fire('newSignal', signal)


class PositionManager:

    def __init__(self, strategy: StrategyBase):
        self.__positions = []  # Stores all positions
        self.event_handler = EventHandler('onOpenPosition', 'onClosePosition')

        self.event_handler.link(self.__on_open_position, 'onOpenPosition')
        self.event_handler.link(self.__on_close_position, 'onClosePosition')


        strategy.event_handler.link(self.open, 'newSignal')

    # This callback will be called when onOpenPosition event happens
    def __on_open_position(self, position):
        print("=======================\n"
              "PositionManager.__on_open_position fired!\n")
        print(f"Position Opened:\n"
              f"{position}\n"
              "=======================\n")
        self.__positions.append(position)

    # This callback will be called when onClosePosition event happens
    def __on_close_position(self, position):
        print("=======================\n"
              "PositionManager.__on_close_position fired!\n")
        print(f"Position Closed:\n"
              f"{position}"
              "=======================\n")

    # Now let's define the public methods of the PositionManager to be used outside the class
    def open(self, direction):
        position = {
            "signal": direction,
            "open_timestamp": datetime.utcnow().timestamp(),
            "status": "open"
        }
        print("=======================\n"
              "PositionManager.open() called\n"
              f"Opening {direction} position:\n")
        pprint(position)
        print("\nAbout to fire:\n"
              "self.event_handler.fire('onOpenPosition', position)\n"
              "=======================\n")

        self.event_handler.fire('onOpenPosition', position)

    def close(self, position):
        print("=======================\n"
              "PositionManager.open() called\n"
              f"Closing Position:\n"
              f"{position}")
        position['status'] = "closed"
        position['close_timestamp'] = datetime.utcnow().timestamp()
        print("About to fire:\n"
              "self.event_handler.fire('onClosePosition', position)\n")
        self.event_handler.fire('onClosePosition', position)
