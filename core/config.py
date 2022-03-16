import ccxt
import importlib
from configparser import ConfigParser

import core.exchanges.kucoin_extended
from core.constants import USER_CONFIG_PATH
import core.utils as utils
from core.exchanges.kucoin_extended import KuCoinExtended
from scripts.load_api_keys import load_api_keys

import core.exchanges


class Config:

    name = 'Config'                       # This will be different for any sub-classes

    cfg_filepath = USER_CONFIG_PATH       # Can be overridden
    cfg_parser = ConfigParser()           # python built-in for parsing config files

    exchange_name: str = None             # eg. 'KuCoin'
    exchange_id: str = None               # lowercase eg. 'kucoin'
    exchange: ccxt.Exchange = None        # an object that inherits ccxt.Exchange's methods.
    """The ccxt.Exchange object later assigned to Config.exchange should be initialized with API Keys"""

    debug_mode: bool = True               # For now this is hard-coded as true

    strategy_name: str = None             # Decides which strategy to use
    strategy_import_path: str = None      # Dynamically calculated as an f-string ie. f"strategies.{strategy_name}"

    prompt_for_pairs: bool = None         # If True, the user will be prompted for which pairs to trade
    prompt_borrow_qty: bool = None        # If True, the user will be prompted for quantity to borrow in short trades
    base_pair: str = None                 # Base pair used to make the artificial pair
    quote_pair: str = None                # Quote pair used to make the artificial pair
    synth_pair: str = None                # Synth pair aka. artificial pair derived from base & quote pairs
    stake_currency: str = None            # The currency which end balances are converted to after closing a position
    paper_trade: bool = None              # When True, real orders won't be placed but positions will still be tracked

    api_keys = {
        "exchanges": {
            "KuCoin": {
                "apiKey": None,
                "secret": None,
                "password": None
            },
            "HitBTC": {
                "apiKey": None,
                "password": None
            }
        },
        "telegram": None
    }
    """
    For now the dictionary for api_keys is given here but it would be better to have it 
    somewhere else, and use ccxt.Exchange.requiredCredentials to generate this structure. 
    For now it's just 2 exchanges but that would need to be done before adding all of the 
    exchanges otherwise the same  structure would be copy/pasted for all of the exchanges.
    """

    def __init__(self, params={}, filepath=USER_CONFIG_PATH):

        self.exchange_id = None
        self.exchange = None
        self.exchange_api_keys = None
        self.params = params

        if params is None or len(params) == 0:

            if filepath is not None:
                self.cfg_parser.read([filepath])
            elif filepath is None:
                raise ValueError

            try:
                self.exchange_id = self.cfg_parser['Global Settings']['exchange']
                self.exchange_module_path = f"core.{self.exchange_id}"
                self.strategy_name = self.cfg_parser['Global Settings']['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name}"

                self.prompt_for_pairs = bool(self.cfg_parser['Global Settings']['prompt_for_pairs'])
                self.base_pair = self.cfg_parser['Global Settings']['base_pair_default']
                self.quote_pair = self.cfg_parser['Global Settings']['quote_pair_default']
                self.stake_currency = self.cfg_parser['Global Settings']['stake_currency']
                self.paper_trade = bool(self.cfg_parser['Global Settings']['paper_trade'])
            except:
                raise ValueError("Failed to read from config (Make sure all values are assigned)")
        elif self.params is not None:
            for param in self.params:
                if param not in self.__dict__:
                    raise ValueError(f"Invalid Parameter: '{param}'")

            try:
                self.exchange_id: str = self.params['exchange']
                self.exchange_module_path = f"core.{self.exchange_id}"

                self.strategy_name = self.params['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name['strategy']}"

                self.prompt_for_pairs: bool = params['prompt_for_pairs'],
                self.base_pair: str = params['base_pair'],
                self.quote_pair: str = params['quote_pair'],
                self.stake_currency: str = params['stake_currency']
                self.paper_trade: bool = params['paper_trade']

                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.cfg_file_key]
            except:
                raise ValueError("Params incomplete")
        else:
            raise Exception("Cannot Initialize Config() without either params or config_filepath")

        self.synth_pair = utils.get_synth_pair_symbol(self.base_pair, self.quote_pair)
        self.read_exchange_api_keys(self.exchange_id)

        # self.enabled_exchanges = self.get_enabled_exchanges()
        # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.cfg_file_key.lower()]

        """ This caused circular import
        if self.strategy_name is not None:
            self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
        """

    def new(self, exchange: str, strategy_name: str, prompt_for_pairs: bool, base_pair: str,
            quote_pair: str, stake_currency: str, paper_trade: bool):
        # self.get_enabled_exchanges()
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

    def read_cfg_key(self, cfg_file_key, filepath=USER_CONFIG_PATH):
        """
        Not currently used but will be useful for telegram.
        Also read_exchange_api_keys() can be refacroted to use this method.
        The filepath can be any file that built-in configparses.ConfigParser
        recognizes such as .ini or .cfg files
        """
        if filepath is not None:
            cfg = self.cfg_parser.read(self, filepath)
            if cfg_file_key in cfg:
                return cfg[cfg_file_key]
        else:
            raise ValueError(f"The key: {cfg_file_key} was not found in {filepath}")

    def read_exchange_api_keys(self, exchange_name, filepath=USER_CONFIG_PATH):
        """
        This takes a given exchange_name (not the same as exchange_id which is always lowercase),
        and a filepath
        """
        keys = {}
        if filepath is None:
            filepath = USER_CONFIG_PATH
        if filepath is not None:
            self.cfg_parser.read([filepath])
            cfg = self.cfg_parser
            if cfg.has_section(exchange_name):
                for credential in self.api_keys['exchanges'][exchange_name]:
                    key = cfg[exchange_name][credential]
                    keys[credential] = key

                self.api_keys['exchanges'][exchange_name] = keys

            else:
                raise ValueError(f'Failed to read {exchange_name} API keys from {filepath}')
        else:
            raise ValueError('No filepath was given for reading exchange api key')

        return keys

    def set_exchange(self):
        raise NotImplementedError
