from datetime import datetime
from eventhandler import EventHandler

import ccxt
import pandas as pd
from pprint import pprint


# Fore changes the text's foreground color


# from scripts.kucoin import fetch_borrow_rate

from core.constants import USER_CONFIG_PATH, EXCHANGES_WITH_margin, EXCHANGES_WITH_fetchBorrowRate
from core.config import Config




class Position(Config):
    """
    * This class represents the aggregate PnL & meta-data
      of two simultaneous trades. ie. one for the base
      pair and one for the quote pair.
    * It also keeps track of borrowing coins for the short side
      of the pairs trade which must come before the long side
    * It can be instantiated either by assigning Position()
      or Position().open() to a variable.

    EXAMPLE USAGE: (Outdated. TODO: update examples.)


    """

    borrow_coin = None

    borrow_info = {
        "currency": None,
        "borrow_timestamp_utc": None,
        "borrow_qty": None,
        "repay_timestamp_utc": None,
        "repay_qty": None
    }

    status = {}

    trades_info = {
        "open": {
            "base_pair": {"side": None, "timestamp": None, "fillPrice": None},
            "quote_pair": {"side": None, "timestamp": datetime, "fillPrice": None},
        },
        "close": {
            "base_pair": {"side": '', "timestamp": '', "fillPrice": ''},
            "quote_pair": {"side": '', "timestamp": '', "fillPrice": ''},
        },
    }

    @staticmethod
    def get_borrow_coin(synth_pair_tuple, position_direction):

        if position_direction == 'LONG':
            borrow_coin = synth_pair_tuple[3]
            pass
        elif position_direction == 'SHORT':
            borrow_coin = synth_pair_tuple[1]

        else:
            borrow_coin = ValueError("Invalid position signal. (Must be 'LONG' or 'SHORT')")

        return borrow_coin

    def __init__(self, order_type, direction=None, position_id=None,
                 params={}, config_filepath=USER_CONFIG_PATH):

        super().__init__(params, config_filepath)

        self.borrow_order = None
        if position_id is None:
            self.position_id = ccxt.Exchange.uuid()
        else:
            self.position_id = position_id

        self.status['msg'] = 'INIT Position'
        self.status['position_id'] = self.position_id
        self.status['trades_info'] = self.trades_info

        self.order_type = order_type
        self.status['order_type'] = self.order_type

        self.direction = direction
        self.status['signal'] = self.direction

        if self.direction == 'LONG':
            self.status['msg'] = (f"Opening LONG Position on {self.synth_pair}\n"
                           f"ie. Go short on {self.quote_pair}"
                           f" (Borrow then SELL {self.synth_pair_tuple[3]} for {self.synth_pair_tuple[4]})\n"
                           f"And also go long on {self.base_pair}"
                           f" (BUY {self.synth_pair_tuple[1]} with {self.synth_pair_tuple[2]})")

            self.open_long(self.order_type)
        elif self.direction == 'SHORT':
            self.status['msg'] = (f"Opening SHORT Position on {self.synth_pair}\n"
                           f"ie. Go short on {self.base_pair}"
                           f" (Borrow then SELL {self.synth_pair_tuple[1]} for {self.synth_pair_tuple[2]})\n"
                           f"And also go long on {self.quote_pair}"
                           f" (BUY {self.synth_pair_tuple[3]} with {self.synth_pair_tuple[4]})")

            self.open_short(self.order_type)

        self.status['msg'] = 'OPEN'
        self.open_timestamp = datetime.utcnow().timestamp()

    def open_long(self, order_type='market'):
        # Step 1: * Query exchange to fetch max borrow quantity of borrow_coin.
        #         * Borrow_coin will be base coin of the quote pair
        #           e.g. in ETHUSDT/BTCUSDT it is BTC
        #         * ccxt.exchange.fetch_borrow_rate isn't implemented for
        #           KuCoin so there needs to be at least two approaches for margin
        #           trading ie. with or without knowing that.

        self.trades_info['open']['base_pair']['side'] = 'buy'
        self.trades_info['open']['base_pair']['symbol'] = self.base_pair

        self.trades_info['open']['quote_pair']['side'] = 'sell'
        self.trades_info['open']['quote_pair']['symbol'] = self.quote_pair

        self.borrow_coin = self.get_borrow_coin(self.synth_pair_tuple, 'LONG')
        self.borrow_info['currency'] = self.borrow_coin

        self.status['msg'] = f"Borrow coin for {self.synth_pair} is: {self.borrow_coin}"
        self.status['borrow_coin'] = self.borrow_coin
        self.status['borrow_info'] = self.borrow_info
        self.status['ok'] = True

        self.borrow()

        # ----------------------------------------
        # Step 4: Sell quote pair using the coins borrowed in step 3.
        #         eg. Sell BTC for USDT

        self.status['msg'] = f"Fetching {self.borrow_coin} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.borrow_coin)
        self.status['msg'] = f"{available_balance} {self.borrow_coin} available for margin trading."
        print(self.status['msg'])

        self.status['msg'] = f"Selling {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[4]}\n"
        print(self.status['msg'])
        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.sell_order = self.exchange.place_margin_order('sell', self.quote_pair, available_balance, order_type)
        self.trades_info['open']['quote_pair']['timestamp'] = datetime.utcnow().timestamp()
        self.trades_info['open']['quote_pair']['quantity'] = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[3])

        self.status['msg'] = f"Sold {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[4]}"
        # print(self.status['msg'])
        # ----------------------------------------
        # Step 5: Buy the base coin of the base pair using the quote coin of the base pair.
        #         eg. Buy ETH with USDT

        self.status['msg'] = f"Fetching {self.synth_pair_tuple[2]} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[2])
        self.status['msg'] = f"{available_balance} {self.synth_pair_tuple[2]} available for margin trading."
        print(self.status['msg'])

        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.buy_order = self.exchange.place_margin_order('buy', self.base_pair, available_balance, order_type)
        self.trades_info['open']['base_pair']['timestamp'] = datetime.utcnow().timestamp()
        self.trades_info['open']['base_pair']['quantity'] = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[1])

        self.status['msg'] = (f"Opened {order_type} BUY order on {self.base_pair}.\n"
                              f"Bought {self.synth_pair_tuple[1]} with {available_balance} {self.synth_pair_tuple[2]}")
        print(self.status['msg'])

        self.status['msg'] = f"Opened LONG Position on {self.synth_pair}.\n"

        return self.status

    def open_short(self, order_type='market'):
        # ----------------------------------------
        # Step 1: Query exchange to fetch max borrow quantity of borrow_coin
        #         borrow_coin will be base coin of the base_pair
        #          e.g. in ETHUSDT/BTCUSDT it is ETH

        self.trades_info['open']['base_pair']['side'] = 'buy'
        self.trades_info['open']['base_pair']['symbol'] = self.base_pair

        self.trades_info['open']['quote_pair']['side'] = 'sell'
        self.trades_info['open']['quote_pair']['symbol'] = self.quote_pair

        self.borrow_coin = self.get_borrow_coin(self.synth_pair_tuple, 'SHORT')
        self.borrow_info['currency'] = self.borrow_coin
        self.status['msg'] = f"Borrow coin for {self.synth_pair} is: {self.borrow_coin}"

        self.borrow()

        # ----------------------------------------
        # Step 4: Sell base pair using the coins borrowed in step 3.
        #          eg. Sell ETH for USDT
        self.status['msg'] = f"Fetching {self.borrow_coin} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.borrow_coin)
        self.status['msg'] = f"{available_balance} {self.borrow_coin} available for margin trading."
        print("--------------------------------\n"
              f"{self.status['msg']}")

        self.status['msg'] = (f"Selling {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[2]}\n"
                       f"Opened {order_type} SELL order on {self.base_pair}.\n"
                       f"Quantity: {available_balance}")
        print(self.status['msg'])
        current_bid_price = self.exchange.fetch_ticker(self.base_pair)
        self.sell_order = self.exchange.place_margin_order('sell', self.base_pair, available_balance, order_type)
        self.trades_info['open']['quote_pair']['timestamp'] = datetime.utcnow().timestamp()
        self.trades_info['open']['quote_pair']['quantity'] = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[1])

        self.status['msg'] = f"Sold {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[2]}"
        # ----------------------------------------
        # Step 5: TODO (Can copy/paste/modify from open_buy)
        #         Buy the base coin of the quote pair using the quote coin of the quote pair.
        #          eg. Buy BTC with USDT
        self.status['msg'] = f"Fetching {self.synth_pair_tuple[4]} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[4])
        self.status['msg'] = f"{available_balance} {self.synth_pair_tuple[4]} available for margin trading."
        print("--------------------------------\n"
              f"{self.status['msg']}")

        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.buy_order = self.exchange.place_margin_order('buy', self.quote_pair, available_balance, order_type)
        self.status['msg'] = (f"Selling {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[2]}\n"
                       f"Opened {order_type} BUY order on {self.base_pair}.\n"
                       f"Quantity: {available_balance}")
        print(self.status['msg'])

        if self.debug_mode:
            print("\n--------------------------------\n"
                  f"\n[DEBUG] Available Balances: \n{self.exchange.fetch_available_margin_balances()}")

        pass

    def close(self, order_type='market'):
        self.status['msg'] = f"Closing {self.direction} Position on {self.synth_pair}"
        print(f"{self.status['msg']}\n")
        # 1. Repay borrowed funds
        # DEBUG_outstanding_loan = self.exchange.fetch_outstanding_loan(self.borrow_coin)
        # self.borrow_info['repay_qty'] = self.exchange.get_borrow_order(self.borrow_info['orderId'])
        self.status['msg'] = (f"Repaying borrowed {self.borrow_coin}")
        print(f"{self.status['msg']}\n")
        # self.exchange.repay_loan(self.borrow_info['orderId'])

        try:
            self.repay_record = self.exchange.get_repay_record()
        except:
            raise ValueError("Unable to get repay record from exchange")
        #self.exchange.repay_all_loans()

        # 2. Convert funds back to stake currency
        self.status['msg'] = f"Converting funds back to {self.stake_currency}"
        print(f"{self.status['msg']}\n")
        self.exchange.convert_all_funds_to_one_currency(self.stake_currency)
        self.status['msg'] = 'CLOSED'
        return self, 0

    def repay_all_outstanding_liabilities(self):
        try:
            self.repay_record = self.exchange.get_repay_record()
            # DEBUG_repay_record = self.repay_record
            # breakpoint()
        except:
            self.status['ok'] = False
            self.status['msg'] = ValueError("Unable to pay back  record from exchange")
            print(self.status)

        self.status['repaid'] = []

        for item in self.repay_record['data']['items']:
            trade_id = item['tradeId']
            currency = item['currency']
            liability = item['liability']

            # if self.debug_mode:
                # breakpoint()
                # self.exchange.convert_all_funds_to_one_currency(item['currency'])
            # self.status['repaid']['tradeId'] = self.exchange.repay_single_order(currency=item['currency'],
            #                                    trade_id=item['tradeId'],
            #                                    size=item['liability'])

    def borrow(self):
        if self.debug_mode:
            self.status['msg'] = "[DEBUG] Repaying all current liabilities before proceeding..."

            self.repay_all_outstanding_liabilities()

            # self.exchange.repay_all_loans()

        self.status['msg'] = f"Checking which methods {self.exchange_name} has for margin...\n"
        if self.exchange.has['fetchBorrowRate']:
            self.status['msg'] = f"{self.exchange_name} has fetchBorrowRate"
            # available_margin = self.exchange.fetch_borrow_rate(self.borrow_coin)
            self.status['ok'] = True
        else:
            self.status['msg'] = (f"{self.exchange_name} doesn't have fetchBorrowRate.\n"
                                  f"Checking if {self.exchange_name} has fetchMaxBorrowSize..\n"
                                  f"Note: This is a non-standard method. If possible, find a way "
                                  f"to use fetchBorrowRate instead, or some other method. "
                                  f"The only exchange which has the method `fetchMaxBorrowSize`"
                                  " is kucoin_extended, but if others are added, this will find it.")

            if self.exchange.has['fetchMaxBorrowSize']:
                self.status['msg'] = f"{self.exchange_name} has fetchMaxBorrowSize."

                max_borrow_size = float(self.exchange.fetch_max_borrow_size(self.borrow_coin))

                self.status['msg'] = f"\nMax borrow amount: {max_borrow_size}  {self.borrow_coin}"
                self.status['ok'] = True

                print("--------------------------------\n"
                      f"{self.status['msg']}")
            else:
                self.status['ok'] = False
                raise Exception(
                    f"{self.exchange_name} doesn't have fetchMaxBorrowSize or fetchBorrowRate. Can't proceed.")
        self.status['borrow_info'] = self.borrow_info
        # ----------------------------------------
        # Step 2: If prompt_borrow is true, print the max borrow amount retrieved
        #         in step 1, then prompt the user to either accept the max amount
        #         or instead enter an amount.

        if self.prompt_borrow_qty:

            while self.borrow_info['borrow_qty'] is None:
                borrow_qty_input = input(  # Will change this to max amount, but it's at 1% for testing
                    f"\nTo borrow 10% of the max amount ({round(max_borrow_size / 10, 4)} {self.borrow_coin}), press enter.\n"
                    "Otherwise, type an amount:\n")
                if borrow_qty_input == "":
                    self.borrow_info['borrow_qty'] = round(max_borrow_size / 10, 4)
                    self.status[
                        'msg'] = f"Borrowing 10% of max amount: {self.borrow_info['borrow_qty']} {self.borrow_coin}"
                else:
                    try:
                        self.borrow_info['borrow_qty'] = round(float(borrow_qty_input), 4)

                        self.status['msg'] = f"Borrowing {borrow_qty_input} {self.borrow_coin}\n"
                        self.status['ok'] = True
                    except:
                        self.status['ok'] = False
                        self.status['msg'] = 'Invalid Number entered. Trying again..'

        else:
            self.status['msg'] = f"Borrowing max amount: {max_borrow_size} {self.borrow_coin}\n"
            self.borrow_info['borrow_qty'] = max_borrow_size

        self.status['borrow_info'] = self.borrow_info
        self.status['ok'] = True

        print(self.status['msg'])
        # ----------------------------------------
        # Step 3: Borrow from the exchange in the desired quantity
        if 'borrow' in self.exchange.has and self.exchange.has['borrow']:  # If the key is present and is True
            self.borrow_order = self.exchange.borrow(self.borrow_coin, self.borrow_info['borrow_qty'])
            self.borrow_info['orderId'] = self.borrow_order['data']['orderId']
            self.borrow_info['borrow_timestamp_utc'] = datetime.utcnow().timestamp()
            self.borrow_info['order'] = self.borrow_order

            self.status['borrow_info'] = self.borrow_info
            self.status['msg'] = f"Borrowed {self.borrow_info['borrow_qty']} {self.borrow_coin}\n"
            self.status['ok'] = True
            print(self.status['msg'])

        else:
            self.status['ok'] = False
            raise ValueError(f"{self.exchange_id} doesn't have a 'borrow' method")

        self.status['borrow_info'] = self.borrow_info


