# EACL Rescue Paper-Ready Summary

Recommended paper posture:

> EffectBench-Omega introduces Effect Kernel certificates for tool-agent
> traces. In local open-weight experiments, final-state success
> substantially overstates certified least-effect success. Projection-only
> safeguards reduce but do not remove strict excess, while the no-oracle
> EffectGuard reference controller reduces strict excess under the fixed
> declared effect lattice. A native-fidelity validation block and full
> certificate replay support the auditability claim.

Use these main numbers:

| Claim | Value | Source |
|---|---:|---|
| Controlled local headline split contains 128 tasks x 7 regimes x 2 seeds x 4 models x 3 systems. | 21504 | `effectbench_omega/tables/frontier_canonical_main_mc_postfix_all_local_canonical.csv` |
| Paper-grade strict-excess labels for the controlled split use enumerated-frontier certificates. | 4089 | `effectbench_omega/tables/frontier_canonical_main_mc_postfix_all_local_canonical.csv` |
| BASE final-state success overstates certified least-effect success in the controlled split. | 57.0033% | `effectbench_omega/tables/main_mc_postfix_all_local_canonical/online_control_main.csv` |
| PROJ_GUARD_V2 leaves residual strict excess. | 7.3242% | `effectbench_omega/tables/guard_v2_main_with_base_all_local_canonical/online_control_main.csv` |
| EFFECTGUARD_V2 removes strict excess in this corrected local split. | 0.0000% | `effectbench_omega/tables/guard_v2_main_with_base_all_local_canonical/online_control_main.csv` |
| Native-fidelity validation block has 48 native tasks x 4 regimes x 2 seeds x 4 models x 3 systems. | 4608 | `effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet` |
| Native-fidelity validation block has counted terminal failures. | 391 | `effectbench_omega/outputs/native_subset_v1_all_local/traces.parquet` |
| Full replay passes for all paper-cited canonical bundles generated in Stage 6. | 11508 | `effectbench_omega/tables/stage6_full_replay_summary.csv` |
| Full replay found no certificate failures. | 0 | `effectbench_omega/tables/stage6_full_replay_summary.csv` |

Figures available:

- `effectbench_omega/figures/main_mc_postfix_all_local_canonical/`
- `effectbench_omega/figures/guard_v2_main_with_base_all_local_canonical/`
- `effectbench_omega/figures/native_subset_v1_all_local_canonical/`

Required limitations:

- Local/open-weight only; no frontier or Bedrock leaderboard.
- Controlled adapter headline split has 100% raw success; use it for least-effect certification, not task-difficulty claims.
- Native-fidelity subset is compact and source-backed, not a full upstream server re-host.
- Projection baselines are deterministic projection baselines, not faithful reproductions of every named SOTA system.
- Lattice sensitivity is appendix/diagnostic only in this rescue package.
- No human-eval claim.
