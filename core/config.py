import ccxt
import importlib
from configparser import ConfigParser

from core.constants import USER_CONFIG_PATH
import core.utils as utils
from core.exchanges.kucoin_extended import KuCoinExtended


class Config:
    __dict__ = {
        "exchange": str,
        "strategy_name": str,
        "strategy": None,  # : StrategyBase, (Caused circular import when setting type to StrategyBase)
        "prompt_for_pairs": bool,
        "base_pair": str,
        "quote_pair": str,
        "stake_currency": str,
        "paper_trade": bool,

        "debug_mode": bool
    }

    cfg_parser = ConfigParser()

    # I will disable or enable debug_mode by changing this hard-coded line
    # so that it doesn't accidentally happen.
    debug_mode = True

    def __init__(self, params={}, filepath=USER_CONFIG_PATH):

        self.params = params

        if params is None or len(params) == 0:

            if filepath is not None:
                self.cfg_parser.read([filepath])
            elif filepath is None:
                raise ValueError

            try:
                self.exchange_id = self.cfg_parser['Global Settings']['exchange']
                self.strategy_name = self.cfg_parser['Global Settings']['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name}"

                self.prompt_for_pairs = bool(self.cfg_parser['Global Settings']['prompt_for_pairs'])
                self.base_pair = self.cfg_parser['Global Settings']['base_pair_default']
                self.quote_pair = self.cfg_parser['Global Settings']['quote_pair_default']
                self.stake_currency = self.cfg_parser['Global Settings']['stake_currency']
                self.paper_trade = bool(self.cfg_parser['Global Settings']['paper_trade'])

                # self.synth_pair = self.get_synth_pair_symbol(self.base_pair, self.quote_pair)
                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id]
            except:
                raise ValueError("Failed to read from config (Make sure all values are assigned)")
        elif self.params is not None:
            for param in self.params:
                if param not in self.__dict__:
                    raise ValueError(f"Invalid Parameter: '{param}'")

            try:
                self.exchange_id: str = self.params['exchange']
                self.strategy_name = self.params['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name['strategy']}"

                self.prompt_for_pairs: bool = params['prompt_for_pairs'],
                self.base_pair: str = params['base_pair'],
                self.quote_pair: str = params['quote_pair'],
                self.stake_currency: str = params['stake_currency']
                self.paper_trade: bool = params['paper_trade']

                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id]
            except:
                raise ValueError("Params incomplete")
        else:
            raise Exception("Cannot Initialize Config() without either params or config_filepath")

        self.synth_pair = utils.get_synth_pair_symbol(self.base_pair, self.quote_pair)
        self.enabled_exchanges = self.get_enabled_exchanges()
        self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id.lower()]

        """ This caused circular import
        if self.strategy_name is not None:
            self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
        """

    def new(self, exchange: str, strategy_name: str, prompt_for_pairs: bool, base_pair: str,
            quote_pair: str, stake_currency: str, paper_trade: bool):
        self.get_enabled_exchanges()
        self.strategy_name = strategy_name
        try:
            self.exchange_id = exchange
            self.strategy_import_path = f"strategies.{strategy_name}"

            self.prompt_for_pairs: bool = prompt_for_pairs,
            self.base_pair: str = base_pair
            self.quote_pair: str = quote_pair
            self.stake_currency: str = stake_currency
            self.paper_trade: bool = paper_trade
        except:
            raise ValueError("Invalid Config Params")

        self.strategy_name = importlib.import_module(f"strategies.{self.strategy_name}")
        self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id]

    def get_enabled_exchanges(self):
        self.cfg_parser.read(USER_CONFIG_PATH)

        enabled_exchanges = {}
        try:
            enabled_exchanges['kucoin'] = KuCoinExtended({
                "apiKey": self.cfg_parser['KuCoin']['apiKey'],
                "secret": self.cfg_parser['KuCoin']['secret'],
                "password": self.cfg_parser['KuCoin']['password']
            })
            print("KuCoin enabled")
        except:
            print("Failed to enable KuCoin. Check API credentials")

        try:
            enabled_exchanges['hitbtc'] = hitbtc = ccxt.hitbtc({
                "apiKey": self.cfg_parser['HitBTC']['apiKey'],
                "secret": self.cfg_parser['HitBTC']['apiKey']
            })
            print("HitBTC enabled")
        except:
            print("Failed to enable KuCoin. Check API credentials")

        self.enabled_exchanges = enabled_exchanges
        return enabled_exchanges
