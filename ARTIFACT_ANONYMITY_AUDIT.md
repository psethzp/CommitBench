# Artifact Anonymity Audit

Last updated: 2026-06-29 UTC.

## Final Artifact

The final anonymous artifact bundle is:

```text
CommitBench_final_anonymous_artifact_20260629.zip
```

It is built from a temporary staging directory rather than directly zipping the
working tree. This allows the package to keep the experiment evidence while
excluding stale or identity-bearing material.

## Excluded From Final Zip

| Exclusion | Reason |
|---|---|
| `.env`, `.env.*` | Local secrets |
| `.git/` | Repository identity/history |
| `.venv/`, `.pytest_cache/`, `__pycache__/` | Local execution caches |
| `effectbench_omega/models/` | Model cache placeholders, not paper artifacts |
| `effectbench_omega/upstreams/` | Cloned upstream repos are pinned/re-creatable |
| Generated smoke/dry-run outputs | Useful for development, not needed for paper proof |
| Existing `*.zip` files | Prevent nested stale archives |
| Historical `CommitBench.pdf` | Stale manuscript; not submission-ready |
| Presentation deck | Identity-bearing and not part of the paper artifact |
| `rebuttal_1.md`, `rebuttal_2.md` | Internal planning memos with stale warnings |
| Archived Bedrock-era runbook/cost notes | Not active local-only evidence |

## Included Evidence

The final zip keeps:

- source code, scripts, tests, configs, schemas, and manifests;
- local/open-weight outputs, reports, tables, figures, metrics, and witness bundles;
- Rebuttal-2 fresh no-system-prompt v3 audit artifacts;
- final runbooks and Markdown handoff docs;
- claim registry and replay/robustness/no-oracle evidence.

## Scrub Checks

The final staging directory is checked for:

- local absolute workspace paths;
- user-name identifiers;
- Google Slides links;
- stale large-grid episode claims;
- stale focused-frontier block claims;
- active commercial/frontier leaderboard claims;
- stale human-evaluation claims;
- nested zip files;
- stale PDF/PPT binaries.
- generated smoke/dry-run artifact directories.

The final zip is also checked with `unzip -tq`.
