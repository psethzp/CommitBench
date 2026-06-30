# AGENTS.md — Exact handoff for review-rescue agents

## Global mission

Turn the current Effect Kernel / CommitBench submission into a defensible ARR/EACL paper by fixing the review blockers: novelty positioning, close SOTA, reproducible model provenance, artifact hygiene, direct baselines, human/expert validation, uncertainty, and EffectGuard framing.

Public paper name should be changed from `CommitBench` to `EffectKernelBench` unless the PI overrides this.

## Global rules

1. No broad new model sweeps.
2. No Bedrock/API assumptions.
3. 4×L40 local GPUs only.
4. Final paper exposes one canonical split: `final_paired_control`.
5. Do not expose development split labels: `v1`, `v2`, `v3`, `legacy`, `minimal_plus`, `workflow_smoke`.
6. Do not call projection baselines official reimplementations.
7. Every paper number must map to a claim-registry row and a source file.
8. All final artifacts must pass clean-environment checks.

---

## Agent 1 — Paper positioning agent

### Inputs

- Current manuscript source.
- `SOTA_POSITIONING_MATRIX.md`.
- Review markdown.
- Final results tables.

### Tasks

1. Rename paper to `EffectKernelBench` or `TraceKernelBench`.
2. Rewrite abstract around this claim:

   > complete-trace Pareto effect certification with replayable witnesses for successful tool-agent traces.

3. Add related work paragraphs for:
   - tau-bench/tau2/tau3
   - ToolSandbox
   - multi-turn degradation regimes
   - AgentDojo
   - ToolEmu
   - ToolSword
   - MobileSafetyBench
   - SafeAgentBench
   - Progent
   - ToolChoiceConfusion/CMTF
   - RACG
   - ToolPrivBench
   - Cordon
   - SkillGuard
4. Add a novelty-boundary table with columns:

```text
Prior line | What it checks | What our certificate adds | Baseline/projection used
```

5. Replace “EffectGuard beats SOTA” with “EffectGuard is a no-oracle reference controller / constructive upper bound.”
6. Ensure Limitations is in the main paper.

### Output

- `paper/main.tex`
- `paper/sections/related_work.tex`
- `paper/sections/limitations.tex`
- `paper/tables/novelty_boundary.tex`

### Done criteria

- No unsupported “first least-effect benchmark” claim.
- No stale 204,800/frontier/API claims.
- No hidden v1/v2/v3 labels.
- 8-page ARR long-paper body before references/appendices.

---

## Agent 2 — Artifact cleanup agent

### Inputs

- Current artifact directory.
- `ARTIFACT_REQUIREMENTS.md`.

### Tasks

1. Build a clean artifact tree from scratch:

```text
EffectKernelBench_artifact/
  README.md
  LICENSE
  environment.lock
  configs/
  scripts/
  effectkernelbench/
  data/
  manifests/
  outputs/
  tables/
  figures/
  metrics/
  witness_bundles/
  tests/
  hashes/
```

2. Remove stale directories and references:

```text
minimal_plus
workflow_smoke
legacy
v1
v2
v3
bedrock
api_frontier
old_claim_registry
```

3. Fix `scripts/run_online.py --help`. It must not import Bedrock or unavailable clients at import time.
4. Fix `scripts/reproduce.py --check-only` so it passes.
5. Add SHA-256 manifest:

```bash
find . -type f | sort | xargs sha256sum > hashes/SHA256SUMS.txt
```

6. Add `scripts/verify_claim_registry.py`.
7. Add `scripts/final_submission_gate.py`.

### Output

- `EffectKernelBench_artifact.zip`
- `artifact_check_report.md`

### Done criteria

All commands pass:

```bash
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_online.py --help
pytest -q tests
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
```

---

## Agent 3 — Model-provenance agent

### Inputs

- Local model paths for:
  - Mistral-Small-3.2-24B-Instruct
  - Qwen3.6-35B-A3B
  - Gemma-3-27B-it
  - Llama-3.3-70B-AWQ
- `rescue_config.yaml`

### Tasks

1. Check whether full raw proposal logs exist for the final no-system prompt run.
2. If missing, run fresh proposal generation:

```text
128 tasks × 7 regimes × 2 seeds × 4 models × BASE_PROPOSAL = 7,168 calls
```

3. Save raw outputs before parsing.
4. Save model revisions, backend versions, prompts, decoding params, timestamps/run IDs, token counts if available, repair logs, and hardware manifest.
5. Replay deterministic guards from the frozen proposals:

```text
BASE
PROJ_GUARD
EFFECTGUARD_REF
```

6. Produce final paired-control ledgers and claim-registry source files.

### Output

