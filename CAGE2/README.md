# CAGE-2 network defense

Code for the CAGE-2 case study (Figure 2), on a reduced interface over the CybORG simulator.

## Setup

`CybORG/` is a copy of the CybORG simulator from the CAGE Challenge 2 repository, under its own MIT license (`CybORG/LICENSE.txt`). Install it once, from this folder:

```bash
pip install -e CybORG
pip install -r requirements.txt
```

Then run `check_interface.ipynb`. It plays a scripted red kill chain and every blue action, and prints the simulator's responses, which confirms the interface works before any training.

## Benchmark

The interface covers the user hosts User1 to User4 and the enterprise servers Enterprise0 and Enterprise1:
- **Blue (the defender)** has 15 actions: Sleep, Monitor (four groups), Analyse, Remove, and Restore.
- **Red (the attacker)** has 17 actions over a foothold phase on the user hosts and an enterprise phase that discovers, exploits, escalates, and Impacts its targets.

Each round red moves, then blue. Blue never observes the state; Monitor and Analyse return a partial signal, and the other actions return none.

Each episode draws a latent context:
- **Target weights:** red's normalized weights over the two enterprise hosts. Known only to red.
- **Head start:** h ∈ {0, …, 5} red-only steps before play begins. Known only to red.
- **Impact disruption:** a probability p ∈ {0, 0.5, 1} per enterprise host that Impact fails, with at least one targeted host below 1. Unknown to both players.

Our method trains on a shaped payoff that adds bonuses for informative observations and penalties for idle or redundant actions. Evaluation and the baselines use the physical payoff, the protection of hosts and of the targeted servers.

## Notebooks

| Notebook | What it does | Writes |
|---|---|---|
| `Initialize.ipynb` | Reduced interface, latent context, representation, stage-game solver, networks, training updates, baseline architectures, and defender wrappers. | nothing |
| `check_interface.ipynb` | Manual check of the red and blue actions. | nothing |
| `main.ipynb` | Trains our method from scratch: encoder, centralized critic, and both actors. | `encoder.pth`, `critic.pth`, `player1.pth`, `player2.pth` |
| `baselines.ipynb` | Trains R-PPO, DR-RPPO, VariBAD, and MMD with the same budget as our method. | `compared/<baseline>.pth` |
| `best_response.ipynb` | Trains a recurrent-PPO best-response red against each frozen defender. | `compared/BR_attacker_<defender>.pth`, `br_curves.jpg` |
| `eval.ipynb` | Evaluates every defender against the four attackers; prints the worst-case return, the impacted fraction, and the containment rate, and draws Figure 2. | `cage2.png` |

Run order: `check_interface.ipynb`, `main.ipynb`, `baselines.ipynb`, `best_response.ipynb`, then `eval.ipynb`.

## Budgets and seeds

| Component | Budget | Seed |
|---|---|---|
| Our method | 10,000 episodes × 50 rounds = 500,000 environment steps | 20 |
| Each baseline | 10,000 episodes × 50 rounds = 500,000 environment steps | 101 to 505 |
| Each best-response red | 1,000 episodes, the same for every defender | 777 to 782 |
| Evaluation | 200 contexts drawn with seed 12345, episode seeds 1000 to 1199 | |

Returns are discounted with γ = 0.98. In evaluation, red's head start is played by the trained red for every attacker. The impacted fraction is the target-weighted fraction of rounds with Impact active, under the defender's worst-case attacker.
