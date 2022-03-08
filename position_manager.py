import ccxt
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

exchange = ccxt.kucoin({
    "apiKey": config.KUCOIN_API_KEY,
    "secret": config.KUCOIN_SECRET_KEY,
    "password": config.KUCOIN_PASSWORD
})


def open_position(direction: str,
                  base_pair: str,
                  quote_pair: str,
                  borrow_coin: str,
                  borrow_qty: float,
                  prompt_confirmation: bool):
    pass


class Position:
    """
    If other position types are added,
    this class should be renamed to pairs_position
    """
    borrow_coin = {
        "name": None,
        "quantity": None,
        "borrow_timestamp": None,
        "repay_timestamp": None
    }

    def __init__(self, synth_pair, base_pair, quote_pair, direction, orders):
        self.order_type = None
        self.borrow_qty = None
        self.synth_pair = synth_pair
        self.base_pair = base_pair
        self.quote_pair = quote_pair
        self.direction = direction
        self.orders = orders

    pass

    def open(self, synth_pair, base_pair, quote_pair, borrow_coin, borrow_qty, direction,
             order_type='market', prompt_borrow_confirmation=False):

        self.synth_pair = synth_pair
        self.base_pair = base_pair
        self.quote_pair = quote_pair

        self.borrow_coin = borrow_coin
        self.borrow_qty = borrow_qty

        self.direction = direction
        self.order_type = order_type

        print(f'Opening {self.direction} Position on {self.synth_pair}...\n'
              f'Order Type: {order_type}')

        if self.direction.lower() == 'long':
            self.open_long(base_pair, quote_pair, borrow_coin, borrow_qty, prompt_borrow_confirmation)
        elif self.direction.lower == 'short':
            self.open_short(base_pair, quote_pair, borrow_coin, borrow_qty)
        else:
            raise ValueError('direction is invalid')

        return self, 0

    def open_long(self, base_pair: str, quote_pair: str, borrow_coin: str, prompt_borrow: bool):
        # ----------------------------------------
        # Step 1: Query exchange to fetch max
        # [TODO]  borrow quantity of borrow_coin
        #         borrow_coin will be base coin
        #         eg. BTC
        #         of the quote_pair
        #         eg. BTCUSDT
        # ----------------------------------------
        # Step 2: If prompt_borrow is true, print
        # [TODO]  the max borrow amount retrieved
        #         in step 1, then prompt the user
        #         to either accept the max amount
        #         or instead enter an amount.
        # ----------------------------------------
        # Step 3: Borrow from the exchange in the
        # [TODO]  desired quantity
        # ----------------------------------------
        # Step 4: Sell quote pair using the coins
        # [TODO]  borrowed in step 3.
        #         eg. Sell BTC for USDT
        # ----------------------------------------
        # Step 5: Buy the base coin of the base
        # [TODO]  pair using the quote coin of the
        #         base pair.
        #         eg. Buy ETH with USDT
        # ----------------------------------------
        # Step 6: Generate & Send Email with all
        # [TODO]  of the details about the open
        #         position included.
        pass

    def open_short(base_pair: str,
                   quote_pair: str,
                   borrow_coin: str,
                   borrow_qty: float,
                   prompt_confirmation: bool):
        # ----------------------------------------
        # Step 1: Query exchange to fetch max
        # [TODO]  borrow quantity of borrow_coin
        #         borrow_coin will be base coin
        #         eg. ETH
        #         of the base_pair
        #         eg. ETHUSDT
        # ----------------------------------------
        # Step 2: If prompt_borrow is true, print
        # [TODO]  the max borrow amount retrieved
        #         in step 1, then prompt the user
        #         to either accept the max amount
        #         or instead enter an amount.
        # ----------------------------------------
        # Step 3: Borrow from the exchange in the
        # [TODO]  desired quantity
        # ----------------------------------------
        # Step 4: Sell base pair using the coins
        # [TODO]  borrowed in step 3.
        #         eg. Sell ETH for USDT
        # ----------------------------------------
        # Step 5: Buy the base coin of the quote
        # [TODO]  pair using the quote coin of the
        #         quote pair.
        #         eg. Buy BTC with USDT
        # ----------------------------------------
        # Step 6: Generate & Send Email with all
        # [TODO]  of the details about the open
        #         position included.
        pass

    def close(self, order_type='market'):
        print(f'Closing {self.direction} Position on {self.synth_pair}...\n'
              f'Order Type: {order_type}'
              f'TODO: Implement logic for def close() in position_manager.py')

        return self, 0