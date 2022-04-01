from ccxt.kucoin import kucoin
import random
import string

from ccxt.base.errors import BadSymbol

class kucoin_extended(kucoin):
    """
    This inherits ccxt.kucoin and overrides its methods to implement things which aren't
    implemented by ccxt for kucoin eg. margin trading.

    - fetchMaxBorrowSize is a non-standard CCXT method that I made up. None of the other
      exchanges seem to have it, so any strategies which need it won't work on other exchanges
      (i.e. the N2SuperTrend strategy as it was written in the requirements).

    - It would also be possible to make another version of the strategy which doesn't
      rely on fetchMaxBorrowSize, but to fulfil your requirements exactly as they
      were written, it needs to be implemented.
    """

    @staticmethod
    def generate_order_id(length=24):
        str = string.ascii_lowercase
        return ''.join(random.choice(str) for i in range(length))

    def describe(self):
        return self.deep_extend(super(kucoin_extended, self).describe(), {
            'id': 'kucoin_extended',
            'alias': True,
            'version': 'v0.0.1',
            'has': {
                # 'fetchBorrowRate': True,  # If/when this is implemented, I'll un-comment this line
                'fetchMaxBorrowSize': True,
                'borrow': True
            },
            'urls': {  # Delete this to use on a live account
                'api': {
                    'public': 'https://openapi-sandbox.kucoin.com',
                    'private': 'https://openapi-sandbox.kucoin.com',
                }
            }
        })

    def fetch_max_borrow_size(self, currency):
        """
        Fetches the maximum available borrow amount for a given currency.

        NOTE: From reading KuCoin's API, there's 2 ways to do this:
            1. The first way is by querying the `margin/account` endpoint with a GET
               request. (For more info, see https://docs.kucoin.com/#get-margin-account)
            2. The second way is by querying the `risk/limit/strategy` endpoint which
               requires a parameter `marginModel` which apparently only works when
               set to 'corss' (typo?) and not 'isolated'.
               (For more info, see https://docs.kucoin.com/#query-the-cross-isolated-margin-risk-limit)
            * How this works now is the first way.
            * `self.privateGetMarginAccount()` is an implicit method which CCXT parses and maps to a REST API request.
                 ie. `GET {url}/margin/account`
            *  For another endpoint eg. 'GET {url}/risk/limit/strategy' it would be `self.privateGetRiskLimitStrategy()`
        """

        # GET {url}/margin/account

        response = self.privateGetMarginAccount()
        # {
        #     "accounts": [
        #         {
        #             "availableBalance": "990.11",
        #             "currency": "USDT",
        #             "holdBalance": "7.22",
        #             "liability": "66.66",
        #             "maxBorrowSize": "88.88",
        #             "totalBalance": "997.33"
        #         },
        #         {...},
        #         {...}
        #     ],
        #     "debtRatio": "0.33"
        # }

        try:
            for account in response['data']['accounts']:
                if account['currency'] == currency:
                    max_borrow_size = account['maxBorrowSize']
                    return max_borrow_size
        except:
            return ValueError(f'{currency} margin account not found')

    def fetch_borrow_rate(self, currency):
        """
        KuCoin doesn't have an API method for fetchBorrowRate. If it's possible to infer that somehow,
        then it will be possible to implement this in a way that conforms to CCXT's standards.
        """
        raise NotImplementedError("This isn't natively supported by KuCoin's API.\n"
                                  "It might be possible to implement this somehow")

    def borrow(self, currency, size, order_type='FOK'):
        params = {
            "currency": currency,
            "type": order_type,
            "size": round(size, 2)
        }
        # POST /api/v1/margin/borrow
        response = self.privatePostMarginBorrow(params)

        return response

    def fetch_available_margin_balance(self, currency="*", non_zero=False):
        response = self.privateGetMarginAccount()
        # {
        #     "accounts": [
        #         {
        #             "availableBalance": "990.11",
        #             "currency": "USDT",
        #             "holdBalance": "7.22",
        #             "liability": "66.66",
        #             "maxBorrowSize": "88.88",
        #             "totalBalance": "997.33"
        #         },
        #         {...},
        #         {...}
        #     ],
        #     "debtRatio": "0.33"
        # }

        try:
            for account in response['data']['accounts']:
                if account['currency'] == currency:
                    available_balance = account['availableBalance']
                    return available_balance
        except:
            return ValueError(f'{currency} margin account not found')

        pass

    def fetch_available_margin_balances(self):
        response = self.privateGetMarginAccount()
        # {
        #     "accounts": [
        #         {
        #             "availableBalance": "990.11",
        #             "currency": "USDT",
        #             "holdBalance": "7.22",
        #             "liability": "66.66",
        #             "maxBorrowSize": "88.88",
        #             "totalBalance": "997.33"
        #         },
        #         {...},
        #         {...}
        #     ],
        #     "debtRatio": "0.33"
        # }

        available_balances = {}

        for account in response['data']['accounts']:
            if float(account['availableBalance']) > 0:
                available_balances[account['currency']] = account['availableBalance']

        return available_balances

    def fetch_transferable_balance(self, currency, account):
        accounts = ['MAIN', 'TRADE', 'MARGIN']
        if account.upper() not in accounts:
            return ValueError(f'There is no account called {account}')
        params = {
            "currency": currency,
            "type": account
        }
        response = self.privateGetAccountsTransferable(params)
        raise NotImplementedError("Need to parse the response for this method to work, "
                                  "but I realized I don't need this method yet")
        return response

    def transfer_between_accounts(self, currency, from_account, to_account, amount):
        order_id = self.generate_order_id()
        params = {

        }
        raise NotImplementedError("Don't need this yet.")

    def place_margin_order(self, side, symbol, size, type='market', price=None, params={}):
        self.load_markets()
        marketId = self.market_id(symbol)
        clientOrderId = self.safe_string_2(params, 'clientOid', 'clientOrderId', self.uuid())

        if float(size) > 2000:
            print("Size of margin order exceeds KuCoin's limit of 2000 per order,\n"
                  "so reducing it to 2000\n"
                  "TODO: break these types of orders into multiple orders")
            size = '2000'

        if type == 'limit':

            if price == 'current':
                # TODO: fetch best ask/bids
                # breakpoint()
                order_book = self.fetch_order_book(marketId)
                # list
                # raise NotImplementedError('Must fetch best ask/bids first and assign correct value to price param')
                type = 'market'  # Before this gets implemented, limit orders are changed into market order. This will change
                params = {
                    # "clientOid": order_id,
                    "side": side,
                    "symbol": marketId,
                    "type": type,
                    "size": size,
                    "price": price
                }

        if type == 'market':
            # breakpoint()
            params = {
                "clientOid": clientOrderId,
                "side": side,
                "symbol": marketId,
                "type": type,
                "size": size
            }




        response = self.privatePostMarginOrder(params)

        return response

    def fetch_outstanding_loans(self):
        response = self.privateGetMarginBorrowOutstanding()

        items = response['data']['items']
        return items

    def get_borrow_order(self, order_id):
        params = {
            "orderId": order_id
        }
        response = self.privateGetMarginBorrow(params)

        order = response
        return order

    def fetch_outstanding_loan(self, currency):
        params = {
            "currency": currency
        }
        response = self.privateGetMarginBorrowOutstanding(params)
        info = response['data']['items']

    def repay_single_order(self, currency, trade_id, size):
        params = {
            "currency": currency,
            "tradeId": trade_id,
            "size": size
        }
        response = self.privatePostMarginRepaySingle(params)

        # list
        return response

    def get_repay_record(self, currency=None):
        if currency is not None:
            params = {
                "currency": currency
            }
            response = self.privateGetMarginBorrowOutstanding(params)
        else:
            response = self.privateGetMarginBorrowOutstanding()
        return response
        pass


    def repay_all_loans(self, sequence='HIGHEST_RATE_FIRST'):
        self.load_markets()
        outstanding_loans = self.fetch_outstanding_loans()

        for loan in outstanding_loans:
            currency = loan['currency']
            liability = loan['liability']

            params = {
                "currency": currency,
                "sequence": sequence,
                "size": liability
            }
            response = self.privatePostMarginRepayAll(params)


        return self.fetch_outstanding_loans()



    def convert_all_funds_to_one_currency(self, _currency='USDT'):
        balances = self.fetch_available_margin_balances()
        currencies = list(balances.keys())

        for currency in currencies:
            if currency != _currency:

                size = balances[currency]

                try:
                    symbol = f"{currency}-{_currency}"
                    DEBUG_response = self.place_margin_order('sell', symbol, size)
                    # list
                except BadSymbol:
                    symbol = f"{_currency}-{currency}"

                    DEBUG_response = self.place_margin_order('buy', symbol, size, type='limit', price='current')

                    # list



        new_balances = self.fetch_available_margin_balances()
        # list
        return new_balances