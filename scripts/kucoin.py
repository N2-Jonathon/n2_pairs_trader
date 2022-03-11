# Since the fetchBorrowRate isn't implemented for KuCoin by ccxt yet
# I have to do it myself for this project
import base64
import hashlib
import hmac
import json
import datetime
import os

import ccxt
import requests
import configparser
import time

from ccxt.base.exchange import Exchange, long

from core import utils


def iso8601(timestamp=None):
    if timestamp is None:
        return timestamp
    if not isinstance(timestamp, (int, long)):
        return None
    if int(timestamp) < 0:
        return None

    try:
        utc = datetime.datetime.utcfromtimestamp(timestamp // 1000)
        return utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-6] + "{:03d}".format(int(timestamp) % 1000) + 'Z'
    except (TypeError, OverflowError, OSError):
        return None


def safe_currency(currency_id, currency=None):
    if currency_id is None and currency is not None:
        return currency
    if (ccxt_kucoin.currencies_by_id is not None) and (currency_id in ccxt_kucoin.currencies_by_id):
        return ccxt_kucoin.currencies_by_id[currency_id]
    return {
        'id': currency_id,
        'code': ccxt_kucoin.common_currency_code(currency_id.upper()) if currency_id is not None else currency_id
    }


def safe_currency_code(currency_id, currency=None):
    currency = safe_currency(currency_id, currency)
    return currency['code']


def safe_value(dictionary, key, default_value=None):
    return dictionary[key] if Exchange.key_exists(dictionary, key) else default_value


def safe_string(dictionary, key, default_value=None):
    return str(dictionary[key]) if Exchange.key_exists(dictionary, key) else default_value


def parse_number(value, default=None):
    if value is None:
        return default
    else:
        try:
            return str(value)
        except Exception:
            return default


def safe_number(dictionary, key, default=None):
    value = safe_string(dictionary, key)
    return parse_number(value, default)


def split_pair(pair, pair_type):
    if pair_type == 'coin_pair':
        print(f"{pair}\n"
              f"{pair[:4]}\n"
              f"{pair[:3]}\n")
        if utils.fetch_ticker(ccxt_kucoin, pair[:4]) is not None:
            base_coin = pair[:4]
            quote_index = 4
        elif utils.fetch_ticker(ccxt_kucoin, pair[:3]) is not None:
            base_coin = pair[:3]
            quote_index = 3
        else:

            raise ValueError("Invalid Base Coin")

        if utils.fetch_ticker(ccxt_kucoin, pair[quote_index:]) is not None:
            quote_coin = pair[quote_index:]
        else:
            raise ValueError("Invalid Quote Coin")
        return {
            "pair": pair,
            "base": base_coin,
            "quote": quote_coin
        }

    elif pair_type == 'pair_of_coin_pairs':
        if '/' in pair:
            return pair.split('/')
        else:
            raise ValueError('Invalid trading pair')


config = configparser.ConfigParser()
config_path = os.path.join(os.getcwd(), 'config.ini')
config.read(config_path)

api_url = 'https://api.kucoin.com'

api_key = config['KuCoin']['apiKey']
api_secret = config['KuCoin']['secret']
api_passphrase = config['KuCoin']['password']

ccxt_kucoin = ccxt.kucoin({
    "apiKey": api_key,
    "secret": api_secret,
    "password": api_passphrase
})


def query_margin_risk_limit():
    endpoint = '/api/v1/risk/limit/strategy?marginModel=cross'
    now = int(time.time() * 1000)

    str_to_sign = str(now) + 'GET' + endpoint
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"

    }
    response = requests.get(f"{api_url}{endpoint}", headers=headers)
    return response.content


def fetch_borrow_rates(params={}, exchange=ccxt_kucoin):
    response = json.loads(query_margin_risk_limit())
    now = int(time.time() * 1000)
    data = safe_value(response, 'data')
    timestamp = str(now)

    rates = {}
    for i in range(0, len(data)):
        rate = data[i]
        code = safe_currency_code(safe_string(rate, 'currency'))
        rates[code] = {
            'currency': code,
            'borrowMaxAmount': safe_number(rate, 'borrowMaxAmount'),
            'rate': safe_number(rate, 'interestRate'),
            'buyMaxAmount': safe_number(rate, 'buyMaxAmount'),
            'period': 86400000,
            'timestamp': timestamp,
            'datetime': iso8601(timestamp),
            'info': rate,
        }
    return rates


def fetch_borrow_rate(coin):
    rates = fetch_borrow_rates()
    _rate = rates[coin]
    return _rate


# [DEBUG]
# print(split_pair('ETHUSD', 'coin_pair'))

data = safe_value(ccxt_kucoin.base_currencies, 'data')

print(data)


# rate = fetch_borrow_rate('ETH')
# rate = query_margin_risk_limit()
# print(rate)
