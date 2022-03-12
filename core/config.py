import os
import ccxt
import sys
import importlib
from configparser import ConfigParser

sys.path.append(os.getcwd())
from core.exchanges.exchanges import exchanges
from strategies import strategy_base


class Config:
    __dict__ = {
        "exchange": str,
        "strategy": str,
        "prompt_for_pairs": bool,
        "base_pair": str,
        "quote_pair": str,
        "stake_currency": str
    }

    def __int__(self, config: ConfigParser.read = ConfigParser.read("user/user-config.ini")):
        """
        - This is the default way to initialize `Config()`
        - It works with either no params, which defaults to the user config,
        - Or it can be overridden with a python built-in parsed config file
          as a param which you can get by calling:
                `ConfigParser.read("<filepath>.ini")`

        :param config:
        :type ConfigParser.read:
        :return:
        :rtype:
        """
        try:
            self.exchange_id = config['Global Settings']['exchange']
            self.exchange = exchanges[config['Global Settings']['exchange']]
            self.strategy = config['Global Settings']['strategy']
            self.prompt_for_pairs = config['Global Settings']['prompt_for_pairs']
            self.base_pair = config['Global Settings']['base_pair_default']
            self.quote_pair = config['Global Settings']['quote_pair_default']
            self.stake_currency = config['Global Settings']['stake_currency']
        except:
            raise ValueError("Failed to read from user-config.ini (Make sure all values are assigned)")
        return self

    def __init__(self, exchange: ccxt.Exchange, strategy: strategy_base, prompt_for_pairs: bool,
                 base_pair: str, quote_pair: str, stake_currency: str):
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

        try:
            self.exchange_id: str = exchange
            self.exchange: ccxt.Exchange = exchanges[exchange]
            self.strategy = importlib.import_module(f"strategies.{strategy}")
            self.prompt_for_pairs: bool = prompt_for_pairs,
            self.base_pair: str = base_pair,
            self.quote_pair: str = quote_pair,
            self.stake_currency: str = stake_currency
        except:
            raise ValueError("Invalid params")

    def __init__(self, params={}):
        """
        Not sure if this is really necessary, but this third way of
        initializing Config() it allows taking the params as a dict,
        then assigns them to the class properties.

        :param params:
        :type params:
        """
        for param in params:
            if param not in self.__dict__:
                raise ValueError(f"Invalid Parameter: '{param}'")
        try:
            self.exchange_id: str = params['exchange']
            self.exchange: ccxt.Exchange = exchanges[self.exchange_id]
            self.strategy = importlib.import_module(f"strategies.{params['strategy']}")
            self.prompt_for_pairs: bool = params['prompt_for_pairs'],
            self.base_pair: str = params['base_pair'],
            self.quote_pair: str = params['quote_pair'],
            self.stake_currency: str = params['stake_currency']
        except:
            raise ValueError("Params incomplete")
