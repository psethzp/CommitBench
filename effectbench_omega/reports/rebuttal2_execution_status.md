# Rebuttal 2 Execution Status

Status: `complete`
Pipeline job: `rebuttal2_pipeline_20260629T054550Z`
Queue job: `rebuttal2_base_nosystem_v1_20260629T054550Z`

| Check | Value |
|---|---:|
| Full stress replay bundles | 3072 |
| Full stress replay failures | 0 |
| Fresh no-system shared traces | 21504 |
| Fresh no-system complete shared groups | 7168 |
| Fresh no-system unexplained mismatches | 0 |
| Stage 4 gate rows | 49 |
| Stage 4 base-gap failures | 0 |
| Stage 4 projection failures | 0 |
| Stage 4 EffectGuard-zero failures | 0 |

## Fresh No-System Online Control

| System | Strict excess / success | Raw success |
|---|---:|---:|
| `BASE` | 0.5620814732142857 | 1.0 |
| `EFFECTGUARD_V2` | 0.0 | 1.0 |
| `PROJ_GUARD_V2` | 0.0849609375 | 1.0 |

## Artifacts

- Full stress replay: `effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md`
- Fresh BASE split: `effectbench_omega/outputs/base_nosystem_v1_all_local/`
- Fresh shared proposal split: `effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/`
- Fresh canonical report: `effectbench_omega/reports/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.md`
- Refreshed leave-one robustness: `effectbench_omega/reports/stage4_leave_one_robustness.md`
