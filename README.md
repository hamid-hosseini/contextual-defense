# Contextual defenses against strategic adversaries

Code for learning defenses in zero-sum partially observable games whose dynamics, observations, payoffs, and attacker are shaped by a latent context hidden from the defender. The defender acts on a nested representation: a state component that tracks the fast-moving state, and a context component, a Transformer over its action-observation history trained with a Soft-InfoNCE contrastive objective, that identifies the context. A centralized minimax critic and both players' actors are trained jointly with it under centralized training and decentralized execution.

Each defense is evaluated by its empirical exploitability: its worst-case return against a suite of admissible attackers, including a recurrent-PPO best response trained from scratch against that defense.

## Benchmarks

| Folder | Benchmark | Results |
|---|---|---|
| [`AG/`](AG/) | Attack graph: 8 hosts and 2 servers, hidden wiring, attacker with hidden objectives and irrationality. Also the encoder ablation and AG-mini, an exactly solvable reduction used to check the exploitability bound. | Table 2 (AG), Table 3, Figure 1 |
| [`Blotto/`](Blotto/) | Dynamic Colonel Blotto: 4 troops over 5 towns for 50 rounds, with hidden responsiveness, valuations, and reachability. | Table 2 (BLT) |
| [`PE/`](PE/) | Grid pursuit-evasion: a 6 × 6 grid with a hidden obstacle layout and a hidden exit. | Table 2 (PE) |
| [`CAGE2/`](CAGE2/) | CAGE-2 network defense, through a reduced interface on the CybORG simulator, with hidden attacker targets, head start, and Impact disruption. | Figure 2 |

Every folder is self-contained: an `Initialize.ipynb` that the other notebooks run first, a `main.ipynb` that trains our method, `baselines.ipynb` for R-PPO, DR-RPPO, VariBAD, PEARL (not on CAGE-2), and MMD, `best_response.ipynb` for the per-defense best-response attackers, and `eval.ipynb` for the evaluation. Each folder's README gives its benchmark, run order, budgets, and seeds.

## Setup

Python 3.10 or later:

```bash
pip install -r AG/requirements.txt      # the same packages serve every folder
pip install -e CAGE2/CybORG             # only for CAGE2/
jupyter notebook
```

Run each folder's notebooks from inside that folder. A GPU is optional.

## Shared evaluation protocol

Each frozen defender plays the same pre-drawn episodes against four admissible attackers: the trained attacker, a myopic best response to the defender's mixed action under the critic, the critic's stage-game equilibrium attacker, and a recurrent-PPO best response trained from scratch against that defender. Defenders sample from their own action distributions, as at deployment. A defender's worst-case return is its lowest mean discounted return over the four attackers, and its empirical exploitability is the gap to the best worst-case return among the evaluated defenders. Every baseline trains for the same number of environment steps as our method.

## License

MIT, see [`LICENSE`](LICENSE). `CAGE2/CybORG/` is a copy of the CybORG simulator from the CAGE Challenge 2 repository and keeps its own MIT license (`CAGE2/CybORG/LICENSE.txt`).
