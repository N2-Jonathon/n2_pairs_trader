import os
import sys
sys.path.append(os.getcwd())
from configparser import ConfigParser
from pprint import pprint
user_config = ConfigParser()
user_config.read("../user/user-config.ini")

print(user_config['Global Settings']['exchange'])

import ccxt
# import core.exchanges.exchanges as exchanges
import importlib


# strategy = importlib.import_module(f"strategies.{params['strategy']}")