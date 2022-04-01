# This is where emails will be sent and/or telegram notifications.

from core.position_manager import PositionManager

import asyncio
from pyrogram import Client
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from pprint import pprint


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
        pm.event_handler.link(self.send_position_report, 'onOpenPosition')
        pm.event_handler.link(self.send_position_report, 'onClosePosition')
        # self.schedule_tasks()

    def schedule_tasks(self: object) -> None:
        """ Minimal selection of tasks for this demonstation. """
        loop = self.loop
        # DEBUG_task = self.loop.create_task(self.run_pyrogram_client())
        self.loop.run_until_complete(self.run_pyrogram_client())
        # list

    def send_position_report(self, position):

        if position.status['msg'] == 'OPEN':

            report = (f"**__OPENED {position.direction} POSITION:__**\n\n"
                      f"Artificial Pair: **{self.pm.synth_pair}**\n"
                      f"Exchange: {self.pm.exchange_name}\n\n"
                      "**Borrow Order Info:**\n"
                      f"  Quantity: {position.borrow_info['borrow_qty']}\n"
                      f"  Timestamp: {position.borrow_info['borrow_timestamp_utc']}\n"
                      f"  Currency: {position.borrow_info['currency']}\n"
                      f"  orderId: {position.borrow_info['orderId']}\n\n"
                      "**Underlying trades to open position:**\n"
                      f"  **Base Pair: {position.trades_info['open']['base_pair']['symbol']}**\n"
                      f"    Side: {position.trades_info['open']['base_pair']['side']}\n"
                      f"    Timestamp: {position.trades_info['open']['base_pair']['timestamp']}\n"
                      f"  **Quote Pair: {position.trades_info['open']['quote_pair']['symbol']}**\n"
                      f"    Side: {position.trades_info['open']['quote_pair']['side']}\n"
                      f"    Timestamp: {position.trades_info['open']['quote_pair']['timestamp']}\n")
            print("Sending Telegram Notification...\n"
                  "Position Info:\n")
            pprint(report)
        elif position.status['msg'] == 'CLOSED':
            report = (f"**__CLOSED {position.direction} POSITION:__**\n\n"
                      f"Artificial Pair: **{self.pm.synth_pair}**\n"
                      f"Exchange: {self.pm.exchange_name}\n\n"
                      "**Borrow Order Info:**\n"
                      f"  Quantity: {position.borrow_info['borrow_qty']}\n"
                      f"  Timestamp: {position.borrow_info['borrow_timestamp_utc']}\n"
                      f"  Currency: {position.borrow_info['currency']}\n"
                      f"  orderId: {position.borrow_info['orderId']}\n\n"
                      "**Underlying trades to close position:**\n"
                      "TODO: track & display relevant information here")
        # list
        self.loop.run_until_complete(self.send_telegram_msg(str(report)))
        # list


    async def send_telegram_msg(self, msg: str):
        msg = str(msg)
        # list
        async with self.pyrogram_tg_client as tg:
            await tg.send_message('jonathon_test', msg)

