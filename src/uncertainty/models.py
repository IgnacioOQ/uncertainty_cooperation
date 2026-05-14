"""MC-Dropout and Deep-Ensemble regressors for the 1-D uncertainty sandbox."""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def generate_data(n_samples=100):
    """Generate noisy sinusoidal data with a gap in [-1, 1].

    The gap lets us observe whether a model reports high uncertainty
    in regions it hasn't seen — crucial for UCB-style exploration.
    """
    x = np.linspace(-4, 4, n_samples)
    # Create a gap in data between -1 and 1
    mask = (x < -1) | (x > 1)
    x = x[mask]

    # Target function: y = x * sin(x) + noise
    y = x * np.sin(x) + 0.1 * np.random.randn(*x.shape)

    # Reshape for PyTorch
    x_tensor = torch.FloatTensor(x).unsqueeze(1)
    y_tensor = torch.FloatTensor(y).unsqueeze(1)
    return x, y, x_tensor, y_tensor


class DropoutNet(nn.Module):
    def __init__(self, dropout_rate=0.2):
        super(DropoutNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x)


def train_dropout_model(x_train, y_train, epochs=1000):
    model = DropoutNet(dropout_rate=0.1)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    print("Training MC Dropout Model...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(x_train)
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()
    return model


def predict_mc_dropout(model, x_test, n_passes=50):
    """Perform multiple forward passes with Dropout enabled during evaluation."""
    model.train()  # KEEP dropout active
    predictions = []

    with torch.no_grad():
        for _ in range(n_passes):
            predictions.append(model(x_test).numpy())

    predictions = np.array(predictions).squeeze()  # Shape: (n_passes, n_samples)
    mean_pred = predictions.mean(axis=0)
    std_pred = predictions.std(axis=0)  # This represents uncertainty
    return mean_pred, std_pred


def train_ensemble(x_train, y_train, n_models=5, epochs=1000):
    models = []
    print(f"Training Deep Ensemble ({n_models} models)...")

    for i in range(n_models):
        # Initialize a standard net (no dropout needed, relying on init seed)
        model = nn.Sequential(
            nn.Linear(1, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        for epoch in range(epochs):
            optimizer.zero_grad()
            output = model(x_train)
            loss = criterion(output, y_train)
            loss.backward()
            optimizer.step()

        models.append(model)

    return models


def predict_ensemble(models, x_test):
    predictions = []
    with torch.no_grad():
        for model in models:
            model.eval()
            predictions.append(model(x_test).numpy())

    predictions = np.array(predictions).squeeze()
    mean_pred = predictions.mean(axis=0)
    std_pred = predictions.std(axis=0)  # Uncertainty from ensemble disagreement
    return mean_pred, std_pred
