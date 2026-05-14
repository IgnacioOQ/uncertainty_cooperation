# Strand 4 — Deep Ensemble Models

## Question

When point estimates are replaced by a deep ensemble's predictive distribution, can the ensemble's *epistemic* uncertainty drive the same UCB-style cooperation in high-dimensional state spaces — where no tabular Q-table is feasible?

## Files

- [`uncertainty_estimation_sandbox.ipynb`](uncertainty_estimation_sandbox.ipynb) — the method, in isolation. A 1-D regression on noisy sinusoidal data with a deliberate gap in the training range, comparing MC-Dropout against a deep ensemble of independently-initialised regressors. The point of the gap is to check that the ensemble reports high variance where it has no data — the property that any UCB-style exploration term depends on.
- [`deep_ensemble_polluted_river.ipynb`](deep_ensemble_polluted_river.ipynb) — the method, in the dilemma. The Polluted River MDP from Strand 3 is now solved by a deep Q-ensemble using **randomized prior functions** (Osband et al.) plus a UCB-style intrinsic bonus on the ensemble standard deviation, compared against ε-greedy and softmax DQN baselines.

## Connection to the paper

Section 3.3 of [`../notes/paper_outline.docx`](../notes/paper_outline.docx). The deep-ensemble agent is the high-dimensional generalisation of the tabular UCB learner studied in Strand 2: the ensemble standard deviation plays the role of the tabular confidence radius.

The Polluted River environment and the agent classes are duplicated with [`../03_sequential_games_ucb/polluted_river_public_goods.ipynb`](../03_sequential_games_ucb/polluted_river_public_goods.ipynb); a shared-module refactor is tracked in `TODO_WORKFLOW.md`.
