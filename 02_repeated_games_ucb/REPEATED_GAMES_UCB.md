# Strand 2 — Reinforcement Learning with UCB in Repeated Social Dilemmas

## Question

In one-shot-payoff repeated games (no temporal credit assignment), why does **deterministic optimism** (UCB) sustain cooperation in social dilemmas while **stochastic exploration** (ε-greedy, softmax) collapses to defection? The mechanism — trembling-hand noise, calcification of decaying ε, and UCB's endogenous knowledge-based decay — is laid out in [`../notes/rl_cooperation.docx`](../notes/rl_cooperation.docx).

## Files

- [`stag_hunt_egreedy_vs_ucb.ipynb`](stag_hunt_egreedy_vs_ucb.ipynb) — a clean two-agent Stag-Hunt comparison: decaying-ε-greedy vs UCB, averaged across many trials. The simplest demonstration of the mechanism.
- [`ucb_testing_cooperation.ipynb`](ucb_testing_cooperation.ipynb) — the broader study. Contextual bandits with type "flags" play repeated matches in the PD, the Stag-Hunt, and Hawk-Dove. The number of types sweeps from full anonymity (one type) to no anonymity (a type per agent). Under ε-greedy and softmax, cooperation degrades as types multiply; under UCB, cooperation is preserved across the whole range.

## Connection to the paper

Sections 1.3 ("Inevitability of Mutual Defection") and 1.4 ("Unaccounted Uncertainty") of [`../notes/paper_outline.docx`](../notes/paper_outline.docx). These notebooks are the central empirical evidence for the headline claim: the *form* of exploration, not just its *magnitude*, determines whether cooperation survives.
