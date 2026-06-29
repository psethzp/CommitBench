# Shared-Proposal V2 Canonical Summary

This is the Stage 2 paired-proposal fairness audit. Every system consumes the same frozen BASE model proposal for each task/model/regime/seed; no GPU and no new model calls were used.

| Gate / Metric | Value |
|---|---:|
| Shared proposal groups | 7,168 |
| Trace rows | 21,504 |
| Proposal-action equality groups | 7,168 / 7,168 |
| Canonical gate passed | True |
| Enumerated candidates | 1,205,248 |
| Unexplained mismatches | 0 |
| No-oracle rows checked | 21,504 |
| No-oracle failures | 0 |

| System | Trajectories | Raw success | Strict excess | Kernel success |
|---|---:|---:|---:|---:|
| `BASE` | 7,168 | 100.0000% | 57.0033% (4,086) | 42.9967% (3,082) |
| `PROJ_GUARD_V2` | 7,168 | 100.0000% | 9.1657% (657) | 90.8343% (6,511) |
| `EFFECTGUARD_V2` | 7,168 | 100.0000% | 0.0000% (0) | 100.0000% (7,168) |

## Caveat

The audit replays BASE proposals generated before the no-system prompt fix, so it tests guard-comparison proposal sharing rather than the distribution of a fresh no-system prompt.

Future model-call runs now omit the `system=` field from proposal prompt user content in `effectbench_omega/scripts/run_online.py`.
