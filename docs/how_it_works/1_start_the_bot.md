# 1. Start the bot:

- From a terminal, run `python __main__.py`
- Inside `__main__.py`, the `run_bot()` function is called which takes the optional param `strategy=`. When it's not specified, it currently defaults to `strategy=N2SuperTrend()` which initializes the strategy.

```python
if __name__ == '__main__':

    run_bot()  # Can pass a Strategy to override default eg. run_bot(strategy=YourStrategy)
```

- you can edit this part of `__main__.py` to override the default strategy. you also need to import the Strategy at the top of `__main__`:

```python
from strategies.another_strategy import AnotherStrategy
...
if __name__ == '__main__':

    run_bot(strategy=AnotherStrategy())
```

- **TODO**: I want to make it so that it you can pass the strategy as an argument from terminal, which could be useful for implementing backtesting

