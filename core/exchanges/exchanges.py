import os
import sys
sys.path.append(os.getcwd())

from configparser import ConfigParser
import ccxt
from scripts.kucoin_extended import KuCoinExtended


config = ConfigParser()
config.read("user/user-config.ini")

exchanges = {
    "kucoin"
}
kucoin = KuCoinExtended({
    "apiKey": config['KuCoin']['apiKey'],
    "secret": config['KuCoin']['secret'],
    "password": config['KuCoin']['password']
})

hitbtc = ccxt.hitbtc({
    "apiKey": config['HitBTC']['apiKey'],
    "secret": config['HitBTC']['apiKey']
})
