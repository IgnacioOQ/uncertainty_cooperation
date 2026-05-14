"""Polluted-River agents: Ensemble (UCB / Maximax), epsilon-greedy, and softmax DQN.

The Ensemble agent supports both notebook 03 (always-UCB) and notebook 04
(`use_maximax` toggle) via a constructor flag.
"""

import copy

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from src.polluted_river.networks import QNetwork, ReplayBuffer


class EnsembleAgent:
    def __init__(
        self,
        state_dim,
        action_dim,
        agent_id,
        device,
        num_models=5,
        lr=5e-4,
        gamma=0.999,
        batch_size=64,
        buffer_size=10000,
        target_update_freq=10,
        prior_bias=-2.0,
        prior_scale=3.0,
        ucb_beta_start=5.0,
        ucb_beta_min=0.1,
        ucb_beta_decay=0.995,
        use_maximax=False,
    ):
        self.agent_id = agent_id
        self.name = f"Ensemble_{agent_id}"
        self.device = device
        self.num_models = num_models
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.use_maximax = use_maximax

        # Beta Decay State
        self.beta = ucb_beta_start
        self.beta_min = ucb_beta_min
        self.beta_decay = ucb_beta_decay

        # PESSIMISTIC INITIALIZATION
        priors = [prior_bias] * num_models

        self.models = [
            QNetwork(state_dim, action_dim, prior_bias=p, use_rpf=True, prior_scale=prior_scale).to(device)
            for p in priors
        ]

        self.target_models = [copy.deepcopy(m) for m in self.models]
        for tm in self.target_models:
            tm.eval()

        self.optimizers = [optim.Adam(model.parameters(), lr=lr) for model in self.models]
        self.criterion = nn.MSELoss()
        self.buffer = ReplayBuffer(buffer_size)

        self.train_steps = 0
        self.reset_diagnostics()

    def reset_diagnostics(self):
        self.action_stats = {a: {'q': [], 'std': []} for a in range(4)}

    def get_action(self, state):
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_list = []
        with torch.no_grad():
            for model in self.models:
                q_list.append(model(state_t).cpu().numpy())

        q_ens = np.vstack(q_list)
        q_mean = np.mean(q_ens, axis=0)
        q_std = np.std(q_ens, axis=0)

        for a in range(4):
            self.action_stats[a]['q'].append(q_mean[a])
            self.action_stats[a]['std'].append(q_std[a])

        if self.use_maximax:
            # Maximax: Select the action with the highest Q-value predicted by ANY ensemble member
            q_max = np.max(q_ens, axis=0)
            return np.argmax(q_max), np.mean(q_std)
        else:
            # UCB Rule: Optimism in the face of Uncertainty (Mean + Beta * Std)
            ucb_values = q_mean + self.beta * q_std
            return np.argmax(ucb_values), np.mean(q_std)

    def update(self):
        if len(self.buffer) < self.batch_size:
            return
        self.train_steps += 1

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards_t = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        for i in range(self.num_models):
            model = self.models[i]
            target_model = self.target_models[i]
            opt = self.optimizers[i]

            curr_q = model(states_t).gather(1, actions_t)
            with torch.no_grad():
                next_q = target_model(next_states_t).max(1)[0].unsqueeze(1)
                target_q = rewards_t + (self.gamma * next_q * (1 - dones_t))

            loss = self.criterion(curr_q, target_q)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

        if self.train_steps % (self.target_update_freq * 10) == 0:
            self.update_targets()

    def update_targets(self):
        for i in range(self.num_models):
            self.target_models[i].load_state_dict(self.models[i].state_dict())

    def decay_beta(self):
        self.beta = max(self.beta_min, self.beta * self.beta_decay)


class EpsilonGreedyAgent:
    def __init__(
        self,
        state_dim,
        action_dim,
        agent_id,
        device,
        lr=5e-4,
        gamma=0.999,
        batch_size=64,
        buffer_size=10000,
        target_update_freq=10,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.96,
    ):
        self.agent_id = agent_id
        self.name = f"EGreedy_{agent_id}"
        self.device = device
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        # Standard Init (No RPF, Neutral Bias)
        self.model = QNetwork(state_dim, action_dim, prior_bias=0.0, use_rpf=False).to(device)
        self.target_model = copy.deepcopy(self.model)
        self.target_model.eval()

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.buffer = ReplayBuffer(buffer_size)

        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.train_steps = 0

    def get_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(4), 0.0

        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_t)
        return torch.argmax(q_values).item(), 0.0

    def update(self):
        if len(self.buffer) < self.batch_size:
            return
        self.train_steps += 1

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        curr_q = self.model(states).gather(1, actions)
        with torch.no_grad():
            # Target Network for stability
            next_q = self.target_model(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + (self.gamma * next_q * (1 - dones))

        loss = self.criterion(curr_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()

        # Target Sync
        if self.train_steps % (self.target_update_freq * 10) == 0:
            self.update_targets()

    def update_targets(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


class SoftmaxAgent:
    def __init__(
        self,
        state_dim,
        action_dim,
        agent_id,
        device,
        lr=5e-4,
        gamma=0.999,
        batch_size=64,
        buffer_size=10000,
        target_update_freq=10,
        temp_start=5.0,
        temp_min=0.1,
        temp_decay=0.96,
    ):
        self.agent_id = agent_id
        self.name = f"Softmax_{agent_id}"
        self.device = device
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        # Standard Init (No RPF)
        self.model = QNetwork(state_dim, action_dim, prior_bias=0.0, use_rpf=False).to(device)
        self.target_model = copy.deepcopy(self.model)
        self.target_model.eval()

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.buffer = ReplayBuffer(buffer_size)

        self.temperature = temp_start
        self.temp_min = temp_min
        self.temp_decay = temp_decay
        self.train_steps = 0

    def get_action(self, state):
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_t)

        probs = F.softmax(q_values / self.temperature, dim=1)
        action = torch.multinomial(probs, 1).item()

        return action, 0.0

    def update(self):
        if len(self.buffer) < self.batch_size:
            return
        self.train_steps += 1

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        curr_q = self.model(states).gather(1, actions)
        with torch.no_grad():
            # Target Network
            next_q = self.target_model(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + (self.gamma * next_q * (1 - dones))

        loss = self.criterion(curr_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()

        # Target Sync
        if self.train_steps % (self.target_update_freq * 10) == 0:
            self.update_targets()

    def update_targets(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_temperature(self):
        self.temperature = max(self.temp_min, self.temperature * self.temp_decay)
