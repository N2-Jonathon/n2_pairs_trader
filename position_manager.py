import ccxt
import configparser
import utils

config = configparser.ConfigParser()
config.read("config.ini")


class Position:
    """
    * This class represents the aggregate PnL & meta-data
      of two simultaneous trades. ie. one for the base
      pair and one for the quote pair.
    * It also keeps track of borrowing coins for the short side
      of the pairs trade which must come before the long side
    * It can be instantiated either by assigning Position()
      or Position().open() to a variable.
    """
    borrow_coin = {
        "name": None,
        "quantity": None,
        "borrow_timestamp": None,
        "repay_timestamp": None
    }

    def __init__(self, base_pair, quote_pair, direction,
                 borrow_coin,
                 order_type='market', prompt_borrow_qty=False, exchange=config['Bot Settings']['exchange']):
        self.status = 'init'
        self.exchange_name = exchange
        self.base_pair = base_pair
        self.quote_pair = quote_pair
        self.synth_pair = utils.get_synth_pair_symbol(self.base_pair, self.quote_pair)

        self.direction = direction

        self.borrow_coin = borrow_coin
        self.order_type = order_type
        self.prompt_borrow_qty = prompt_borrow_qty

        if self.exchange_name.lower() == 'kucoin':
            self.exchange = ccxt.kucoin({"apiKey": config['KuCoin']['apiKey'],
                                         "secret": config['KuCoin']['secret'],
                                         "password": config['KuCoin']['password']
                                         })
        else:
            raise NotImplementedError("Unsupported Exchange:\n"
                                      "Currently the only tested exchange is KuCoin.")

    def open_order(self, pair, direction, quantity, order_type='market'):
        order = self.exchange.create_order(pair, order_type, direction, quantity)
        return order

    # ----------------------------------------------------------------
    # * Position.open_position() is for opening a position with two trades
    #   It has the same params as the constructor __init__
    #   TODO:
    #   - [ ] Returns a DataFrame containing information about the open
    #     trades.
    #   - [ ] For calculating things like PnL, the DataFrame should then
    #     be passed to `Position.refresh_live_data()`
    # ----------------------------------------------------------------
    # * When you supply an already initialized yet unopened
    #   Position() instance to open, it will inherit its attributes.
    # ----------------------------------------------------------------
    def open_position(self, direction, order_type='market', prompt_borrow_qty=False):

        self.status = 'opening'

        self.direction = direction
        self.order_type = order_type
        self.prompt_borrow_qty = prompt_borrow_qty

        print(f'Opening {self.direction} Position on {self.synth_pair}...\n'
              f'Order Type: {order_type}')

        if self.direction == 'LONG':
            """
                self.open_long(base_pair, quote_pair, borrow_coin, borrow_qty, prompt_borrow_confirmation, borrow_qty)
            """
            print("DEBUG: Open Long Position here:")
            self.open_long(order_type, prompt_borrow_qty)
        elif self.direction == 'SHORT':
            # self.open_short(base_pair, quote_pair, borrow_coin)
            print("DEBUG: Open Short Position here:")
        elif self.direction != 'LONG' and self.direction != 'SHORT':
            raise ValueError('direction is invalid')

        return self, 0

    def open_long(self, order_type='market', prompt_borrow_qty=False):
        # ----------------------------------------
        # Step 1: Query exchange to fetch max
        # [TODO]  borrow quantity of borrow_coin
        #         borrow_coin will be base coin
        #         eg. BTC
        #         of the quote_pair
        #         eg. BTCUSDT
        #         ccxt.exchange.fetch_fetch_borrow_rate isn't
        #         implemented for KuCoin I had to modify the
        #         ccxt lib. The modified ccxt only exists in
        #         my venv, so I will change it so the function
        #         is in the local dir. The other steps will be
        #         easy after that.

        available_margin = self.exchange.fetch_borrow_rate(self.borrow_coin)
        print(available_margin)

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


# DEBUG

my_position = Position(base_pair='ETHUSDT',
                       quote_pair='BTCUSDT',
                       direction='LONG',
                       borrow_coin='BTC',
                       order_type='market',
                       prompt_borrow_qty=False)

my_position = my_position.open_position(direction='LONG',
                                        order_type='market',
                                        prompt_borrow_qty=False)

print(my_position)
