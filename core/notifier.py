# This is where emails will be sent and/or telegram notifications.
import asyncio
from datetime import datetime
import time

from eventhandler import EventHandler

import configparser

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import asyncio
import threading


from core.config import Config
from core.constants import USER_CONFIG_PATH
from core.position_manager import PositionManager, Position

config = configparser.ConfigParser()
config.read("config.ini")



class Notifier(Config):

    def __init__(self, pm: PositionManager, type='telegram', params={}, config_filepath=USER_CONFIG_PATH):
        # thread = threading.Thread(target=self.connect_telegram, args=())
        # thread.daemon = True
        # thread.start()

        super().__init__(params, config_filepath)
        self.telegram_client = None
        self.interval = 5
        self.read_telegram_api_keys()
        # self.connect_telegram()

        # try:
        #     asyncio.get_event_loop().run_until_complete(self.authenticate_telegram(self.api_keys['telegram']['phone']))
        # except RuntimeError as ex:
        #     if "There is no current event loop in thread" in str(ex):
        #         loop = asyncio.new_event_loop()
        #         asyncio.set_event_loop(loop)
        #         asyncio.get_event_loop().run_until_complete(
        #             self.authenticate_telegram(self.api_keys['telegram']['phone']))

        self.telegram_client = TelegramClient(self.api_keys['telegram']['username'],
                                             self.api_keys['telegram']['app_api_id'],
                                             self.api_keys['telegram']['api_hash'])

        # self.authenticate_telegram(self.api_keys['telegram']['phone'])
        # self.connect_telegram()
        # self.telegram_client.send_message(entity=self.api_keys['telegram']['notification_channel_id'],
        #                                   message='hello telegram')

        self.event_handler = EventHandler
        pm.event_handler.link(self.send_telegram_notification, 'onOpenPosition')
        pm.event_handler.link(self.send_telegram_notification, 'onClosePosition')

    def run(self):
        pass

    def send_telegram_notification(self, position):
        print("Sending Telegram Notification...\n"
              "Position Info:\n")
        print(position)

    async def authenticate_telegram(self, phone):

        async def authenticate():
            if not await self.telegram_client.is_user_authorized():
                await self.telegram_client.send_code_request(phone)
                try:
                    await self.telegram_client.sign_in(phone, input('Enter the code: '))
                except SessionPasswordNeededError:
                    await self.telegram_client.sign_in(password=input('Password: '))

            await self.telegram_client.send_message(entity=self.api_keys['telegram']['notification_channel_id'],
                                              message='hello telegram')

    async def connect_telegram(self):

                #return asyncio.get_event_loop()
        self.telegram_client = TelegramClient(self.api_keys['telegram']['username'],
                                              self.api_keys['telegram']['app_api_id'],
                                              self.api_keys['telegram']['api_hash'])

        # self.authenticate_telegram(self.api_keys['telegram']['phone'])

        while True:
            # More statements comes here
            print(datetime.now().__str__() + ' : Start task in the background')
            await self.telegram_client.send_message(entity=self.api_keys['telegram']['notification_channel_id'],
                                                    message='hello telegram')
            await asyncio.sleep(self.interval)

        # task = asyncio.create_task(self.telegram_client)
        # asyncio.get_running_loop().run_until_complete(task)
        # return task.result()


class TelegramNotifier:
    #client = TelegramClient('spliffli', api_id, api_hash)

    pass

class EmailNotifier:
    pass