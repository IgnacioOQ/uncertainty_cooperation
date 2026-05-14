"""Q-network and replay buffer for the Polluted-River deep RL agents."""

import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn


class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim, prior_bias=0.0, use_rpf=True, prior_scale=3.0):
        super(QNetwork, self).__init__()
        self.use_rpf = use_rpf
        self.prior_scale = prior_scale

        # Trainable Network
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )
        self._init_weights(self.net, prior_bias)

        # Prior Network (Only used if RPF is enabled)
        if self.use_rpf:
            self.prior_net = nn.Sequential(
                nn.Linear(state_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, action_dim),
            )
            self._init_weights(self.prior_net, bias=0.0)
            for param in self.prior_net.parameters():
                param.requires_grad = False

    def _init_weights(self, module, bias):
        for m in module.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
        nn.init.constant_(module[-1].bias, bias)

    def forward(self, x):
        val = self.net(x)
        if self.use_rpf:
            val += self.prior_scale * self.prior_net(x)
        return val


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        return (np.array(state), np.array(action), np.array(reward),
                np.array(next_state), np.array(done))

    def __len__(self):
        return len(self.buffer)
