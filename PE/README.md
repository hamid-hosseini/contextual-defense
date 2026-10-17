# Grid pursuit-evasion

Code for the pursuit-evasion benchmark (Table 2, PE column) and the episode-outcome table.

## Benchmark

A pursuer (the defender) chases an evader (the attacker) on a 6 × 6 grid for at most 40 rounds. Both move simultaneously. Capture, meaning the same cell or the two players swapping cells, ends the episode. The evader wins by standing on its exit, uncaptured, at the horizon.

The pursuer's payoff, with the game zero sum:
- +4 for a capture off the exit, and +2 for a capture on it,
- −4 if the evader escapes,
- otherwise a small distance-shaping term.

Each episode draws a latent context:
- **Obstacle layout:** one of 20 four-cell patterns of walls, blocks, and corner chokepoints. Unknown to both players.
- **Exit:** one of the four corners. Known only to the evader.

The pursuer observes its own position and a signal placing the evader in a random 2 × 2 block containing it, summarized by a Bayes filter over the evader's cell.

## Notebooks

| Notebook | What it does | Writes |
|---|---|---|
| `Initialize.ipynb` | Environment, latent context, representation (a Bayes-filter state component and a Transformer context component), stage-game solver, networks, training updates, baseline architectures, and defender wrappers. | nothing |
| `main.ipynb` | Trains our method from scratch and records how many environment steps it used. | `encoder.pth`, `critic.pth`, `player1.pth`, `player2.pth`, `main_budget.json` |
| `baselines.ipynb` | Trains R-PPO, DR-RPPO, VariBAD, PEARL, and MMD until each has used the step count in `main_budget.json`. | `compared/<baseline>.pth` |
| `best_response.ipynb` | Trains a recurrent-PPO best-response evader against each frozen pursuer. | `compared/BR_attacker_<pursuer>.pth`, `br_curves.jpg` |
| `eval.ipynb` | Evaluates every pursuer against the four evaders and prints the worst-case return and exploitability. | nothing (prints the table) |
| `outcomes.ipynb` | Capture, off-exit capture, and escape rates and the mean capture time against the trained evader. | nothing (prints the table) |

Run order: `main.ipynb`, `baselines.ipynb`, `best_response.ipynb`, then `eval.ipynb` and `outcomes.ipynb`. `baselines.ipynb` needs the `main_budget.json` that `main.ipynb` writes.

## Budgets and seeds

| Component | Budget | Seed |
|---|---|---|
| Our method | 5,000 episodes; episodes end at capture, so the step count varies and is saved to `main_budget.json` | 20 |
| Each baseline | the same number of environment steps as our method | 101 to 505 |
| Each best-response evader | 1,000 episodes, the same for every pursuer | 777 to 784 |
| Evaluation | 200 episodes, configurations drawn with seed 12345, episode seeds 1000 to 1199 | |
| Episode outcomes | 250 episodes, episode seeds 2000 to 2249 | |

Returns are discounted with γ = 0.99.
