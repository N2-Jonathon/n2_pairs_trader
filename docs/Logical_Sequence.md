# Sequence of Events:

## Initialize main( ):
1. From a terminal, run `python __main__.py`
2. Inside `__main__.py`, the `run_bot()` function is called which takes the optional param `strategy=`. When it's not specified, it currently defaults to `strategy=N2SuperTrend()` which initializes the strategy.

```python
if __name__ == '__main__':

    run_bot()  # Can pass a Strategy to override default eg. run_bot(strategy=YourStrategy)
```

3. When the strategy class eg. `N2SuperTrend` is initialized without params then is loads the values set in `user/user-config.ini`

```python
def run_bot(strategy=N2SuperTrend()):
  ...
```

4. At this point, you can access the following Fields inherited by StrategyBase:


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

## 
* 4. hello world
