# 7. Further ideas:

- 1 Saving reports to a database?
- 2 Backtesting engine
  - 2.1 This should be done in a lower level language eg. Cython which is python compiled into   `.pyx`/`.pyd` C-like modules with python syntax that can be accessed as normal modules but run   compiled machine code is run instead of having a runtime interperet the script. Cython is also what Hummingbot uses for calculation-intensive modules.
- 3 Combine with triangular arbitrage strategy, using any exposed coins in an open position as stake currencies that execute arbitrage signals and be returned back to the same coin to resume the position
- 4 Add support for normal trading pairs, not just combined trading pairs