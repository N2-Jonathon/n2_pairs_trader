from ccxt.kucoin import kucoin
from ccxt import Exchange

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


class kucoin_extended(kucoin):
    """ The default ccxt.kucoin which this inherits, doesn't have/need an __init__ method?
    """

    def describe(self):
        return self.deep_extend(super(kucoin_extended, self).describe(), {
            'id': 'kucoin_extended',
            'alias': True,
            'has': {
                'fetchBorrowRate': True,
                'fetchMaxBorrowAmount': True
            }
        })

    """
    def __init__(self, config={}):
        super().__init__()
    """
        

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