"""Two-arm Stag Hunt payoff matrix used by the egreedy-vs-UCB comparison."""

STAG_PAYOFF = 5       # High reward (Cooperation)
HARE_PAYOFF = 1       # Safe reward (Defection)
SUCKER_PAYOFF = 0     # Penalty if you hunt Stag alone
TEMPTATION_PAYOFF = 3 # Reward if you hunt Hare while other hunts Stag

STAG = 0
HARE = 1
ACTIONS = [STAG, HARE]
ACTION_NAMES = ["Stag", "Hare"]


class StagHuntGame:
    def get_payoffs(self, action_a, action_b):
        """
        Returns (payoff_a, payoff_b)
        Matrix:
                    B:Stag    B:Hare
        A:Stag      (5,5)     (0,3)
        A:Hare      (3,0)     (1,1)
        """
        if action_a == STAG and action_b == STAG:
            return STAG_PAYOFF, STAG_PAYOFF
        elif action_a == STAG and action_b == HARE:
            return SUCKER_PAYOFF, TEMPTATION_PAYOFF
        elif action_a == HARE and action_b == STAG:
            return TEMPTATION_PAYOFF, SUCKER_PAYOFF
        else:  # HARE, HARE
            return HARE_PAYOFF, HARE_PAYOFF
