# Cooperation in Social Dilemmas under Uncertainty

This repository accompanies an in-progress paper on **how the representation of uncertainty in an agent's beliefs determines whether cooperation can emerge in social dilemmas**. The headline empirical result — surprising to us — is that learning agents who reason with **upper confidence bounds (UCB)** over their action-value estimates cooperate in the iterated Prisoner's Dilemma, the Stag Hunt, and a sequential public-goods task, while otherwise-identical agents using ε-greedy or softmax exploration converge to mutual defection.

The classical impossibility result (defection is strictly dominant; the unique correlated equilibrium under expected-utility maximisation puts probability one on mutual defection) assumes **point-estimate beliefs and deterministic payoffs**. Relaxing the point-estimate assumption — to credal sets, frequentist interval estimates, or learned predictive distributions — and pairing it with a decision rule that is sensitive to that interval changes the picture. The work here pursues that thesis across four complementary strands.

## Research strands

| # | Strand | Folder | Core question |
|---|---|---|---|
| 1 | Imprecise probabilities & set-point estimations | [`01_imprecise_probabilities/`](01_imprecise_probabilities/IMPRECISE_PROBABILITIES.md) | How does the initial estimate (the prior point in Q-space) determine whether a UCB learner finds the cooperative equilibrium in the iterated PD? |
| 2 | Reinforcement learning with UCB in repeated social dilemmas | [`02_repeated_games_ucb/`](02_repeated_games_ucb/REPEATED_GAMES_UCB.md) | In one-shot-payoff repeated games, why does deterministic optimism (UCB) sustain cooperation where stochastic exploration (ε-greedy, softmax) does not? |
| 3 | Sequential games with RL and UCB | [`03_sequential_games_ucb/`](03_sequential_games_ucb/SEQUENTIAL_GAMES_UCB.md) | Does the result survive when the dilemma is embedded in an MDP with temporal credit assignment (a public-goods cleanup task)? |
| 4 | Deep ensemble models | [`04_deep_ensembles/`](04_deep_ensembles/DEEP_ENSEMBLES.md) | When point estimates are replaced by a deep ensemble's predictive distribution, can the ensemble's epistemic uncertainty drive the same UCB-style cooperation in high-dimensional state spaces? |

## Conceptual framing

Three accompanying notes in [`notes/`](notes/) develop the theory:

- [`paper_outline.docx`](notes/paper_outline.docx) — formal paper outline: correlated equilibria, payoff variance and CVaR, imprecise probabilities (credal sets, Γ-maximin, maximality), confidence-bound choice rules.
- [`rl_cooperation.docx`](notes/rl_cooperation.docx) — the mechanism: the *trembling hand* of ε-greedy, the *calcification* problem of decaying ε, and UCB's endogenous, knowledge-based decay.
- [`game_decomposition.docx`](notes/game_decomposition.docx) — background on game decomposition (zero-sum + cooperative components) used to motivate the choice of test environments.

## Repository map

```
.
├── README.md                          # this file
├── LICENSE                            # MIT
├── HOUSEKEEPING.md                    # repository audit workflow
├── WORKLOG.md                         # append-only session history
├── TODO_WORKFLOW.md                   # cross-session backlog
├── setup.sh                           # bootstrap a .venv and register a Jupyter kernel
├── requirements.txt                   # pinned core deps (no torch)
├── requirements-deep.txt              # core + torch, for strand 4
├── notes/                             # paper outline + research notes (docx)
├── src/                               # extracted classes; notebooks orchestrate, modules define
│   ├── init_study/                    # bandit env + UCB contextual bandit (strand 1)
│   ├── stag_hunt/                     # StagHuntGame, decaying-ε-greedy, UCB (strand 2)
│   ├── polluted_river/                # env, QNetwork, ReplayBuffer, agents (strands 3 & 4)
│   └── uncertainty/                   # MC-Dropout + Deep-Ensemble regressors (strand 4)
├── 01_imprecise_probabilities/
│   ├── IMPRECISE_PROBABILITIES.md
│   └── ucb_initialization_study.ipynb # fine-grained sweep over initial Q-values in PD
├── 02_repeated_games_ucb/
│   ├── REPEATED_GAMES_UCB.md
│   ├── stag_hunt_egreedy_vs_ucb.ipynb # 2-agent Stag-Hunt: decaying-ε-greedy vs UCB
│   └── ucb_testing_cooperation.ipynb  # contextual-bandit anonymity study (PD / Stag-Hunt / Hawk-Dove)
├── 03_sequential_games_ucb/
│   ├── SEQUENTIAL_GAMES_UCB.md
│   └── polluted_river_public_goods.ipynb  # sequential public-goods MDP, tabular UCB & baselines
├── 04_deep_ensembles/
│   ├── DEEP_ENSEMBLES.md
│   ├── uncertainty_estimation_sandbox.ipynb  # MC-Dropout vs deep ensembles on 1-D regression
│   └── deep_ensemble_polluted_river.ipynb    # randomized-prior-function DQN ensemble on the same MDP
└── results/                           # generated figures and logs (gitignored)
```

## Reproducing the experiments

```bash
./setup.sh                  # core deps (tabular notebooks in strands 1, 2, 3)
./setup.sh --with-torch     # core + torch (everything, incl. strand 4 deep ensembles)
source .venv/bin/activate
jupyter lab
```

`setup.sh` creates a `.venv`, installs from pinned `requirements.txt` (or `requirements-deep.txt`), and registers a Jupyter kernel named *Python (uncertainty_cooperation)*. Select that kernel inside each notebook.

Pins were captured on macOS x86_64 / Python 3.10.9. The notebooks are self-contained: each defines its environment, agents, and plotting in a single file. Random seeds are set inside each notebook where determinism matters. The deep-ensemble notebooks (`04_deep_ensembles/`) have historically been run on Google Colab; they will also run locally with `--with-torch`, but training the Polluted-River ensemble on CPU is slow.

## Status

Early research code. Each strand stands on its own; the cross-strand synthesis lives in `notes/paper_outline.docx` and is the next consolidation milestone (tracked in `TODO_WORKFLOW.md`).

## License

[MIT](LICENSE). © 2026 Ignacio Ojea Quintana.
