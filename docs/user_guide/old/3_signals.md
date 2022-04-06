# 3. Market Data & Signals:

- The strategy will have its own ccxt.Exchange type initialized with api keys read from the user config that gets stored in `self.exchange` and PositionManager object as a Fields and which can be accessed from inside or outside of the strategy class (better inside):

### Going back to the run_bot() function in __main__.py:

```python
def run_bot(strategy=N2SuperTrend()):
    running = True

    pm: PositionManager = strategy.position_manager

    while running:

        if strategy.debug_mode:
            """If in debug mode, prompt for signal override"""
            override_signal = input("[DEBUG]Enter a signal to emulate: ([LONG]|SHORT|CLOSE)")
            if override_signal == "":
                signal = 'LONG'  # Default if you just press enter at the prompt
            elif override_signal.upper() == 'SHORT' or override_signal == 'LONG':
                signal = override_signal
        else:
            """If not in debug mode, call the get_signal method of the strategy"""
            signal = strategy.listen_for_signals()

        ...


if __name__ == '__main__':
    run_bot()  # Can pass a Strategy to override default eg. main(strategy=YourStrategy)
```

- First, the strategy's PositionManager is assigned to the variable `pm` (can be called anything)
- Then, it enters a while loop: `while running:`
  This while loop is essentially one tick, and it would be better to move this out of `__main__.py` and into a a new method of `StrategyBase` or `Config`: called `run()` or `start()`
- I haven't yet accounted for rate limits, but it's possible to fetch rate limits for an exchange with ccxt.

## Getting a signal from the strategy

When the `strategy.get_signal` method is called, it will run whatever logic you have defined in that method for your strategy.

- If you don't create a method in your strategy called `get_signal`, it will default to the one in `StrategyBase` and raise a `NotImplemented` error:
- Otherwise, when you do define a `get_signal` method, it will override the one in `StrategyBase` and you can implement whatever logic and conditions  to generate the strategy's net signal in that method.
- The signal can either based on one timeframe or you can enable and define **Multi-timeframe signal rules** as a `dict` with keys for each timeframe that have `bool` values. Whichever timeframes are set to true, must reach a consensus of their signals for them to generate an aggregated signal.
  - **[TODO]**: make it so that in multi-timeframe mode, instead of fetching signals for all timeframes at every tick, they will each have different intervals to stay within rate limits.
  - I also need to change how `get_signal` is currently fetching historic bars every time it's called when it should only need to do that once, and then update the price with live tick data from by using `ccxt.Exchange.fetch_ticker()`

```python
def run_bot(strategy=N2SuperTrend()):
    running = True
    pm: PositionManager = strategy.position_manager

    while running:
        ...
        signal = strategy.listen_for_signals()

        if signal is not None and signal != 'CLOSE':
            """If there is a new signal to LONG or SHORT:"""
            if pm.get_current_position() is None:
                """
                If there's no current position open, then open one
                in the signal of the signal and set it as pm's
                current_position
                """
                position = Position(strategy.base_pair, strategy.quote_pair,
                                    direction=signal,
                                    order_type='limit').open()
                # TODO: Here is where the `core.notifier` class would be
                #   used to report the opening of the position and send
                #   send a notification via telegram and/or email.
                pm.set_current_position(position)

        elif signal == 'CLOSE':
            """
            If the signal is 'CLOSE', then close the pm.current_position
            """
            pm.current_position.close()
            # TODO: Here `core.notifier` would be used again to report
            #   the closing of the trade and send via email/telegram

        tick_interval = 60  # This should be adjusted to take API rate limits into account
        """For now the tick_interval is set here, but it should be set by params config file by Config.__init__()"""

        time.sleep(tick_interval)
        # await asyncio.sleep(tick_interval)
```