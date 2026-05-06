import random

#existing base candles have small wicks. Adjust to make more consistent with synthetic 
#keep candle generation modular
def add_wicks_to_existing(buf):
    """Adds random wick lengths to existing candles."""
    for c in buf:
        body = abs(c["close"] - c["open"])
        #add visual variability
        wick = body * random.uniform(0.6, 1.4)
        c["high"] = max(c["open"], c["close"]) + wick
        c["low"] = min(c["open"], c["close"]) - wick

#react to volatility, trend. Adjust visuals
def generate_tick(floor, sym, training=False):
    """Generates a synthetic micro‑tick for a symbol.
       If training=True, buffer is allowed to grow beyond 50 candles."""
    buf = floor.buffers[sym]
    price = floor.current_price[sym]

    # Recent volatility from last 20 candles
    recent = buf[-20:]
    ranges = [c["high"] - c["low"] for c in recent]
    avg_range = sum(ranges) / len(ranges) if ranges else 1.0

    # Volatility multiplier
    VOL_MULT = 3.5
    vol = max((avg_range / 20) * VOL_MULT, 0.05)

    # Trend bias from last candle
    last = buf[-1]
    trend = (last["close"] - last["open"]) / 25

    # Rare volatility bursts to replicate realistic market behavior
    if random.random() < 0.05:
        vol *= 2.2

    # Volatility clustering
    if random.random() < 0.15:
        vol *= 1.4

    # Micro‑tick move
    move = random.gauss(trend, vol)
    open_p = price
    close_p = open_p + move
    #update current floor price
    floor.current_price[sym] = close_p

    # Wick amplification
    wick = abs(move) * random.uniform(1.2, 2.0)

    # Append new candle
    buf.append({
        "open": open_p,
        "close": close_p,
        "high": max(open_p, close_p) + wick,
        "low": min(open_p, close_p) - wick,
    })

    # Keep buffer at 50 candles ONLY during gameplay
    if not training and len(buf) > 50:
        buf.pop(0)
