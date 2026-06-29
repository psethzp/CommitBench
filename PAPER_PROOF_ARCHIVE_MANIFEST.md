# CommitBench Paper-Proof Archive Manifest

Archive requested: 2026-06-26 UTC.

Target archive name:

```text
CommitBench_paper_proof_full_20260626.zip
```

## Included Scope

This archive is intended to contain the full local-only paper evidence bundle:

| Category | Included paths / examples |
|---|---|
| Top-level docs | `README.md`, `PLAN.md`, `AGENTS.md`, `COST_AUDIT.md`, `results.md`, `implementations.md`, `rebuttal_1.md` |
| Paper-facing files | `CommitBench.pdf`, `effectbench_supervisor_explainer.pptx` |
| V2 handoff docs | `V2/PLAN.md`, `V2/AGENTS.md`, `V2/Details.md`, `V2/eacl_rescue_local_only_config.yaml` |
| Code | `effectbench_omega/effectbench/`, `effectbench_omega/scripts/`, `effectbench_omega/tests/`, `pyproject.toml` |
| Configs and schemas | `effectbench_omega/configs/`, `effectbench_omega/schemas/`, `effectbench_minimal_plus_config.yaml` |
| Manifests and pins | `effectbench_omega/manifests/`, `effectbench_omega/artifacts/`, `effectbench_omega/tables/artifact_manifest.csv` |
| Generated outputs | `effectbench_omega/outputs/`, including canonical kernels and rebuttal Stage 2/3 outputs |
| Logs/jobs | `effectbench_omega/jobs/`, including local queues, stage jobs, and smoke logs |
| Reports | `effectbench_omega/reports/`, including final reproducibility, paper-ready, rebuttal Stage 2/3/4/6 reports |
| Results tables | `effectbench_omega/tables/`, including projection, uncertainty, no-oracle, CEGAR, lattice, shared-proposal, Stage 3 stress, and Stage 4 robustness tables |
| Figures | `effectbench_omega/figures/` |
| Metrics/claims | `effectbench_omega/metrics/`, including final claim registries |
| Witness bundles | `effectbench_omega/witness_bundles/` |
| Git tracking metadata | `.gitattributes`, `.gitignore` |

## Explicit Exclusions

The archive intentionally excludes non-paper or sensitive material:

```text
.env and any .env.* files
.git/
.venv/
__pycache__/ and *.pyc
.pytest_cache/
.DS_Store
effectbench_omega/models/
effectbench_omega/upstreams/
older *.zip archives
```

Rationale: model caches and upstream benchmark clones are large/re-creatable
and are pinned in `effectbench_omega/artifacts/`; secrets and local virtual
environments should never be bundled into a paper proof artifact.
