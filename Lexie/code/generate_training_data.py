import json
import random
from trading_floor import TradingFloor
from market_layer import Market

def generate_data(samples=50000):
    market = Market()
    symbols = ["SIM"]
    tf = TradingFloor(market, symbols)

    data = []

    buf = tf.buffers["SIM"]

    for _ in range(samples):
        tf.generate_tick("SIM")
        seq = buf[-50:]
        next_candle = buf[-1]

        close = next_candle["close"]
        hl = next_candle["high"] - next_candle["low"]
        pct = (next_candle["close"] - next_candle["open"]) / max(next_candle["open"], 1e-6)

        label = {
            "volatility": hl,
            "direction": pct,
            "breakout": 1.0 if hl > 2.5 * (sum([(c["high"] - c["low"]) for c in seq]) / 50) else 0.0
        }

        data.append({
            "seq": seq,
            "label": label
        })

    with open("training_data.json", "w") as f:
        json.dump(data, f)

    print("Saved training_data.json")

if __name__ == "__main__":
    generate_data()
