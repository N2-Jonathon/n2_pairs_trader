from ccxt.kucoin import kucoin

from ccxt.base.exchange import Exchange
import hashlib
import math
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import PermissionDenied
from ccxt.base.errors import AccountSuspended
from ccxt.base.errors import BadRequest
from ccxt.base.errors import BadSymbol
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidAddress
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import NotSupported
from ccxt.base.errors import RateLimitExceeded
from ccxt.base.errors import ExchangeNotAvailable
from ccxt.base.errors import InvalidNonce
from ccxt.base.precise import Precise


class KuCoinExtended(kucoin):
    """ The default ccxt.kucoin which this inherits, doesn't have/need an __init__ method?
    """
    def describe(self):
        return self.deep_extend(super(kucoin, self).describe(), {
            'id': 'kucoin',
            'name': 'KuCoinExtended',
            'countries': ['SC'],
            # note "only some endpoints are rate-limited"
            # so I set the 'ratelimit' on those which supposedly 'arent ratelimited'
            # to the limit of the cheapest endpoint
            # 60 requests in 3 seconds = 20 requests per second =>( 1000ms / 20 ) = 50 ms between requests on average
            'rateLimit': 50,
            'version': 'v0.01',
            'certified': False,
            'pro': True,
            'comment': 'This is an extended version of ccxt.kucoin made by Jonathon Quick',
            'quoteJsonNumbers': False,
            'has': {
                'CORS': None,
                'spot': True,
                'margin': True, # This is set to False in the non-extended version
                'swap': False,
                'future': False,
                'option': None,
                'cancelAllOrders': True,
                'cancelOrder': True,
                'createDepositAddress': True,
                'createOrder': True,
                'fetchAccounts': True,
                'fetchBalance': True,
                'fetchBorrowRate': False,
                'fetchBorrowRates': False,
                'fetchClosedOrders': True,
                'fetchCurrencies': True,
                'fetchDepositAddress': True,
                'fetchDeposits': True,
                'fetchFundingFee': True,
                'fetchFundingHistory': False,
                'fetchFundingRate': False,
                'fetchFundingRateHistory': False,
                'fetchFundingRates': False,
                'fetchIndexOHLCV': False,
                'fetchL3OrderBook': True,
                'fetchLedger': True,
                'fetchMarkets': True,
                'fetchMarkOHLCV': False,
                'fetchMyTrades': True,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchOrder': True,
                'fetchOrderBook': True,
                'fetchOrdersByStatus': True,
                'fetchPremiumIndexOHLCV': False,
                'fetchStatus': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchTime': True,
                'fetchTrades': True,
                'fetchTradingFee': True,
                'fetchTradingFees': False,
                'fetchWithdrawals': True,
                'transfer': True,
                'withdraw': True,
                # Below are non-standard methods I've added:
                'fetchMaxBorrowAmount': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/51840849/87295558-132aaf80-c50e-11ea-9801-a2fb0c57c799.jpg',
                'referral': 'https://www.kucoin.com/?rcode=E5wkqe',
                'api': {
                    'public': 'https://openapi-v2.kucoin.com',
                    'private': 'https://openapi-v2.kucoin.com',
                    'futuresPrivate': 'https://api-futures.kucoin.com',
                    'futuresPublic': 'https://api-futures.kucoin.com',
                },
                'test': {
                    'public': 'https://openapi-sandbox.kucoin.com',
                    'private': 'https://openapi-sandbox.kucoin.com',
                    'futuresPrivate': 'https://api-sandbox-futures.kucoin.com',
                    'futuresPublic': 'https://api-sandbox-futures.kucoin.com',
                },
                'www': 'https://www.kucoin.com',
                'doc': [
                    'https://docs.kucoin.com',
                ],
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'password': True,
            },
            'api': {
                'public': {
                    'get': {
                        'timestamp': 1,
                        'status': 1,
                        'symbols': 1,
                        'markets': 1,
                        'market/allTickers': 1,
                        'market/orderbook/level{level}_{limit}': 1,
                        'market/orderbook/level2_20': 1,
                        'market/orderbook/level2_100': 1,
                        'market/histories': 1,
                        'market/candles': 1,
                        'market/stats': 1,
                        'currencies': 1,
                        'currencies/{currency}': 1,
                        'prices': 1,
                        'mark-price/{symbol}/current': 1,
                        'margin/config': 1,
                    },
                    'post': {
                        'bullet-public': 1,
                    },
                },
                'private': {
                    'get': {
                        'market/orderbook/level{level}': 1,
                        'market/orderbook/level2': {'v3': 2},  # 30/3s = 10/s => cost = 20 / 10 = 2
                        'market/orderbook/level3': 1,
                        'accounts': 1,
                        'accounts/{accountId}': 1,
                        # 'accounts/{accountId}/ledgers': 1, Deprecated endpoint
                        'accounts/ledgers': 3.333,  # 18/3s = 6/s => cost = 20 / 6 = 3.333
                        'accounts/{accountId}/holds': 1,
                        'accounts/transferable': 1,
                        'base-fee': 1,
                        'sub/user': 1,
                        'sub-accounts': 1,
                        'sub-accounts/{subUserId}': 1,
                        'deposit-addresses': 1,
                        'deposits': 10,  # 6/3s = 2/s => cost = 20 / 2 = 10
                        'hist-deposits': 10,  # 6/3 = 2/s => cost = 20 / 2 = 10
                        'hist-orders': 1,
                        'hist-withdrawals': 10,  # 6/3 = 2/s => cost = 20 / 2 = 10
                        'withdrawals': 10,  # 6/3 = 2/s => cost = 20 / 2 = 10
                        'withdrawals/quotas': 1,
                        'orders': 2,  # 30/3s =  10/s => cost  = 20 / 10 = 2
                        'order/client-order/{clientOid}': 1,
                        'orders/{orderId}': 1,
                        'limit/orders': 1,
                        'fills': 6.66667,  # 9/3s = 3/s => cost  = 20 / 3 = 6.666667
                        'limit/fills': 1,
                        'margin/account': 1,
                        'margin/borrow': 1,
                        'margin/borrow/outstanding': 1,
                        'margin/borrow/borrow/repaid': 1,
                        'margin/lend/active': 1,
                        'margin/lend/done': 1,
                        'margin/lend/trade/unsettled': 1,
                        'margin/lend/trade/settled': 1,
                        'margin/lend/assets': 1,
                        'margin/market': 1,
                        'margin/trade/last': 1,
                        'stop-order/{orderId}': 1,
                        'stop-order': 1,
                        'stop-order/queryOrderByClientOid': 1,
                        'trade-fees': 1.3333,  # 45/3s = 15/s => cost = 20 / 15 = 1.333
                    },
                    'post': {
                        'accounts': 1,
                        'accounts/inner-transfer': {'v2': 1},
                        'accounts/sub-transfer': {'v2': 25},  # bad docs
                        'deposit-addresses': 1,
                        'withdrawals': 1,
                        'orders': 4,  # 45/3s = 15/s => cost = 20 / 15 = 1.333333
                        'orders/multi': 20,  # 3/3s = 1/s => cost = 20 / 1 = 20
                        'margin/borrow': 1,
                        'margin/order': 1,
                        'margin/repay/all': 1,
                        'margin/repay/single': 1,
                        'margin/lend': 1,
                        'margin/toggle-auto-lend': 1,
                        'bullet-private': 1,
                        'stop-order': 1,
                    },
                    'delete': {
                        'withdrawals/{withdrawalId}': 1,
                        'orders': 20,  # 3/3s = 1/s => cost = 20/1
                        'orders/client-order/{clientOid}': 1,
                        'orders/{orderId}': 1,  # rateLimit: 60/3s = 20/s => cost = 1
                        'margin/lend/{orderId}': 1,
                        'stop-order/cancelOrderByClientOid': 1,
                        'stop-order/{orderId}': 1,
                        'stop-order/cancel': 1,
                    },
                },
                'futuresPublic': {
                    # cheapest futures 'limited' endpoint is 40  requests per 3 seconds = 14.333 per second => cost = 20/14.333 = 1.3953
                    'get': {
                        'contracts/active': 1.3953,
                        'contracts/{symbol}': 1.3953,
                        'ticker': 1.3953,
                        'level2/snapshot': 2,  # 30 requests per 3 seconds = 10 requests per second => cost = 20/10 = 2
                        'level2/depth20': 1.3953,
                        'level2/depth100': 1.3953,
                        'level2/message/query': 1.3953,
                        'level3/message/query': 1.3953,  # deprecated，level3/snapshot is suggested
                        'level3/snapshot': 1.3953,  # v2
                        'trade/history': 1.3953,
                        'interest/query': 1.3953,
                        'index/query': 1.3953,
                        'mark-price/{symbol}/current': 1.3953,
                        'premium/query': 1.3953,
                        'funding-rate/{symbol}/current': 1.3953,
                        'timestamp': 1.3953,
                        'status': 1.3953,
                        'kline/query': 1.3953,
                    },
                    'post': {
                        'bullet-public': 1.3953,
                    },
                },
                'futuresPrivate': {
                    'get': {
                        'account-overview': 2,  # 30 requests per 3 seconds = 10 per second => cost = 20/10 = 2
                        'transaction-history': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                        'deposit-address': 1.3953,
                        'deposit-list': 1.3953,
                        'withdrawals/quotas': 1.3953,
                        'withdrawal-list': 1.3953,
                        'transfer-list': 1.3953,
                        'orders': 1.3953,
                        'stopOrders': 1.3953,
                        'recentDoneOrders': 1.3953,
                        'orders/{order-id}': 1.3953,  # ?clientOid={client-order-id}  # get order by orderId
                        'orders/byClientOid': 1.3953,  # ?clientOid=eresc138b21023a909e5ad59  # get order by clientOid
                        'fills': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                        'recentFills': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                        'openOrderStatistics': 1.3953,
                        'position': 1.3953,
                        'positions': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                        'funding-history': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                    },
                    'post': {
                        'withdrawals': 1.3953,
                        'transfer-out': 1.3953,  # v2
                        'orders': 1.3953,
                        'position/margin/auto-deposit-status': 1.3953,
                        'position/margin/deposit-margin': 1.3953,
                        'bullet-private': 1.3953,
                    },
                    'delete': {
                        'withdrawals/{withdrawalId}': 1.3953,
                        'cancel/transfer-out': 1.3953,
                        'orders/{order-id}': 1.3953,  # 40 requests per 3 seconds = 14.333 per second => cost = 20/14.333 = 1.395
                        'orders': 6.666,  # 9 requests per 3 seconds = 3 per second => cost = 20/3 = 6.666
                        'stopOrders': 1.3953,
                    },
                },
            },
            'timeframes': {
                '1m': '1min',
                '3m': '3min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '1hour',
                '2h': '2hour',
                '4h': '4hour',
                '6h': '6hour',
                '8h': '8hour',
                '12h': '12hour',
                '1d': '1day',
                '1w': '1week',
            },
            'exceptions': {
                'exact': {
                    'order not exist': OrderNotFound,
                    'order not exist.': OrderNotFound,  # duplicated error temporarily
                    'order_not_exist': OrderNotFound,  # {"code":"order_not_exist","msg":"order_not_exist"} ¯\_(ツ)_/¯
                    'order_not_exist_or_not_allow_to_cancel': InvalidOrder,  # {"code":"400100","msg":"order_not_exist_or_not_allow_to_cancel"}
                    'Order size below the minimum requirement.': InvalidOrder,  # {"code":"400100","msg":"Order size below the minimum requirement."}
                    'The withdrawal amount is below the minimum requirement.': ExchangeError,  # {"code":"400100","msg":"The withdrawal amount is below the minimum requirement."}
                    'Unsuccessful! Exceeded the max. funds out-transfer limit': InsufficientFunds,  # {"code":"200000","msg":"Unsuccessful! Exceeded the max. funds out-transfer limit"}
                    '400': BadRequest,
                    '401': AuthenticationError,
                    '403': NotSupported,
                    '404': NotSupported,
                    '405': NotSupported,
                    '429': RateLimitExceeded,
                    '500': ExchangeNotAvailable,  # Internal Server Error -- We had a problem with our server. Try again later.
                    '503': ExchangeNotAvailable,
                    '101030': PermissionDenied,  # {"code":"101030","msg":"You haven't yet enabled the margin trading"}
                    '200004': InsufficientFunds,
                    '230003': InsufficientFunds,  # {"code":"230003","msg":"Balance insufficient!"}
                    '260100': InsufficientFunds,  # {"code":"260100","msg":"account.noBalance"}
                    '300000': InvalidOrder,
                    '400000': BadSymbol,
                    '400001': AuthenticationError,
                    '400002': InvalidNonce,
                    '400003': AuthenticationError,
                    '400004': AuthenticationError,
                    '400005': AuthenticationError,
                    '400006': AuthenticationError,
                    '400007': AuthenticationError,
                    '400008': NotSupported,
                    '400100': BadRequest,
                    '400350': InvalidOrder,  # {"code":"400350","msg":"Upper limit for holding: 10,000USDT, you can still buy 10,000USDT worth of coin."}
                    '400500': InvalidOrder,  # {"code":"400500","msg":"Your located country/region is currently not supported for the trading of self token"}
                    '401000': BadRequest,  # {"code":"401000","msg":"The interface has been deprecated"}
                    '411100': AccountSuspended,
                    '415000': BadRequest,  # {"code":"415000","msg":"Unsupported Media Type"}
                    '500000': ExchangeNotAvailable,  # {"code":"500000","msg":"Internal Server Error"}
                    '260220': InvalidAddress,  # {"code": "260220", "msg": "deposit.address.not.exists"}
                },
                'broad': {
                    'Exceeded the access frequency': RateLimitExceeded,
                    'require more permission': PermissionDenied,
                },
            },
            'fees': {
                'trading': {
                    'tierBased': True,
                    'percentage': True,
                    'taker': self.parse_number('0.001'),
                    'maker': self.parse_number('0.001'),
                    'tiers': {
                        'taker': [
                            [self.parse_number('0'), self.parse_number('0.001')],
                            [self.parse_number('50'), self.parse_number('0.001')],
                            [self.parse_number('200'), self.parse_number('0.0009')],
                            [self.parse_number('500'), self.parse_number('0.0008')],
                            [self.parse_number('1000'), self.parse_number('0.0007')],
                            [self.parse_number('2000'), self.parse_number('0.0007')],
                            [self.parse_number('4000'), self.parse_number('0.0006')],
                            [self.parse_number('8000'), self.parse_number('0.0005')],
                            [self.parse_number('15000'), self.parse_number('0.00045')],
                            [self.parse_number('25000'), self.parse_number('0.0004')],
                            [self.parse_number('40000'), self.parse_number('0.00035')],
                            [self.parse_number('60000'), self.parse_number('0.0003')],
                            [self.parse_number('80000'), self.parse_number('0.00025')],
                        ],
                        'maker': [
                            [self.parse_number('0'), self.parse_number('0.001')],
                            [self.parse_number('50'), self.parse_number('0.0009')],
                            [self.parse_number('200'), self.parse_number('0.0007')],
                            [self.parse_number('500'), self.parse_number('0.0005')],
                            [self.parse_number('1000'), self.parse_number('0.0003')],
                            [self.parse_number('2000'), self.parse_number('0')],
                            [self.parse_number('4000'), self.parse_number('0')],
                            [self.parse_number('8000'), self.parse_number('0')],
                            [self.parse_number('15000'), self.parse_number('-0.00005')],
                            [self.parse_number('25000'), self.parse_number('-0.00005')],
                            [self.parse_number('40000'), self.parse_number('-0.00005')],
                            [self.parse_number('60000'), self.parse_number('-0.00005')],
                            [self.parse_number('80000'), self.parse_number('-0.00005')],
                        ],
                    },
                },
                'funding': {
                    'tierBased': False,
                    'percentage': False,
                    'withdraw': {},
                    'deposit': {},
                },
            },
            'commonCurrencies': {
                'HOT': 'HOTNOW',
                'EDGE': 'DADI',  # https://github.com/ccxt/ccxt/issues/5756
                'WAX': 'WAXP',
                'TRY': 'Trias',
                'VAI': 'VAIOT',
            },
            'options': {
                'version': 'v1',
                'symbolSeparator': '-',
                'fetchMyTradesMethod': 'private_get_fills',
                'fetchBalance': 'trade',
                'fetchMarkets': {
                    'fetchTickersFees': True,
                },
                # endpoint versions
                'versions': {
                    'public': {
                        'GET': {
                            'status': 'v1',
                            'market/orderbook/level2_20': 'v1',
                            'market/orderbook/level2_100': 'v1',
                            'market/orderbook/level{level}_{limit}': 'v1',
                        },
                    },
                    'private': {
                        'GET': {
                            'market/orderbook/level2': 'v3',
                            'market/orderbook/level3': 'v3',
                            'market/orderbook/level{level}': 'v3',
                        },
                        'POST': {
                            'accounts/inner-transfer': 'v2',
                            'accounts/sub-transfer': 'v2',
                        },
                    },
                    'futuresPrivate': {
                        'GET': {
                            'account-overview': 'v1',
                            'positions': 'v1',
                        },
                        'POST': {
                            'transfer-out': 'v2',
                        },
                    },
                    'futuresPublic': {
                        'GET': {
                            'level3/snapshot': 'v2',
                        },
                    },
                },
                'accountsByType': {
                    'trade': 'trade',
                    'trading': 'trade',
                    'spot': 'trade',
                    'margin': 'margin',
                    'main': 'main',
                    'funding': 'main',
                    'future': 'contract',
                    'futures': 'contract',
                    'contract': 'contract',
                    'pool': 'pool',
                    'pool-x': 'pool',
                },
                'networks': {
                    'ETH': 'eth',
                    'ERC20': 'eth',
                    'TRX': 'trx',
                    'TRC20': 'trx',
                    'KCC': 'kcc',
                    'TERRA': 'luna',
                },
            },
        })

    def __init__(self, config={}):
        super().__init__()
        self.name = 'KuCoin (Extended for N2 Pairs Trader)'

    def fetch_borrow_rate(self, currency):
        """Not working yet"""
        raise NotImplementedError("This isn't natively supported by Kucoin's API.\n"
                                "It might be possible to implement this somehow")
        rates = fetch_borrow_rates()
        _rate = rates[coin]
        return _rate

    def fetch_max_borrow_amount(self, currency):
        """Not working yet"""
        raise NotImplementedError()