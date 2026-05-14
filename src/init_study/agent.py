"""Contextual UCB / fallback bandit agent used by the Q-value initialisation sweep."""

import numpy as np


class ContextualBandit:
    def __init__(self, num_arms, num_contexts, explore_param, decay, min_explore, flag, choice_type='ucb', initial_q=0.0):
        self.num_arms = num_arms
        self.num_contexts = num_contexts

        # Initialize Q-values with the sweep parameter
        self.q_table = np.full((num_contexts, num_arms), initial_q)

        self.arm_counts = np.ones((num_contexts, num_arms))
        self.flag = flag
        self.choice_type = choice_type
        self.decay = decay
        self.min_explore = min_explore
        self.explore_param = explore_param
        self.time = 0
        self.UCB_estimation = np.zeros((num_contexts, num_arms))

    def choice(self, context):
        self.time += 1

        if self.choice_type == 'ucb':
            # UCB Calculation
            # Add small epsilon to denominator to avoid division by zero if counts are 0 (though we init at 1)
            confidence = self.explore_param * np.sqrt(np.log(self.time + 1) / (self.arm_counts[context]))
            self.UCB_estimation[context] = self.q_table[context] + confidence

            # Tie-breaking: critical when Q-values are identical (initialization)
            max_val = np.max(self.UCB_estimation[context])
            candidates = np.where(self.UCB_estimation[context] == max_val)[0]
            choice = np.random.choice(candidates)
        else:
            # Fallback (shouldn't be used in this sweep)
            choice = np.random.randint(self.num_arms)

        self.arm_counts[context, choice] += 1
        return choice

    def update(self, context, arm, reward):
        # Standard Q-learning / Average update
        # Q_new = Q_old + (1/N) * (Reward - Q_old)
        alpha = 1.0 / self.arm_counts[context, arm]
        self.q_table[context, arm] += alpha * (reward - self.q_table[context, arm])

        # Decay the exploration parameter (UCB 'c' value)
        self.explore_param = max(self.min_explore, self.explore_param * self.decay)
