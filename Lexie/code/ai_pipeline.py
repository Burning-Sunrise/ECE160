import torch
import os
from model import MarketLSTM
print("USING AI PIPELINE FROM:", __file__)

class AIPipeline:
    def __init__(self, model_path="model.pth"):
        self.model = MarketLSTM()
        try:
            self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
            print("AI model loaded.")
        except FileNotFoundError:
            print("WARNING: model.pth not found — using untrained model.")
        self.model.eval()

    # 8‑FEATURE ENCODER (NO VOLUME REQUIRED)
    def encode(self, seq):
        X = []
        for c in seq:
            open_  = c["open"]
            high   = c["high"]
            low    = c["low"]
            close  = c["close"]

            body   = close - open_          # feature 5
            range_ = high - low             # feature 6
            ret    = (close / open_) - 1    # feature 7
            wick   = (high - close)         # feature 8 (upper wick size)

            X.append([
                open_,      # 1
                high,       # 2
                low,        # 3
                close,      # 4
                body,       # 5
                range_,     # 6
                ret,        # 7
                wick        # 8
            ])

        return torch.tensor([X], dtype=torch.float32)

    # Predict next 5 candles
    def predict(self, seq):
        seq = seq[-50:]  # last 50 candles
        X = self.encode(seq)

        with torch.no_grad():
            out = self.model(X)[0]  # shape: (5, 4)

        preds = []
        for i in range(5):
            o, h, l, c = out[i].tolist()
            preds.append([o, h, l, c])

        return preds
