# **Home:**

!!! todo

    - [x] **1.** Write a script which scrapes the contents of what the `describe()` method returns. This was necessary to avoid having to import every exchange to be able to get this information which I was trying to do before with many issues.

    ---

    - [x] **2.** Fix imports in `core.constants` for the scraped data to not give any errors when saved as a python dict.
        * [x] For now I only need the content of `rateLimit` `requiredCredentials` and `has` which don't have any out of scope variable names like the rest of the errors, so I can ommit the rest for now and focus on getting those two working first, then sort out the imports after.
        * Having every exchange's `requiredCredentials` as a constant helps in the `Config` & `StrategyBase` classes where the exchange isn't yet imported or initialized but I still need to know what those credentials need to be
        * Having every exchange's `has` as a constant will make it very easy to see which exchanges support what, and be able to judge which strategies are suitable for which exchanges. eg. which exchanges already support margin trading and `fetchBorrowRate` etc

    ---

    - [x] **3.** Make a list of all ccxt exchanges which have:
        * [x] margin trading 
        * [x] `fetchBorrowRate`
    * ***NOTE:***
        You can view this info & more by looking at the 'CCXT Insights' section of the docs

    ---

    - [ ] **4.** Fully implement each step of Long/Short positions including borrowing.
        - [x] ***[4.1]*** **open_long:**
            - [x] **Step 1:**
            Query exchange to fetch max borrow quantity of borrow_coin.
                - **borrow_coin** will be the base coin of the quote pair
                - e.g. in ETHUSDT/**BTC**USDT it is **BTC**
            - [x] **Step 2:**
            If prompt_borrow is true, print the max borrow amount retrieved in step 1, then prompt the user to either accept the max amount or instead enter an amount.
            - [x] **Step 3:**
            Borrow from the exchange in the desired quantity
            - [x] **Step 4:**
            Sell quote pair using the coins borrowed in step 3.
                - eg. Sell BTC for USDT
            - [x] **Step 5:**
            Buy the base coin of the base pair using the quote coin of the base pair.
                - eg. Buy ETH with USDT
        - [x] ***[4.2]*** **open_short:**
            - [x] Copy & modify steps from open_long (refactor this later)
            - **borrow_coin** will be the base coin of the base pair
                - e.g. in **ETH**USDT/BTCUSDT it is **ETH**
        - [ ] ***[4.3]*** **close:**
            - [ ] Re-pay loan
            - [ ] Sell assets back to stake currency USDT 

    ---

    - [ ] **5.** Implement Telegram Notifications with telethon
        - **Note:** I did this in my last project so I can just copy/paste that 

    ---

    - [ ] **6.** Submit working Minimum Viable Product

    ---

!!! note
    ***(March 25th, 2022)***
    ***[22:34 CET | 19:31 EDT]***

    This is already partially usable. At the very least, you can see it open long or short positions, and now I'm just making it save more metadata which will be used to close each position. Once that works, the telegram bot will just send the contents of either `pm.current_position.status` or `pm.current_position.borrow_info` & `pm.current_position.trade_info`.

    - If you want to test this out, then I'd recommend doing so on [KuCoin's sandbox exchange](https://sandbox.kucoin.com/) which works the same as the normal exchange but without real funds. 
    - Right now the bot is using the sandbox API urls/endpoints, so to try it on the real exchange you'd need to delete lines **34-39** from **core/exchanges/kucoin_extended.py**

    ***(March 24th, 2022)***
    ***[16:31 CET | 11:31 EDT]***

    Now each step in open_long works. So next I will do (almost) the same thing for open_short, then move onto close & send notification.

    ***(March 23rd, 2022)***
    ***[20:21 CET | 17:37 EDT]***

    !!! success
        I thought that after borrowing, I'd be able to use normal trades, but KuCoin's API is different for trading with the regular trading account and the margin account, so I am adding a new method for posting a margin order which you can see [here](/KuCoin_Extended/)
        
        {--Right now I'm--} {++I was++} getting this error as a response from KuCoin:
        ```
        {'code': '200000', 'msg': 'position internal error'}
        ```

        {--I'm working on figuring it out--} {++I figured it out++}, and I've also [posted an issue](https://github.com/ccxt/ccxt/issues/12457) in the ccxt repo. I was calling the API incorrectly, but also it seems a bug on their end didn't give the correct error code. 

    ***(March 23rd, 2022)***
    ***[07:37am CET | 03:37am EDT]***

    So I didn't manage to get it finished on Wednesday since yet again I mis-judged how long it would take. However, I have made loads of progress since then and it's looking quite promising. Getting closer to the finish line, since I already managed to properly extend `ccxt.kucoin` and added 2 new methods to it: `fetchMaxBorrowSize` and `borrow` which work properly. 

    - Actually making trades is simple compared to that, since it's already built in and it won't be difficult to figure out how to get ccxt to do that like it was with the margin-related stuff
    - I've been using KuCoin's sandbox exchange for testing which works the same way as the real one.
    - Once `open_long` works, then I can just copy, paste & tweak it for `open_short`
    - Then I'll add a `close` method which closes the position & repays the loan 
    - If you want to see how it's working, you can open the program in an IDE with a debugger, and just watch `self.status`. I will walk you through that when it's submitted.

    ***(March 21st, 2022)***

    ***[11:08am CET | 06:08am EDT]***

    Like I said last night, I'm trying to get this functional by the end of today. Since our last message, I've managed to get through steps 2 & 3 which is going to help a lot with step 4.

    ***(March 20th, 2022)***

    Hi Nico, this is my first update in a couple of days since I got stuck on a problem which I've just recently (mostly) solved. I will explain that below.

    I've also migrated the **TODO** list to here for now while I'm developing this, but after the first release I will migrate the **TODO** to its own page, and this will be the Index/Home.

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