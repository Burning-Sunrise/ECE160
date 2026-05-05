import torch
import numpy as np
from model import MarketLSTM

class AIPipeline:
    def __init__(self, model_path="model.pth"):
        self.model = MarketLSTM()
        try:
            self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
            print("AI model loaded.")
        except FileNotFoundError:
            print("WARNING: model.pth not found — using untrained model.")
        self.model.eval()

    def encode(self, seq):
        X = []
        for c in seq:
            close = c["close"]
            hl = c["high"] - c["low"]
            pct = (c["close"] - c["open"]) / max(c["open"], 1e-6)
            vol = hl
            X.append([close, hl, pct, vol, 0])
        return torch.tensor([X], dtype=torch.float32)

    def predict(self, seq):
        X = self.encode(seq)
        with torch.no_grad():
            out = self.model(X)[0]  # shape: (5, 4)

        preds = []
        for i in range(5):
            o, h, l, c = out[i].tolist()
            preds.append({
                "open": o,
                "high": h,
                "low": l,
                "close": c
            })

        return preds