class PositionManager(Config):

    current_position = None
    past_positions = []
    status = {}

    def __init__(self, strategy, params={}, config_filepath=USER_CONFIG_PATH):
        super().__init__(params, config_filepath)

        self.strategy = strategy

        self.event_handler = EventHandler('onOpenPosition', 'onClosePosition')

        self.event_handler.link(self.__on_open_position, 'onOpenPosition')
        self.event_handler.link(self.__on_close_position, 'onClosePosition')

        strategy.event_handler.link(self.open, 'newSignal')
        strategy.event_handler.link(self.close, 'newSignal')

    # This callback will be called when onOpenPosition event happens
    def __on_open_position(self, position):
        print("=======[DEBUG]==========\n"
              "PositionManager.__on_open_position fired!\n")
        print(f"Position Opened:\n"
              f"{position}\n"
              "========================\n")

    # This callback will be called when onClosePosition event happens
    def __on_close_position(self, position):
        print("=======[DEBUG]==========\n"
              "PositionManager.__on_close_position fired!\n")
        print(f"Position Closed:\n"
              f"{position}\n"
              "========================\n")

    def save_closed_position(self):
        pass

    def open(self, signal=None, order_type='market'):
        self.status['msg'] = ("PositionManager.open() called")
        #self.event_handler.fire('onOpenPosition', signal)  # self.current_position)

        if signal is None:
            raise ValueError("Can't open a position without a signal")

        if self.debug_mode:
            print("=======[DEBUG]==========\n"
                  f"{self.status['msg']}")

        if signal != 'CLOSE':
            if not self.paper_trade:
                self.status['pre-open_balances'] = self.exchange.fetch_available_margin_balances()
                self.status['msg'] = f"Pre-open Available Balances: \n{self.status['pre-open_balances']}"

                self.current_position = Position(order_type=order_type,
                                                 direction=signal)

                self.status['post-open_balances'] = self.exchange.fetch_available_margin_balances()
                self.status['msg'] = f"Post-open Available Balances: \n{self.status['post-open_balances']}"
                self.status['current_position'] = self.current_position

            print(f"POSITION INFO: \n"
                  f"Borrow Info:\n"
                  f"{str(self.current_position.borrow_info)}\n\n"
                  f"Trades Info:\n"
                  f"{str(self.current_position.trades_info)}\n")
            if self.debug_mode:
                # list
            self.event_handler.fire('onOpenPosition', self.current_position)
            return self.status
        else:
            self.status['msg'] = "signal was CLOSE, so not opening"
            if self.debug_mode:
                print(f"{self.status['msg']}\n"
                      "========================\n")

    def close(self, position):
        self.status['msg'] = "PositionManager.close() called."
        if self.debug_mode:
            print("=======[DEBUG]==========\n"
                  f"{self.status['msg']}\n")

        self.status['pre-close_balances'] = self.exchange.fetch_available_margin_balances()
        self.status['msg'] = f"Pre-close Available Balances: \n{self.status['pre-close_balances']}"

        if type(position) == str and position != 'CLOSE':
            self.status['msg'] = "signal was not CLOSE, so not closing"
            if self.debug_mode:
                print(f"{self.status['msg']}\n"
                      "=======================\n")
            return
        elif type(position) == Position:
            position.close()
        elif position == 'CLOSE':
            position = self.current_position
            position.close()

        self.status['post-close_balances'] = self.exchange.fetch_available_margin_balances()
        self.status['msg'] = f"Pre-close Available Balances: \n{self.status['post-close_balances']}"

        self.event_handler.fire('onClosePosition', self.current_position)
        self.past_positions.append(self.current_position)
        self.current_position = None
        return self.status
