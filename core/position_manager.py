from datetime import datetime

import ccxt
from pprint import pprint

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
        "borrow_timestamp": None,
        "borrow_qty": None,
        "repay_timestamp": None,
        "repay_qty": None
    }

    status = None

    trades_info = {
        "open": {
            "base_pair": {"timestamp": None, "fillPrice": None},
            "quote_pair": {"timestamp": None, "fillPrice": None},
        },
        "close": {
            "base_pair": {"timestamp": None, "fillPrice": None},
            "quote_pair": {"timestamp": None, "fillPrice": None},
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
            borrow_coin = ValueError("Invalid position direction. (Must be 'LONG' or 'SHORT')")

        return borrow_coin

    def __init__(self, order_type, base_pair=None, quote_pair=None, direction=None,
                 params={}, config_filepath=USER_CONFIG_PATH):

        super().__init__(params, config_filepath)
        self.status = 'INIT Position'

        self.order_type = order_type
        self.direction = direction

        if self.direction == 'LONG':
            self.status = (f"Opening LONG Position on {self.synth_pair}\n"
                           f"ie. Go short on {self.quote_pair}"
                           f" (Borrow then SELL {self.synth_pair_tuple[3]} for {self.synth_pair_tuple[4]})\n"
                           f"And also go long on {self.base_pair}"
                           f" (BUY {self.synth_pair_tuple[1]} with {self.synth_pair_tuple[2]})")

            self.open_long(self.order_type)
        elif self.direction == 'SHORT':
            self.status = (f"Opening SHORT Position on {self.synth_pair}\n"
                           f"ie. Go short on {self.base_pair}"
                           f" (Borrow then SELL {self.synth_pair_tuple[1]} for {self.synth_pair_tuple[2]})\n"
                           f"And also go long on {self.quote_pair}"
                           f" (BUY {self.synth_pair_tuple[3]} with {self.synth_pair_tuple[4]})")

            self.open_short(self.order_type)

        self.status = 'OPEN'
        self.open_timestamp = datetime.utcnow()

    def open_long(self, order_type='market'):
        # Step 1: * Query exchange to fetch max borrow quantity of borrow_coin.
        #         * Borrow_coin will be base coin of the quote pair
        #           e.g. in ETHUSDT/BTCUSDT it is BTC
        #         * ccxt.exchange.fetch_borrow_rate isn't implemented for
        #           KuCoin so there needs to be at least two approaches for margin
        #           trading ie. with or without knowing that.

        self.borrow_coin = self.get_borrow_coin(self.synth_pair_tuple, 'LONG')
        self.borrow_info['currency'] = self.borrow_coin
        self.status = f"Borrow coin for {self.synth_pair} is: {self.borrow_coin}"

        self.status = f"Checking which methods {self.exchange_name} has for margin...\n"
        if self.exchange.has['fetchBorrowRate']:
            self.status = f"{self.exchange_name} has fetchBorrowRate"
            # available_margin = self.exchange.fetch_borrow_rate(self.borrow_coin)
        else:
            self.status = (f"{self.exchange_name} doesn't have fetchBorrowRate.\n"
                           f"Checking if {self.exchange_name} has fetchMaxBorrowSize..\n"
                           f"Note: This is a non-standard method. If possible, find a way "
                           f"to use fetchBorrowRate instead, or some other method. "
                           f"The only exchange which has the method `fetchMaxBorrowSize`"
                           " is kucoin_extended, but if others are added, this will find it.")

            if self.exchange.has['fetchMaxBorrowSize']:
                self.status = f"{self.exchange_name} has fetchMaxBorrowSize."

                max_borrow_size = float(self.exchange.fetch_max_borrow_size(self.borrow_coin))
                self.status = f"\nMax borrow amount: {max_borrow_size}  {self.borrow_coin}"
                print(self.status)
            else:
                raise Exception(f"{self.exchange_name} doesn't have fetchMaxBorrowSize or fetchBorrowRate. Can't proceed.")

        # ----------------------------------------
        # Step 2: If prompt_borrow is true, print the max borrow amount retrieved
        #         in step 1, then prompt the user to either accept the max amount
        #         or instead enter an amount.

        if self.prompt_borrow_qty:

            while self.borrow_info['borrow_qty'] is None:
                borrow_qty_input = input(  # Will change this to max amount, but it's at 1% for testing
                    f"\nTo borrow 1% of the max amount ({round(max_borrow_size/100, 4)} {self.borrow_coin}), press enter.\n"
                    "Otherwise, type an amount:")
                if borrow_qty_input == "":
                    self.borrow_info['borrow_qty'] = round(max_borrow_size/100, 4)
                    self.status = f"Borrowing 1% of max amount: {self.borrow_info['borrow_qty']} {self.borrow_coin}"
                else:
                    try:
                        self.borrow_info['borrow_qty'] = float(borrow_qty_input)

                        self.status = f"Borrowing {borrow_qty_input} {self.borrow_coin}\n"
                    except:
                        self.status = 'Invalid Number entered. Trying again..'

        else:
            self.status = f"Borrowing max amount: {max_borrow_size} {self.borrow_coin}"
            self.borrow_info['borrow_qty'] = max_borrow_size

        print(self.status)
        # ----------------------------------------
        # Step 3: Borrow from the exchange in the desired quantity
        if 'borrow' in self.exchange.has and self.exchange.has['borrow']:  # If the key is present and is True
            self.borrow_order = self.exchange.borrow(self.borrow_coin, self.borrow_info['borrow_qty'])

            self.status = f"Borrowed {self.borrow_info['borrow_qty']} {self.borrow_coin}"
            print(self.status)

        else:
            raise ValueError(f"{self.exchange_id} doesn't have a 'borrow' method")

        # ----------------------------------------
        # Step 4: Sell quote pair using the coins borrowed in step 3.
        #         eg. Sell BTC for USDT

        self.status = f"Fetching {self.borrow_coin} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.borrow_coin)
        self.status = f"{available_balance} {self.borrow_coin} available for margin trading."
        print(self.status)

        self.status = f"Selling {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[4]}"
        print(self.status)
        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.sell_order = self.exchange.place_margin_order('sell', self.quote_pair, available_balance, order_type)
        self.status = f"Sold {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[4]}"
        # print(self.status)
        # ----------------------------------------
        # Step 5: Buy the base coin of the base pair using the quote coin of the base pair.
        #         eg. Buy ETH with USDT

        self.status = f"Fetching {self.synth_pair_tuple[2]} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[2])
        self.status = f"{available_balance} {self.synth_pair_tuple[4]} available for margin trading."
        print(self.status)

        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.buy_order = self.exchange.place_margin_order('buy', self.base_pair, available_balance, order_type)
        self.status = (f"Opened {order_type} BUY order on {self.base_pair}.\n"
                       f"Quantity: {available_balance}")
        print(self.status)
        pass

    def open_short(self, order_type='market'):
        # ----------------------------------------
        # Step 1: TODO (Can copy/paste/modify from open_buy)
        #         Query exchange to fetch max borrow quantity of borrow_coin
        #         borrow_coin will be base coin of the base_pair
        #          e.g. in ETHUSDT/BTCUSDT it is ETH

        self.borrow_coin = self.get_borrow_coin(self.synth_pair_tuple, 'SHORT')
        self.borrow_info['currency'] = self.borrow_coin
        self.status = f"Borrow coin for {self.synth_pair} is: {self.borrow_coin}"

        self.status = f"Checking which methods {self.exchange_name} has for margin...\n"
        if self.exchange.has['fetchBorrowRate']:
            self.status = f"{self.exchange_name} has fetchBorrowRate"
            # available_margin = self.exchange.fetch_borrow_rate(self.borrow_coin)
        else:
            self.status = (f"{self.exchange_name} doesn't have fetchBorrowRate.\n"
                           f"Checking if {self.exchange_name} has fetchMaxBorrowSize..\n"
                           f"Note: This is a non-standard method. If possible, find a way "
                           f"to use fetchBorrowRate instead, or some other method. "
                           f"The only exchange which has the method `fetchMaxBorrowSize`"
                           " is kucoin_extended, but if others are added, this will find it.")

            if self.exchange.has['fetchMaxBorrowSize']:
                self.status = f"{self.exchange_name} has fetchMaxBorrowSize."

                max_borrow_size = round(float(self.exchange.fetch_max_borrow_size(self.borrow_coin)), 2)
                self.status = f"\nMax borrow amount: {max_borrow_size}  {self.borrow_coin}"
                print(self.status)
            else:
                raise Exception(
                    f"{self.exchange_name} doesn't have fetchMaxBorrowSize or fetchBorrowRate. Can't proceed.")
        # ----------------------------------------
        # Step 2: TODO (Can copy/paste/modify from open_buy)
        #         If prompt_borrow is true, print the max borrow amount retrieved
        #         in step 1, then prompt the user to either accept the max amount
        #         or instead enter an amount.
        if self.prompt_borrow_qty:

            while self.borrow_info['borrow_qty'] is None:
                borrow_qty_input = input(  # Will change this to max amount, but it's at 1% for testing
                    f"\nTo borrow 1% of the max amount ({round(max_borrow_size/100, 2)} {self.borrow_coin}), press enter.\n"
                    "Otherwise, type an amount:")
                if borrow_qty_input == "":
                    self.borrow_info['borrow_qty'] = round(max_borrow_size/100, 2)
                    self.status = f"Borrowing 1% of max amount: {self.borrow_info['borrow_qty']} {self.borrow_coin}"
                else:
                    try:
                        self.borrow_info['borrow_qty'] = float(borrow_qty_input)

                        self.status = f"Borrowing {borrow_qty_input} {self.borrow_coin}\n"
                    except:
                        self.status = 'Invalid Number entered. Trying again..'

        else:
            self.status = f"Borrowing max amount: {max_borrow_size} {self.borrow_coin}"
            self.borrow_info['borrow_qty'] = max_borrow_size

        print(self.status)
        # ----------------------------------------
        # Step 3: TODO (Can copy/paste/modify from open_buy)
        #         Borrow from the exchange in the desired quantity
        if 'borrow' in self.exchange.has and self.exchange.has['borrow']:  # If the key is present and is True
            self.borrow_order = self.exchange.borrow(self.borrow_coin, self.borrow_info['borrow_qty'])

            self.status = f"Borrowed {self.borrow_info['borrow_qty']} {self.borrow_coin}"
            print(self.status)

        else:
            raise ValueError(f"{self.exchange_id} doesn't have a 'borrow' method")
        # ----------------------------------------
        # Step 4: TODO (Can copy/paste/modify from open_buy)
        #         Sell base pair using the coins borrowed in step 3.
        #          eg. Sell ETH for USDT
        self.status = f"Fetching {self.borrow_coin} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.borrow_coin)
        self.status = f"{available_balance} {self.borrow_coin} available for margin trading."
        print(self.status)

        self.status = f"Selling {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[2]}"
        print(self.status)
        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.sell_order = self.exchange.place_margin_order('sell', self.quote_pair, available_balance, order_type)
        self.status = f"Sold {available_balance} {self.borrow_coin} for {self.synth_pair_tuple[2]}"
        # ----------------------------------------
        # Step 5: TODO (Can copy/paste/modify from open_buy)
        #         Buy the base coin of the quote pair using the quote coin of the quote pair.
        #          eg. Buy BTC with USDT
        self.status = f"Fetching {self.synth_pair_tuple[4]} available margin balance..."
        available_balance = self.exchange.fetch_available_margin_balance(self.synth_pair_tuple[4])
        self.status = f"{available_balance} {self.synth_pair_tuple[4]} available for margin trading."
        print(self.status)

        current_bid_price = self.exchange.fetch_ticker(self.quote_pair)
        self.buy_order = self.exchange.place_margin_order('buy', self.base_pair, available_balance, order_type)
        self.status = (f"Opened {order_type} BUY order on {self.base_pair}.\n"
                       f"Quantity: {available_balance}")
        print(self.status)
        pass

    def close(self, order_type='market'):
        print(f'Closing {self.direction} Position on {self.synth_pair}...\n'
              f'Order Type: {order_type}'
              f'TODO: Implement logic for def close() in position_manager.py')

        return self, 0


class PositionManager(Config):

    current_position = None
    history = None

    def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
        super().__init__(params, config_filepath)

    def set_current_position(self, position: Position):
        self.current_position = position

    def get_current_position(self):
        return self.current_position

    def save_closed_position(self):
        pass

    def open(self, direction=None, order_type='market'):

        if direction is None:
            raise ValueError('Direction not specified')
        else:
            DEBUG_direction = direction
            if not self.paper_trade:
                self.current_position = Position(order_type=order_type,
                                                 base_pair=self.base_pair,
                                                 quote_pair=self.quote_pair,
                                                 direction=direction)

                self.status = (f"[PAPER_TRADE]\n"
                               f"Opened {self.current_position.direction} position:\n"
                               f"{self.current_position.synth_pair}\n"
                               f"Trade 1: SHORT Quote Pair (SELL {self.current_position.synth_pair_tuple[3]} for {self.current_position.synth_pair_tuple[4]})\n"
                               f"    borrow coin: {self.current_position.borrow_info}\n"
                               f"     order type: {self.current_position.order_type}\n"
                               f"     fill price: {self.current_position.qp_open_fill_price}\n"
                               f"      timestamp: {self.current_position.qp_open_timestamp}\n"
                               f"Trade 2: LONG Base Pair (BUY {self.current_position.synth_pair_tuple[1]} with {self.current_position.synth_pair_tuple[2]})\n"
                               f"     order type: {self.current_position.order_type}\n"
                               f"     fill price: {self.current_position.qp_open_fill_price}\n"
                               f"      timestamp: {self.current_position.qp_open_timestamp}\n"
                               )
            return 0



# DEBUG


