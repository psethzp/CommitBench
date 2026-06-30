# PAPER_REWRITE_BLUEPRINT.md — final ARR/EACL paper shape

## Title

Recommended:

> EffectKernelBench: Replayable Least-Effect Certificates for Tool-Agent Traces

Avoid:

> CommitBench

## Abstract skeleton

Use this structure:

1. Existing tool-agent benchmarks and safeguards evaluate final state, path validity, privilege, contracts, transactions, or risk exposure.
2. These are necessary but projected: a successful trace can remain unnecessarily invasive relative to another task-equivalent success.
3. We introduce Effect Kernels: complete-trace Pareto certificates with replayable lower-effect witnesses.
4. Labels: nondominated, strict-excess, necessary-high, incomparable.
5. Experiments: 21,504 final paired local trajectories with four open-weight models; raw success fixed/controlled to isolate least-effect certification; projection baselines reduce but do not eliminate residual strict-excess; EffectGuard reference controller reaches the frontier in the controlled setting.
6. Audits: raw model provenance, direct baselines, human validation, CIs, CEGAR, no-oracle, native validation, stress split.
7. Limitations: closed/wrapped tools, declared effects, domain-governed lattice, EffectGuard reference status.

## 8-page main paper structure

### 1. Introduction

Key claim:

> Final-state success is not enough; the missing label is whether the complete successful trace is dominated by another task-equivalent trace with lower declared effects.

One motivating example:

```text
edit passenger name vs cancel+rebook+notify
```

End with contributions:

1. Effect Kernel certificate semantics.
2. Enumerator/verifier and replayable witness bundles.
3. Projection-baseline comparison to closest safety mechanisms.
4. Local open-weight evaluation plus human/reproducibility audits.

### 2. Effect Kernel certificates

Define:

```text
M = (S, A, delta, s0, G, equiv_q, E)
Eff(tau)
strict dominance
strict-excess
necessary-high
incomparable
certificate = terminal equivalence + witness or nondominance proof + effect vectors + state hashes
```

Add theorem/proposition:

- preservation under suffix-complete abstraction;
- projection incompleteness;
- hidden side effects invalidate certificates.

### 3. Relationship to prior tool-agent safety work

Use the novelty-boundary table. Do not bury this in appendix.

Main wording:

> Progent, CMTF, RACG, ToolPrivBench, Cordon, and SkillGuard address privilege, exposure, transactions, and permissions. We compare to these as deterministic projections and ask what remains after those predicates accept a trace.

### 4. Experimental design

Separate clearly:

- controlled successful-trace certificate split: main semantics experiment;
- native validation: terminal success can fail;
- stress split: necessary-high/incomparable;
- human validation;
- artifact/provenance.

State:

> The controlled split is not a task-solving leaderboard. It fixes successful proposals to isolate the least-effect certificate question.

### 5. Main results

Tables:

1. Main results with CI.
2. Direct projection baselines.
3. Stress + native validation.
4. Audit/validation table.

Avoid too many plots.

### 6. Discussion

Explain:

- why 100% raw success in controlled split is by design;
- why EffectGuard is reference/constructive upper bound;
- why projection residual is the central empirical finding;
- where the kernel is useful: audits, benchmarks, policy development.

### 7. Limitations

Must be in main paper.

Include:

- closed/wrapped tools only;
- declared effects only;
- hidden/delayed effects;
- domain-governed effect lattice;
- human validation not universal moral truth;
- reference controller status;
- external environment validation limited.

## Claims to keep

- Complete-trace Pareto certificate with replayable witnesses.
- Projection predicates are incomplete for complete-trace least-effect labels.
- Controlled results show large strict-excess under declared effect lattice.
- Human/expert validation supports many witness labels.
- Artifact is reproducible from raw local model proposals and paired replay.

## Claims to remove

- “first least-effect benchmark” without qualification.
- “guaranteed acceptance.”
- “best paper.”
- “faithful SOTA reimplementation.”
- “frontier commercial model evidence.”
- “EffectGuard universally optimal.”
- “raw success benchmark” as headline.

## Main table plan

### Table 1 — Novelty boundary

Columns:

```text
Prior line | Local/runtime question | Our complete-trace certificate question | Baseline/projection
```

### Table 2 — Experimental blocks

Rows:

```text
final_paired_control
native_validation
necessary_high_incomparable_stress
human_validation
fresh_smoke
```

### Table 3 — Main results with CI

Rows:

```text
BASE
PROGENT_DSL_LITE
CMTF_CONTRACT
RACG_LITE
CORDON_LITE
MODERN_PROJECTION_STACK
EFFECTGUARD_REF
KERNEL_FULL
```

### Table 4 — Human validation and artifact audit

Rows:

```text
model proposal provenance
claim registry
canonical enumeration
certificate replay
CEGAR
no-oracle
human/expert validation
fresh smoke
```

## Appendix

- Full lattice definitions.
- Annotation guidelines.
- Baseline implementation details.
- Extra robustness tables.
- Full artifact manifest.
- Worked witness examples.
