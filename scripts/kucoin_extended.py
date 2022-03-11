# Since the fetchBorrowRate isn't implemented for KuCoin by ccxt yet
# I have to do it myself for this project
""" ORIGINAL IMPORTS (DELETE LATER)
import base64
import hashlib
import hmac
import json
import datetime
import os

import ccxt
import requests
import configparser
import time

from ccxt.base.exchange import Exchange, long

from core import utils

from main import config
import ccxt
from ccxt.base.exchange import Exchange as ccxt_exchange
"""
import ccxt

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

from ccxt.base.decimal_to_precision import decimal_to_precision
from ccxt.base.decimal_to_precision import DECIMAL_PLACES, NO_PADDING, TRUNCATE, ROUND, ROUND_UP, ROUND_DOWN
from ccxt.base.decimal_to_precision import number_to_string
from requests.utils import default_user_agent
from requests import Session
import logging

import types



class KuCoinExtended(ccxt.kucoin):
    """
    This class inherits ccxt.kucoin, and any methods defined here will
    override the inherited methods.
    The purpose of that is to add features which are missing from
    ccxt.kucoin which I need - such as function for margin trading -
    yet still keep the convenience of having all the ccxt.kucoin
    methods that do work (Which is most of them)
    """

    def __init__(self, config={}):

        self.precision = dict() if self.precision is None else self.precision
        self.limits = dict() if self.limits is None else self.limits
        self.exceptions = dict() if self.exceptions is None else self.exceptions
        self.headers = dict() if self.headers is None else self.headers
        self.balance = dict() if self.balance is None else self.balance
        self.orderbooks = dict() if self.orderbooks is None else self.orderbooks
        self.tickers = dict() if self.tickers is None else self.tickers
        self.trades = dict() if self.trades is None else self.trades
        self.transactions = dict() if self.transactions is None else self.transactions
        self.positions = dict() if self.positions is None else self.positions
        self.ohlcvs = dict() if self.ohlcvs is None else self.ohlcvs
        self.currencies = dict() if self.currencies is None else self.currencies
        self.options = dict() if self.options is None else self.options  # Python does not allow to define properties in run-time with setattr
        self.decimal_to_precision = decimal_to_precision
        self.number_to_string = number_to_string

        # version = '.'.join(map(str, sys.version_info[:3]))
        # self.userAgent = {
        #     'User-Agent': 'ccxt/' + __version__ + ' (+https://github.com/ccxt/ccxt) Python/' + version
        # }

        self.origin = self.uuid()
        self.userAgent = default_user_agent()

        settings = self.deep_extend(self.describe(), config)

        for key in settings:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, self.deep_extend(getattr(self, key), settings[key]))
            else:
                setattr(self, key, settings[key])

        if self.api:
            self.define_rest_api(self.api, 'request')

        if self.markets:
            self.set_markets(self.markets)

        # convert all properties from underscore notation foo_bar to camelcase notation fooBar
        cls = type(self)
        for name in dir(self):
            if name[0] != '_' and name[-1] != '_' and '_' in name:
                parts = name.split('_')
                # fetch_ohlcv → fetchOHLCV (not fetchOhlcv!)
                exceptions = {'ohlcv': 'OHLCV', 'le': 'LE', 'be': 'BE'}
                camelcase = parts[0] + ''.join(exceptions.get(i, self.capitalize(i)) for i in parts[1:])
                attr = getattr(self, name)
                if isinstance(attr, types.MethodType):
                    setattr(cls, camelcase, getattr(cls, name))
                else:
                    setattr(self, camelcase, attr)

        self.tokenBucket = self.extend({
            'refillRate': 1.0 / self.rateLimit if self.rateLimit > 0 else float('inf'),
            'delay': 0.001,
            'capacity': 1.0,
            'defaultCost': 1.0,
        }, getattr(self, 'tokenBucket', {}))

        self.session = self.session if self.session or not self.synchronous else Session()
        self.logger = self.logger if self.logger else logging.getLogger(__name__)

    def describe(self):
        return self.deep_extend(super(KuCoinExtended, self).describe(), {
            'id': 'kucoin_extended',
            'name': 'KuCoin Extended',
            'countries': ['SC'],
            # note "only some endpoints are rate-limited"
            # so I set the 'ratelimit' on those which supposedly 'arent ratelimited'
            # to the limit of the cheapest endpoint
            # 60 requests in 3 seconds = 20 requests per second =>( 1000ms / 20 ) = 50 ms between requests on average
            'rateLimit': 50,
            'version': 'v0.0.0.1',
            'certified': False,
            'pro': True,
            'comment': 'Platform 2.0',
            'quoteJsonNumbers': False,
            'has': {
                'CORS': None,
                'spot': True,
                'margin': None,
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



# --------------------------------------------------------------------------

"""
def iso8601(timestamp=None):
    if timestamp is None:
        return timestamp
    if not isinstance(timestamp, (int, long)):
        return None
    if int(timestamp) < 0:
        return None

    try:
        utc = datetime.datetime.utcfromtimestamp(timestamp // 1000)
        return utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-6] + "{:03d}".format(int(timestamp) % 1000) + 'Z'
    except (TypeError, OverflowError, OSError):
        return None


def safe_currency(currency_id, currency=None):
    if currency_id is None and currency is not None:
        return currency
    if (ccxt_kucoin.currencies_by_id is not None) and (currency_id in ccxt_kucoin.currencies_by_id):
        return ccxt_kucoin.currencies_by_id[currency_id]
    return {
        'id': currency_id,
        'code': ccxt_kucoin.common_currency_code(currency_id.upper()) if currency_id is not None else currency_id
    }


def safe_currency_code(currency_id, currency=None):
    currency = safe_currency(currency_id, currency)
    return currency['code']


def safe_value(dictionary, key, default_value=None):
    return dictionary[key] if Exchange.key_exists(dictionary, key) else default_value


def safe_string(dictionary, key, default_value=None):
    return str(dictionary[key]) if Exchange.key_exists(dictionary, key) else default_value


def parse_number(value, default=None):
    if value is None:
        return default
    else:
        try:
            return str(value)
        except Exception:
            return default


def safe_number(dictionary, key, default=None):
    value = safe_string(dictionary, key)
    return parse_number(value, default)


def split_pair(pair, pair_type):
    if pair_type == 'coin_pair':
        print(f"{pair}\n"
              f"{pair[:4]}\n"
              f"{pair[:3]}\n")
        if utils.fetch_ticker(ccxt_kucoin, pair[:4]) is not None:
            base_coin = pair[:4]
            quote_index = 4
        elif utils.fetch_ticker(ccxt_kucoin, pair[:3]) is not None:
            base_coin = pair[:3]
            quote_index = 3
        else:

            raise ValueError("Invalid Base Coin")

        if utils.fetch_ticker(ccxt_kucoin, pair[quote_index:]) is not None:
            quote_coin = pair[quote_index:]
        else:
            raise ValueError("Invalid Quote Coin")
        return {
            "pair": pair,
            "base": base_coin,
            "quote": quote_coin
        }

    elif pair_type == 'pair_of_coin_pairs':
        if '/' in pair:
            return pair.split('/')
        else:
            raise ValueError('Invalid trading pair')


config = configparser.ConfigParser()
user_config_path = os.path.join(os.getcwd(), 'user-config.ini')
config.read(user_config_path)

api_url = 'https://api.kucoin.com'

api_key = config['KuCoin']['apiKey']
api_secret = config['KuCoin']['secret']
api_passphrase = config['KuCoin']['password']

ccxt_kucoin = ccxt.kucoin({
    "apiKey": api_key,
    "secret": api_secret,
    "password": api_passphrase
})


def query_margin_risk_limit():
    endpoint = '/api/v1/risk/limit/strategy?marginModel=cross'
    now = int(time.time() * 1000)

    str_to_sign = str(now) + 'GET' + endpoint
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"

    }
    response = requests.get(f"{api_url}{endpoint}", headers=headers)
    return response.content


def fetch_borrow_rates(params={}, exchange=ccxt_kucoin):
    response = json.loads(query_margin_risk_limit())
    now = int(time.time() * 1000)
    data = safe_value(response, 'data')
    timestamp = str(now)

    rates = {}
    for i in range(0, len(data)):
        rate = data[i]
        code = safe_currency_code(safe_string(rate, 'currency'))
        rates[code] = {
            'currency': code,
            'borrowMaxAmount': safe_number(rate, 'borrowMaxAmount'),
            'rate': safe_number(rate, 'interestRate'),
            'buyMaxAmount': safe_number(rate, 'buyMaxAmount'),
            'period': 86400000,
            'timestamp': timestamp,
            'datetime': iso8601(timestamp),
            'info': rate,
        }
    return rates


def fetch_borrow_rate(coin):
    rates = fetch_borrow_rates()
    _rate = rates[coin]
    return _rate


# [DEBUG]
# print(split_pair('ETHUSD', 'coin_pair'))

# data = safe_value(ccxt_kucoin.base_currencies, 'data')

# print(data)

# rate = fetch_borrow_rate('ETH')
# rate = query_margin_risk_limit()
"""