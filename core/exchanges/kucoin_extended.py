from ccxt.kucoin import kucoin


class KuCoinExtended(kucoin):
    """ The default ccxt.kucoin which this inherits, doesn't have an __init__ method?
    """
    def __init__(self, config={}):
        super().__init__()
        self.name = 'KuCoin Extended'

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