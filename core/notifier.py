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

        self.telethon_tg_client = TelegramClient(pm.api_keys['telegram']['username'],
                                                 pm.api_keys['telegram']['app_api_id'],
                                                 pm.api_keys['telegram']['api_hash'])
        pm.event_handler.link(self.send_telegram_notification, 'onOpenPosition')
        pm.event_handler.link(self.send_telegram_notification, 'onClosePosition')
        self.schedule_tasks()
        self.send_telegram_notification()


    def schedule_tasks(self) -> None:
        """ Minimal selection of tasks for this demonstation. """
        self.loop.create_task(self.pyrogram_send_msg())
        self.loop.run_until_complete(self.pyrogram_send_msg())
        self.loop.create_task(self.telethon_authenticate_telegram(self.pm.api_keys['telegram']['phone']))


    def send_telegram_notification(self, position=None):
        print("Sending Telegram Notification...\n"
              "Position Info:\n")
        print(position)
        breakpoint()
        self.loop.create_task(self.telethon_authenticate_telegram(self.pm.api_keys['telegram']['phone']))
        breakpoint()

    async def telethon_authenticate_telegram(self, phone):
        if not await self.telethon_tg_client.is_user_authorized():
            await self.telethon_tg_client.send_code_request(phone)
            try:
                await self.telethon_tg_client.sign_in(phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await self.telethon_tg_client.sign_in(password=input('Password: '))

        await self.telethon_tg_client.send_message(entity=self.api_keys['telegram']['notification_channel_id'],
                                                   message='hello telegram')

    async def telethon_run_in_background(self):
        pass


    async def pyrogram_send_msg(self):
        async with self.pyrogram_tg_client as tg:
            await tg.send_message('jonathon_test', 'hello')


