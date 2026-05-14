# Strand 1 — Imprecise Probabilities & Set-Point Estimations

## Question

When an agent's belief about a stranger's behaviour is a *single point* in Q-space, where does that point have to be for an optimistic learner (UCB) to find the cooperative equilibrium in the iterated Prisoner's Dilemma? This is the operational version of the imprecise-probability question: a set of beliefs collapses to a point estimate, and we sweep the point.

## Files

- [`ucb_initialization_study.ipynb`](ucb_initialization_study.ipynb) — fine-grained sweep over the initial Q-value used to seed a contextual-bandit UCB learner playing the PD, with the cooperation rate as a function of that seed. The classes `BanditEnvironment` and `ContextualBandit` are local to this notebook.

## Connection to the paper

Section 2.3 ("Frequentist Interval Estimates") and Section 3.3 ("Confidence Bounds and Risk Minimization") of [`../notes/paper_outline.docx`](../notes/paper_outline.docx). The initialisation sweep is the empirical handle on the "what does the agent assume before any evidence arrives?" question that distinguishes a credal-set agent from a point-estimate agent.
