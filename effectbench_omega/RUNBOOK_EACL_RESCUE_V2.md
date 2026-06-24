# EffectBench-Omega EACL Rescue V2 Runbook

Last updated: 2026-06-24 UTC

## Operating Rules

This runbook tracks the V2 rescue plan under `V2/`.

Hard boundaries:

- Do not use Bedrock/API.
- Do not add or download new headline models.
- Do not overwrite the frozen split:
  `effectbench_omega/outputs/main_mc_postfix_all_local/`.
- Do not overwrite the frozen Stage 3 job:
  `effectbench_omega/jobs/stage3_hardened_main_mc_postfix_all_local_20260623T220316Z/`.
- All new experiment outputs must use new split names.
- Update this runbook, `README.md`, and `results.md` after each stage.
- Stop after each stage and wait for operator approval before moving on.

## Stage Status

| Stage | Name | Status | Approval Gate |
|---|---|---:|---|
| 0 | Freeze and preflight | Complete | Awaiting approval for Stage 1 |
| 1 | Enumerated frontier completeness audit | Pending | Requires Stage 0 approval |
| 2 | Corrected guards V2 implementation | Pending | Requires Stage 1 approval |
| 3 | V2 smoke and Qwen repair sensitivity | Pending | Requires Stage 2 approval |
| 4 | Full corrected-guard local run | Pending | Requires Stage 3 approval |
| 5 | Native-fidelity subset | Pending | Requires Stage 4 approval |
| 6 | Full replay and targeted CEGAR stress | Pending | Requires Stage 5 approval |
| 7 | Lattice policy and paper freeze | Pending | Requires Stage 6 approval |

## Stage 0: Freeze And Preflight

Completed on 2026-06-24 UTC.

Branch:

```text
eacl-rescue-v2
```

Commands run:

```bash
.venv/bin/python effectbench_omega/scripts/sanity_check.py --local-only
.venv/bin/python effectbench_omega/scripts/verify_local_open_model_cache.py
.venv/bin/python -m pytest -q effectbench_omega/tests/no_oracle
.venv/bin/python effectbench_omega/effectbench/metrics/claim_registry_check.py \
  --registry effectbench_omega/metrics/claim_registry_main_mc_postfix_all_local.csv
.venv/bin/python effectbench_omega/scripts/no_red_placeholders.py \
  --root . \
  --out effectbench_omega/reports/no_red_placeholders.md
```

Results:

| Check | Status | Detail |
|---|---:|---|
| Branch created | Pass | `eacl-rescue-v2` from current `main` |
| Sanity/import check | Pass | Python `3.11.15`; required modules imported; 4 x NVIDIA L40S visible |
| Required local model cache | Pass | Mistral, Qwen3.6-35B-A3B, Llama 3.3 70B AWQ, and Gemma 3 27B IT ready |
| Optional local model cache | Informational | Qwen3-14B-AWQ and Qwen3-30B-A3B cached but not in headline grid |
| Full Llama 3.3 70B precision cache | Informational | Not cached; AWQ substitute remains active |
| No-oracle pytest | Pass | `9 passed, 1 warning` |
| Claim registry check | Pass | 50 rows |
| Placeholder scan | Pass | `effectbench_omega/reports/no_red_placeholders.md` reports PASS |
| Bedrock/API use | Pass | No paid/API runs launched |
| Frozen split modified | Pass | No experiment reruns launched in Stage 0 |

Stage 0 conclusion:

```text
The environment is ready for Stage 1. The frozen current run remains the
baseline evidence package. Next implementation should start with the offline
enumerated-frontier audit only.
```

## Stage 1 Plan: Enumerated Frontier Completeness Audit

Do after operator approval only.

Implementation target:

```text
effectbench_omega/effectbench/kernel/enumerate_frontier.py
effectbench_omega/scripts/run_frontier_completeness.py
```

Important decision:

```text
Do not write enumerated artifacts into the frozen split's existing kernel
directory. Write them into:
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/
```

Required outputs:

```text
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/frontier_enumerated.parquet
effectbench_omega/outputs/frontier_audit_main_mc_postfix_all_local/certificates_enumerated.parquet
effectbench_omega/tables/frontier_completeness_main_mc_postfix_all_local.csv
effectbench_omega/reports/frontier_completeness_main_mc_postfix_all_local.md
```

Acceptance gate:

```text
label_agreement >= 0.995
unexplained_mismatches = 0
```

