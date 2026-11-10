# Local validation report

Evaluated using the original `harness/run_eval.py`, `harness/scoring.py` and provided data, without modifying either harness or evaluation file.

| Check | Result |
|---|---:|
| Public practice questions | 40 |
| Practice evaluation overall (present pillars) | **0.9690** |
| Stale-value traps | 0 |
| Answer exceptions | 0 |
| Accuracy pillar | 0.9690 |
| Consistency | 1.0000 (scaled by accuracy in final score) |
| Speed pillar | 1.0000 (scaled by accuracy in final score) |
| p95 answer latency | ~0.02 sec |
| Full 5-snapshot ingest | ~10–11 sec |
| Kit self-test with conflict gold | **1.0000** |
| Synthetic unit tests | 11 passing |

**Interpretation:** The public scorer has no `conflicts_gold.json` for the 40 practice questions, so its displayed final score renormalizes among the available pillars. Conflict detection is separately verified on the kit self-test but cannot be comprehensively graded without hidden gold. One public item lacks both required answer facts and expected source URLs; the published numeric scorer awards no credit to that item even when a substantive answer is returned. Evaluation on the organizers' hidden suite is unknown.

**Reproducibility:** Extract the participant kit outside this repository, copy the `submission` directory next to its `harness` directory, and run the commands from the project README. Do not include or upload any participant website snapshots to GitHub.