import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import MarketLSTM

class MarketDataset(Dataset):
    def __init__(self, path):
        with open(path, "r") as f:
            raw = json.load(f)

        self.X = []
        self.y = []

        for item in raw:
            seq = item["seq"]
            label = item["label"]

            X = []
            for c in seq:
                close = c["close"]
                hl = c["high"] - c["low"]
                pct = (c["close"] - c["open"]) / max(c["open"], 1e-6)
                vol = hl
                X.append([close, hl, pct, vol, 0])

            self.X.append(X)
            self.y.append([label["volatility"], label["direction"], label["breakout"]])

        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def train():
    ds = MarketDataset("training_data.json")
    dl = DataLoader(ds, batch_size=64, shuffle=True)

    model = MarketLSTM()
    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    for epoch in range(10):
        total_loss = 0
        for X, y in dl:
            out = model(X)
            pred = torch.cat([out["volatility"], out["direction"], out["breakout"]], dim=1)
            loss = loss_fn(pred, y)

            opt.zero_grad()
            loss.backward()
            opt.step()

            total_loss += loss.item()

        print("Epoch", epoch, "Loss", total_loss)

    torch.save(model.state_dict(), "model.pth")
    print("Saved model.pth")

if __name__ == "__main__":
    train()
