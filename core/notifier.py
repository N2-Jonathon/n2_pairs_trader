# This is where emails will be sent and/or telegram notifications.

from core.position_manager import PositionManager

import asyncio
from pyrogram import Client
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError


class Notifier:

    def __init__(self: object, pm: PositionManager) -> None:
        self.pm = pm
        self.loop = asyncio.get_event_loop()


        self.pyrogram_tg_client = Client(self.pm.api_keys['telegram']['username'],
                                         self.pm.api_keys['telegram']['app_api_id'],
                                         self.pm.api_keys['telegram']['api_hash'])
        '''
        self.telethon_tg_client = TelegramClient(self.pm.api_keys['telegram']['username'],
                                                 self.pm.api_keys['telegram']['app_api_id'],
                                                 self.pm.api_keys['telegram']['api_hash'])
        '''
        # self.loop.run_until_complete(self.run_pyrogram_client())
        pm.event_handler.link(self.send_telegram_notification, 'onOpenPosition')
        pm.event_handler.link(self.send_telegram_notification, 'onClosePosition')
        # self.schedule_tasks()

    def schedule_tasks(self: object) -> None:
        """ Minimal selection of tasks for this demonstation. """
        loop = self.loop
        # DEBUG_task = self.loop.create_task(self.run_pyrogram_client())
        self.loop.run_until_complete(self.run_pyrogram_client())
        breakpoint()

    def send_telegram_notification(self, position):
        print("Sending Telegram Notification...\n"
              "Position Info:\n")
        print(position)
        # breakpoint()
        self.loop.run_until_complete(self.send_telegram_msg(str(position)))
        breakpoint()


    async def send_telegram_msg(self, msg: str):
        async with self.pyrogram_tg_client as tg:
            await tg.send_message('jonathon_test', msg)

