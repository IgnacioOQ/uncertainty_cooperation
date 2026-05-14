"""Decaying-epsilon-greedy and UCB agents for the Stag Hunt."""

import numpy as np

from src.stag_hunt.env import ACTIONS


class DecayingEpsilonGreedyAgent:
    def __init__(self, epsilon_start=1.0, decay_rate=0.005, alpha=0.1):
        self.q_values = np.zeros(2)  # [Q(Stag), Q(Hare)]
        self.epsilon = epsilon_start
        self.decay_rate = decay_rate
        self.alpha = alpha  # Learning rate
        self.t = 0

    def select_action(self):
        self.t += 1
        # Decay epsilon
        current_epsilon = self.epsilon / (1 + self.decay_rate * self.t)

        if np.random.random() < current_epsilon:
            return np.random.choice(ACTIONS)
        else:
            # Break ties randomly to avoid defaulting to index 0 always
            max_q = np.max(self.q_values)
            best_actions = [a for a, q in enumerate(self.q_values) if q == max_q]
            return np.random.choice(best_actions)

    def update(self, action, reward):
        # Standard Q-learning update
        self.q_values[action] += self.alpha * (reward - self.q_values[action])


class UCBAgent:
    def __init__(self, c=2.0):
        self.q_values = np.zeros(2)  # Average reward
        self.counts = np.zeros(2)    # N_t(a)
        self.c = c                   # Exploration parameter
        self.t = 0

    def select_action(self):
        self.t += 1
        # Initialization: If an arm hasn't been pulled, pull it (standard UCB logic)
        for a in ACTIONS:
            if self.counts[a] == 0:
                return a

        # UCB Calculation
        ucb_values = self.q_values + self.c * np.sqrt(np.log(self.t) / self.counts)

        # Select max (break ties randomly)
        max_val = np.max(ucb_values)
        best_actions = [a for a, v in enumerate(ucb_values) if v == max_val]
        return np.random.choice(best_actions)

    def update(self, action, reward):
        self.counts[action] += 1
        n = self.counts[action]
        # Incremental average update
        self.q_values[action] += (1 / n) * (reward - self.q_values[action])
