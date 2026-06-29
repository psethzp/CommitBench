# Rebuttal Stage 6 Final Freeze

Completed: 2026-06-26 UTC.

## Completed Rebuttal Additions

| Stage | Status | Main artifact |
|---|---:|---|
| Stage 1 claim reset | Complete | `README.md`, `results.md`, `effectbench_omega/reports/eacl_rescue_paper_ready_summary.md` |
| Stage 2 shared-proposal audit | Complete | `effectbench_omega/outputs/shared_proposal_v2_audit_all_local/` |
| Stage 3 necessary-high/incomparable stress | Complete | `effectbench_omega/outputs/stage3_stress_all_local/` |
| Stage 4 leave-one robustness | Complete | `effectbench_omega/reports/stage4_leave_one_robustness.md` |
| Stage 5 native expansion | Skipped by instruction | Existing native validation remains `effectbench_omega/outputs/native_subset_v1_all_local/` |
| Stage 6 final freeze addendum | Complete | this report |

## Key Rebuttal Gates

| Gate | Value |
|---|---:|
| Shared-proposal groups complete | 7,168 / 7,168 |
| Shared-proposal unexplained mismatches | 0 |
| Stage 3 stress traces | 3,072 |
| Stage 3 stress failures | 0 |
| Stage 3 necessary-high EffectGuard decisions | 704 |
| Stage 3 incomparable EffectGuard decisions | 320 |
| Stage 4 leave-one gate rows | 39 |
| Stage 4 base-gap failures | 0 |
| Stage 4 required projection-residual failures | 0 |
| Stage 4 EffectGuard-zero failures | 0 |

## Final Light Gates

| Check | Result |
|---|---:|
| `py_compile` for changed scripts/modules | Pass |
| `pytest -q effectbench_omega/tests` | 18 passed, 1 warning |
| `claim_registry_check.py` | 38 rows, pass |
| `no_red_placeholders.py` | Pass |
| Active CommitBench/vLLM jobs | None |
| GPU compute apps | None |

## Paper-Proof Archive

The refreshed paper-proof archive should bundle the code, plans, runbooks,
reports, tables, figures, generated traces, logs, witness bundles, manifests,
claim registries, and paper-facing PDFs/decks needed to audit the local-only
EACL rescue results. It intentionally excludes `.env`, `.git`, Python
virtualenvs, model caches, cloned upstream repositories, temporary caches, and
older zip files.

Archive generated:

```text
file: CommitBench_paper_proof_full_20260626.zip
entries: 14,607
archive size: about 82 MiB on disk after compression
integrity: unzip -tq passed
exclusion audit: 0 bad entries
```

## Remaining Work

No additional experiments are required by the current rebuttal plan. The
remaining work is paper writing:

- rewrite the manuscript around the local/open-weight certificate-semantics claim;
- cite Stage 2 as the paired proposal-control audit;
- cite Stage 3 as the necessary-high/incomparable stress audit;
- cite Stage 4 as leave-one-model/family robustness;
