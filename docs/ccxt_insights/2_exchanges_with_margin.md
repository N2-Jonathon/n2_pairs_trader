These are the exchanges that have margin trading implemented by ccxt.

It's not very many, and there are probably more exchanges like kucoin which do have margin trading but are not on this list. For those exchanges, extra work will be needed identify them and to implement margin trading by extending the ccxt exchange.


|    | EXCHANGE    | requiredCredentials   | rateLimit   | has   | margin   | fetchBorrowRate   |
|---:|:------------|:----------------------|:------------|:------|:---------|:------------------|
| 19 | ZB          | False                 | True        | True  | True     | True              |
| 34 | BINANCE     | False                 | True        | True  | True     | True              |
| 42 | GATEIO      | True                  | True        | True  | True     | False             |
| 46 | HUOBI       | False                 | True        | True  | True     | True              |
| 52 | WOO         | False                 | True        | True  | True     |                   |
| 60 | KRAKEN      | False                 | True        | True  | True     | False             |
| 61 | OKX         | True                  | True        | True  | True     | True              |
| 64 | FTX         | False                 | True        | True  | True     | True              |
| 65 | BEQUANT     | False                 | False       | False | True     | True              |
| 90 | CURRENCYCOM | False                 | True        | True  | True     |                   |