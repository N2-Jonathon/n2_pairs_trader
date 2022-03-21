These are the exchanges that have fetchBorrowRate implemented by ccxt.

It's only 6 exchanges which will work out of the box for margin trading. If you can find any more exchanges which have margin trading but aren't on this list (eg. kucoin) then I can try to implement it myself for those exchanges.

For the exchanges on the previous page which have margin trading, but don't have fetchBorrowRate, I will have to find an alternative way to implement margin trading

!!! warning
    I need to know `requiredCredentials` to be able to initialize an exchange with API keys to be able to access their private methods needed for trading.

    Therefore, any exchanges which don't have that, I'll need to manually add those values as constants.

    Thankfully, that's the easiest thing to implement (all it takes is checking the exchange's API docs), and I will probably do a pull request on ccxt once I've implemented some stuff that they haven't.

It's a very grand idea to have a unified API for all exchanges, and I realize now from seeing this data, that it's still very incomplete and many things still need to be implemented.

That said, I still think ccxt is an amazing starting point to build upon.

|    | EXCHANGE   | requiredCredentials   | rateLimit   | has   | margin   | fetchBorrowRate   |
|---:|:-----------|:----------------------|:------------|:------|:---------|:------------------|
| 19 | ZB         | False                 | True        | True  | True     | True              |
| 34 | BINANCE    | False                 | True        | True  | True     | True              |
| 46 | HUOBI      | False                 | True        | True  | True     | True              |
| 61 | OKX        | True                  | True        | True  | True     | True              |
| 64 | FTX        | False                 | True        | True  | True     | True              |
| 65 | BEQUANT    | False                 | False       | False | True     | True              |