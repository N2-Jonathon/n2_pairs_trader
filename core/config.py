import ccxt
import importlib
from configparser import ConfigParser

import core.exchanges.kucoin_extended
from core.constants import USER_CONFIG_PATH, EXCHANGES, EXTENDED_EXCHANGES
import core.utils as utils
from core.exchanges.kucoin_extended import kucoin_extended
from dev_scripts.load_api_keys import load_api_keys

import core.exchanges


class Config:

    name = 'Config'                       # This will be different for any sub-classes

    cfg_filepath = USER_CONFIG_PATH       # Can be overridden
    cfg_parser = ConfigParser()           # python built-in for parsing config files
    params = None

    exchange_name: str = None             # eg. 'KuCoin'
    exchange_id: str = None               # lowercase eg. 'kucoin'
    exchange: ccxt.Exchange = None        # an object that inherits ccxt.Exchange's methods.
    """The ccxt.Exchange object later assigned to Config.exchange should be initialized with API Keys"""
    using_extended_exchange: bool

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
        "exchanges": {},
        "telegram": {
            "app_api_id": None,
            "api_hash": None,
            "username": None,
            "phone": None,
            "notification_channel_id": None
        }
    }
    status = {}

    @staticmethod
    def split_pair(pair, pair_type=None):

        if '/' in pair:
            return pair.split('/')
        else:
            raise ValueError('Invalid trading pair')
        pass

    @staticmethod
    def get_synth_pair_tuple(base_pair, quote_pair):
        base_pair_split = Config.split_pair(base_pair)
        quote_pair_split = Config.split_pair(quote_pair)

        synth_pair = (f"{base_pair_split[0]}{base_pair_split[1]}"
                      f"/{quote_pair_split[0]}{quote_pair_split[1]}")

        synth_pair_tuple = (synth_pair,
                            base_pair_split[0],
                            base_pair_split[1],
                            quote_pair_split[0],
                            quote_pair_split[1])
        return synth_pair_tuple

    def __init__(self, params={}, filepath=USER_CONFIG_PATH):

        self.params = params

        if params is None or len(params) == 0:

            if filepath is not None:
                self.cfg_parser.read([filepath])
            elif filepath is None:
                raise ValueError

            try:
                self.status['msg'] = f"Reading values from {filepath}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.exchange_name = self.cfg_parser['Global Settings']['exchange']
                self.status['exchange_name'] = self.exchange_name
                self.status['msg'] = f"exchange_name: {self.exchange_name}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.exchange_id = self.exchange_name.lower()
                self.status['exchange_id'] = self.exchange_id
                self.status['msg'] = f"exchange_id: {self.exchange_id}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")


                self.strategy_name = self.cfg_parser['Global Settings']['strategy']
                self.status['strategy_name'] = self.strategy_name
                self.status['msg'] = f"strategy_name: {self.strategy_name}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.strategy_import_path = f"strategies.{self.strategy_name}"
                self.status['strategy_import_path'] = self.strategy_import_path
                self.status['msg'] = f"strategy_import_path: {self.strategy_import_path}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.prompt_for_pairs = 'true' in self.cfg_parser['Global Settings']['prompt_for_pairs'].lower()
                self.status['prompt_for_pairs'] = self.prompt_for_pairs
                self.status['msg'] = f"prompt_for_pairs: {self.prompt_for_pairs}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.prompt_borrow_qty = 'true' in self.cfg_parser['Global Settings']['prompt_borrow_qty'].lower()
                self.status['prompt_borrow_qty'] = self.prompt_borrow_qty
                self.status['msg'] = f"prompt_borrow_qty: {self.prompt_borrow_qty}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.base_pair = self.cfg_parser['Global Settings']['base_pair_default']
                self.status['base_pair'] = self.base_pair
                self.status['msg'] = f"base_pair: {self.base_pair}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.quote_pair = self.cfg_parser['Global Settings']['quote_pair_default']
                self.status['quote_pair'] = self.quote_pair
                self.status['msg'] = f"quote_pair: {self.quote_pair}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.stake_currency = self.cfg_parser['Global Settings']['stake_currency']
                self.status['stake_currency'] = self.stake_currency
                self.status['msg'] = f"stake_currency: {self.stake_currency}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.paper_trade = 'true' in self.cfg_parser['Global Settings']['paper_trade'].lower()
                self.status['paper_trade'] = self.paper_trade
                self.status['msg'] = f"paper_trade: {self.paper_trade}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")

                self.telegram_enabled = 'true' in self.cfg_parser['telegram']['enabled'].lower()
                self.status['telegram_enabled'] = self.telegram_enabled
                self.status['msg'] = f"telegram_enabled: {self.telegram_enabled}"
                if self.debug_mode:
                    print(f"{self.status['msg']}\n")
                # breakpoint()
            except:
                print(self.status['msg'])
                raise ValueError("Failed to read from config (Make sure all values are assigned)")
        elif self.params is not None:
            for param in self.params:
                if param not in self.__dict__:
                    raise ValueError(f"Invalid Parameter: '{param}'")

            try:
                self.exchange_name: str = self.params['exchange']
                self.exchange_id = self.exchange_name.lower()
                self.exchange_module_path = f"ccxt.{self.exchange_id}"

                self.strategy_name = self.params['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name['strategy']}"

                self.prompt_for_pairs: bool = params['prompt_for_pairs'],
                self.base_pair: str = params['base_pair'],
                self.quote_pair: str = params['quote_pair'],
                self.stake_currency: str = params['stake_currency']
                self.paper_trade: bool = params['paper_trade']
                self.telegram_enabled = params['telegram_enabled']

                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.cfg_file_key]
            except:
                raise ValueError("Params incomplete")
        else:
            raise Exception("Cannot Initialize Config() without either params or config_filepath")

        self.synth_pair_tuple = self.get_synth_pair_tuple(self.base_pair, self.quote_pair)
        self.synth_pair = self.synth_pair_tuple[0]
        self.read_exchange_api_keys()
        if self.telegram_enabled:
            self.read_telegram_api_keys()

        if self.exchange_id in EXTENDED_EXCHANGES:
            self.exchange_module_path = EXTENDED_EXCHANGES[self.exchange_id][0]
            self.exchange_name = EXTENDED_EXCHANGES[self.exchange_id][1]
            self.using_extended_exchange = True
        else:
            self.exchange_module_path = f"ccxt.{self.exchange_id}"
            self.using_extended_exchange = False

        self.exchange_module = importlib.import_module(self.exchange_module_path)
        self.exchange = getattr(self.exchange_module, self.exchange_id + '_extended')
        self.exchange = self.exchange(self.api_keys['exchanges'][self.exchange_id])
        DEBUG_describe_exchange = self.exchange.describe()

        pass

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

    def read_telegram_api_keys(self):
        self.status['msg'] = "Reading telegram API Keys..."
        if self.debug_mode:
            print("=======[DEBUG]==========\n"
                  f"{self.status['msg']}\n")
        keys = {}
        cfg = self.cfg_parser
        if cfg.has_section('telegram'):
            for key in self.api_keys['telegram']:
                self.api_keys['telegram'][key] = cfg['telegram'][key]

            self.status['msg'] = "Got telegram API Keys"
            if self.debug_mode:
                print(f"{self.status['msg']}\n"
                      "========================\n")
            return self.api_keys['telegram']
        else:
            self.status['ok'] = False
            self.status['msg'] = 'No telegram section in config file'

            return 1

    def read_exchange_api_keys(self, filepath=USER_CONFIG_PATH):
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
            if cfg.has_section(self.exchange_id):
                # for credential in self.api_keys['exchanges'][exchange_name]:
                DEBUG_requiredCredentials = []
                if EXCHANGES[self.exchange_id.upper()]['requiredCredentials']:
                    for credential in EXCHANGES[self.exchange_id.upper()]['requiredCredentials']:
                        key = cfg[self.exchange_id][credential]
                        keys[credential] = key
                        DEBUG_requiredCredentials.append(key)

                else:
                    raise NotImplementedError(f'ccxt.{self.exchange_id} does not have requiredCredentials')

                self.api_keys['exchanges'][self.exchange_id] = keys

            else:
                raise ValueError(f'Failed to read {self.exchange_id} API keys from {filepath}')
        else:
            raise ValueError('No filepath was given for reading exchange api key')

        return keys

    def set_exchange(self):
        raise NotImplementedError
