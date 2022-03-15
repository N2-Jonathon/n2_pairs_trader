from ccxt.kucoin import kucoin


class KuCoinExtended(kucoin):
    def __init__(self):
        super().__init__()
        self.name = KuCoinExtended

