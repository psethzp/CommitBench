# EffectKernelBench: Certificate Semantics for Least-Effect Tool-Agent Evaluation

## Abstract

Tool-agent evaluations usually ask whether an agent reached a correct final state. In many deployed workflows, however, multiple successful traces can differ sharply in privacy exposure, write scope, reversibility, user burden, observability, compensation cost, and contract fragility. We introduce EffectKernelBench, an evaluation artifact for complete-trace least-effect certification. Given a successful trace, the verifier enumerates admissible task-equivalent alternatives and certifies whether the observed trace is nondominated, strictly dominated by a lower-effect witness, necessary-high, or incomparable. Across a local open-weight 21,504-trajectory paired-control split, final-state success substantially overstates certified least-effect success: BASE has 56.21% strict excess among successful traces. Deterministic projection baselines reduce but do not remove residual strict excess, while an effect-aware no-oracle reference controller removes residual strict excess in this scaffold. The artifact includes raw local model proposal provenance for 7,168 calls, a 512-call fresh smoke, direct projection baselines, uncertainty tables, no-oracle reports, canonical certificates, replayable bundles, and a claim registry. Human validation is intentionally not claimed in this freeze; a blinded 300-bundle annotation package is included only for optional follow-up.

## 1. Introduction

Final-state success is an incomplete proxy for safe tool-agent behavior. A support agent can solve a refund request by editing the right order, but it may also expose excess account data, issue unnecessary external notifications, create a harder-to-reverse write, or impose avoidable burden on the user. These traces can be terminally successful while still being dominated by another trace that achieves the same task outcome with lower effects.

EffectKernelBench evaluates this gap directly. The core object is an effect kernel: a certificate semantics over complete tool traces. The verifier compares a trace against admissible task-equivalent alternatives under a declared effect lattice. It labels strict excess only when a successful lower-effect witness exists. It reports incomparability separately and records necessary-high decisions when higher-effect actions are required by the task.

The paper makes a narrow claim:

> Among task-equivalent successful tool-agent traces, final-state success and several projected safeguards can accept strictly Pareto-dominated traces. Effect kernels provide replayable witness certificates, and a no-oracle reference controller demonstrates how the certificate semantics can guide lower-effect substitution in a local open-weight scaffold.

This is not a frontier leaderboard and not a claim of universal online optimality. It is a reproducible certificate-semantics artifact.

## 2. Effect Kernel Semantics

Each trace is converted into an effect ledger over seven ordered dimensions:

| Dimension | Examples of movement |
|---|---|
| Data scope | self record to linked account to third-party/account-wide data |
| Write scope | draft to item-level write to account/order-level write |
| Reversibility | idempotent to reversible to compensable to irreversible |
| Observability | private to user-visible to partner-visible to public/external |
| Compensation cost | zero to local rollback to service credit to financial/legal work |
| User burden | no ask to confirmation to multi-turn clarification to manual task |
| Contract fragility | stable token to expiring token to byte-bound artifact |

For a task, the verifier enumerates admissible task-equivalent alternatives and computes the nondominated frontier. A successful trace is strict excess only if another admissible successful trace has no higher effect dimension and at least one lower dimension. The verifier records the witness trace, effect vectors, dominance relation, terminal-equivalence proof, and abstraction/hash-chain evidence. Incomparable and necessary-high cases are not counted as strict excess.

## 3. Systems and Baselines

The main online systems are:

| System | Role |
|---|---|
| BASE | Vanilla local model proposal followed by declared tool execution. |
| PROJ_GUARD | Projection-only safeguard baseline using local permission, contract, menu, staging, and revisability predicates. |
| EFFECTGUARD_REF | No-oracle reference controller that substitutes lower-effect admissible actions when current evidence supports the substitution. |

The artifact also includes deterministic projection baselines. These are not official reproductions of prior systems. They are faithful approximations of the kinds of predicates close methods expose.

| Baseline | What it tests |
|---|---|
| FINAL_STATE | Terminal success alone. |
| PROGENT_DSL_LITE | Least-privilege and simple program/policy constraints. |
| CMTF_CONTRACT | Causal read/write and contract-frontier checks. |
| RACG_LITE | Risk/authorization projection on top of contract checks. |
| TOOLPRIV_DETECTOR | Data/write/observability privilege projection. |
| CORDON_LITE | Transaction/outbox/reversibility projection. |
| REVISABILITY_ONLY | Reversibility and externality checks. |
| MODERN_PROJECTION_STACK | Union of the strongest deterministic projections. |
| KERNEL_FULL | The full effect-kernel certificate predicate. |

## 4. Experimental Setup

The review-facing split is `final_paired_control`.

| Item | Value |
|---|---:|
| Tasks | 128 |
| Regimes | 7 |
| Seeds | 2 |
| Local models | 4 |
| Systems | 3 |
| Final paired-control trajectories | 21,504 |
| Shared proposal groups | 7,168 |

The four local models are Mistral-Small-3.2-24B, Qwen3.6-35B-A3B, Llama-3.3-70B-AWQ, and Gemma-3-27B-it. The regimes are FULL, CONCAT, SHARDED, SNOWBALL, REVISE, MEMORY_REVISE, and ADV_EFFECT. The artifact is local/open-weight only. No Bedrock, commercial API, frontier leaderboard, or broad model sweep is used for the paper claims.

Raw model provenance is preserved for 7,168 local BASE proposal calls: raw outputs, token counts, timestamps, request IDs, latency, prompt hashes, model revisions, and server-log hashes. A separate fresh smoke generated 512 local calls using the final scripts and schema, with 0 failures and 512 merged certificates.

