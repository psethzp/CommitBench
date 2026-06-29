# Final Submission Status

Last updated: 2026-06-29 UTC.

## Status

The experiment package is frozen after Rebuttal-2. No additional GPU
experiments are needed for the current paper claim.

| Area | Status | Evidence |
|---|---:|---|
| Main controlled split | Complete | 21,504 local/open-weight trajectories |
| Canonical verifier | Complete | Enumerated-frontier certificates, 0 unexplained mismatches |
| Fresh shared-proposal audit | Complete | v3 no-system-prompt audit, 21,504 traces |
| Full stress replay | Complete | 3,072 bundles checked, 0 failures |
| Native validation | Complete | 4,608 trajectories with real terminal failures |
| Leave-one robustness | Complete | 49 gate rows, 0 failures |
| No-oracle checks | Complete | v3 audit has 21,504/21,504 pass |
| Claim registry | Complete | 42 rows after Rebuttal-2 |
| Final anonymous artifact | Complete | Generated as `CommitBench_final_anonymous_artifact_20260629.zip` |

## Paper-Facing Result

Use the fresh no-system-prompt shared-proposal v3 audit as the clean paired
guard comparison:

| System | Trajectories | Raw success | Strict excess / success | Kernel success / success |
|---|---:|---:|---:|---:|
| `BASE` | 7,168 | 100.0000% | 56.2081% | 43.7919% |
| `PROJ_GUARD_V2` | 7,168 | 100.0000% | 8.4961% | 91.5039% |
| `EFFECTGUARD_V2` | 7,168 | 100.0000% | 0.0000% | 100.0000% |

The v3 audit supersedes the old shared-proposal caveat because its BASE
proposals were generated after the no-system-prompt fix.

## Submission Boundaries

Do claim:

- Effect Kernels as certificate semantics for least-effect tool-agent traces.
- Final-state success can overstate certified least-effect success.
- Projection-only safeguards reduce but do not remove strict excess.
- `EFFECTGUARD_V2` is a no-oracle reference controller in this local scaffold.
- Native validation demonstrates the machinery also handles terminal failures.

Do not claim:

- Commercial/frontier leaderboard coverage.
- Human-evaluation validation.
- Faithful reproduction of named prior systems.
- Universal optimal online control.
- Alternate-lattice robustness as a main claim.

## Artifact Boundary

The final anonymous zip excludes:

- local secrets and environment files;
- `.git`, virtualenvs, model caches, and upstream clones;
- old proof zip files;
- the stale historical PDF and presentation deck;
- historical planning memos with identity-bearing or obsolete internal notes.

Use `PAPER_EACL2027_REWRITE.md` as the current paper rewrite scaffold.
