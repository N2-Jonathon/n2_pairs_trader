# **Home:**

!!! todo 
    ***(March 20th, 2022)***

    Hi Nico, this is my first update in a couple of days since I got stuck on a problem which I've just recently (mostly) solved. I will explain that below.

    I've also migrated the **TODO** list to here for now while I'm developing this, but after the first release I will migrate the **TODO** to its own page, and this will be the Index/Home

    - [x] Write a script which scrapes the contents of what the `describe()` method returns. This was necessary to avoid having to import every exchange to be able to get this information which I was trying to do before with many issues.
    - [ ] Fix imports in `core.constants` for the scraped data to not give any errors when saved as a python dict.
        * [ ] For now I only need the content of `requiredCredentials` and `has` which don't have any out of scope variable names like the rest of the errors, so I can ommit the rest for now and focus on getting those two working first, then sort out the imports after.
        * Having every exchange's `requiredCredentials` as a constant helps in the `Config` & `StrategyBase` classes where the exchange isn't yet imported or initialized but I still need to know what those credentials need to be
        * Having every exchange's `has` as a constant will make it very easy to see which exchanges support what, and be able to judge which strategies are suitable for which exchanges. eg. which exchanges already support margin trading and `fetchBorrowRates` etc



---

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
  - I've added a new method `KuCoinExtended.fetch_max_borrow_amount`, and I'm going to override the
    `fetch_borrow_rate()` method so that it calculates what the rate would be if that's possible? And then it would be
    possible for me to unify how all the strategies are implemented in this codebase so they always use the same
    abstractions. I should make a wrapper method which handles which one to use but for now that has to be done inside
    the strategy.
