# Strand 3 — Sequential Games with RL and UCB

## Question

Does the UCB-cooperation result survive when the dilemma is no longer one-shot — when it lives inside an MDP with temporal credit assignment? A sequential public-goods task lets us check whether optimism still pays once an agent has to *plan*, not just *choose*.

## Files

- [`polluted_river_public_goods.ipynb`](polluted_river_public_goods.ipynb) — a "Polluted River" cleanup game: agents may eat apples (immediate reward) or clean the river (immediate cost, future common benefit). The river has carrying capacity that the agents can collectively exceed. The notebook implements the environment and a deep Q-ensemble agent with randomized prior functions, alongside ε-greedy and softmax DQN baselines, and tracks a "temptation gap" metric over training.

## Connection to the paper

Bridges Strands 2 and 4: the same UCB-versus-stochastic-exploration question, but in an MDP where the cost of cleaning is **immediate** and the benefit is **delayed**. This is where the discount factor (`GAMMA`) starts to interact with the form of exploration — see the in-notebook commentary on the "time telescope."

The same environment is also used by the deep-ensemble study in [`../04_deep_ensembles/deep_ensemble_polluted_river.ipynb`](../04_deep_ensembles/deep_ensemble_polluted_river.ipynb); see `TODO_WORKFLOW.md` for the planned shared-module refactor.
