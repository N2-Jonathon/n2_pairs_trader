from ccxt.kucoin import kucoin


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
            "size": size
        }
        # POST /api/v1/margin/borrow
        response = self.privatePostMarginBorrow(params)

        return response