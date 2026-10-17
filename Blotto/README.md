# Dynamic Colonel Blotto

Code for the dynamic Colonel Blotto benchmark (Table 2, BLT column) and the appendix figure on contested-town control.

## Benchmark

A defender and an attacker each allocate B = 4 troop units over N = 5 towns every round (70 allocations each) for 50 rounds. The state is the defender's control of each town, in [0, 1]. Each round, town i moves toward σ(2.5 (a_i − u_i)) with mixture weight ρ_i, through a Beta transition. The defender earns the value-weighted control ⟨w, x_{k+1}⟩, and the game is zero sum.

Each episode draws a latent context θ = (ρ, w, R):
- **Responsiveness** ρ_i ∈ {0.1, 0.9}: unknown to both players.
- **Valuations** w: three valued towns with weights 0.15, 0.30, and 0.55. Known only to the attacker.
- **Reachability** R: the three towns the attacker may strike. Known only to the attacker, and it restricts the attacker's admissible allocations.

The defender observes only its own allocations and a noisy reading of its control (Gaussian noise, standard deviation 0.05).

## Notebooks

| Notebook | What it does | Writes |
|---|---|---|
| `Initialize.ipynb` | Environment, latent context, representation (a GRU state component and a Transformer context component), stage-game solvers, networks, training updates, baseline architectures, and defender wrappers. | nothing |
| `main.ipynb` | Trains our method from scratch: encoder, state GRU, centralized critic, and both actors. | `encoder.pth`, `z_s_enc.pth`, `critic.pth`, `player1.pth`, `player2.pth` |
| `baselines.ipynb` | Trains R-PPO, DR-RPPO, VariBAD, PEARL, and MMD with the same budget as our method. | `compared/<baseline>.pth` |
| `best_response.ipynb` | Trains a recurrent-PPO best-response attacker against each frozen defender. | `compared/BR_attacker_<defender>.pth`, `br_curves.jpg` |
| `eval.ipynb` | Evaluates every defender against the four attackers and prints the worst-case return and exploitability. | nothing (prints the table) |
| `control.ipynb` | Weight-averaged control of the contested towns (valued and reachable) against the trained attacker. | `appendix_control.jpg` |

Run order: `main.ipynb`, `baselines.ipynb`, `best_response.ipynb`, then `eval.ipynb` and `control.ipynb`.

## Budgets and seeds

| Component | Budget | Seed |
|---|---|---|
| Our method | 10,000 episodes × 50 rounds = 500,000 environment steps | 20 |
| Each baseline | 10,000 episodes × 50 rounds = 500,000 environment steps | 101 to 505 |
| Each best-response attacker | 5,000 episodes × 50 rounds, the same for every defender | 777 to 784 |
| Evaluation | 500 episodes, contexts drawn with seed 12345, episode seeds 1000 to 1499 | |
| Contested control | 100 episodes per case, contexts drawn with seeds 2026 and 2027, episode seeds from 2000 | |

Returns are discounted with γ = 0.95. The critic's bootstrap value uses batched regret matching (200 iterations) over the attacker's admissible allocations, within about 0.05% of the exact linear program on 70-action games. The actors' equilibrium targets use the exact linear program.
