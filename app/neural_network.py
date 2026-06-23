import torch.nn as nn


class PhishingANN(nn.Module):
    """
    Dense Multi-Layer Perceptron designed to evaluate 30-feature UCI structural profiles.
    Includes Batch Normalization and Dropout for regularization on tabular data.
    """

    def __init__(self, input_dim):
        super(PhishingANN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # BCEWithLogitsLoss expects raw logits, so no sigmoid is applied at the output layer.
        return self.network(x)