```text
outputs/model_proposals_final_no_system/raw_model_outputs.parquet
outputs/model_proposals_final_no_system/api_logs.parquet
outputs/model_proposals_final_no_system/model_revision_manifest.csv
outputs/model_proposals_final_no_system/prompt_templates.json
outputs/model_proposals_final_no_system/parse_failures.csv
outputs/final_paired_control/certificates.parquet
outputs/final_paired_control/ledger.parquet
outputs/final_paired_control/summary.json
```

### Done criteria

- `new_model_calls > 0` for proposal-generation stage.
- Offline replay logs clearly say they are replaying from `raw_model_outputs.parquet`.
- Paper wording says model proposals are generated fresh once, then systems are paired by deterministic replay.

---

## Agent 4 — Direct-baseline agent

### Inputs

- Final paired-control proposals.
- Effect signatures.
- Policy/admissibility definitions.
- `BASELINE_SPECS.md`.

### Tasks

Implement and score these baselines:

1. `FINAL_STATE`
2. `PROGENT_DSL_LITE`
3. `CMTF_CONTRACT`
4. `RACG_LITE`
5. `TOOLPRIV_DETECTOR`
6. `CORDON_LITE`
7. `REVISABILITY_ONLY`
8. `MODERN_PROJECTION_STACK`
9. `KERNEL_FULL`

For each, produce:

```text
accepted_successes
residual_strict_excess
false_denial
raw_success_retention
added_turns / burden if applicable
```

### Output

```text
tables/direct_baselines.csv
tables/direct_baselines.tex
reports/direct_baselines.md
```

### Done criteria

- Baselines are explicitly labeled as deterministic approximations/projections.
- There is at least one row for least privilege, CMTF, RACG, ToolPriv, and Cordon classes.
- Claims do not say “official SOTA reproduction.”

---

## Agent 5 — Human/expert-validation agent

### Inputs

- Witness bundles.
- `ANNOTATION_PROTOCOL.md`.

### Tasks

1. Sample 300 bundles:
   - 75 strict-excess
   - 75 minimal/nondominated
   - 50 necessary-high
   - 50 incomparable
   - 50 projection-residual
2. Create blind annotation CSV/HTML forms.
3. Get 2–3 independent annotations per bundle.
4. Compute:
   - label agreement
   - witness preference agreement
   - terminal-equivalence agreement
   - admissibility agreement
   - effect-dimension agreement
   - kappa/alpha
5. Create disagreement examples and corrections.

### Output

```text
annotation/annotation_sample.csv
annotation/annotation_guidelines.md
annotation/annotation_results.csv
annotation/annotation_report.md
tables/human_validation.tex
```

### Done criteria

- At least 2 annotators per item.
- Agreement metrics reported honestly.
- Disagreements included in limitations.

---

## Agent 6 — Stats/uncertainty agent

### Inputs

- Final result ledgers.
- Baseline tables.
- Annotation results.

### Tasks

1. Paired bootstrap over task IDs, 10,000 samples.
2. Cluster bootstrap by task family, regime, and model.
3. Leave-one-model/family/regime analysis.
4. Confidence intervals for all main deltas.

### Output

```text
tables/main_results_with_ci.csv
tables/main_results_with_ci.tex
tables/leave_one_robustness.csv
tables/leave_one_robustness.tex
reports/uncertainty_report.md
```

### Done criteria

- Every main paper point estimate has CI or robustness support.
- Direction of headline claims survives leave-one checks.

---

## Agent 7 — Runtime/no-oracle agent

### Inputs

- Runtime guard implementation.
- Evaluator implementation.

### Tasks

1. Static scan for forbidden evaluator/gold/frontier fields in runtime code.
2. Sentinel test: inject adversarial forbidden fields and confirm decisions do not change.
3. Prove/describe prefix-visible decision invariant.
4. Produce a no-oracle audit table.

### Output

```text
reports/no_oracle_static_scan.md
reports/no_oracle_sentinel.md
tables/no_oracle_audit.tex
```

### Done criteria

- 0 static forbidden-field violations.
- 100% sentinel invariance.
- Paper clearly labels EffectGuard as reference controller unless deployability proof is accepted by PI.

---

## Agent 8 — Final submission gate agent

### Inputs

- Paper PDF/source.
- Artifact ZIP.
- Claim registry.

### Tasks

Run final checks:

```bash
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml --dry-run false
pytest -q tests
python scripts/verify_claim_registry.py --registry metrics/claim_registry.csv
python scripts/final_submission_gate.py --strict
pdffonts paper.pdf
pdfinfo paper.pdf
```

Also run text scans:

```text
CommitBench
v1
v2
v3
legacy
minimal_plus
workflow_smoke
Bedrock
GPT-5
Claude
Gemini
204,800
20,480
human audit over 2,400
faithful SOTA
best paper
```

### Output

```text
FINAL_SUBMISSION_REPORT.md
```

### Done criteria

- All checks pass.
- Any remaining banned term is justified in the report.
- The artifact opens and reproduces from clean checkout.
