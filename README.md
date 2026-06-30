# EffectKernelBench / CommitBench Rescue Workspace

Public submission name for the rescued paper/artifact should be
**EffectKernelBench**. `CommitBench` remains only the repository/workspace
name and should not be used as the final paper title.

Local handoff/setup repo for the EffectBench-Ω minimal-plus experiment suite.

Current active plan: **local/open-weight only**. Bedrock/API runs are archived and should not be used for headline claims.

Historical Bedrock smoke notes exist in older runbooks, but the active `PLAN.md` path does not require Bedrock access.

Review-rescue artifact status: **EffectKernelBench artifact is built**.
The clean review-facing artifact is generated at `EffectKernelBench_artifact/`
and zipped as `EffectKernelBench_artifact.zip`. It exposes one canonical split,
`final_paired_control`, plus normalized raw model-proposal provenance,
deterministic close-method projection baselines, uncertainty tables,
no-oracle reports, a completed 512-call fresh local smoke, a 300-bundle
optional annotation package, and a final Markdown paper draft.

Final review-rescue zip:

```text
EffectKernelBench_artifact.zip
size: 4.0 MiB
sha256: cd1ad054d2552dcd8a4e6971f11348f82dfe67ea3e9f797dd9a1e5f39dc6d73a
```

The stale historical `CommitBench.pdf`, presentation deck, old proof zips,
development split labels, model caches, and upstream clones are excluded from
the review-facing artifact.

## Current Status

