# This is where emails will be sent and/or telegram notifications.

from core.position_manager import PositionManager

class Notifier:

    def __init__(self, pm: PositionManager):
        pm.event_handler.link(self.send_telegram_notification, 'onOpenPosition')
        pm.event_handler.link(self.send_telegram_notification, 'onClosePosition')

    def send_telegram_notification(self, position):
        print("Sending Telegram Notification...\n"
              "Position Info:\n")
        print(position)