import json
from trading_floor import TradingFloor
from market_layer import MarketLayer as Market
from tick_generator import generate_tick


def generate_training_data(samples=5000, seq_len=50, future_len=5):
    print(f"Generating {samples} samples...")

    symbols = ["SIM"]
    market = Market(symbols, use_real_data=False)
    tf = TradingFloor(market, symbols, use_real_data=False)

    data = []
    buf = tf.buffers["SIM"]

    # Warm up the buffer so we have enough candles
    for _ in range(200):
        generate_tick(tf, "SIM", training=True)

    for i in range(samples):
        # Generate enough ticks to form a new candle
        generate_tick(tf, "SIM", training=True)

        # Ensure we have enough history
        if len(buf) < seq_len + future_len:
            continue

        # Extract the last 50 candles
        seq = buf[-(seq_len + future_len):-future_len]

        # Extract the next 5 candles (ground truth)
        future = buf[-future_len:]

        # Store the sample
        data.append({
            "seq": seq,
            "future": future
        })

        if i % 1000 == 0:
            print(f"{i}/{samples}...")

    # Save to JSON
    with open("training_data.json", "w") as f:
        json.dump(data, f)

    print(f"Saved {len(data)} samples to training_data.json")


if __name__ == "__main__":
    generate_training_data()
