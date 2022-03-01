import ccxt
import config

exchange = ccxt.kucoin({
  "apiKey": config.KUCOIN_API_KEY,
  "secret": config.KUCOIN_SECRET_KEY,
  "password": config.KUCOIN_PASSWORD
})

def open_position(direction: str, 
                  base_pair: str,
                  quote_pair: str,
                  borrow_coin: str,
                  borrow_qty: float,
                  prompt_confirmation: bool):
  
  if direction.lower() == 'long':
    open_long(base_pair, quote_pair, borrow_coin, borrow_qty, prompt_confirmation)
  elif direction.lower == 'short':
    open_short(base_pair, quote_pair, borrow_coin, borrow_qty, prompt_confirmation)
  else:
    raise ValueError('direction is invalid')

def open_long(base_pair: str,
              quote_pair: str,
              borrow_coin: str,
              prompt_borrow: bool):
  # ----------------------------------------
  # Step 1: Query exchange to fetch max     
  # [TODO]  borrow quantity of borrow_coin 
  #         borrow_coin will be base coin
  #         eg. BTC
  #         of the quote_pair
  #         eg. BTCUSDT
  # ----------------------------------------
  # Step 2: If prompt_borrow is true, print
  # [TODO]  the max borrow amount retrieved
  #         in step 1, then prompt the user
  #         to either accept the max amount 
  #         or instead enter an amount.
  # ----------------------------------------
  # Step 3: Borrow from the exchange in the 
  # [TODO]  desired quantity
  # ----------------------------------------
  # Step 4: Sell quote pair using the coins
  # [TODO]  borrowed in step 3.
  #         eg. Sell BTC for USDT
  # ----------------------------------------
  # Step 5: Buy the base coin of the base
  # [TODO]  pair using the quote coin of the
  #         pair.
  #         eg. Buy ETH with USDT
  # ----------------------------------------
  # Step 6: Generate & Send Email with all
  #         of the details about the open 
  #         position included.
  pass

def open_short(base_pair: str,
              quote_pair: str,
              borrow_coin: str,
              borrow_qty: float,
              prompt_confirmation: bool):
  raise NotImplementedError("Will implement this after open_long")
  pass