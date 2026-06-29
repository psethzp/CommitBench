# Stage 4 Leave-One Robustness

This audit is fully offline. It uses saved traces and canonical enumerated-frontier certificates only.

## Gate Summary

| Split | Drop type | Failing base-gap slices | Failing projection slices | Failing EffectGuard-zero slices |
|---|---|---:|---:|---:|
| `corrected_guard_v2` | `drop_family` | 0 | 0 | 0 |
| `corrected_guard_v2` | `drop_model` | 0 | 0 | 0 |
| `corrected_guard_v2` | `none` | 0 | 0 | 0 |
| `main_controlled_legacy_guards` | `drop_family` | 0 | 0 | 0 |
| `main_controlled_legacy_guards` | `drop_model` | 0 | 0 | 0 |
| `main_controlled_legacy_guards` | `none` | 0 | 0 | 0 |
| `native_validation` | `drop_family` | 0 | 0 | 0 |
| `native_validation` | `drop_model` | 0 | 0 | 0 |
| `native_validation` | `none` | 0 | 0 | 0 |
| `shared_proposal_v2` | `drop_family` | 0 | 0 | 0 |
| `shared_proposal_v2` | `drop_model` | 0 | 0 | 0 |
| `shared_proposal_v2` | `none` | 0 | 0 | 0 |
| `shared_proposal_v3_nosystem` | `drop_family` | 0 | 0 | 0 |
| `shared_proposal_v3_nosystem` | `drop_model` | 0 | 0 | 0 |
| `shared_proposal_v3_nosystem` | `none` | 0 | 0 | 0 |

## Stress Summary

| Metric | Value |
|---|---:|
| `available` | True |
| `trace_count` | 3072 |
| `canonical_strict_excess` | 0 |
| `necessary_high_effectguard_decisions` | 704 |
| `incomparable_effectguard_decisions` | 320 |
| `minimal_with_incomparables` | 960 |

Detailed per-system metrics are in `effectbench_omega/tables/stage4_leave_one_metrics.csv`.
Detailed gate rows are in `effectbench_omega/tables/stage4_leave_one_gates.csv`.
