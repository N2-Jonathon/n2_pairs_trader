# Further ideas:

1. Saving reports to a database?
2. Backtesting engine
    - This should be done in a lower level language eg. Cython which is python compiled into   `.pyx`/`.pyd` C-like modules with python syntax that can be accessed as normal modules but run   compiled machine code is run instead of having a runtime interperet the script. Cython is also what Hummingbot uses for calculation-intensive modules.
3. Combine with triangular arbitrage strategy by using any exposed coins in an open position as stake currencies which execute arbitrage signals and are then returned back to the same coin to resume the position.
4. Add support for normal trading pairs, not just combined trading pairs
5. Add support for all tradingview indicators via web scraping or api
6. Add support for MetaTrader indicators via a [ZeroMQ Bridge](https://github.com/darwinex/dwx-zeromq-connector)