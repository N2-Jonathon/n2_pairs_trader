# **Home:**

!!! info

    Finished tasks migrated to [here](/Releases/dev_v0.0.1/dev-journal/)

<a href="https://wakatime.com"><img src="https://wakatime.com/share/@spliffli/f8c024ff-274d-4aaa-b573-1e3f432f2f27.png" /></a>

(Thankfully I don't charge per hour...) I know I can eventually deliver a high quality, reliable and properly tested product if I spend enough time on it.

- Some of this time was spent on other things, but most of the time was actually spent on your project. I'll be able to see a more detailed breakdown when I get WakaTime Premium
- Also, after releasing **[v0.0.1](/Releases/dev_v0.0.1/dev-journal/) (dev)** on github & recording some explanatory videos, I have to request some kind of payment because even though I've been avoiding asking about that so far, the truth is I have no money left in my bank account and my rent is due tomorrow. It's okay if you can't pay on the spot tomorrow and you need time to test it out yourself etc, as long as I'm able to pay my rent eventually then it's okay.
- As you can see my productivity has been declining the past few days and it's because I'm feeling kind of burnt out, so I'd also highly appreciate if I can take a bit of a break between when **[v0.0.1](/Releases/dev_v0.0.1/dev-journal/)** is released before moving on to the unit tests and the **[v0.1.0](/Releases/stable_v0.0.1/dev-journal/) (stable)**

!!! todo

    - [ ] **[6]**  Submit working demo/mvp/proof-of-concept **[Dev v0.0.1](/Releases/dev_v0.0.1/dev-journal/) (not unit tested, only for demo)** & accompanying video
    - [ ] **[7]** Plan which features which will be released incrementally in order of priority, with version numbers to make tracking progress more managable
    - [ ] **[8]** Work on all the steps required for the first stable & unit tested release ***[v0.1.0](/Releases/stable_v0.1.0/dev-journal/) (planned)***

In these docs I will explain how this program works and its architecture, and try to make it easy to understand for
both users or developers.

This initially started out as a way to implement a single strategy ie. the SuperTrend Long/Short Strategy, but it's
designed in a way to be scalable for use with other strategies and exchanges, and have things abstracted in such a
way that each strategy only needs to deal with checking indicator signals, and opening/closing positions, instead of
having to think about the underlying trades that comprise the positions while writing a new strategy.

It will also generate a report whenever a trade is opened or closed, then save it to a log file, and if notifications
are enabled then it will send notifications either via email or telegram or both including information about each
position, which strategy it's from, which pair, the signals taken, trades opened, timestamps, PnL, etc

It should be possible out of the box to use margin trading for any exchange which ccxt has implemented that for, which
unfortunately is not unified nor implemented for some exchanges, unlike some other unified methods for things like
fetching market data, opening trades, etc.

- Unfortunately, KuCoin falls into that category of not having margin trading implemented currently, so I've had to
  implement that myself by:
  - Extending the default ccxt.kucoin in `core.exchanges.kucoin_extended` and overriding the
    methods so that it does still support margin trading. the default method ccxt uses for margin trading is
    `exchange.fetch_borrow_rate()` but KuCoin's API doesn't have that, and it's only possible to get the max borrow
    amount
  - I've added a new method `kucoin_extended.fetch_max_borrow_size`, and I'm going to override the
    `fetch_borrow_rate()` method so that it calculates what the rate would be if that's possible? And then it would be
    possible for me to unify how all the strategies are implemented in this codebase so they always use the same
    abstractions. I should make a wrapper method which handles which one to use but for now that has to be done inside
    the strategy.

# Objectives & Requirements

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
