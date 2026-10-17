# Attack graph (AG) and AG-mini

Code for the attack-graph benchmark: the main comparison against baselines (Table 2, AG column), the encoder ablation (Table 3), the target-server compromise curves, and the AG-mini check of the Corollary 1 bound (Figure 1).

## Benchmark

A defender protects eight hosts and two servers (2^10 = 1,024 states) against an attacker. Each round the attacker strikes one host (8 actions) and the defender takes one of seven group-remediation actions, two of which clean a server directly at a cost of 0.1.

Each episode draws a latent context θ:
- **Wiring:** which two of the five terminal hosts lead to the two servers. It is unknown to both players.
- **Attacker type:** which servers the attacker values (at least one), and an irrationality level λ ~ Unif[0, 0.5]. It is known only to the attacker, which acts uniformly at random with probability λ.

The defender sees noisy alerts from both servers and two random hosts per round, with 10% miss and false-alarm rates. Its payoff is 0.1 per uncompromised host, plus each valued server that stays uncompromised, minus the cleaning cost. The game is zero sum.

## Notebooks

| Notebook | What it does | Writes |
|---|---|---|
| `Initialize.ipynb` | Environment, latent context, state filter, stage-game solver, networks, training updates, baseline architectures, and defender wrappers. Every other notebook except `bound.ipynb` runs it first. | nothing |
| `main.ipynb` | Trains our method from scratch: the nested context-state encoder, the centralized critic, and both actors, alternating a representation step on Eq. (3) with a game step. | `encoder.pth`, `critic.pth`, `player1.pth`, `player2.pth` |
| `baselines.ipynb` | Trains R-PPO, DR-RPPO, VariBAD, PEARL, and MMD on the same observation interface and the same interaction budget as our method. | `compared/<baseline>.pth` |
| `best_response.ipynb` | Trains a fresh recurrent-PPO best-response attacker against each frozen defender, under one shared budget. | `compared/BR_attacker_<defender>.pth`, `br_curves.jpg` |
| `eval.ipynb` | Evaluates every defender against four attackers on 200 shared episodes and prints the worst-case return, the empirical exploitability, and the fraction of the Oracle's return recovered. | nothing (prints the table) |
| `compromise.ipynb` | Target-server compromise rate over time for each defender, against the trained attacker with λ = 0. | `Result1.jpg` |
| `ablation.ipynb` | Trains seven variants of the encoder objective in `main.ipynb`'s pipeline, evaluates them, and prints the ablation table. | `ablation_ckpts/` |
| `bound.ipynb` | Self-contained AG-mini experiment: trains a recurrent posterior encoder, then compares the Corollary 1 bound with the measured exploitability at seven checkpoints. | `bound_ckpts/`, `agmini_bound.jpg` |

## Running

Run the notebooks in this order, from this folder:

1. `main.ipynb`
2. `baselines.ipynb`
3. `best_response.ipynb` (needs the outputs of steps 1 and 2)
4. `eval.ipynb` and `compromise.ipynb`

`ablation.ipynb` and `bound.ipynb` are independent of the others and can run at any time. `ablation.ipynb` skips any variant already trained to the full budget; to train variants in parallel, run copies of it with different `TRAIN_VARIANTS`. `bound.ipynb` evaluates existing checkpoints without retraining when `SKIP_TRAINING = True`.

Trained checkpoints are included in this folder, and the evaluation notebooks load them directly: `eval.ipynb`, `compromise.ipynb`, the evaluation part of `ablation.ipynb`, and `bound.ipynb` with `SKIP_TRAINING = True`.

## Evaluation protocol

Each defender plays the same pre-drawn episodes (wiring, attacker type, λ, and initial state) against four admissible attackers:

| Attacker | Description |
|---|---|
| `Trained P2` | the trained attacker from `main.ipynb` |
| `Critic-BR P2` | a myopic best response to the defender's current mixed action under the critic |
| `Equilibrium P2` | the equilibrium column of the critic's stage game |
| `BR-PPO P2` | the recurrent-PPO best response trained against that defender in `best_response.ipynb` |

All four act uniformly at random with probability λ, so they stay admissible. Returns are the defender's discounted payoff (γ = 0.99, 50 rounds), and every defender samples its action from its own distribution, as at deployment. A defender's worst-case return Ŵ is its lowest mean over the four attackers. Its empirical exploitability is Δ̂ = V̂* − Ŵ, where V̂* is the best worst-case return among the evaluated defenders, with standard errors paired over the shared episodes.

The defenders are `Critic P1` (the Oracle, the critic's equilibrium row with privileged access to the state and context), `Trained P1` (our method), the five baselines, and `Random P1` (uniform random).

## Budgets and seeds

| Component | Budget | Seed |
|---|---|---|
| Our method (`main.ipynb`) | 5,000 episodes × 50 steps = 250,000 environment steps | 20 |
| Each baseline (`baselines.ipynb`) | 5,000 episodes × 50 steps = 250,000 environment steps | 101 to 505 |
| Each best-response attacker | 500 episodes × 50 steps, the same for every defender | 777 to 784 |
| Each ablation variant | the same as our method | 20 |
| Evaluation | 200 episodes, configurations drawn with seed 12345, episode seeds 1000 to 1199 | |
| AG-mini | 25,000 training batches of 64 episodes; 1,000 evaluation episodes | 0 (training), 12345 (evaluation) |

## Ablation variants

| Variant | Change from the full method |
|---|---|
| `full` | none: Eq. (3) with the nested z^S / z^Θ split |
| `no_contrastive` | λ_Θ = 0 |
| `binary_infonce` | binary InfoNCE in place of Soft-InfoNCE |
| `raw_param` | Soft-InfoNCE with a raw-parameter distance in place of d̃_Θ |
| `single_encoder` | no split: actor and critic see only the context embedding |
| `no_nextrep` | λ_p = 0 |
| `no_reward` | λ_r = 0 |

Every variant, including `full`, is trained by the same pipeline, seed, and budget, so each row differs from `full` in one factor. The ablation is evaluated against the three attackers that need no per-defender training (the first three above).

## AG-mini

A reduction of the attack graph with four hosts and two servers (64 states) and 48 contexts, small enough for the exact oracle belief to be computed by Bayes filtering. A recurrent encoder with a joint posterior readout is trained by cross-entropy, and at each of seven checkpoints the deployed defender plays QMDP on the learned posterior. The notebook estimates ε_b as the 95th percentile of the total-variation distance between the exact and learned posteriors over on-policy histories, and compares the bound ε_φ + 2R_sp/(1 − γ)² ε_b with the measured exploitability. In AG-mini the attacker's type fixes its response, so each context has a single admissible attacker, and ε_φ = 0 because the deployed policy and the exact-belief reference use the same QMDP rule.

## Requirements

Python 3.10 or later and the packages in `requirements.txt`:

```bash
pip install -r requirements.txt
jupyter notebook
```

A GPU is optional; every notebook falls back to the CPU.