- Historical V2 rescue branch: **`eacl-rescue-v2`**. Current review-rescue work is on **`effectkernelbench-review-rescue`**. EACL rescue Stages 0-11 are complete locally: canonical labels, corrected guards, native-fidelity validation, full replay, targeted CEGAR stress, lattice-policy freeze, final claim registry, final reproducibility gate, paper-ready summary, and LFS artifact tracking setup.
- Main Bedrock experiments: **not run**.
- Full local Qwen experiment grid: **not run by request**.
- Local-open 21,504-row manifest: **built** at `effectbench_omega/manifests/tasks_local_open.csv`.
- Selected-four local-open dry smoke: **passed** on 60 traces.
- Historical live local model-call smoke: **passed** with `qwen3_14b_awq_local` on 1 trajectory, 0 failures.
- Selected-four live model-call smokes: **passed** for Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Gemma-3-27B-it, and Llama-3.3-70B-AWQ.
- Open model cache: Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Gemma-3-27B-it, and Llama-3.3-70B-AWQ are ready in the shared HF cache. Qwen3-14B-AWQ and Qwen3-30B-A3B are also cached but no longer in the locked headline grid.
- Local vLLM endpoint: **stopped** after completed Stage 5 queue; GPUs are idle.
- Upstream benchmark repos: **cloned and pinned**.
- Headline local-only manifest: **generated, 21,504 rows**.
- End-to-end workflow smoke: **passed** on local dry trajectories plus one live local Qwen14 call.
- Final local verification pass: **passed**.
- Native-source audit: **passed**; four benchmark families are source-backed, delegated-docs is explicitly controlled synthetic.
- Stage 1 live per-model smoke: **passed** for all four locked local models, 12 traces/model, 0 failures/model, no-oracle 100%, local cost $0.
- Stage 2 ordered local queue: **complete**. All four local slices finished, 21,504 traces total, 0 final failures, no-oracle 100%, local cost $0.
- Model-controlled action-policy smoke: **passed with hardened defaults**. `local_open_smoke_mc_default_20260622T204613Z` ran 21 traces/model across all regimes and systems, 84 total traces, 0 failures, no-oracle 100%, local cost $0, JSON proposals 21/21 for every model, empty repair logs 21/21 for every model, proposal diversity gate passed.
- Stage 2b model-controlled queue: **complete** as `local_open_main_mc_postfix_20260622T214941Z`; all four slices finished, 21,504 traces, 0 failures, no-oracle 100%, local cost $0.
- Stage 3 merge: **complete** at `effectbench_omega/outputs/main_mc_postfix_all_local/`; 21,504 merged traces, 21,504 API log rows, 0 failures.
- Stage 3 hardened offline suite: **complete** as `stage3_hardened_main_mc_postfix_all_local_20260623T220316Z`; this is now archived as the legacy generated-trace verifier view, not the paper-grade strict-label source.
- Canonical enumerated-frontier suite: **complete** as `stage3_canonical_main_mc_postfix_all_local_20260624T162051Z`; 21,504 canonical certificates, 4,089 strict-excess certificates, 1,060 spurious legacy witnesses diagnosed, 0 unexplained mismatches, canonical gate passed, and 160 replay bundles checked with 0 failures.
- Hardened metrics: **complete**. Projection baselines are data-derived, bootstrap uses paired/task-cluster/hierarchical resampling with 2,000 draws, CEGAR uses reduced abstract-state collision checks, and `guard_tie` explains PROJ_GUARD vs EFFECTGUARD.
- Stage 3 figures and lite claim registry: **complete**. Aggregate writes PNG/PDF figures under `effectbench_omega/figures/main_mc_postfix_all_local/` and a 50-row computed registry at `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv`.
- EACL rescue V2 Stage 0: **complete**. Sanity/import check passed, required local model caches are ready, no-oracle pytest passed (`9 passed`), claim registry check passed with 50 rows, and placeholder scan passed.
- EACL rescue V2 Stage 1: **complete, legacy-agreement gate failed but canonical gate passes**. The enumerated-frontier audit relabeled 21,504 successful traces across 7,168 groups, found 4,089 strict-excess labels versus 5,149 old generated-trace labels, strictness agreement 95.0707%, exact label agreement 92.9315%, 1,060 spurious legacy witnesses, and 0 unexplained mismatches. Paper-grade labels now use canonical enumerated-frontier certificates.
- EACL rescue V2 Stage 2: **complete**. Added `PROJ_GUARD_V2` and `EFFECTGUARD_V2`, a 14,336-row V2 guard manifest, V2 guard tests, and a 14-row balanced dry smoke with 0 failures and 100% no-oracle pass rate.
- EACL rescue V2 Stage 3: **complete**. Four-model V2 live smokes passed with 14 traces/model, 0 failures/model, JSON proposals 14/14 for every model, empty repair logs for every model, no-oracle 100%, and local cost $0. Qwen same-prompt repair sensitivity reran 168 affected rows with 0 proposal/effect/verdict changes and 0.0 pp strict-rate delta.
- EACL rescue canonical scoring: **complete**. `run_stage3_offline.sh` defaults to `CANONICAL_CERT_MODE=enumerated`; projection, bootstrap, CEGAR, lattice, guard-tie, replay, aggregate figures, and claim registry consume `kernel_canonical/certificates_enumerated.parquet`.
- EACL rescue V2 Stage 4: **complete**. The guard-only queue ran `PROJ_GUARD_V2` and `EFFECTGUARD_V2` with `SLICE_LIMIT=3584` per model, TP=4 on GPUs `0,1,2,3`, model order Mistral, Qwen, Llama, Gemma. All four slices finished with 14,336 V2 guard traces, 0 failures, and local cost $0. Combined canonical scoring with frozen `BASE` produced 21,504 trajectories, canonical gate pass, 4,611 canonical strict-excess labels, 1,010 spurious legacy witnesses, 0 unexplained mismatches, and replay 160/160 pass.
- EACL rescue V2 Stage 5: **complete**. Native-fidelity subset implementation is complete and the live local queue `local_open_native_subset_v1_20260625T085816Z` finished all four models with 4,608 traces, 0 runner failures, and local cost $0. Merged canonical scoring in `stage5_canonical_native_subset_v1_20260625T191826Z` passed: 4,217 native successes, 391 native terminal failures, 848 canonical strict-excess labels, 0 unexplained mismatches, 160/160 native replay bundles passed, and no-oracle 100%.
- EACL rescue V2 Stage 6: **complete**. Full replay checked 11,508 bundles across the controlled, corrected-guard, and native canonical splits with 0 failures; 1,348 native bundles replayed in the native wrappers. Targeted CEGAR stress now produces label-changing collisions for all seven future-relevant fields, including `policy_obligation`, `contract_artifact_hash`, `virtual_clock`, and `compensation_or_payment_hold`.
- EACL rescue V2 Stage 7: **complete**. Lattice sensitivity is frozen as appendix/diagnostic only; main claims use the fixed declared Pareto lattice.
- EACL rescue V2 Stage 8: **complete**. Final claim registry has 23 mapped claims at `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv`.
- EACL rescue V2 Stage 9: **complete**. Final reproducibility gate passed: no-oracle tests, placeholder scan, claim-registry check, check-only reproducer, cost audit, and full replay checks.
- EACL rescue V2 Stage 10: **complete**. Paper-ready summary is available at `effectbench_omega/reports/eacl_rescue_paper_ready_summary.md`.
- EACL rescue V2 Stage 11: **complete locally**. Git LFS is configured for generated traces/logs/bundles/figures and the artifact manifest indexes 13,836 files / 416,877,747 bytes with SHA-256 hashes.
- Rebuttal Stage 1 claim reset: **complete in repo docs/code posture**. The submission story is local/open-weight certificate semantics only: no Bedrock/frontier leaderboard, no human-eval claim, no stale 204,800-episode framing, and no broad SOTA-system reproduction claim.
- Rebuttal Stage 2 shared-proposal audit: **complete, CPU-only**. `effectbench_omega/scripts/build_shared_proposal_v2_audit.py` built `effectbench_omega/outputs/shared_proposal_v2_audit_all_local/` by replaying `BASE`, `PROJ_GUARD_V2`, and `EFFECTGUARD_V2` from the exact same frozen `BASE` model proposal for each task/model/regime/seed. It produced 21,504 traces, 7,168/7,168 complete shared groups, 0 failures, 0 new model calls, canonical gate pass, 1,205,248 enumerated candidates, 0 unexplained mismatches, and no-oracle 21,504/21,504 pass. Canonical strict-excess rates under shared proposals: `BASE` 57.0033%, `PROJ_GUARD_V2` 9.1657%, `EFFECTGUARD_V2` 0.0000%.
- Rebuttal Stage 3 necessary-high/incomparable stress block: **complete** as `stage3_stress_live_20260626T162912Z` plus canonical job `stage3_stress_canonical_20260626T191036Z`. The live run produced 3,072 traces, 0 failures, canonical gate pass, 0 unexplained mismatches, no-oracle pass, replay pass, 704 necessary-high `EFFECTGUARD_V2` decisions, and 320 incomparable `EFFECTGUARD_V2` decisions. Merged output: `effectbench_omega/outputs/stage3_stress_all_local/`.
- Rebuttal Stage 4 leave-one robustness: **complete, CPU-only**. `effectbench_omega/scripts/run_stage4_robustness.py` produced 117 metric rows and 39 gate rows across the main controlled, corrected-guard V2, shared-proposal V2, and native-validation splits. There were 0 base-gap failures, 0 required projection-residual failures, and 0 EffectGuard-zero failures. BASE raw-vs-kernel gap stays at least 53.3110 pp in controlled/shared/corrected leave-one slices and 61.9102 pp in native-validation leave-one slices.
- Rebuttal Stage 6 final freeze addendum: **complete**. Final rebuttal registry/docs now include Stage 2 shared proposals, Stage 3 stress, and Stage 4 robustness. Final light gates pass: py_compile, pytest, claim-registry check, placeholder scan, and active-job/GPU-idle check.
- Paper-proof archive refresh: **complete** as `CommitBench_paper_proof_full_20260626.zip` in the repo root. It contains 14,607 entries and is about 82 MiB on disk after compression; integrity check passed and the exclusion audit found 0 sensitive/cache entries.
- Rebuttal-2 fresh no-system-prompt audit: **complete**. The BASE-only TP=4 queue finished across all four local models; the v3 shared-proposal audit has 21,504 traces, 7,168 complete paired groups, 0 unexplained canonical mismatches, no-oracle 100%, full stress replay 3,072/3,072 pass, and Stage 4 leave-one robustness 49/49 gates pass.
- Final anonymous artifact package: **ready**. The final package excludes secrets, virtualenvs, model caches, upstream clones, old zip files, stale PDF/PPT binaries, and historical planning memos that contain identity-bearing or obsolete claims.
- EffectKernelBench review-rescue artifact: **ready for the no-human-eval scope**. It includes 7,168 normalized real local BASE proposal logs, the 21,504-row `final_paired_control` split, direct projection baselines, uncertainty/no-oracle audits, 300 optional blinded annotation bundles, a completed 512-call fresh smoke, and `PAPER_EFFECTKERNELBENCH_FINAL.md`. Human validation is explicitly skipped and not claimed.
- Queue defaults: **Step 2b hardened path**. `run_local_open_queue.sh` now defaults to `main_mc_postfix`, `MODEL_CONTROLS_POLICY=1`, `MODEL_PROPOSAL_MODE=actions`, TP=4 on GPUs `0,1,2,3`.
- Prompt fairness: **locked for future runs**. `run_online.py` no longer exposes the evaluated system label in proposal prompt user content. All four local models receive the same system instruction, task context, user-turn rendering, action enum, `terminal_action` requirement, temperature, and max token budget; only the structured-output transport differs by serving support.

