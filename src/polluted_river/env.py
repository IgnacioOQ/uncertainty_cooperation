"""Polluted-River cleanup environment.

Shared between strands 3 (sequential public-goods) and 4 (deep-ensemble DQN).
The two notebooks use different physics constants and different episode horizons,
so all of them are constructor arguments. Defaults match notebook 03
(`polluted_river_public_goods.ipynb`); notebook 04 overrides them explicitly.
"""

import numpy as np


class PollutedRiverEnv:
    """A 'Cleanup' game simulating a public-goods / volunteer's-dilemma.

    OBSERVATION SPACE (per agent):
    1. Local apples: is there food in my immediate vicinity (`window_size`)?
    2. Local agents: who is near me?
       - Values: 1.0 (Neutral), 0.5 (Harvesting/Grit), -1.0 (Cleaning/Glow).
    3. Global pollution: float in [0, 1]. Everyone sees the same number.
    4. Global signal: did ANYONE clean last turn? (1.0 or 0.0).

    ACTIONS: 0 Left, 1 Right, 2 Eat, 3 Clean.
    """

    def __init__(
        self,
        map_size=20,
        window_size=5,
        n_agents=2,
        max_steps=150,
        pollution_per_eat=0.05,
        natural_decay=0.025,
        clean_reduction=0.10,
        clean_cost=0.05,
    ):
        self.map_size = map_size
        self.window_size = window_size
        self.n_agents = n_agents
        self.max_steps = max_steps

        self.state_dim = (window_size * 2 + 1) * 2 + 2
        self.action_dim = 4  # 0 Left, 1 Right, 2 Eat, 3 Clean
        self.agents = [0, self.map_size - 1]
        self.apples = np.ones(self.map_size)
        self.pollution = 0.0
        self.last_actions = [None] * n_agents
        self.someone_cleaned_last_turn = 0.0

        self.POLLUTION_PER_EAT = pollution_per_eat
        self.NATURAL_DECAY = natural_decay
        self.CLEAN_REDUCTION = clean_reduction
        self.CLEAN_COST = clean_cost

    def reset(self):
        self.agents = [0, self.map_size - 1]
        self.apples = np.ones(self.map_size)
        self.pollution = 0.0
        self.steps = 0
        self.last_actions = [None] * self.n_agents
        self.someone_cleaned_last_turn = 0.0
        return self._get_obs()

    def _get_obs(self):
        obs_n = []
        for i, pos in enumerate(self.agents):
            padded_apples = np.pad(self.apples, self.window_size, 'constant', constant_values=0)
            agent_map = np.zeros(self.map_size)
            for j, other_pos in enumerate(self.agents):
                if i != j:
                    signal = 1.0
                    if self.last_actions[j] is not None:
                        if self.last_actions[j] == 3:
                            signal = -1.0
                        elif self.last_actions[j] == 2:
                            signal = 0.5
                    agent_map[other_pos] = signal

            padded_agents = np.pad(agent_map, self.window_size, 'constant', constant_values=0)
            view_start = pos
            view_end = pos + (self.window_size * 2) + 1
            b_view = padded_apples[view_start:view_end]
            a_view = padded_agents[view_start:view_end]
            g_view = np.array([self.pollution, self.someone_cleaned_last_turn])

            obs_n.append(np.concatenate([b_view, a_view, g_view]))
        return np.array(obs_n)

    def step(self, actions):
        rewards = [0.0, 0.0]
        cleaned_counts = [0, 0]
        self.steps += 1
        self.last_actions = actions
        self.someone_cleaned_last_turn = 0.0

        for i, action in enumerate(actions):
            if action == 0:
                self.agents[i] = max(0, self.agents[i] - 1)
            elif action == 1:
                self.agents[i] = min(self.map_size - 1, self.agents[i] + 1)
            elif action == 2:
                pos = self.agents[i]
                if self.apples[pos] > 0:
                    self.apples[pos] = 0
                    rewards[i] += 1.0
                    self.pollution = min(1.0, self.pollution + self.POLLUTION_PER_EAT)
            elif action == 3:
                self.pollution = max(0.0, self.pollution - self.CLEAN_REDUCTION)
                rewards[i] -= self.CLEAN_COST
                cleaned_counts[i] = 1
                self.someone_cleaned_last_turn = 1.0

        if self.pollution > 0:
            self.pollution = max(0.0, self.pollution - self.NATURAL_DECAY)

        spawn_prob = 0.20 * (1.0 - self.pollution)
        if spawn_prob > 0:
            for x in range(self.map_size):
                if self.apples[x] == 0:
                    if np.random.rand() < spawn_prob:
                        self.apples[x] = 1

        done = self.steps >= self.max_steps
        return self._get_obs(), rewards, done, cleaned_counts
