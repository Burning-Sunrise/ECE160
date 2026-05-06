import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import MarketLSTM

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Training on:", DEVICE)

# DATASET
class CandleDataset(Dataset):
    def __init__(self, path):
        with open(path, "r") as f:
            self.raw = json.load(f)

    def __len__(self):
        return len(self.raw)

    def __getitem__(self, idx):
        item = self.raw[idx]

        seq = item["seq"]
        future = item["future"]

        X = []
        for i, c in enumerate(seq):
            open_p = c["open"]
            close_p = c["close"]
            high = c["high"]
            low = c["low"]

            body = close_p - open_p
            upper = high - max(open_p, close_p)
            lower = min(open_p, close_p) - low
            pct = (close_p - open_p) / max(abs(open_p), 1e-6)

            if i >= 20:
                recent = seq[i-20:i]
                rv = np.std([x["high"] - x["low"] for x in recent])
            else:
                rv = 0.0

            if i >= 5:
                momentum = close_p - seq[i-5]["close"]
            else:
                momentum = 0.0

            norm_close = close_p / 100.0

            X.append([
                close_p,
                body,
                upper,
                lower,
                pct,
                rv,
                momentum,
                norm_close
            ])

        Y = []
        for c in future:
            Y.append([c["open"], c["high"], c["low"], c["close"]])

        return torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32)


# TRAINING LOOP
def train():
    dataset = CandleDataset("training_data.json")
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = MarketLSTM().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    EPOCHS = 10

    for epoch in range(EPOCHS):
        total_loss = 0.0

        for X, Y in loader:
            X = X.to(DEVICE)  # (batch, 50, 8)
            Y = Y.to(DEVICE)  # (batch, 5, 4)

            optimizer.zero_grad()
            pred = model(X)  # (batch, 5, 4)

            loss = loss_fn(pred, Y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS}  Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), "model.pth")
    print("Training complete. Saved model.pth")

# ENTRY POINT
if __name__ == "__main__":
    train()