## Current Caveats

- Qwen full slice has `42/5,376` audited repaired-fallback proposals. The primary run remains frozen; any same-prompt rerun of those rows should be reported as a sensitivity/ablation, not silently substituted.
- V2 Stage 3 same-prompt Qwen sensitivity reproduced the same 42 repair-fallback parses and changed no proposal/effect/verdict/headline metric. This downgrades the Qwen issue from volatility risk to audit-disclosed parse-status caveat.
- Shared-proposal v2 caveat: the older v2 audit replays frozen `BASE` proposals generated before the 2026-06-26 prompt fix. The Rebuttal-2 v3 audit supersedes that caveat for paper-facing claims by regenerating fresh no-system-prompt `BASE` proposals and replaying `BASE`, `PROJ_GUARD_V2`, and `EFFECTGUARD_V2` from those shared proposals.
- Legacy generated-trace strict labels are archived only. The old `5,149` strict-excess count must not be used for headline claims; canonical enumerated-frontier scoring gives `4,089` strict-excess labels and records the `1,060` old labels as spurious legacy witnesses.
- Stage 3 projection/bootstrap/CEGAR are now replayable data-derived local audits. They are still simulator-local, not external human audits. CEGAR no-collision fields are a conservative-audit strength: the checker does not reject omissions without observed label-changing collisions; that means "not exercised by this scaffold," not "never future-relevant."
- Legacy `PROJ_GUARD` and `EFFECTGUARD` are effectively tied in this local implementation: only `3/7,168` paired units differ in verifier verdict, all Mistral telecom confirm-target cases. Corrected `PROJ_GUARD_V2`/`EFFECTGUARD_V2` and the shared-proposal audit support the V2 comparison instead.
- Active claims are local/open-weight only. Do not claim commercial/frontier leaderboard coverage from this run.
- EffectKernelBench human-validation caveat: human validation is skipped for this freeze. The annotation package exists, but the paper must not claim human agreement, kappa/alpha, human preference, or human-audited correctness unless 2-3 annotators complete the 300 blinded bundles later.
- Fresh smoke parse caveat: 498/512 proposals parsed as JSON. Qwen accounts for the non-JSON rows: 9 text-scan, 1 low/high-format, and 4 repaired fallbacks. All rows completed runner, verifier, no-oracle, and cost checks; the parse audit is included in the artifact.
- The historical `CommitBench.pdf` is stale and is excluded from the final anonymous artifact package. Use `PAPER_EACL2027_REWRITE.md` as the current paper rewrite scaffold.
- V2 rescue work must not overwrite `effectbench_omega/outputs/main_mc_postfix_all_local/`; all new outputs need new split names.
- Stage 5 native-fidelity subset is a compact native-style validation block over pinned upstream task records, not a full re-host of the upstream benchmark servers. It supports native predicate/state-delta validation; keep the boundary explicit in paper wording.
- Lattice sensitivity is appendix/diagnostic only. Do not claim robustness across alternate value-governance lattices from the current invariant sensitivity tables.

