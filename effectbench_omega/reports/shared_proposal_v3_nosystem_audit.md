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
| `BASE` | `json` | 7,082 |
| `BASE` | `low_high_legacy` | 8 |
| `BASE` | `text_scan` | 52 |
| `BASE` | `unparsed:repair_fallback` | 26 |
| `EFFECTGUARD_V2` | `json` | 7,082 |
| `EFFECTGUARD_V2` | `low_high_legacy` | 8 |
| `EFFECTGUARD_V2` | `text_scan` | 52 |
| `EFFECTGUARD_V2` | `unparsed:repair_fallback` | 26 |
| `PROJ_GUARD_V2` | `json` | 7,082 |
| `PROJ_GUARD_V2` | `low_high_legacy` | 8 |
| `PROJ_GUARD_V2` | `text_scan` | 52 |
| `PROJ_GUARD_V2` | `unparsed:repair_fallback` | 26 |

## Caveat

Fresh no-system-prompt BASE proposals are replayed to BASE, PROJ_GUARD_V2, and EFFECTGUARD_V2, removing the prior source-prompt caveat.

Split artifact: `effectbench_omega/outputs/shared_proposal_v3_nosystem_all_local`.
