import os
import ccxt
import sys
import importlib
sys.path.append(os.getcwd())
from configparser import ConfigParser

print(f"{os.getcwd()}/user/user-config.ini")
user_config_filepath = f"{os.getcwd()}/user/user-config.ini"
user_config = ConfigParser()
user_config.read("/user/user-config.ini")
import strategies
from core.exchanges.kucoin_extended import KuCoinExtended


class Config:
    __dict__ = {
        "exchange": str,
        "strategy": str,
        "prompt_for_pairs": bool,
        "base_pair": str,
        "quote_pair": str,
        "stake_currency": str,
        "paper_trade": bool
    }

    user_config = ConfigParser()
    user_config_filepath = f"{os.getcwd()}/user/user-config.ini"

    def __init__(self, params={}, config_filepath=None):
        """
        This is another way to initialize Config() by specifying each
        of the values as params instead of reading from a file

        :param exchange:
        :type ccxt.Exchange:
        :param strategy:
        :type base_strategy:
        :param prompt_for_pairs:
        :type bool:
        :param base_pair:
        :type str:
        :param quote_pair:
        :type str:
        :param stake_currency:
        :type str:
        """

        self.params = params

        if params is None or len(params) == 0:
            if config_filepath is None:
                self.config_filepath = f"{os.getcwd()}/user/user-config.ini"
                print(f"[DEBUG] self.config_filepath = {self.config_filepath}")

            self.user_config.read(self.user_config_filepath)

            try:
                self.exchange_id = self.user_config['Global Settings']['exchange']
                self.strategy_name = self.user_config['Global Settings']['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name}"

                self.prompt_for_pairs = bool(self.user_config['Global Settings']['prompt_for_pairs'])
                self.base_pair = self.user_config['Global Settings']['base_pair_default']
                self.quote_pair = self.user_config['Global Settings']['quote_pair_default']
                self.stake_currency = self.user_config['Global Settings']['stake_currency']
                self.paper_trade = bool(self.user_config['Global Settings']['paper_trade'])

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
            raise ValueError("Cannot Initialize Config() without either params or config_filepath")
        self.enabled_exchanges = self.get_enabled_exchanges()
        self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id.lower()]
        if self.strategy_name is not None:
            self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")


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
        self.user_config.read(user_config_filepath)

        enabled_exchanges = {}
        try:
            enabled_exchanges['kucoin'] = KuCoinExtended({
                                            "apiKey": self.user_config['KuCoin']['apiKey'],
                                            "secret": self.user_config['KuCoin']['secret'],
                                            "password": self.user_config['KuCoin']['password']
                                        })
            print("KuCoin enabled")
        except:
            print("Failed to enable KuCoin. Check API credentials")

        try:
            enabled_exchanges['hitbtc'] = hitbtc = ccxt.hitbtc({
                                            "apiKey": self.user_config['HitBTC']['apiKey'],
                                            "secret": self.user_config['HitBTC']['apiKey']
                                        })
            print("HitBTC enabled")
        except:
            print("Failed to enable KuCoin. Check API credentials")

        self.enabled_exchanges = enabled_exchanges
        return enabled_exchanges