## 5. Results

### 5.1 Main Paired-Control Results

| System | Trajectories | Raw success | Strict-excess rate | Kernel success |
|---|---:|---:|---:|---:|
| BASE | 7,168 | 100.00% | 56.21% | 43.79% |
| PROJ_GUARD | 7,168 | 100.00% | 8.50% | 91.50% |
| EFFECTGUARD_REF | 7,168 | 100.00% | 0.00% | 100.00% |

BASE reaches terminal success in this controlled split, but more than half of successful BASE traces are strictly dominated under the effect kernel. PROJ_GUARD removes most strict excess but leaves 8.50% residual strict excess. EFFECTGUARD_REF removes residual strict excess in this scaffold. This should be read as a constructive reference-controller result, not as a universal deployed-agent claim.

The paired bootstrap estimate for BASE raw-minus-kernel success is 56.21 percentage points with a 95% interval of 55.02 to 57.37 percentage points. Leave-one model, family, and regime checks preserve the sign of the gap.

### 5.2 Direct Projection Baselines

| Baseline | Accepted successes | Residual strict excess | Residual rate | False denial rate |
|---|---:|---:|---:|---:|
| FINAL_STATE | 21,504 | 4,638 | 21.57% | 0.00% |
| PROGENT_DSL_LITE | 20,230 | 3,370 | 16.66% | 5.92% |
| CMTF_CONTRACT | 20,122 | 3,616 | 17.97% | 6.43% |
| RACG_LITE | 19,870 | 3,370 | 16.96% | 7.60% |
| TOOLPRIV_DETECTOR | 20,230 | 3,370 | 16.66% | 5.92% |
| CORDON_LITE | 20,230 | 3,370 | 16.66% | 5.92% |
| REVISABILITY_ONLY | 20,373 | 3,507 | 17.21% | 5.26% |
| MODERN_PROJECTION_STACK | 19,842 | 3,370 | 16.98% | 7.73% |
| KERNEL_FULL | 16,866 | 0 | 0.00% | 21.57% |

The direct baselines show the central projection-loss result: plausible local predicates reduce some risky traces but still accept many dominated successes. The full kernel predicate has zero residual strict excess by construction because it directly asks the dominance question.

### 5.3 Audits

| Audit | Result |
|---|---:|
| No-oracle runtime rows checked | 21,504 |
| No-oracle failures | 0 |
| Shared proposal groups paired | 7,168/7,168 |
| Fresh smoke calls | 512 |
| Fresh smoke failures | 0 |
| Native-validation rows | 4,608 |
| Necessary-high/incomparable stress rows | 3,072 |

The fresh smoke passed for all four local models. Mistral, Llama, and Gemma parsed 128/128 rows through JSON. Qwen parsed 114/128 rows through JSON, 9 through text scan, 1 through the low/high-format path, and 4 through repaired fallback. These parser paths are logged as audit metadata; the rows had 0 runner failures, 0 no-oracle failures, and completed verifier checks.

## 6. Relation to Close Methods

EffectKernelBench is closest to work on tool-agent safety, constrained execution, permissioning, contract checks, risk-aware guards, and revisability. The difference is the semantic target. These methods typically project a local predicate over a trace or action. Effect kernels certify whether a successful trace is dominated by an admissible task-equivalent lower-effect witness. This changes the question from "did the trace satisfy a guard predicate?" to "was there a successful trace with no greater effects and some strictly lower effect?"

The artifact therefore reports close methods as deterministic projections or faithful approximations, not as official SOTA reimplementations. This avoids overclaiming and makes the comparison auditable.

## 7. Limitations

The evidence is local/open-weight only. It does not support commercial-model or frontier-leaderboard claims.

The controlled split is a successful-trace certification scaffold, not a replacement for task-solving benchmarks.

The direct baselines are deterministic projections and faithful approximations, not official implementations of all named prior systems.

EFFECTGUARD_REF is a no-oracle reference controller in this scaffold, not a universal online policy.

Human/domain validation is intentionally skipped in this freeze. The artifact includes a 300-bundle blinded annotation package for optional follow-up, but the paper must not claim human agreement, kappa/alpha, human preference, or human-audited correctness.

Main claims use the declared Pareto lattice. Alternate-lattice sensitivity remains diagnostic and should not be framed as a governance-robustness theorem.

## 8. Artifact and Reproducibility

The final artifact is `EffectKernelBench_artifact.zip`. It contains the clean review-facing tree, canonical split, raw model provenance, baselines, uncertainty, no-oracle reports, fresh-smoke proof, claim registry, hashes, tests, and this paper draft. It excludes model caches, virtualenvs, old proof archives, stale manuscript/deck files, and provider/API experiments.

The primary reviewer commands are:

```bash
python scripts/reproduce.py --check-only
python scripts/reproduce.py --tables
python scripts/run_fresh_smoke.py --config configs/fresh_smoke.yaml
```

Inside the clean artifact, the fresh-smoke command verifies included 512-call smoke evidence. From the source repository, the same script can launch the GPU smoke when outputs are absent or when forced.

## 9. Conclusion

EffectKernelBench provides a certificate semantics for least-effect evaluation of successful tool-agent traces. The main result is that final-state success and several projected safeguards can accept strictly dominated successful traces, while effect-kernel certificates expose the lower-effect witnesses. The artifact is intentionally conservative: local models only, deterministic replay instead of human validation, and reference-controller wording instead of universal deployment claims.
