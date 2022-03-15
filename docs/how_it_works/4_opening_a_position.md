# 4. Opening a Position:

A position can be opened either by using the `open()` method of the `Position` class:

```python
position = Position(base_pair, quote_pair,
                    direction=signal,
                    order_type='limit').open()
```

Or, an instance/object of that class (which inherits self.base_pair & self.quote_pair):

```python
from strategies.your_strategy import YourStrategy

strategy=YourStrategy

pm = YourStrategy.position_manager()

position = pm.Position(direction=signal, order_type='limit').open()
```




