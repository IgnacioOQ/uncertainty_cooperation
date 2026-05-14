"""Bandit environment used by the Q-value initialisation sweep."""


class BanditEnvironment:
    def __init__(self, num_arms, num_contexts, game):
        self.game = game
        self.num_arms = num_arms
        self.num_contexts = num_contexts
        self.timestep = 0
        self.action_translation = {0: 'cooperate', 1: 'defect'}

    def get_reward_single_game(self, p1_choice, p2_choice):
        self.timestep += 1
        p1_reward = self.game[p1_choice][p2_choice]
        p2_reward = self.game[p2_choice][p1_choice]
        return p1_reward, p2_reward
