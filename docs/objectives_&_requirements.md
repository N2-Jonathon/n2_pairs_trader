# Objectives & Requirements Interactive docs

This is a platform that's designed for pairs trading strategies.

Pairs trading is when you take two tradeable pairs eg. `ETH/USDT` and `BTC/USDT` and combine them to make what can be called an 'artificial', 'synthetic', or 'double' pair (I may use those names interchangeably in these docs) by dividing each of the OHLCV data points in the base currency by the quote currency ie. `ETHUSDT/BTCUSDT`

Each position in a pairs trade is composed of at least two trades, with one for each sub-pair:

- To open a short position on the artificial pair `ETHUSDT/BTCUSDT`, that requires going short on the base pair `ETH/USDT` (ie. Sell ETH for USDT), and then going long on the quote pair `BTC/USDT` (ie. Buy BTC with USDT)
- Conversely, to open a long position on `ETHUSDT/BTCUSDT`, that requires going short on the quote pair `BTC/USDT` (ie. Sell BTC for USDT), and then going long on the base pair `ETH/USDT` (ie. Buy ETH with USDT)
- The position's PnL is calculated by adding the PnL from each trade together.

The reason the short trade should be opened before the long trade, is so that borrowed margin can be used to sell the short asset, and the resulting asset from that trade can be funneled into the long trade.


---
## **ETH/USDT|D1|KUCOIN**
![ETH/USDT:D1:KUCOIN - 2022-03-13 22-35-29](images/ETHUSDT-D1-KUCOIN%20-%202022-03-13%2022-35-29.png)

---
## BTC/USDT:D1:KUCOIN
![BTC/USDT:D1:KUCOIN - 2022-03-13 22-34-17](images/BTCUSDT:D1:KUCOIN%20-%20%202022-03-13%2022-34-17.png)

---
## ETHUSDT/BTCUSDT:D1:KUCOIN
![ETHUSDT/BTCUSDT:D1:KUCOIN - 2022-03-13 22-35-29](images/ETHUSDT-BTCUSDT:D1:KUCOIN%20-%202022-03-13%2022-40-24.png)