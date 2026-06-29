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
| Fresh no-system-prompt shared-proposal BASE strict excess. | 56.2081% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
| Fresh no-system-prompt shared-proposal PROJ_GUARD_V2 residual strict excess. | 8.4961% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
| Fresh no-system-prompt shared-proposal EFFECTGUARD_V2 strict excess. | 0.0000% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
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

## 2026-06-26 Rebuttal Addendum

Stage 1 claim reset is complete: the manuscript must use the local/open-weight
certificate-semantics framing above and must delete legacy large-grid,
commercial/frontier leaderboard, human-evaluation, and broad SOTA-system
reproduction claims.

Stage 2 shared-proposal audit is complete:

| Claim | Value | Source |
|---|---:|---|
| Shared-proposal paired groups | 7168 | `effectbench_omega/reports/shared_proposal_v2_audit_canonical_summary.md` |
| Shared-proposal trace rows | 21504 | `effectbench_omega/reports/shared_proposal_v2_audit_canonical_summary.md` |
| Proposal-action equality groups | 7168 / 7168 | `effectbench_omega/reports/shared_proposal_v2_audit_canonical_summary.md` |
| Shared-proposal canonical gate unexplained mismatches | 0 | `effectbench_omega/tables/frontier_canonical_shared_proposal_v2_audit_all_local_canonical.csv` |
| Shared-proposal PROJ_GUARD_V2 strict excess | 9.1657% | `effectbench_omega/tables/shared_proposal_v2_audit_online_control.csv` |
| Shared-proposal EFFECTGUARD_V2 strict excess | 0.0000% | `effectbench_omega/tables/shared_proposal_v2_audit_online_control.csv` |

This v2 shared-proposal audit is archived as the first paired proposal-control
audit. The paper-facing response to the system-label/proposal-distribution
confound is now the Rebuttal-2 v3 audit below.

## 2026-06-26 Rebuttal Stage 3/4/6 Addendum

Stage 3 necessary-high/incomparable stress is complete:

| Claim | Value | Source |
|---|---:|---|
| Stress block denominator | 3,072 traces | `effectbench_omega/outputs/stage3_stress_all_local/traces.parquet` |
| EffectGuard necessary-high decisions | 704 | `effectbench_omega/outputs/stage3_stress_all_local/traces.parquet` |
| EffectGuard incomparable decisions | 320 | `effectbench_omega/outputs/stage3_stress_all_local/traces.parquet` |
| Stress canonical unexplained mismatches | 0 | `effectbench_omega/tables/frontier_canonical_stage3_stress_all_local_canonical.csv` |

Stage 4 leave-one robustness is complete:

| Claim | Value | Source |
|---|---:|---|
| Leave-one gate rows | 39 | `effectbench_omega/tables/stage4_leave_one_gates.csv` |
| Base-gap failures | 0 | `effectbench_omega/reports/stage4_leave_one_robustness.json` |
| Required projection-residual failures | 0 | `effectbench_omega/reports/stage4_leave_one_robustness.json` |
| EffectGuard-zero failures | 0 | `effectbench_omega/reports/stage4_leave_one_robustness.json` |
| Minimum controlled/shared/corrected BASE gap | 53.3110 pp | `effectbench_omega/tables/stage4_leave_one_gates.csv` |

Stage 6 final freeze addendum is complete. The rebuttal package now removes
the main reviewer-kill points identified in `rebuttal_1.md`: stale claims,
between-system proposal confounding, EffectGuard-tautology concern, and
single-model/family fragility.

## 2026-06-29 Rebuttal-2 Final Addendum

Rebuttal-2 is complete. The fresh no-system-prompt `BASE` proposal queue ran
all four local models and produced a new paired v3 shared-proposal audit.

| Claim | Value | Source |
|---|---:|---|
| Fresh no-system shared-proposal traces | 21,504 | `effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/shared_proposal_summary.json` |
| Fresh no-system paired groups | 7,168 / 7,168 | `effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local/shared_proposal_summary.json` |
| Fresh no-system canonical unexplained mismatches | 0 | `effectbench_omega/tables/frontier_canonical_shared_proposal_v3_nosystem_all_local_canonical.csv` |
| Fresh no-system BASE strict excess | 56.2081% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
| Fresh no-system PROJ_GUARD_V2 residual strict excess | 8.4961% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
| Fresh no-system EFFECTGUARD_V2 strict excess | 0.0000% | `effectbench_omega/tables/shared_proposal_v3_nosystem_online_control.csv` |
| Full stress replay bundles | 3,072 | `effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md` |
| Full stress replay failures | 0 | `effectbench_omega/reports/certificate_replay_stage3_stress_all_local_canonical_full.md` |
| Refreshed leave-one gate rows | 49 | `effectbench_omega/reports/stage4_leave_one_robustness.json` |

Use v3 as the clean paper-facing paired proposal-control audit. The final
anonymous artifact package excludes the stale historical PDF and presentation
deck; use `PAPER_EACL2027_REWRITE.md` for the manuscript rewrite.
