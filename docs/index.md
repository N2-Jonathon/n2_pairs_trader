# Home:

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
