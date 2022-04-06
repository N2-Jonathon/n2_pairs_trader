# Creating a new strategy
:: stub

### **[TODO]**:
Write some content here which explains:

- How to create a new strategy 
  by extending the BaseStrategy() class eg. `class N2SuperTrend(BaseStrategy)`
- How to initialize those strategies in `__main__.py` with different configurations eg.

```python
from strategies.n2_supertrend import N2SuperTrend

# initialize using default configuration read from user/user-config.ini
strategy = N2SuperTrend()

# another way to initialize (eg. for backtesting if that gets implemented):
strategy = N2SuperTrend(params={
  # TODO: Document which params need to go in here. This isn't really needed 
  #  at this point but might be helpful later
})
```