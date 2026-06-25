# Stage 8 Claim Audit

Final claim registry rows: 23

| Paper status | Rows |
|---|---:|
| `allowed_audit` | 3 |
| `allowed_caveat` | 1 |
| `allowed_main` | 11 |
| `allowed_main_with_caveat` | 1 |
| `allowed_reproducibility` | 1 |
| `allowed_validation` | 5 |
| `archive_only` | 1 |

Rules enforced by the final registry:

- Use canonical enumerated-frontier labels for strict-excess claims.
- Treat generated-trace strict labels as archived diagnostics only.
- Keep local/open-weight claims separate from Bedrock/frontier claims.
- Report the native-fidelity subset as validation, not as the headline denominator.
- Do not use lattice sensitivity as a main-paper robustness claim.
- Do not claim human evaluation or commercial-model leaderboards.

Registry path: `effectbench_omega/metrics/claim_registry_eacl_rescue_final.csv`.