## Implemented Features

| Area | Status | Notes |
|---|---|---|
| Task families | Working local adapters | Retail, airline, telecom, delegated docs, and ToolSandbox/contract-style tasks. |
| Regimes | Working | `FULL`, `CONCAT`, `SHARDED`, `SNOWBALL`, `REVISE`, `MEMORY_REVISE`, `ADV_EFFECT`. |
| Manifest builder | Working | `effectbench_omega/manifests/tasks_local_open.csv` has the locked 21,504-row denominator. |
| Online systems | Working local policies | `BASE`, `PROJ_GUARD`, `EFFECTGUARD`. |
| Model proposal parser | Working | JSON, text-scan, LOW/HIGH legacy, explicit repaired fallback action proposals, required `terminal_action`, Mistral tool calls, and JSON-schema constrained proposals for Qwen/Llama/Gemma. |
| No-oracle guard | Working | Runtime forbidden-field checks plus audit reports. |
| Kernel verifier | Working | Legacy generated-trace verifier is retained for audit; canonical paper scoring uses enumerated admissible-frontier certificates with canonical gate `unexplained_mismatches=0`. |
| Offline metrics/audits | Working | Projection loss, CEGAR, lattice sensitivity, bootstrap, cost audit, aggregate tables, figures, claim registry, replay bundles. |
| Local vLLM models | Working | Generic launcher supports the active local model keys; Mistral uses official Mistral tokenizer/config/tool parser. |
| Stage 1 live smokes | Passed | `effectbench_omega/scripts/run_selected4_live_smokes.sh`; four locked models, 48 total live model-call traces, 0 failures. |
| Stage 2 queue | Complete | `effectbench_omega/scripts/run_local_open_queue.sh`; four local slices complete. |
| Stage 2b model-controlled queue | Complete | `main_mc_postfix`; four local model slices complete, 21,504 total traces, 0 failures. |
| Stage 3 merge helper | Complete | `effectbench_omega/scripts/merge_local_open_slices.py`; merged output is `effectbench_omega/outputs/main_mc_postfix_all_local/`. |
| Stage 3 hardened offline suite | Complete | `effectbench_omega/scripts/run_stage3_offline.sh`; hardened projection/bootstrap/CEGAR/guard-tie outputs generated for `main_mc_postfix_all_local`. |
| EACL rescue V2 runbook | Active | `effectbench_omega/RUNBOOK_EACL_RESCUE_V2.md`; Stage 1 complete with failed validation gate, Stage 2 and Stage 3 complete. |
| Enumerated frontier audit | Working, canonical gate passed | `effectbench_omega/scripts/run_frontier_completeness.py`; legacy agreement failed as expected, but canonical scoring has 0 unexplained mismatches. |
| Corrected guard V2 systems | Working | `PROJ_GUARD_V2` is projection-only; `EFFECTGUARD_V2` performs current-state admissible lower-effect substitution. |
| V2 live smokes | Passed | `effectbench_omega/scripts/run_stage3_v2_smoke_queue.sh`; four locked models, 56 total live V2 traces, 0 failures. |
| Qwen repair sensitivity | Passed | 168 affected rows rerun same-prompt; 0 proposal/effect/verdict changes; 0.0 pp strict-rate delta. |
| Stage 4 merge/scoring path | Complete | `local_open_guard_v2_main_20260624T200115Z` finished all four V2 guard slices; `build_guard_v2_main_split.py` combined frozen `BASE` with V2 guard rows; canonical scoring completed as `stage3_canonical_guard_v2_main_with_base_20260625T082959Z`. |
| Stage 5 native-fidelity subset | Complete | Native wrappers, manifest, full live queue, merge, canonical scoring, and native replay passed. |
| Stage 6 full replay and CEGAR stress | Complete | 11,508 full replay bundles passed; targeted CEGAR stress exercises all seven future-relevant fields. |
| Stage 7 lattice policy freeze | Complete | Main claims use the fixed declared Pareto lattice; lattice sensitivity is appendix/diagnostic only. |
| Stage 8 final claim registry | Complete | 23 final claim rows map numbers to source artifacts and allowed paper posture. |
| Stage 9 final reproducibility gate | Complete | No-oracle, replay, cost, placeholder, registry, and check-only gates passed. |
| Stage 10 paper-ready summary | Complete | `effectbench_omega/reports/eacl_rescue_paper_ready_summary.md`. |
| Stage 11 artifact tracking | Complete locally | Git LFS configured; artifact manifest indexes generated experiment artifacts. |
| Rebuttal Stage 1 claim reset | Complete | Paper posture narrowed to local/open-weight certificate semantics; stale frontier/human/SOTA claims are disallowed. |
| Rebuttal Stage 2 shared-proposal audit | Complete | `build_shared_proposal_v2_audit.py` replays V2 guards from frozen `BASE` proposals; canonical gate and no-oracle passed. |
| Rebuttal Stage 3 stress block | Complete | Necessary-high and incomparable stress run complete; canonical gate, replay, and no-oracle passed. |
| Rebuttal Stage 4 robustness | Complete | Leave-one-model/family gates pass for main, corrected, shared-proposal, and native splits. |
| Rebuttal Stage 6 freeze addendum | Complete | Final docs/registry updated and light gates passed. |
| Bedrock | Archived | Not part of the active local-only plan. |

