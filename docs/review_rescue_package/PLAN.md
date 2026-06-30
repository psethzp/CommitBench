# PLAN.md — EACL/ARR rescue plan after critical review

## 0. Triage verdict

The review identifies real blockers. Treat it as a pre-submission reject and fix the paper before ARR/EACL. The idea is still viable, but the submission must be reframed from a broad “new least-effect benchmark / controller” claim into a narrower and stronger claim:

> We introduce a complete-trace Pareto effect-certification layer for successful tool-agent traces. The artifact provides enumerated task-equivalent alternatives, replayable lower-effect witnesses, and nondominance certificates. Runtime guards and prior safety mechanisms are compared as projections of this certificate question.

The next work is mostly **artifact cleaning, direct baselines, validation, uncertainty, and writing**. Do **not** add more broad model families.

## 1. Non-negotiable changes

### 1.1 Rename the paper

Do not submit as `CommitBench`. Use one of:

- `EffectKernelBench: Replayable Least-Effect Certificates for Tool-Agent Traces`
- `TraceKernelBench: Complete-Trace Least-Effect Certification for Tool Agents`
- `EffectTrace: Pareto Witnesses for Least-Effect Tool-Agent Evaluation`

Reason: `CommitBench` is already used for a commit-message-generation benchmark. Avoid confusion and reviewer annoyance.

### 1.2 Narrow the novelty claim

Replace broad claims like:

- “first least-effect benchmark”
- “new SOTA tool-agent benchmark”
- “EffectGuard beats all prior systems”

with:

- “complete-trace Pareto certification with replayable witnesses”
- “post-hoc certificate semantics over successful traces”
- “projection baselines corresponding to prior safeguards leave residual strict-excess”
- “EffectGuard is a reference controller / constructive upper bound, not the central contribution”

### 1.3 Remove all v1/v2/v3 exposure

The final paper and artifact should expose one canonical split:

```text
final_paired_control
```

Development split names may remain only in archived internal folders excluded from the submission artifact. In the final paper, earlier runs become:

- native validation
- necessary-high/incomparable stress
- leave-one robustness
- CEGAR stress
- no-oracle audit
- certificate replay

No reviewer should see `v1`, `v2`, `v3`, `legacy`, `minimal_plus`, or `workflow_smoke` unless those are in an explicitly named `dev_archive_NOT_FOR_REVIEW/` folder that is excluded from the artifact.

## 2. Required workstreams

### Workstream A — Manuscript repositioning

Owner: Paper agent.

Deliverables:

1. New title using `EffectKernelBench` or equivalent.
2. One-sentence contribution:

   > We contribute an enumerated complete-trace effect-kernel certificate that labels successful tool-agent traces as nondominated, strict-excess, necessary-high, or incomparable.

3. Related work section that directly addresses:
   - tau-bench / tau2 / tau3
   - ToolSandbox
   - multi-turn degradation regimes
   - AgentDojo
   - ToolEmu
   - ToolSword
   - MobileSafetyBench
   - SafeAgentBench
   - Progent
   - CMTF / ToolChoiceConfusion
   - RACG
   - ToolPrivBench
   - Cordon
   - SkillGuard
4. A novelty-boundary table: prior work question vs our added certificate question.
5. EffectGuard framed as **reference controller**, not competitive SOTA.
6. Limitations section in main paper.

Acceptance gate:

- No “first benchmark for least-effect agents” phrasing.
- No “SOTA leaderboard” phrasing.
- No claim that projection baselines are faithful reimplementations unless they are.

### Workstream B — Artifact reproducibility

Owner: Artifact agent.

Deliverables:

1. Clean artifact zip from a fresh directory, not a development tree.
2. `README.md` with exactly three commands:

```bash
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
```

3. `scripts/run_online.py --help` must not import Bedrock or any missing backend.
4. `scripts/reproduce.py --check-only` must pass from a clean checkout.
5. SHA-256 manifest for every released table, figure, parquet, config, and script.
6. Claim registry mapping every paper number to a source file, filter, and script.
7. No stale paths: remove `minimal_plus`, `workflow_smoke`, `legacy`, `bedrock`, `v1`, `v2`, `v3` from review-facing configs and tables.

Acceptance gate:

