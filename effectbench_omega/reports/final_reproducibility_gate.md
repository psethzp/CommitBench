# Final Reproducibility Gate

Completed on 2026-06-25 UTC.

| Gate | Result | Detail |
|---|---:|---|
| Finalization script compile | Pass | `py_compile effectbench_omega/scripts/finalize_eacl_rescue.py` |
| No-oracle tests | Pass | `9 passed, 1 warning` |
| Final claim registry check | Pass | 23 rows in `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv` |
| Placeholder scan | Pass | `effectbench_omega/reports/no_red_placeholders.md` reports PASS |
| Check-only reproducer | Pass | Missing required files: none; local endpoint is stopped as expected |
| Cost audit | Pass | 47,616 local request rows, total cost `$0`, unpriced Bedrock rows `0` |
| Main controlled replay | Pass | 4,819 bundles checked, 0 failures |
| Corrected-guard replay | Pass | 5,341 bundles checked, 0 failures |
| Native-fidelity replay | Pass | 1,348 bundles checked, 1,348 native replays, 0 failures |

Interpretation: the local-only EACL rescue artifact is frozen for writing. The
paper must use canonical enumerated-frontier labels, keep lattice sensitivity
as appendix/diagnostic only, and avoid Bedrock/frontier/human-eval claims.
