import random

class SignalEngine:
    def __init__(self):
        self.active_node = None

        # Intel
        self.captured_signal = None
        self.captured_label = None

        # Stats
        self.nodes_accessed = 0
        self.enemies_defeated = 0

        # Live stock data (injected from main)
        self.live_data = None

        # Payout ranges
        self.base_payouts = {
            "very_weak": (10, 30),
            "weak": (30, 60),
            "neutral": (60, 120),
            "strong": (150, 250),
            "very_strong": (300, 600)
        }

    def set_live_data(self, live_data):
        self.live_data = live_data

    def set_active_node(self, node):
        self.active_node = node
        symbol = node.symbol

        stock = self.live_data.get(symbol)
        if not stock:
            self.captured_label = "neutral"
            return

        change = stock.get("change", 0)
        volume = stock.get("volume", 0)

        self.captured_label = self.evaluate_stock(change, volume)

    def evaluate_stock(self, change, volume):
        if change > 4 and volume > 5_000_000:
            return "very_strong"
        if change > 2 and volume > 2_000_000:
            return "strong"
        if -1 <= change <= 2:
            return "neutral"
        if change < -2:
            return "weak"
        return "very_weak"

    def tap_in(self):
        self.nodes_accessed += 1
        return self.captured_label

    def cash_out(self):
        if not self.captured_label:
            return 0

        low, high = self.base_payouts[self.captured_label]
        payout = random.randint(low, high)

        self.captured_label = None
        return payout

    def get_display_data(self):
        return {
            "current_signal": {
                "label": self.captured_label
            },
            "intel": self.captured_label,
            "nodes": self.nodes_accessed,
            "enemies": self.enemies_defeated
    }

    def update(self, dt):
        pass