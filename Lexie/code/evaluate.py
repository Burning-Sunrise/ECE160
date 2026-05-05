import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from model import MarketLSTM
from train import CandleDataset, DEVICE
import numpy as np

def evaluate():
    print("Loading dataset...")
    ds = CandleDataset("training_data.json")
    dl = DataLoader(ds, batch_size=1, shuffle=False)

    print("Loading model...")
    model = MarketLSTM().to(DEVICE)
    model.load_state_dict(torch.load("model.pth", map_location=DEVICE))
    model.eval()

    mae_list = []
    direction_matches = 0
    total = 0

    for X, Y in dl:
        X = X.to(DEVICE)
        Y = Y.to(DEVICE)

        with torch.no_grad():
            pred = model(X)[0]  # shape: (5,4)

        pred = pred.cpu().numpy()
        actual = Y[0].cpu().numpy()

        # MAE on close prices
        mae = np.mean(np.abs(pred[:, 3] - actual[:, 3]))
        mae_list.append(mae)

        # Direction accuracy
        for i in range(5):
            pred_dir = 1 if pred[i][3] > pred[i][0] else 0
            act_dir = 1 if actual[i][3] > actual[i][0] else 0
            if pred_dir == act_dir:
                direction_matches += 1
            total += 1

    print("\n===== MODEL ACCURACY REPORT =====")
    print(f"Samples evaluated: {len(ds)}")
    print(f"Average MAE (close price): {np.mean(mae_list):.4f}")
    print(f"Direction Accuracy: {(direction_matches / total) * 100:.2f}%")
    print("=================================\n")

if __name__ == "__main__":
    evaluate()