```bash
python -m zipfile -t EffectKernelBench_artifact.zip
unzip -t EffectKernelBench_artifact.zip
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
pytest -q tests
```

### Workstream C — Model-generation provenance

Owner: Inference/provenance agent.

The review’s artifact objection is severe: final logs looked like offline replay, not model inference. Fix this by clearly separating:

- **fresh model proposal generation**: actual local model calls producing raw proposals;
- **paired replay**: deterministic guard/evaluator intervention from the frozen proposals.

Required if full raw model outputs are not already present:

```text
Run fresh no-system BASE proposal generation:
128 tasks × 7 regimes × 2 seeds × 4 models × 1 proposal system = 7,168 local model calls
```

Save:

```text
outputs/model_proposals_final_no_system/raw_model_outputs.parquet
outputs/model_proposals_final_no_system/api_logs.parquet
outputs/model_proposals_final_no_system/model_revision_manifest.csv
outputs/model_proposals_final_no_system/prompt_templates.json
outputs/model_proposals_final_no_system/parse_failures.csv
outputs/model_proposals_final_no_system/inference_server_logs.jsonl
```

Every row must include:

- task_id, family, regime, seed, model_id, model_revision/hash
- prompt template ID and rendered prompt hash
- decoding parameters
- inference backend and version
- timestamp/run_id
- raw text before parsing
- parsed action proposal
- token counts or vLLM/SGLang equivalent accounting if available
- parse/repair status
- GPU host/hardware summary

Then pair all systems by replaying guards from the same proposals:

```text
BASE
PROJ_GUARD
EFFECTGUARD_REF
```

If 7,168 calls cannot be run, run the smoke below and explicitly state that the main results are frozen-replay results from previously generated local proposals. This is weaker.

Minimum fresh smoke:

```text
32 tasks × 4 regimes × 1 seed × 4 models = 512 fresh model calls
```

Acceptance gate:

- full proposal provenance exists, or the paper explicitly weakens all empirical claims;
- `run_fresh_smoke.py` regenerates a stratified sample and matches the saved parsing/ledger format.

### Workstream D — Direct baselines against close methods

Owner: Baseline agent.

Add deterministic / faithful-approximation baselines. Do not claim they are official implementations.

Required baselines:

1. `PROGENT_DSL_LITE` — least-privilege policy control.
2. `CMTF_CONTRACT` — causal minimal next-step tool frontier.
3. `RACG_LITE` — risk-aware causal gating using risk labels and authorization preconditions.
4. `TOOLPRIV_DETECTOR` — flags high-privilege selection when a lower-privilege witness suffices.
5. `CORDON_LITE` — semantic transaction staging/outbox/commit/rollback projection.
6. `STANDARD_FINAL_STATE` — final state / task success only.

Compute each over `final_paired_control` proposals and canonical enumerated frontier. Main table columns:

```text
system, native_predicate, accepted_successes, residual_strict_excess, false_denial, raw_success_retention, added_turns, notes
```

Acceptance gate:

- Every closest-method class has at least one row.
- Every row states “faithful deterministic approximation” or “projection baseline,” not “official SOTA.”
- Projection residuals remain nonzero for at least Progent/CMTF/RACG/Cordon-like baselines.

### Workstream E — Human/domain-expert validation

Owner: Annotation agent.

The review explicitly demands independent validation of the effect lattice and witnesses. Run this; it requires no GPUs.

Recommended sample:

```text
300 bundles total
- 75 strict-excess
- 75 minimal/nondominated
- 50 necessary-high
- 50 incomparable
- 50 projection-residual cases
```

Annotators:

- Minimum: 2 independent annotators + adjudication.
- Better: 3 annotators.
- Annotators should not see model/system name.

Questions per bundle:

1. Do the model and witness traces satisfy the same terminal task goal?
2. Is the witness executable/admissible under the policy?
3. For each effect dimension, which trace is lower/equal/higher?
4. Does one trace strictly dominate the other?
5. Is the high-effect trace necessary, excessive, or an incomparable tradeoff?
6. Is the lower-effect witness preferable for deployment?

Metrics:

- Cohen’s kappa or Fleiss’ kappa for categorical labels.
- Krippendorff’s alpha for ordinal effect-dimension judgments.
- Human agreement with kernel labels.
- Human preference for witness over model trace.
- Disagreement analysis with examples.

Acceptance gates:

```text
human/kernel label agreement >= 80%
witness-preferable rate for strict-excess >= 85%
terminal-equivalence agreement >= 90%
admissibility agreement >= 85%
Cohen/Fleiss kappa >= 0.60 preferred, >=0.50 minimum with caveats
```

If this fails, do not hide it. Use disagreements to refine lattice definitions and report limitations.

### Workstream F — Uncertainty and robustness

Owner: Stats agent.

Add uncertainty intervals to all main result tables.

Required:

1. Paired bootstrap over task IDs, 10,000 resamples.
2. Cluster bootstrap by family/regime/model.
3. Leave-one-model, leave-one-family, leave-one-regime tables.
4. Confidence intervals for:
   - BASE strict-excess
   - projection residuals
   - EffectGuard residuals
   - raw-vs-kernel gap
   - native validation success/effect rates
   - human validation agreement

Acceptance gate:

- Direction of main claims stable under leave-one analyses.
- Main differences have intervals not crossing zero where claimed.

### Workstream G — EffectGuard status and no-oracle proof

Owner: Formal/runtime agent.

Rewrite EffectGuard as:

> a no-oracle reference controller / constructive upper bound over declared current-state effects.

Do not call it a SOTA deployable baseline unless you prove deployability. Add a proof-style invariant:

```text
EffectGuard decision at time t is a function only of prefix-visible user turns, prior observations, public policy, declared effect signatures, current abstract state, and currently admissible lower-bound continuations. It is not a function of offline frontier IDs, gold terminal state, future user turns, final outcome, or evaluator labels.
```

Implementation audit:

- Static scan for forbidden imports/fields from evaluator/kernel scorer in runtime code.
- Runtime sentinel injection: forbidden fields are set to adversarial values; decisions must not change.
- Shared proposal audit: same proposal distribution for BASE, projections, and EffectGuard.

Acceptance gate:

```text
static forbidden-field scan: 0 violations
sentinel decision-invariance: 100%
shared proposal pairing: 100% groups paired
```

## 3. Optional work for best-paper-level shot

Only after all required gates pass:

1. External bridge: 32–64 cases from tau3, ToolSandbox, or AgentDojo-style tasks, using 2 local models.
2. Model-ranking inversion: show that raw success and kernel success rank models/systems differently.
3. More formal theorem: preservation/minimality relative to effect-output suffix transducer, plus a clear non-guarantee theorem for hidden effects.

This is not required for a credible EACL attempt, but it helps with “Best Paper” credibility.

## 4. Timeline to ARR/EACL

EACL 2027 ARR deadline: 2026-08-03.

### Days 1–2

- Rename paper and repo.
- Remove stale artifact labels.
- Fix scripts and imports.
- Add final config.

### Days 3–4

- Run or reconstruct fresh model-proposal provenance.
- Add raw outputs and local inference logs.
- Implement `run_fresh_smoke.py`.

### Days 5–6

- Implement direct projection baselines: Progent-lite, CMTF, RACG-lite, ToolPriv detector, Cordon-lite.
- Regenerate tables.

### Days 7–9

- Human/expert annotation of 300 bundles.
- Compute agreement and disagreement analysis.

### Days 10–11

- Add CIs, cluster bootstrap, leave-one robustness.
- Finalize stress/native/audit appendix.

### Days 12–15

- Rewrite paper to 8 pages.
- Add SOTA table and precise novelty claim.
- Reframe EffectGuard.

### Days 16–17

- Final artifact build from clean environment.
- Run zip, tests, reproduce, claim-registry checks.
- Run ACL/ARR formatting checks.

### Days 18–20

- Internal review and final edits.
- Submit.

## 5. What not to do

- Do not add more Qwen/Phi/random models.
- Do not claim commercial/frontier model coverage.
- Do not call projections official SOTA reimplementations.
- Do not rely on offline replay as the only evidence of model behavior.
- Do not hide 100% controlled raw success; explain it as a controlled successful-trace certificate setting.
- Do not submit with stale scripts, broken imports, or zero-token replay logs as the only provenance.
