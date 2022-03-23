# **KuCoin Extended**

To do margin trading on KuCoin with CCXT, it requires extending the 
`ccxt.kucoin` class which I've done in `core.exchanges.kucoin_extended`.

The methods I've added so far are:

```python
@staticmethod
def generate_order_id(length=24)

def describe(self)

def fetch_max_borrow_size(self, currency)

def fetch_borrow_rate(self, currency)

def borrow(self, currency, size, order_type='FOK')

def fetch_available_margin_balance(self, currency="*")

def fetch_transferable_balance(self, currency, account)

def transfer_between_accounts(self, currency, from_account, to_account, amount)

def place_margin_order(self, side, symbol, size, type)
```

I will eventually show and document each of these, but for now I'm going to focus on `place_margin_order` since as I wrote on the homepage, it's not working properly yet (even though the borrow method does work).

```python
def place_margin_order(self, side, symbol, size, type='market'):
    order_id = self.generate_order_id()

    if type == 'market':
        params = {
            "clientOid": order_id,
            "side": side,
            "symbol": symbol,
            "type": type,
            "size": size
        }
    elif type == 'limit':
        pass
    response = self.privatePostMarginOrder(params)

    pass
```

!!! bug
    I thought that after borrowing, I'd be able to use normal trades, but KuCoin's API is different for trading with the regular trading account and the margin account, so I am adding a new method for posting a margin order.
    
    Right now I'm getting this error as a response from KuCoin:
    ```
    {'code': '200000', 'msg': 'position internal error'}
    ```

    I'm working on figuring it out, and I've also [posted an issue](https://github.com/ccxt/ccxt/issues/12457) in the ccxt repo (They are usually fast at getting back)
  
