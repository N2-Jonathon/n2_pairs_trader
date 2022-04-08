!!! important

    Previously finished tasks from before release Once ***[v0.1.0](/Releases/stable_v0.1.0/dev-journal/)*** migrated to [here](/Releases/dev_v0.0.1/dev-journal/)
    
!!! todo

    - [x] **[6]**  Submit working demo/mvp/proof-of-concept **[Dev v0.0.1](/Releases/dev_v0.0.1/dev-journal/) (not unit tested, only for demo)**
        - Github release viewable [here](https://github.com/N2-Jonathon/n2_pairs_trader/releases/tag/v0.0.2-dev)
    - [x] **[7]** Submit demo videos
    - [ ] **[8]** Write User Guide:
          - [x] 1. Installation
          - [x] 2. Running an instance
          - [ ] 3. Changing the configuration
          - [ ] 4. Running multiple instances
          - [ ] 5. Monitoring Positions
          - [ ] Afterwards add screenshots to all of those pages
    - [ ] **[9]** Work on all the steps required for the first stable & unit tested release ***[v0.1.0](/Releases/stable_v0.1.0/dev-journal/) (planned)***
    - [ ] **[10]** Collaboratively plan which features which will be released incrementally in order of priority, clarifying the criteria for each to be fulfilled & assign planned version numbers to make tracking progress more objective. 



## **1. Demo**

Audio quality of my mic sounds like a tin can, so apologies for that. Once ***[v0.1.0](/Releases/stable_v0.1.0/dev-journal/)*** is released, I'll record new videos with concise & easy to follow guides for users, and seperate guides for developers (And I'll get a better mic first)

Also, the first two videos were recorded after the third video so when I refer to the previous video I mean the third video. Th first video ends abruptly since it is the same video as the second one and I just chopped it into two.

EDIT: Minor correction to what I say in the video: When it's in debug mode it's not actually listening for signals, and it's only asking for the prompt. I can however change it so that it is doing both at the same time. If you disable debug_mode, then it will actually be waiting for real signals.

<iframe width="600" height="315" src="https://www.youtube.com/embed/ZX-9DyGvBLo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---

## **2. Looking at the code**

<iframe width="600" height="315" src="https://www.youtube.com/embed/YNiF0Oj13O4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---

## **3. Octobot vs. FreqTrade** 

<iframe width="600" height="315" src="https://www.youtube.com/embed/7OnZLGU81Zw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---

<a href="https://wakatime.com"><img src="https://wakatime.com/share/@spliffli/f8c024ff-274d-4aaa-b573-1e3f432f2f27.png" /></a>

(Thankfully I don't charge per hour...) I know I can eventually deliver a high quality, reliable and properly tested product if I spend enough time on it.

- Some of this time was spent on other things, but most of the time was actually spent on your project. I'll be able to see a more detailed breakdown when I get WakaTime Premium

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

---

# **Objectives & Requirements**

This is a platform that's designed for pairs trading strategies.

Pairs trading is when you take two tradeable pairs eg. `ETH/USDT` and `BTC/USDT` and combine them to make what can be called an 'artificial', 'synthetic', or 'double' pair (I may use those names interchangeably in these docs) by dividing each of the OHLCV data points in the base currency by the quote currency ie. `ETHUSDT/BTCUSDT`

Each position in a pairs trade is composed of at least two trades, with one for each sub-pair:

- To open a short position on the artificial pair `ETHUSDT/BTCUSDT`, that requires going short on the base pair `ETH/USDT` (ie. Sell ETH for USDT), and then going long on the quote pair `BTC/USDT` (ie. Buy BTC with USDT)
- Conversely, to open a long position on `ETHUSDT/BTCUSDT`, that requires going short on the quote pair `BTC/USDT` (ie. Sell BTC for USDT), and then going long on the base pair `ETH/USDT` (ie. Buy ETH with USDT)
- The position's PnL is calculated by adding the PnL from each trade together.

The reason the short trade should be opened before the long trade, is so that borrowed margin can be used to sell the short asset, and the resulting asset from that trade can be funneled into the long trade.

---

## **ETH/USDT**:D1:KUCOIN

![ETH/USDT:D1:KUCOIN - 2022-03-13 22-35-29](images/ETHUSDT-D1-KUCOIN%20-%202022-03-13%2022-35-29.png)

---

## **BTC/USDT**:D1:KUCOIN

![BTC/USDT:D1:KUCOIN - 2022-03-13 22-34-17](images/BTCUSDT:D1:KUCOIN%20-%20%202022-03-13%2022-34-17.png)

---

## **ETHUSDT/BTCUSDT**:D1:KUCOIN

![ETHUSDT/BTCUSDT:D1:KUCOIN - 2022-03-13 22-35-29](images/ETHUSDT-BTCUSDT:D1:KUCOIN%20-%202022-03-13%2022-40-24.png)
