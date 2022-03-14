# Sequence of Events:

1. From a terminal, run `python __main__.py`
2. `main()` function is called with no params. It also takes the optional param `strategy`. When it's not specified, it currently defaults to `def main(strategy=N2SuperTrend())` which initializes the strategy with the values set in the user config.
3. At this point, you can access the following Fields inherited by StrategyBase:

   ```python
   strategy.exchange: str,
   strategy.strategy_name: str,
   strategy.prompt_for_pairs: bool,
   strategy.base_pair: str,
   strategy.quote_pair: str,
   strategy.synth_pair: str,  # Not sure if this is set properly by __init__ yet
   strategy.stake_currency: str,
   strategy.paper_trade: bool,

   strategy.position_manager: PositionManager,
   strategy.previous_tick: datetime,
   strategy.ohlcv_data: dict,
   strategy.signal: str,

   strategy.multi_timeframe_mode: bool
   strategy.multi_timeframe_signal_rules: dict
   ```
4. hello
