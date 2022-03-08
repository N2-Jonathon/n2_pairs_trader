def true_range(data):
    """
      Calculates true range.
      This is needed to calculate ATR & SuperTrend.
    """
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr


def average_true_range(data, period):
    """
      Calculates average true range (ATR).
      This is needed to calculate SuperTrend.
      Can be calculated with either SMA or RMA.
      TradingView uses RMA so this also does.
    """
    data['tr'] = true_range(data)
    atr = data['tr'].rolling(window=period).mean()
    atr_sma = simple_moving_average(data['tr'], period)
    atr_rma = relative_moving_average(data['tr'], period)
    # print(f"\n[atr]\n{atr}\n[atr_sma]\n{atr_sma}\n[atr_rma]\n{atr_rma}")
    return atr_rma


def supertrend(df, period=10, atr_multiplier=2):
    """Calculates SuperTrend"""
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = average_true_range(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = None

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df


def simple_moving_average(data, period):
    sma = data.rolling(window=period).mean()
    return sma


def relative_moving_average(data, period):
    rma = data.ewm(
        alpha=1 / period, adjust=False).mean()
    return rma