## Key Outputs

- Active runbook/checkpoint tracker: `effectbench_omega/RUNBOOK_LOCAL_ONLY.md`
- EACL rescue V2 runbook: `effectbench_omega/RUNBOOK_EACL_RESCUE_V2.md`
- Archived Bedrock-era runbook: `effectbench_omega/RUNBOOK.md`
- Local-open model cache report: `effectbench_omega/artifacts/local_open_model_cache.json`
- Local Qwen cache report: `effectbench_omega/artifacts/local_qwen_cache.json`
- Repo/model pins: `effectbench_omega/artifacts/repo_versions.json`
- Workflow smoke dry outputs: `effectbench_omega/outputs/workflow_smoke_dry/`
- Workflow smoke local-Qwen outputs: `effectbench_omega/outputs/workflow_smoke_local_qwen/`
- Selected-four dry outputs: `effectbench_omega/outputs/selected4_dry/`
- Selected-four live smoke automation: `effectbench_omega/scripts/run_selected4_live_smokes.sh`
- Selected-four live endpoint smoke reports: `effectbench_omega/reports/live_smokes/`
- Selected-four Stage 1 live outputs: `effectbench_omega/outputs/smoke_<model>/`
- Ordered Stage 2 queue runner: `effectbench_omega/scripts/run_local_open_queue.sh`
- Ordered Stage 2 queue monitor: `effectbench_omega/scripts/show_local_open_queue_status.sh`
- Pre-fix model-controlled balanced smoke outputs: `effectbench_omega/outputs/smoke_mc_balanced_<model>/`
- Accepted default model-controlled smoke outputs: `effectbench_omega/outputs/smoke_mc_default_<model>/`
- Recommended next full model-controlled outputs: `effectbench_omega/outputs/main_mc_postfix_<model>/`
- Merged Stage 2b output: `effectbench_omega/outputs/main_mc_postfix_all_local/`
- Stage 3 hardened job log: `effectbench_omega/jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z/`
- Stage 3 main tables: `effectbench_omega/tables/main_mc_postfix_all_local/`
- Stage 3 hardened projection table: `effectbench_omega/tables/projection_loss_main_mc_postfix_all_local.csv`
- Stage 3 hardened uncertainty table: `effectbench_omega/tables/uncertainty_main_mc_postfix_all_local.csv`
- Stage 3 hardened CEGAR table: `effectbench_omega/tables/cegar_rejections_main_mc_postfix_all_local.csv`
- Stage 3 guard-tie report: `effectbench_omega/tables/guard_tie_main_mc_postfix_all_local.md`
- Stage 3 figures: `effectbench_omega/figures/main_mc_postfix_all_local/`
- Stage 3 witness bundles: `effectbench_omega/witness_bundles/main_mc_postfix_all_local/`
- Stage 3 lite claim registry: `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv`
- V2 frontier audit table: `effectbench_omega/tables/frontier_completeness_main_mc_postfix_all_local.csv`
- V2 frontier audit report: `effectbench_omega/reports/frontier_completeness_main_mc_postfix_all_local.md`
- Canonical kernel certificates: `effectbench_omega/outputs/main_mc_postfix_all_local/kernel_canonical/certificates_enumerated.parquet`
- Canonical frontier report: `effectbench_omega/reports/frontier_canonical_main_mc_postfix_all_local_canonical.md`
- Canonical main tables: `effectbench_omega/tables/main_mc_postfix_all_local_canonical/`
- Canonical claim registry: `effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local_canonical.csv`
- V2 guard manifest: `effectbench_omega/manifests/tasks_guard_v2_local.csv`
- V2 dry smoke output: `effectbench_omega/outputs/guard_v2_dry_smoke/`
- V2 dry no-oracle table: `effectbench_omega/tables/no_oracle_guard_v2_dry_smoke.csv`
- V2 Stage 3 job: `effectbench_omega/jobs/stage3_v2_smoke_20260624T143808Z/`
- V2 Stage 3 smoke outputs: `effectbench_omega/outputs/stage3_v2_smoke_<model>/`
- V2 Stage 4 live queue: `effectbench_omega/jobs/local_open_guard_v2_main_20260624T200115Z/`
- V2 Stage 4 slice outputs: `effectbench_omega/outputs/guard_v2_main_<model>/`
- V2 Stage 4 merged guard output: `effectbench_omega/outputs/guard_v2_main_all_local/`
- V2 Stage 4 combined BASE+V2 output: `effectbench_omega/outputs/guard_v2_main_with_base_all_local/`
- V2 Stage 4 canonical job: `effectbench_omega/jobs/stage3_canonical_guard_v2_main_with_base_20260625T082959Z/`
- V2 Stage 4 canonical tables: `effectbench_omega/tables/guard_v2_main_with_base_all_local_canonical/`
- V2 Stage 5 native manifest: `effectbench_omega/manifests/tasks_native_subset.csv`
- V2 Stage 5 native wrappers: `effectbench_omega/effectbench/native/`
- V2 Stage 5 live queue: `effectbench_omega/jobs/local_open_native_subset_v1_20260625T085816Z/`
- V2 Stage 5 merged output: `effectbench_omega/outputs/native_subset_v1_all_local/`
- V2 Stage 5 canonical job: `effectbench_omega/jobs/stage5_canonical_native_subset_v1_20260625T191826Z/`
- V2 Stage 5 canonical tables: `effectbench_omega/tables/native_subset_v1_all_local_canonical/`
- V2 Stage 5 dry native outputs: `effectbench_omega/outputs/native_subset_v1_dry_all/`
- V2 Stage 6 summary report: `effectbench_omega/reports/stage6_full_replay_cegar.md`
- V2 Stage 6 replay summary: `effectbench_omega/tables/stage6_full_replay_summary.csv`
- V2 Stage 6 targeted CEGAR stress: `effectbench_omega/tables/cegar_rejections_stage6_targeted_stress.csv`
- V2 Stage 7 lattice policy freeze: `effectbench_omega/reports/stage7_lattice_policy_freeze.md`
- V2 Stage 8 final claim registry: `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv`
- V2 Stage 8 claim audit: `effectbench_omega/reports/stage8_claim_audit.md`
- V2 Stage 9 final reproducibility gate: `effectbench_omega/reports/final_reproducibility_gate.md`
- V2 Stage 10 paper-ready summary: `effectbench_omega/reports/eacl_rescue_paper_ready_summary.md`
- V2 Stage 11 artifact manifest: `effectbench_omega/tables/artifact_manifest.csv`
- V2 Stage 11 artifact manifest summary: `effectbench_omega/reports/artifact_manifest.md`
- Rebuttal Stage 2 shared-proposal split: `effectbench_omega/outputs/shared_proposal_v2_audit_all_local/`
- Rebuttal Stage 2 shared-proposal audit report: `effectbench_omega/reports/shared_proposal_v2_audit.md`
- Rebuttal Stage 2 canonical summary: `effectbench_omega/reports/shared_proposal_v2_audit_canonical_summary.md`
- Rebuttal Stage 2 online-control table: `effectbench_omega/tables/shared_proposal_v2_audit_online_control.csv`
- Rebuttal Stage 2 canonical frontier table: `effectbench_omega/tables/frontier_canonical_shared_proposal_v2_audit_all_local_canonical.csv`
- Rebuttal Stage 3 stress merged output: `effectbench_omega/outputs/stage3_stress_all_local/`
- Rebuttal Stage 3 canonical report: `effectbench_omega/reports/frontier_canonical_stage3_stress_all_local_canonical.md`
- Rebuttal Stage 4 robustness report: `effectbench_omega/reports/stage4_leave_one_robustness.md`
- Rebuttal Stage 4 robustness gates: `effectbench_omega/tables/stage4_leave_one_gates.csv`
- Rebuttal Stage 4 robustness metrics: `effectbench_omega/tables/stage4_leave_one_metrics.csv`
- Qwen repair rows manifest: `effectbench_omega/manifests/qwen_repair_rows.csv`
- Qwen repair sensitivity report: `effectbench_omega/reports/qwen_repair_sensitivity.md`
- Qwen repair sensitivity table: `effectbench_omega/tables/qwen_repair_sensitivity.csv`
- Live Qwen14 smoke outputs: `effectbench_omega/outputs/local_runner_qwen14_smoke/`
- Selected-four smoke certificates: `effectbench_omega/outputs/smoke_<model>/kernel/certificates.parquet`
- Native source audit: `effectbench_omega/reports/native_source_audit.md`

See `effectbench_omega/RUNBOOK_LOCAL_ONLY.md` for staged commands, status, and the next experiment steps.

<!-- REBUTTAL2_STATUS_START -->
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
<!-- REBUTTAL2_STATUS_END -->
