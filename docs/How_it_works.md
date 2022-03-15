# How it works:
**[Note]**This is a work in progress  and I can't garauntee everything works 100% until this note says otherwise, after doing unit tests for everything. I am also still debugging and there are still a couple more things I have to add before it's operational, but should hopefully have that sorted later today (15th).
---

---



This is the sequence of events that happens when you run the bot. I'm writing this to explain what's going on, and also to be able to properly write unit tests to ensure that it's actually 
working as it should.
## 1. Start the bot:
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

## 2.1 Initialize strategy

- When a strategy class eg. `N2SuperTrend` is initialized without params then it loads the values set in `user/user-config.ini`

```python
def run_bot(strategy=N2SuperTrend()):
  ...
```

- At this point, you can access the following Fields inherited by `StrategyBase` :


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

### 2.2 How a strategy is initialized behind the scenes:
What happens when the strategy object is instantiated eg. `strategy = N2SuperTrend()` is that the `__init__` method inside the `N2SuperTrend` class is called:

```python
class N2SuperTrend(StrategyBase):

  def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
          """
          The first line `super().__init__(params, config_filepath)` means
          it runs the __init__ method in StrategyBase and inherits its
          attributes from there, then the name is set.

          :param params:
          :type params:
          :param config_filepath:
          :type config_filepath:
          """
          super().__init__(params, config_filepath)

          self.name = 'n2_supertrend'
```
- This is all you'd need to put in the `__init__` of any new strategy, and then put the strategy's logic for how it generates a signal inside of the method `YourStrategy.get_signal()`
- Like it says in the comment, the `super()` function on the first line runs the `__init__` of the `StrategyBase` class so it inherits all the attributes and methods of `StrategyBase` and then it assigns a name for the strategy.

Here's what's happening in `StrategyBase.__init__()` where the program executes next before coming back to `N2SuperTrend`:

```python
from core.config import Config

class StrategyBase(Config):
    """
    A strategy is an object whose main purpose is to contain regularly updated market data by pulling OHLCV data from both the base pair and the quote pair, then combining them to make the synth pair, keeping track of PnL for both underlying trades.

    The main logic which is specific to your strategy should be implemented in the `get_signal()` method which should then be called at a regular defined interval.

    The signal can be set either to be for a single timeframe or multiple timeframes by setting the value of `multi_timeframe_signal_mode: Bool` for that strategy.
    """
    ...

    def __int__(self, params={}, config_filepath=USER_CONFIG_PATH):
        """
        The first line: `super().__init__(params, config_filepath)` means
        it runs the __init__ method in Config and inherits its attributes
        from there, then after that, the other attributes are set.

        :param params:
        :type params:
        :param config_filepath:
        :type config_filepath:
        :return:
        :rtype:
        """
        super().__init__(self, params, config_filepath)

        self.name = None
        self.current_signal = None
        self.position_manager = PositionManager()
```

- The `StrategyBase` class inherits the `Config` class and calls the `super()` function on the first line too, which calls the `__init__()` of `Config`. 
- `Config` doesn't inherit anything and it's a base class for other classes to inherit. It provides an extra layer between the strategy and lower level configuration options eg.

-    **[TODO]** OHCLV data source should be configurable so that later when making a backtesting environment that will be given historic market data and a much faster tick interval, it will be possible to have multiple instances of running strategies configured differently. 
    
- It shouldn't need to be edited unless developing/debugging): 
- This is what happens in `Config.__init__()` where the program executes next before coming back to `StrategyBase.__init__()`.

```python
class Config:
    __dict__ = {
        "exchange": str,
        "strategy_name": str,
        "prompt_for_pairs": bool,
        "base_pair": str,
        "quote_pair": str,
        "stake_currency": str,
        "paper_trade": bool,

        "debug_mode": bool
    }

    cfg_parser = ConfigParser()

    def __init__(self, params={}, filepath=USER_CONFIG_PATH):

        self.params = params

        if params is None or len(params) == 0:

            if filepath is not None:
                self.cfg_parser.read([filepath])
            elif filepath is None:
                raise ValueError

            try:
                self.exchange_id = self.cfg_parser['Global Settings']['exchange']
                self.strategy_name = self.cfg_parser['Global Settings']['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name}"

                self.prompt_for_pairs = bool(self.cfg_parser['Global Settings']['prompt_for_pairs'])
                self.base_pair = self.cfg_parser['Global Settings']['base_pair_default']
                self.quote_pair = self.cfg_parser['Global Settings']['quote_pair_default']
                self.stake_currency = self.cfg_parser['Global Settings']['stake_currency']
                self.paper_trade = bool(self.cfg_parser['Global Settings']['paper_trade'])

                # self.synth_pair = self.get_synth_pair_symbol(self.base_pair, self.quote_pair)
                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id]
            except:
                raise ValueError("Failed to read from config (Make sure all values are assigned)")
        elif self.params is not None:
            for param in self.params:
                if param not in self.__dict__:
                    raise ValueError(f"Invalid Parameter: '{param}'")

            try:
                self.exchange_id: str = self.params['exchange']
                self.strategy_name = self.params['strategy']
                self.strategy_import_path = f"strategies.{self.strategy_name['strategy']}"

                self.prompt_for_pairs: bool = params['prompt_for_pairs'],
                self.base_pair: str = params['base_pair'],
                self.quote_pair: str = params['quote_pair'],
                self.stake_currency: str = params['stake_currency']
                self.paper_trade: bool = params['paper_trade']

                # self.strategy = importlib.import_module(f"strategies.{self.strategy_name}")
                # self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id]
            except:
                raise ValueError("Params incomplete")
        else:
            raise Exception("Cannot Initialize Config() without either params or config_filepath")

        self.synth_pair = utils.get_synth_pair_symbol(self.base_pair, self.quote_pair)
        self.enabled_exchanges = self.get_enabled_exchanges()
        self.exchange: ccxt.Exchange = self.enabled_exchanges[self.exchange_id.lower()]
```

 What it's doing is checking to see if params were supplied to override the default config.

- If params are passed to `Config` or any of its subclasses ie. `StrategyBase` or `N2SuperTrend` are instantiated, then it will load those params as a configuration.

- If params are not supplied, it will use a `config.ini` file specified by `filepath`, which defaults to the global constant `USER_CONFIG_PATH` (This is set in `core.constants` to `user/user-config.ini`)

## 3. After strategy is initialized:

- It will have its own PositionManager object as a Field which can be accessed from within a strategy class like this:
```python
    from core.constants import USER_CONFIG_PATH
    from core.position_manager import PositionManager

    class N2SuperTrend(BaseStrategy):
        ...
        def __init__(self, params={}, config_filepath=USER_CONFIG_PATH):
            ...
            self.position_manager: PositionManager = PositionManager()
            ...
```

