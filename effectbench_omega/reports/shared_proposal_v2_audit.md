# Shared-Proposal V2 Audit

This audit replays every V2 system from the exact same frozen BASE model proposal for each task/model/regime/seed.
It is an offline paired-control audit: no GPU and no new model calls were used.

| Metric | Value |
|---|---:|
| Trace rows | 21,504 |
| Shared groups | 7,168 |
| Complete source groups | 7,168 |
| Proposal-action equality groups | 7,168 |
| Failures | 0 |
| New model calls | 0 |

## Systems

`BASE`, `EFFECTGUARD_V2`, `PROJ_GUARD_V2`

## Parse Counts

| System | Parse status | Rows |
|---|---|---:|
| `BASE` | `json` | 7,103 |
| `BASE` | `low_high_legacy` | 2 |
| `BASE` | `text_scan` | 49 |
| `BASE` | `unparsed:repair_fallback` | 14 |
| `EFFECTGUARD_V2` | `json` | 7,103 |
| `EFFECTGUARD_V2` | `low_high_legacy` | 2 |
| `EFFECTGUARD_V2` | `text_scan` | 49 |
| `EFFECTGUARD_V2` | `unparsed:repair_fallback` | 14 |
| `PROJ_GUARD_V2` | `json` | 7,103 |
| `PROJ_GUARD_V2` | `low_high_legacy` | 2 |
| `PROJ_GUARD_V2` | `text_scan` | 49 |
| `PROJ_GUARD_V2` | `unparsed:repair_fallback` | 14 |

## Caveat

The audit replays BASE proposals generated before the no-system prompt fix, so it tests guard-comparison proposal sharing rather than the distribution of a fresh no-system prompt.

Split artifact: `effectbench_omega/outputs/shared_proposal_v2_audit_all_local`.
