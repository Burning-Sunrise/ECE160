import threading
import pygame
import random
from collections import deque


class LiveData:
    def __init__(self, symbols, update_interval=15000):
        self.symbols = symbols

        # latest candle (real or simulated)
        self.data = {s: None for s in symbols}

        # last 4 REAL candles
        self.history = {s: deque(maxlen=4) for s in symbols}

        # last valid candle (real)
        self.last_valid = {s: None for s in symbols}

        self.last_update = 0
        self.update_interval = update_interval
        self.lock = threading.Lock()

    # UPDATE LOOP

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self._start_background_update()

    def _start_background_update(self):
        thread = threading.Thread(target=self._update_all_symbols)
        thread.daemon = True
        thread.start()

    def _update_all_symbols(self):
        with self.lock:
            for symbol in self.symbols:
                try:
                    candle = self._fetch_real_candle(symbol)

                    if candle:
                        # store real candle
                        self.data[symbol] = candle
                        self.last_valid[symbol] = candle
                        self.history[symbol].append(candle)
                    else:
                        # market closed → simulate
                        self.data[symbol] = self._simulate_candle(symbol)

                except Exception as e:
                    print(f"[LiveData] Error fetching {symbol}: {e}")

    # REAL CANDLE 
    def _fetch_real_candle(self, symbol):
        # Your current random candle generator
        open_price = random.uniform(100, 200)
        close_price = open_price + random.uniform(-5, 5)
        change = close_price - open_price

        candle = {
            "open": open_price,
            "close": close_price,
            "high": max(open_price, close_price) + random.uniform(0, 3),
            "low": min(open_price, close_price) - random.uniform(0, 3),
            "volume": random.randint(1_000_000, 5_000_000),
            "change": change,
            "simulated": False
        }

        return candle

    # SIMULATED CANDLE (weekends/holidays)
    def _simulate_candle(self, symbol):
        last4 = list(self.history[symbol])

        # If we have no history yet, fallback to last_valid
        if len(last4) < 4:
            return self.last_valid[symbol]

        closes = [c["close"] for c in last4]

        # average drift from last 4 real candles
        avg_drift = (closes[-1] - closes[0]) / 4

        open_price = closes[-1]
        close_price = open_price + random.uniform(avg_drift - 0.5, avg_drift + 0.5)

        return {
            "open": open_price,
            "close": close_price,
            "high": max(open_price, close_price) + random.uniform(0, 0.3),
            "low": min(open_price, close_price) - random.uniform(0, 0.3),
            "volume": 0,
            "change": close_price - open_price,
            "simulated": True
        }


    # SAFE GETTER
    def get(self, symbol):
        return self.data.get(symbol) or self.last_valid.get(symbol)
