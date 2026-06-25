# Stage 6 Full Replay And Targeted CEGAR Stress

## Full Replay

| Split | Bundles checked | Native replays | Failures |
|---|---:|---:|---:|
| `main_mc_postfix_all_local_canonical` | 4,819 | 0 | 0 |
| `guard_v2_main_with_base_all_local_canonical` | 5,341 | 0 | 0 |
| `native_subset_v1_all_local_canonical` | 1,348 | 1,348 | 0 |

Total replay bundles checked: 11,508
Total native replays checked: 1,348
Total replay failures: 0

## Targeted CEGAR Stress

| Omitted field | Label-change groups | Rejected abstractions | Affected rows | Reason |
|---|---:|---:|---:|---|
| `outbox` | 29 | 29 | 834 | reduced_hash_label_collision |
| `policy_obligation` | 1 | 1 | 2 | reduced_hash_label_collision |
| `contract_artifact_hash` | 1 | 1 | 2 | reduced_hash_label_collision |
| `virtual_clock` | 1 | 1 | 2 | reduced_hash_label_collision |
| `memory_cache` | 103 | 103 | 2682 | reduced_hash_label_collision |
| `user_visible_exposure` | 83 | 83 | 3822 | reduced_hash_label_collision |
| `compensation_or_payment_hold` | 1 | 1 | 2 | reduced_hash_label_collision |

Interpretation: Stage 6 injects deterministic stress pairs for future-relevant fields. Every target omission now produces at least one label-changing reduced-state collision, including `policy_obligation`, `contract_artifact_hash`, `virtual_clock`, and `compensation_or_payment_hold`, which were quiet in the ordinary scaffold. This supports the paper claim that no-collision CEGAR fields were not exercised there, not globally irrelevant.
