from ccxt.kucoin import kucoin


class kucoin_extended(kucoin):
    """
    - KuCoin doesn't have an API method for fetchBorrowRate.
    If it's possible to infer that from fetchMaxBorrowSize (or any other way),
    then I will be able to implement this in a way that conforms to CCXT's standards.

    - fetchMaxBorrowSize is a non-standard CCXT method that I made up. None of the other
    exchanges seem to have it, so any strategies which need it won't work on other exchanges
    (i.e. the N2SuperTrend strategy as it was written in the requirements).
        * It would also be possible to make another version of the strategy which doesn't
        rely on fetchMaxBorrowSize, but I want to fulfil your requirements exactly as they
        were written, so I'm implementing it.
    """

    def describe(self):
        return self.deep_extend(super(kucoin_extended, self).describe(), {
            'id': 'kucoin_extended',
            'alias': True,
            'version': 'v0.0.1',
            'has': {
                # 'fetchBorrowRate': True,  # If/when this is implemented, I'll un-comment this line
                'fetchMaxBorrowSize': True
            },
            'urls': {  # Delete this to use on a live account
                'api': {
                    'public': 'https://openapi-sandbox.kucoin.com',
                    'private': 'https://openapi-sandbox.kucoin.com',
                }
            }
        })

    def fetch_max_borrow_size(self, currency):
        """Fetches the maximum available borrow amount for a given currency"""
        # self.load_markets()
        currency = 'USDT'
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
        """Not working yet"""
        raise NotImplementedError("This isn't natively supported by KuCoin's API.\n"
                                  "It might be possible to implement this somehow")
