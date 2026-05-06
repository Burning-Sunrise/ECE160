import torch
import torch.nn as nn

class MarketLSTM(nn.Module):
    def __init__(self, input_size=8, hidden_size=256, num_layers=2, future_len=5):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        # A deeper prediction head
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, future_len * 4)
        )

        self.future_len = future_len

    def forward(self, x):
        out, _ = self.lstm(x)
        last = out[:, -1, :]  # last timestep
        pred = self.head(last)
        return pred.view(-1, self.future_len, 4)
